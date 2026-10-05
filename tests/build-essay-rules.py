"""Rebuild compressed, exact rubric text from the preserved Python source."""
from pathlib import Path
import base64, gzip, json, sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'apps/zuowenpigai'))
from prompts import EXAM_LEVELS, build_grading_prompt
from language_audit import SYSTEM
lines=[]; lookup={}; indices={}
for exam,cfg in EXAM_LEVELS.items():
 for genre in cfg['genres']:
  ids=[]
  for line in build_grading_prompt(exam,genre,'__HWT_PROMPT__','__HWT_REQUIREMENTS__',is_handwritten=True).split('\n'):
   if line not in lookup: lookup[line]=len(lines); lines.append(line)
   ids.append(lookup[line])
  indices[exam+'|'+genre]=ids
payload=dict(configs=EXAM_LEVELS,audit=SYSTEM,lines=lines,indices=indices)
encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False).encode(),mtime=0)).decode()
target=root/'supabase/functions/hwt-essay/rules.mjs'
target.write_text('// Generated from apps/zuowenpigai/prompts.py; exact text, deduplicated lines.\nconst encoded='+repr(encoded)+';\nexport async function loadRules(){const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));const r=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"))).json();return {configs:r.configs,audit:r.audit,prompts:Object.fromEntries(Object.entries(r.indices).map(([k,ids])=>[k,ids.map(i=>r.lines[i]).join("\\n")]))};}\n')
print('Built',target)
