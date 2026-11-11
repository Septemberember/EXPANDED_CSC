"""Actual CSC/TBFV smoke runs; fresh sessions, bounded time, retained artifacts."""
from pathlib import Path
import subprocess,sys,json,time,shutil,concurrent.futures,argparse
ROOT=Path(__file__).resolve().parents[1]; TOOL=next(candidate for parent in ROOT.parents for candidate in (parent/'project/CSC_EXPANDED', parent) if (candidate/'csc_tool.py').is_file() and (candidate/'csc_engine').is_dir())
def run(s):
 name=s['name']; folder=ROOT/'subjects'/name; out=ROOT/'validation'/name;out.mkdir(parents=True,exist_ok=True)
 for stale in [out/'generation.log.gz',out/'verification.json.gz',out/'verification.json']:
  if stale.exists():stale.unlink()
 session='external_'+name+'_'+str(time.time_ns()); result={'name':name,'session':session}
 cmd=[sys.executable,str(TOOL/'csc_tool.py'),str(folder/(name+'.java')),'--session',session,'--max-iter',str(s.get('max_iter',1000 if name=='SpfWbsStep' else 160)),'--range-bound','40','--bootstrap',s['bootstrap']]
 result['generation_command']=cmd
 try:
  with (out/'generation.log').open('w') as f:r=subprocess.run(cmd,cwd=TOOL,stdout=f,stderr=subprocess.STDOUT,timeout=300)
  result['generation_exit']=r.returncode
 except subprocess.TimeoutExpired:result['generation_exit']='timeout'
 artifacts=TOOL/'csc_tmp'/session/name
 if artifacts.exists():
  dest=out/'artifacts'
  if dest.exists():shutil.rmtree(dest)
  shutil.copytree(artifacts,dest)
  if (artifacts/'testcases.json').exists():
   cmd=[sys.executable,str(TOOL/'refined_tbfv_tool.py'),'--class',name,'--java-file',str(folder/(name+'.java')),'--csc-result-dir',str(artifacts),'--fsf',str(folder/'FSF'/(name+'_FSF.txt')),'--output',str(out/'verification.json'),'--no-annotate-cct','--fail-on-violation','--fail-on-unsupported']
   result['verification_command']=cmd
   try:
    with (out/'verification.log').open('w') as f:r=subprocess.run(cmd,cwd=TOOL,stdout=f,stderr=subprocess.STDOUT,timeout=180)
    result['verification_exit']=r.returncode
   except subprocess.TimeoutExpired:result['verification_exit']='timeout'
   if (out/'verification.json').exists():result['verification_summary']=json.loads((out/'verification.json').read_text())['summary']
  if (artifacts/'cct_stats.json').exists():result['cct']=json.loads((artifacts/'cct_stats.json').read_text())['cct']
 text=(out/'generation.log').read_text();result['generation_terminal_lines']=[l for l in text.splitlines() if any(x in l.lower() for x in ['all branches','maximum','max iteration','no uncovered','coverage complete','stopping','all feasible','no more'])]
 (out/'status.json').write_text(json.dumps(result,indent=2)+'\n');print(name,json.dumps({k:v for k,v in result.items() if k in ['generation_exit','verification_exit','verification_summary','generation_terminal_lines']}),flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('names',nargs='*');a=p.parse_args()
 subjects=json.loads((ROOT/'manifest.json').read_text())['subjects'];subjects=[s for s in subjects if not a.names or s['name'] in a.names]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(run,subjects))
 (ROOT/'validation/latest_run.json').write_text(json.dumps(results,indent=2)+'\n')
