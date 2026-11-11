from pathlib import Path
import json,subprocess,sys,os,time,signal,hashlib,gzip,shutil
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parents[1];ROOT=OUT;TOOL=next(candidate for parent in ROOT.parents for candidate in (parent/'project/CSC_EXPANDED', parent) if (candidate/'csc_tool.py').is_file() and (candidate/'csc_engine').is_dir());sys.path.insert(0,str(TOOL))
from csc_experiments.parallel_generation import compute_generation_fingerprint

def read(p,default=None):
 try:return json.loads(Path(p).read_text())
 except (FileNotFoundError,json.JSONDecodeError):return default

def write(p,data):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(p)

def append(p,data):
 with Path(p).open('a') as f:f.write(json.dumps(data)+'\n')

def invoke(command,folder,step,timeout=180):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);stdout=folder/(step+'.stdout');stderr=folder/(step+'.stderr');t=time.perf_counter();start=datetime.now(timezone.utc).isoformat()
 with stdout.open('w') as a,stderr.open('w') as b:
  process=subprocess.Popen(command,cwd=TOOL,stdout=a,stderr=b,start_new_session=True)
  try:rc=process.wait(timeout=timeout);timed=False
  except subprocess.TimeoutExpired:
   timed=True
   try:os.killpg(process.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   process.wait();rc=124
 wall=time.perf_counter()-t
 result=dict(command=command,returncode=rc,timed_out=timed,wall_time_s=wall,started_at=start,finished_at=datetime.now(timezone.utc).isoformat(),stdout=str(stdout),stderr=str(stderr),stderr_tail=stderr.read_text()[-2500:])
 if stdout.stat().st_size>1024*1024:
  with stdout.open('rb') as src,gzip.open(str(stdout)+'.gz','wb',compresslevel=5) as dst:shutil.copyfileobj(src,dst)
  stdout.unlink();result['stdout']=str(stdout)+'.gz'
 return result

def snapshot(directory,folder):
 dest=Path(folder)/'artifacts';dest.mkdir(exist_ok=True)
 for p in Path(directory).iterdir():
  if p.is_file() and (p.suffix in ['.json','.jsonl','.pkl']):shutil.copy2(p,dest/p.name)
  elif p.name=='traces' and p.is_dir():shutil.copytree(p,dest/'traces',dirs_exist_ok=True)
 return dest

def generation(subject,java,tag,mode,strategy,workers,max_iter):
 name=Path(java).stem;session='extpaper_'+tag+'_'+name+'_'+str(time.time_ns());folder=OUT/'runs'/tag/name
 if (folder/'generation.json').exists():raise RuntimeError('Attempt already exists: '+str(folder))
 command=[sys.executable,str(TOOL/'csc_tool.py'),str(java),'--mode',mode,'--range-bound','200','--strategy',strategy,'--workers',str(workers),'--max-iter',str(max_iter),'--session',session,'--keep-artifacts']
 result=invoke(command,folder,'generation',240);directory=TOOL/'csc_tmp'/session/name
 result.update(subject=subject,class_name=name,session=session,result_dir=str(directory),folder=str(folder),mode=mode,strategy=strategy,workers=workers,max_iter=max_iter,range_bound=200,tag=tag)
 events=[]
 if (directory/'run_log.jsonl').exists():
  for line in (directory/'run_log.jsonl').read_text().splitlines():
   try:events.append(json.loads(line))
   except json.JSONDecodeError:pass
 stats=read(directory/'cct_stats.json',{});result['cct']=stats.get('cct',{});result['testcase_stats']=stats.get('testcases',{});result['full_event']=any(e.get('event')=='cct_full' for e in events)
 errors=[e for e in events if any(x in e.get('event','').lower() for x in ['error','failed'])];result['error_events']=errors
 result['fresh']=sum(e.get('event')=='run_start' for e in events)==1
 result['status']='timeout' if result['timed_out'] else 'error' if result['returncode'] or errors else 'completed' if result['full_event'] and stats else 'partial' if stats else 'error'
 if directory.exists():
  if stats:
   try:result['fingerprint']=compute_generation_fingerprint(directory)
   except Exception as e:result['fingerprint_error']=str(e)
  snapshot(directory,folder)
 widths=[int(e.get('branch_count') or 0) for e in events if e.get('event')=='batch_discover_complete'];result['frontier_mean']=sum(widths)/len(widths) if widths else None;result['frontier_max']=max(widths) if widths else None
 write(folder/'generation.json',result);append(OUT/'generation_runs.jsonl',result);return result

def verify(g,fsf):
 if g['status']!='completed':return dict(status='skipped',reason='generation_'+g['status'])
 folder=Path(g['folder']);directory=Path(g['result_dir']);report=folder/'verification.json'
 command=[sys.executable,str(TOOL/'refined_tbfv_tool.py'),'--csc-result-dir',str(directory),'--java-file',str(next(iter([Path(g['command'][2])]))),'--fsf',str(fsf),'--output',str(report)]
 result=invoke(command,folder,'verification');payload=read(report,{});result['summary']=payload.get('summary',{})
 result['status']='timeout' if result['timed_out'] else 'error' if result['returncode'] or not payload else 'unsupported' if result['summary'].get('unsupported') else 'completed'
 result['killed']=bool(result['summary'].get('failed',0)>0) if result['status']=='completed' else None
 snapshot(directory,folder);write(folder/'verification_status.json',result);return result
