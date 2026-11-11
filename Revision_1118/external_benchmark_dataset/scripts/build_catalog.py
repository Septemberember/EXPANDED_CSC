"""Combine accepted batch manifests without overwriting either batch's records."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];items=[];totals={'differential_cases':0,'executed_testcases':0,'fsf_units':0}
for number,base in [(1,ROOT),(2,ROOT/'batch2')]:
 manifest=json.loads((base/'manifest.json').read_text());audit=json.loads((base/'validation/audit.json').read_text());stats={x['name']:x for x in audit['subjects']}
 for subject in manifest['subjects']:
  name=subject['name'];assert subject['status']=='accepted_smoke_validated'
  for path,key in [(base/'subjects'/name/(name+'.java'),'adapted_sha256'),(base/'subjects'/name/'FSF'/(name+'_FSF.txt'),'fsf_sha256')]:assert hashlib.sha256(path.read_bytes()).hexdigest()==subject[key],(name,'stale manifest')
  stat=stats[name];item=dict(subject);item.update(batch=number,source_repository=subject.get('repository',manifest.get('repository')),source_commit=subject.get('commit',manifest.get('commit')),subject_path=str((base/'subjects'/name).relative_to(ROOT)),validation=stat)
  items.append(item)
  for key in totals:totals[key]+=stat[key]
assert len(items)==20 and len({x['name'] for x in items})==20
(ROOT/'catalog.json').write_text(json.dumps(dict(subject_count=len(items),scope='20 independently callable adapted cores; not 20 independent upstream systems; smoke validated, formal RQ experiments pending',totals=totals,subjects=items),indent=2)+'\n')
print('Catalog:',len(items),'subjects',totals)
