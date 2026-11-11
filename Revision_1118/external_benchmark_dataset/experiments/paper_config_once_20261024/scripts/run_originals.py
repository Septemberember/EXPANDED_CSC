from common import *
subjects=read(OUT/'subjects.json');write(OUT/'originals_progress.json',dict(status='running',completed_subjects=0))
for i,s in enumerate(subjects):
 name=s['subject'];rows=[]
 specs=[('rq1_original','original','sequential',1,2000),('rq1_expanded','expanded','sequential',1,2000)]+[(f'rq2_w{w}','expanded','batch',w,100) for w in [1,2,4,8]]
 for tag,mode,strategy,w,budget in specs:
  try:
   g=generation(name,s['java_file'],tag,mode,strategy,w,budget)
   if tag.startswith('rq1_') or tag=='rq2_w4':g['verification']=verify(g,s['fsf'])
   append(OUT/'original_results.jsonl',g);rows.append(g)
   print(name,tag,g['status'],round(g['wall_time_s'],2),flush=True)
  except Exception as e:
   error=dict(subject=name,tag=tag,status='orchestration_error',reason=repr(e));append(OUT/'original_results.jsonl',error);print(error,flush=True)
 write(OUT/'originals_progress.json',dict(status='running',completed_subjects=i+1,last_subject=name))
write(OUT/'originals_progress.json',dict(status='completed',completed_subjects=len(subjects)))
