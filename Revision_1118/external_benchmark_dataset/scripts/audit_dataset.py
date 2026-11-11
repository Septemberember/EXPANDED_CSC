"""Audit provenance, FSF partition, actual generation completion and scenario matches."""
from pathlib import Path
import json,sys,re,hashlib,gzip,itertools
import z3
ROOT=Path(__file__).resolve().parents[1];TOOL=next(candidate for parent in ROOT.parents for candidate in (parent/'project/CSC_EXPANDED', parent) if (candidate/'csc_tool.py').is_file() and (candidate/'csc_engine').is_dir());sys.path.insert(0,str(TOOL))
from csc_engine import load_fsf_file,java_expr_to_z3
def read_json(path):
 return json.loads(path.read_text() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes()).decode())
manifest=json.loads((ROOT/'manifest.json').read_text());diff=json.loads((ROOT/'validation/differential/report.json').read_text());rows=[]
assert diff['exit_code']==0
for s in manifest['subjects']:
 name=s['name'];folder=ROOT/'subjects'/name;code=(folder/(name+'.java')).read_text();out=ROOT/'validation'/name
 types={n:t for t,n in re.findall(r'\b(int|boolean)\s+(\w+)',re.search(r'public static int test\((.*?)\)',code,re.S).group(1))};types['return_value']='int'
 fsfs=load_fsf_file(folder/'FSF'/(name+'_FSF.txt'));ts=[java_expr_to_z3(x.T,types) for x in fsfs]
 solver=z3.Solver();solver.set(timeout=5000);solver.add(z3.Not(z3.Or(ts)));assert solver.check()==z3.unsat,(name,'incomplete FSF partition')
 for a,b in itertools.combinations(ts,2):
  solver=z3.Solver();solver.set(timeout=5000);solver.add(a,b);assert solver.check()==z3.unsat,(name,'overlapping FSF partition')
 for t in ts:
  solver=z3.Solver();solver.set(timeout=5000);solver.add(t);assert solver.check()==z3.sat,(name,'unreachable FSF')
 state=json.loads((out/'status.json').read_text());report=read_json(out/'verification.json');passed={x['fsf_id'] for x in report['results'] if x['status']=='pass'}
 missing=sorted({x.id for x in fsfs}-passed)
 assert not missing,(name,missing)
 assert state['generation_exit']==0 and state['verification_exit']==0,name
 assert any('CCT is FULL' in l for l in state['generation_terminal_lines']),name
 assert report['summary']['failed']==report['summary']['unsupported']==0,name
 assert diff['results'][name]['status']=='PASS',name
 source=ROOT/'sources/jpf-symbc/src/examples'/s['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==s['source_sha256']
 s['status']='accepted_smoke_validated';s['adapted_sha256']=hashlib.sha256((folder/(name+'.java')).read_bytes()).hexdigest();s['fsf_sha256']=hashlib.sha256((folder/'FSF'/(name+'_FSF.txt')).read_bytes()).hexdigest()
 records=json.loads((out/'artifacts/testcases.json').read_text());executed=sum(1 for x in records if x.get('inputs') is not None)
 row=dict(name=name,differential_cases=diff['results'][name]['cases'],fsf_units=len(fsfs),matched_fsf_units=len(passed),fsf_partition='total/disjoint/nonempty over Java int32/bool',generation_records=len(records),executed_testcases=executed,generation_finished=True,verification=report['summary'],session=state['session']);rows.append(row)
manifest['validation_scope']='Exhaustive mapped finite domains; expanded CSC completion; nontrivial FSF verification with every scenario matched. Not RQ1/RQ2/RQ3 experiments or full upstream verification.'
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
report={'subjects':rows,'total_differential_cases':sum(r['differential_cases'] for r in rows),'tool_sources_sha256':{str(p.relative_to(TOOL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TOOL/'csc_tool.py',TOOL/'refined_tbfv_tool.py',*sorted((TOOL/'csc_engine').glob('*.py'))]},'java_bridge_sha256':hashlib.sha256((TOOL/'java_bridge/target/csc-bridge-0.1.0-jar-with-dependencies.jar').read_bytes()).hexdigest()}
(ROOT/'validation/audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Accepted',len(rows),'subjects;',report['total_differential_cases'],'differential cases')
for r in rows:print(r['name'],r['executed_testcases'],r['fsf_units'])
