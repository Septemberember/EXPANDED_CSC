from common import *
subjects={s['subject']:s for s in read(OUT/'subjects.json')};manifest=[json.loads(x) for x in (OUT/'dataset/mutants_manifest.jsonl').read_text().splitlines()]
originals=[json.loads(x) for x in (OUT/'original_results.jsonl').read_text().splitlines()]
base_eligibility={}
for name in subjects:
 row=next((r for r in originals if r['subject']==name and r['tag']=='rq2_w4'),{})
 verification=row.get('verification',{});summary=verification.get('summary',{})
 base_eligibility[name]=row.get('status')=='completed' and verification.get('status')=='completed' and summary.get('failed')==0 and summary.get('unsupported')==0
write(OUT/'mutants_progress.json',dict(status='running',completed_candidates=0))
for i,m in enumerate(manifest):
 name=m['subject'];mutant=m['mutant_id'];s=subjects[name];recordfile=OUT/'mutation_records'/(mutant+'.json');write(recordfile,m);combined=dict(mutant_id=mutant,subject=name,operator=m['operator'],fault_category=m['fault_category'],loop_bearing=s['loop_bearing'],modes={},localization=dict(status='skipped',reason='no_valid_expanded_run'))
 for mode in ['original','expanded']:
  if not base_eligibility[name]:
   combined['modes'][mode]=dict(status='skipped',reason='original_batch_w4_not_verified_passing');continue
  try:
   java=OUT/'dataset'/m['mutant_file'];g=generation(name,java,'kill_'+mode,mode,'batch',4,100)
   v=verify(g,s['fsf']);g['verification']=v;combined['modes'][mode]=g
   if mode=='expanded' and g['status']=='completed' and v['status']=='completed':
    if not v['killed']:combined['localization']=dict(status='not_detected',reason='no_tbfv_failures')
    else:
     genfile=Path(g['folder'])/'generation.json';step=invoke([sys.executable,str(OUT/'scripts/localize_one.py'),str(recordfile),str(genfile)],g['folder'],'localization',180)
     if step['returncode']==0 and (Path(g['folder'])/'localization.json').exists():combined['localization']=read(Path(g['folder'])/'localization.json')
     else:combined['localization']=dict(status='error',reason='postprocess_timeout' if step['timed_out'] else 'postprocess_failed',step=step)
   snapshot(g['result_dir'],g['folder']) if Path(g['result_dir']).exists() else None
   print(mutant,mode,g['status'],'kill='+str(v.get('killed')),'RQ3='+str(combined['localization'].get('status')),flush=True)
  except Exception as e:
   combined['modes'][mode]=dict(status='orchestration_error',reason=repr(e));print(mutant,mode,'orchestration_error',repr(e),flush=True)
 write(OUT/'mutant_results'/(mutant+'.json'),combined);append(OUT/'mutant_results.jsonl',combined);write(OUT/'mutants_progress.json',dict(status='running',completed_candidates=i+1,last_mutant=mutant))
write(OUT/'mutants_progress.json',dict(status='completed',completed_candidates=len(manifest)))
