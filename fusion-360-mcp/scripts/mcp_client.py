"""Small, synchronous Streamable HTTP client; no automatic mutation retries."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import time
import tomllib
import urllib.request
import uuid
import ipaddress
from urllib.parse import urlsplit
from safe_data import strict_json


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise RuntimeError('MCP redirects are disabled; configure the intended endpoint directly.')


def redact(value,secrets=()):
    if isinstance(value,dict):
        return {key:('[REDACTED]' if str(key).lower() in ('authorization','password','secret','api_key','access_token','refresh_token','mcp-session-id') else redact(item,secrets)) for key,item in value.items()}
    if isinstance(value,list):return [redact(item,secrets) for item in value]
    if isinstance(value,str):
        for secret in sorted((s for s in secrets if s),key=len,reverse=True):value=value.replace(secret,'[REDACTED]')
    return value


def connection_settings():
    """Resolve external settings without requiring a particular agent host."""
    explicit_url = os.environ.get('FUSION_MCP_URL')
    explicit_config = os.environ.get('FUSION_MCP_CONFIG')
    if explicit_url:
        server = {'url': explicit_url}
        source = 'FUSION_MCP_URL'
        if os.environ.get('FUSION_MCP_TIMEOUT_SEC'):
            server['tool_timeout_sec'] = os.environ['FUSION_MCP_TIMEOUT_SEC']
        if os.environ.get('FUSION_MCP_BEARER_TOKEN_ENV'):
            server['bearer_token_env_var'] = os.environ['FUSION_MCP_BEARER_TOKEN_ENV']
    elif explicit_config:
        path = Path(explicit_config).expanduser()
        server = json.loads(path.read_text(encoding='utf-8-sig'))
        source = str(path)
    else:
        if os.environ.get('CODEX_HOME'):
            config_home = Path(os.environ['CODEX_HOME'])
        else:
            profile = Path(os.environ['USERPROFILE']) if os.environ.get('USERPROFILE') else Path.home()
            config_home = profile / '.codex'
        path = config_home / 'config.toml'
        if not path.exists():
            raise RuntimeError('Set FUSION_MCP_URL or FUSION_MCP_CONFIG, or configure fusion360 in the host MCP settings.')
        config = tomllib.loads(path.read_text(encoding='utf-8-sig'))
        server = config.get('mcp_servers', {}).get('fusion360', {})
        source = str(path)
    if not isinstance(server, dict) or server.get('enabled') is False or not isinstance(server.get('url'), str):
        raise RuntimeError('Configure and enable a Fusion MCP connection with a URL.')
    parsed = urlsplit(server['url'])
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Fusion MCP URL must be HTTP(S), without embedded credentials or a fragment.')
    try:loopback=ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:loopback=parsed.hostname.lower()=='localhost'
    if parsed.scheme=='http' and not loopback and server.get('allow_insecure_remote_http') is not True:
        raise ValueError('Non-loopback HTTP requires explicit allow_insecure_remote_http configuration; prefer HTTPS.')
    timeout = float(server.get('tool_timeout_sec', 60))
    if not 0 < timeout < float('inf'):
        raise ValueError('Fusion MCP timeout must be a positive finite number.')
    return server, source


class FusionClient:
    def __init__(self, log_dir):
        self.started = time.perf_counter()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        server, self.config_source = connection_settings()
        self.config_path = None if self.config_source == 'FUSION_MCP_URL' else Path(self.config_source)
        self.url = server['url']
        self.timeout = float(server.get('tool_timeout_sec', 60))
        self.max_response_bytes=int(server.get('max_response_bytes',16*1024*1024))
        if not 1024<=self.max_response_bytes<=64*1024*1024:raise ValueError('MCP response limit must be 1 KiB–64 MiB.')
        self.opener=urllib.request.build_opener(NoRedirects())
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        self.headers.update(server.get('http_headers', {}))
        for header, variable in server.get('env_http_headers', {}).items():
            if variable not in os.environ:
                raise RuntimeError('Configured MCP header environment variable is missing: ' + variable)
            self.headers[header] = os.environ[variable]
        bearer = server.get('bearer_token_env_var')
        if bearer:
            if bearer not in os.environ:
                raise RuntimeError('Configured MCP token environment variable is missing: ' + bearer)
            self.headers['Authorization'] = 'Bearer ' + os.environ[bearer]
        self.secrets=[v for k,v in self.headers.items() if k.lower() not in ('content-type','accept','origin','host')]
        if bearer:self.secrets.append(os.environ[bearer])
        self.counter = 0
        self.last_rpc_seconds = None
        init = self.rpc('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                                     'clientInfo': {'name': 'fusion-360-mcp-skill', 'version': '2.1.0'}})
        version = init['result'].get('protocolVersion')
        if version:
            self.headers['MCP-Protocol-Version'] = version
        self.server_info = init['result'].get('serverInfo', {})
        self.rpc('notifications/initialized', notification=True)
        self.setup_seconds = time.perf_counter() - self.started

    def log(self, event, **fields):
        row = {'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'event': event, **fields}
        with (self.log_dir / 'actions.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(redact(row,self.secrets), ensure_ascii=False,allow_nan=False) + '\n')

    def rpc(self, method, params=None, notification=False):
        self.counter += 1
        payload = {'jsonrpc': '2.0', 'method': method}
        if params is not None:
            payload['params'] = params
        if not notification:
            payload['id'] = self.counter
        start = time.perf_counter()
        try:
            request = urllib.request.Request(self.url, json.dumps(payload,allow_nan=False).encode(), self.headers)
            with self.opener.open(request, timeout=self.timeout) as response:
                session = response.headers.get('Mcp-Session-Id')
                if session:
                    self.headers['Mcp-Session-Id'] = session
                    self.secrets.append(session)
                if 'text/event-stream' in response.headers.get('Content-Type', ''):
                    data = []
                    result = None
                    consumed=0
                    while True:
                        raw=response.readline(self.max_response_bytes-consumed+1)
                        if not raw:break
                        consumed+=len(raw)
                        if consumed>self.max_response_bytes:raise RuntimeError('MCP event stream exceeds response limit.')
                        line = raw.decode().rstrip('\r\n')
                        if line.startswith('data:'):
                            data.append(line[5:].lstrip())
                        elif not line and data:
                            message = strict_json('\n'.join(data))
                            data = []
                            if message.get('id') == payload.get('id'):
                                result = message
                                break
                    if result is None and not notification:
                        raise RuntimeError('MCP stream ended without the requested response.')
                else:
                    body = response.read(self.max_response_bytes+1)
                    if len(body)>self.max_response_bytes:raise RuntimeError('MCP JSON response exceeds response limit.')
                    result = strict_json(body) if body else None
            self.last_rpc_seconds = time.perf_counter() - start
            if not notification and (not result or result.get('id') != payload['id']):
                raise RuntimeError('Missing or mismatched MCP response id.')
            if result and result.get('error'):
                raise RuntimeError(json.dumps(redact(result['error'],self.secrets)))
            self.log('mcp_request', method=method, elapsed_seconds=self.last_rpc_seconds, outcome='ok')
            return result
        except Exception as error:
            self.last_rpc_seconds = time.perf_counter() - start
            self.log('mcp_request', method=method, elapsed_seconds=self.last_rpc_seconds,
                     outcome='failed', error_type=type(error).__name__)
            raise

    def execute(self, script, read_only=False):
        operation_id = str(uuid.uuid4())
        digest = hashlib.sha256(script.encode()).hexdigest()
        # Persist intent before dispatch. A lost reply is an unknown outcome,
        # not evidence that Fusion did nothing. Never replay automatically.
        self.log('fusion_dispatch', operation_id=operation_id, script_sha256=digest,
                 read_only=read_only, outcome='pending')
        try:
            return self._execute(script, read_only, operation_id)
        except Exception as error:
            self.log('fusion_outcome', operation_id=operation_id, script_sha256=digest,
                     outcome='unconfirmed', error_type=type(error).__name__,
                     recovery='Inspect live state before any modifying retry.')
            raise

    def _execute(self, script, read_only, operation_id):
        result = self.rpc('tools/call', {'name': 'fusion_mcp_execute',
                          'arguments': {'featureType': 'script', 'object': {'script': script, 'readOnly': read_only}}})
        response = result['result']
        texts = [item['text'] for item in response.get('content', []) if item.get('type') == 'text']
        outer = strict_json(texts[0]) if texts else {}
        if response.get('isError') or not outer.get('success'):
            self.log('fusion_execution', outcome='failed', script_sha256=hashlib.sha256(script.encode()).hexdigest(), response=outer)
            raise RuntimeError('Fusion rejected or failed the script: ' + json.dumps(redact(outer,self.secrets)))
        try:
            value = strict_json(outer['message'])
        except (KeyError,TypeError,ValueError):
            self.log('fusion_protocol_error',operation_id=operation_id,response=outer,
                     recovery='Inspect live state; do not replay the modifying request.')
            raise RuntimeError('Fusion returned no structured script result; inspect live state. See fusion_protocol_error in actions.jsonl.') from None
        self.log('fusion_execution', operation_id=operation_id, outcome='completed', script_sha256=hashlib.sha256(script.encode()).hexdigest(), result=value)
        return value
