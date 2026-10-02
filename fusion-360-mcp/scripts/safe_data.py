"""Bounded model-file parsing shared by single and multi-part print workflows."""
import math,zipfile,xml.etree.ElementTree as ET
import pyexpat
from pathlib import Path

MODEL_MEMBER='3D/3dmodel.model'
MAX_MODEL_BYTES=64*1024*1024
MAX_ARCHIVE_BYTES=256*1024*1024
MAX_ITEMS=128
MAX_NODES=1000000


def model_xml(path):
    if tuple(pyexpat.version_info)<(2,7,2):raise RuntimeError('XML workflows require Expat 2.7.2+ for CVE-2025-59375. Use an updated Python runtime; input-size limits are not a replacement for this fix.')
    path=Path(path)
    if path.stat().st_size>MAX_ARCHIVE_BYTES:raise ValueError('3MF archive exceeds the configured size limit.')
    with zipfile.ZipFile(path) as archive:
        members=archive.infolist()
        if len(members)>MAX_ITEMS or len({item.filename for item in members})!=len(members):raise ValueError('3MF has too many or duplicate ZIP members.')
        if sum(item.file_size for item in members)>MAX_ARCHIVE_BYTES:raise ValueError('3MF expanded archive exceeds limit.')
        for member in members:
            if member.filename.startswith(('/', '\\')) or '..' in member.filename.replace('\\','/').split('/'):raise ValueError('3MF contains an unsafe member path.')
            if member.flag_bits&1:raise ValueError('Encrypted 3MF members are unsupported.')
        info=archive.getinfo(MODEL_MEMBER)
        if info.file_size>MAX_MODEL_BYTES:raise ValueError('3MF model exceeds XML size limit.')
        with archive.open(info) as stream:raw=stream.read(MAX_MODEL_BYTES+1)
    if len(raw)>MAX_MODEL_BYTES:raise ValueError('3MF model exceeds XML size limit.')
    # This workflow accepts UTF-8 model XML only; declarations/entities are not
    # needed for meshes. Reject them before invoking the XML parser.
    text=raw.decode('utf-8-sig')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():raise ValueError('3MF XML declarations/entities are forbidden.')
    model=ET.fromstring(text)
    if sum(1 for _ in model.iter())>MAX_NODES:raise ValueError('3MF model exceeds node limit.')
    return model


def strict_json(raw):
    import json
    def invalid(value):raise ValueError('Nonfinite JSON numbers are forbidden: '+value)
    return json.loads(raw,parse_constant=invalid)
