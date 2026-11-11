"""Batch2 acceptance: source identity, domain partition, matched FSFs and actual runs."""
from pathlib import Path
import json,sys,re,hashlib,gzip,itertools
import z3
ROOT=Path(__file__).resolve().parents[1];TOOL=next(candidate for parent in ROOT.parents for candidate in (parent/'project/CSC_EXPANDED', parent) if (candidate/'csc_tool.py').is_file() and (candidate/'csc_engine').is_dir());sys.path.insert(0,str(TOOL))
from csc_engine import load_fsf_file,java_expr_to_z3
def read(path):return json.loads(path.read_text() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes()).decode())
manifest=read(ROOT/'manifest.json');diff=read(ROOT/'validation/differential/report.json');rows=[]
assert diff['exit_code']==0
for s in manifest['subjects']:
 name=s['name'];folder=ROOT/'subjects'/name;java=folder/(name+'.java');code=java.read_text();out=ROOT/'validation'/name
 types={n:t for t,n in re.findall(r'\b(int|boolean)\s+(\w+)',re.search(r'public static int test\((.*?)\)',code,re.S).group(1))};types['return_value']='int'
 fsf=folder/'FSF'/(name+'_FSF.txt');fsfs=load_fsf_file(fsf);ts=[java_expr_to_z3(x.T,types) for x in fsfs]
 def check(expr,expected):
  sol=z3.Solver();sol.set(timeout=5000);sol.add(expr);assert sol.check()==expected,(name,str(expr))
 check(z3.Not(z3.Or(ts)),z3.unsat)
 for a,b in itertools.combinations(ts,2):check(z3.And(a,b),z3.unsat)
 for t in ts:check(t,z3.sat)
 state=read(out/'status.json');report=read(out/'verification.json');passed={x['fsf_id'] for x in report['results'] if x['status']=='pass'}
 assert {x.id for x in fsfs}==passed,(name,'unmatched scenarios',{x.id for x in fsfs}-passed)
 assert state['generation_exit']==state['verification_exit']==0,name
 assert any('CCT is FULL' in x for x in state['generation_terminal_lines']),name
 assert report['summary']['failed']==report['summary']['unsupported']==0,name
 assert diff['results'][name]['status']=='PASS',name
 assert hashlib.sha256((ROOT/'sources'/s['source']).read_bytes()).hexdigest()==s['source_sha256']
 s['status']='accepted_smoke_validated';s['adapted_sha256']=hashlib.sha256(java.read_bytes()).hexdigest();s['fsf_sha256']=hashlib.sha256(fsf.read_bytes()).hexdigest()
 records=read(out/'artifacts/testcases.json');executed=sum(x.get('inputs') is not None for x in records)
 rows.append(dict(name=name,differential_cases=diff['results'][name]['cases'],fsf_units=len(fsfs),matched_fsf_units=len(passed),generation_records=len(records),executed_testcases=executed,fsf_partition='total/disjoint/nonempty (int32/bool)',generation_finished=True,verification=report['summary'],session=state['session']))
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
report=dict(subjects=rows,total_differential_cases=sum(x['differential_cases'] for x in rows),total_executed_testcases=sum(x['executed_testcases'] for x in rows),total_fsf_units=sum(x['fsf_units'] for x in rows),tool_sources_sha256={str(p.relative_to(TOOL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TOOL/'csc_tool.py',TOOL/'refined_tbfv_tool.py',*sorted((TOOL/'csc_engine').glob('*.py'))]},java_bridge_sha256=hashlib.sha256((TOOL/'java_bridge/target/csc-bridge-0.1.0-jar-with-dependencies.jar').read_bytes()).hexdigest())
(ROOT/'validation/audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Accepted',len(rows),'subjects; cases',report['total_differential_cases'],'executions',report['total_executed_testcases'],'FSFs',report['total_fsf_units'])
for x in rows:print(x['name'],x['differential_cases'],x['executed_testcases'],x['fsf_units'])
