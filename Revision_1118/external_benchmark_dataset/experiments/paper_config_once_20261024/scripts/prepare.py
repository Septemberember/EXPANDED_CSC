from pathlib import Path
import json,shutil,hashlib,platform,subprocess,sys
OUT=Path(__file__).resolve().parents[1];DATA=OUT.parents[1];REPO=DATA.parents[1];ROOT=DATA;TOOL=next(candidate for parent in ROOT.parents for candidate in (parent/'project/CSC_EXPANDED', parent) if (candidate/'csc_tool.py').is_file() and (candidate/'csc_engine').is_dir())
subjects=json.loads((DATA/'catalog.json').read_text())['subjects'];records=[]
for s in subjects:
 name=s['name'];source=DATA/s['subject_path'];target=OUT/'dataset'/name;target.mkdir(parents=True,exist_ok=True)
 for p in [source/(name+'.java'),source/'FSF'/(name+'_FSF.txt')]:
  dest=target/p.relative_to(source);dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
 java=target/(name+'.java');code=java.read_text();assert hashlib.sha256(java.read_bytes()).hexdigest()==s['adapted_sha256']
 import re
 body=code[code.index('public static int test'):];loop=bool(re.search(r'\b(?:while|for)\s*\(',body))
 records.append(dict(subject=name,batch=s['batch'],java_file=str(java),fsf=str(target/'FSF'/(name+'_FSF.txt')),source_sha256=s['adapted_sha256'],fsf_sha256=s['fsf_sha256'],loop_bearing=loop))
(OUT/'subjects.json').write_text(json.dumps(records,indent=2)+'\n')
config=dict(subject_count=20,repeats=1,range_bound=200,bootstrap='tool default, as in original experiment commands; no per-subject override',rq1_completion=dict(strategy='sequential',max_iter=2000,modes=['original','expanded']),rq1_mutant_killing=dict(strategy='batch',workers=4,max_iter=100,modes=['original','expanded'],scope='loop-bearing subjects for aggregate; loop-free also recorded'),rq2=dict(strategy='batch',max_iter=100,mode='expanded',workers=[1,2,4,8]),rq3=dict(generation='reuse expanded mutant batch-W4-R100 evidence',score='coverage_x_purity (paper Eq. folded-risk and archived rows)',top_k=[1,2,3],sbfl=['ochiai','dstar','tarantula','barinel','op2'],budget='same union of top-k condition nodes and edge-partition statement lines; same source-line budget for SBFL'),timeouts=dict(generation_s=240,postprocess_s=180),mutants_per_subject=6,policy='one attempt per configured cell; on error/timeout/partial, record and skip dependent steps; no subject/FSF/tool repair or tuning',tool_root=str(TOOL),host=platform.platform(),python=sys.version,java=subprocess.run(['java','-version'],capture_output=True,text=True).stderr,source_references=['JSS2026/overleaf/main.tex:2100-2145,2375-2405','project/CSC_EXPANDED/experiments/EX_CSC_dataset/CORE_rerun/experiment_config.json','project/CSC_EXPANDED/experiments/EX_CSC_dataset/rq_extension_b/RQ2-parallel/experiment_config.json'],tool_sha256={str(p.relative_to(TOOL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TOOL/'csc_tool.py',TOOL/'refined_tbfv_tool.py',TOOL/'csc_engine/cct.py',TOOL/'csc_engine/z3_helpers.py']})
(OUT/'config.json').write_text(json.dumps(config,indent=2)+'\n')
print('Prepared',len(records),'unchanged subjects;',sum(s['loop_bearing'] for s in records),'loop-bearing')
