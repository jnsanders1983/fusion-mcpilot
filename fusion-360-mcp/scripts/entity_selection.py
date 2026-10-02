"""Embedded live selectors; occurrence paths are required for assembly edits."""
SOURCE='''
def resolve_body(design,selector):
 path=selector.get('occurrence_path','')
 occurrence=None
 if path:
  matches=[o for o in design.rootComponent.allOccurrences if o.fullPathName==path]
  if len(matches)!=1:raise RuntimeError('Occurrence path missing or ambiguous.')
  occurrence=matches[0];component=occurrence.component
 else:component=design.rootComponent
 token=selector.get('entity_token')
 if token:
  candidates=[adsk.fusion.BRepBody.cast(e) for e in design.findEntityByToken(token)]
  candidates=[b for b in candidates if b is not None and b.isValid and (b.nativeObject or b).parentComponent==component]
 else:candidates=[b for b in component.bRepBodies if b.name==selector.get('name')]
 if len(candidates)!=1:raise RuntimeError('Body selection missing or ambiguous; choose a live token and occurrence path.')
 body=candidates[0].nativeObject or candidates[0]
 return body.createForAssemblyContext(occurrence) if occurrence else body
'''
