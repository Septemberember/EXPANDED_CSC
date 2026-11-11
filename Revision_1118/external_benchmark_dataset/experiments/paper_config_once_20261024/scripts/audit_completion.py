"""Prove the requested scope was attempted and reported without changing tool/subjects."""
from common import *
import collections,re
subjects=read(OUT/'subjects.json');config=read(OUT/'config.json');summary=read(OUT/'summary.json');originals=[json.loads(x) for x in (OUT/'original_results.jsonl').read_text().splitlines()];mutants=[json.loads(x) for x in (OUT/'mutant_results.jsonl').read_text().splitlines()];manifest=[json.loads(x) for x in (OUT/'dataset/mutants_manifest.jsonl').read_text().splitlines()];catalog=read(OUT.parents[1]/'catalog.json')
checks=[]
def check(label,value):
 checks.append(dict(requirement=label,passed=bool(value)))
 if not value:raise AssertionError(label)
expected={(s['subject'],tag) for s in subjects for tag in ['rq1_original','rq1_expanded','rq2_w1','rq2_w2','rq2_w4','rq2_w8']}
actual=[(x['subject'],x['tag']) for x in originals];check('120 original configuration cells exactly once',len(actual)==120 and set(actual)==expected)
check('120 pre-registered mutant records exactly once',len(mutants)==120 and {m['mutant_id'] for m in mutants}=={m['mutant_id'] for m in manifest})
check('all 240 mutant-mode cells terminal',all(set(m['modes'])=={'original','expanded'} and all(g.get('status') not in [None,'pending','running'] for g in m['modes'].values()) for m in mutants))
generation_ledger=[json.loads(x) for x in (OUT/'generation_runs.jsonl').read_text().splitlines()]
attempt_keys=[(g['tag'],g['class_name']) for g in generation_ledger]
check('no repeated generation attempts per configuration',len(attempt_keys)==len(set(attempt_keys)))
reported_commands=originals+[g for m in mutants for g in m['modes'].values() if 'command' in g]
check('all executed generation attempts appear in result records',{g['session'] for g in generation_ledger}=={g['session'] for g in reported_commands if 'session' in g})
check('20 subject rows contain explicit three RQ statuses',len(read(OUT/'subject_results.json'))==20 and all(all(r.get(k) and r[k]!='pending' for k in ['RQ1_completion','RQ2_status','RQ3_status']) for r in read(OUT/'subject_results.json')))
for s in subjects:
 check(s['subject']+' unchanged original hash',hashlib.sha256(Path(s['java_file']).read_bytes()).hexdigest()==s['source_sha256'])
 check(s['subject']+' unchanged FSF hash',hashlib.sha256(Path(s['fsf']).read_bytes()).hexdigest()==s['fsf_sha256'])
for rel,sha in config['tool_sha256'].items():check('unchanged tool '+rel,hashlib.sha256((TOOL/rel).read_bytes()).hexdigest()==sha)
for m in manifest:
 original=(OUT/'dataset'/m['original_file']).read_text();mutant=(OUT/'dataset'/m['mutant_file']).read_text();a,b=m['change']['original_span'];normalized=mutant.replace('public class '+m['mutant_id']+' {','public class '+m['subject']+' {',1)
 check(m['mutant_id']+' one semantic edit and preserved lines',normalized==original[:a]+m['change']['to_text']+original[b:] and original.count('\n')==mutant.count('\n'))
for g in originals+[g for m in mutants for g in m['modes'].values() if 'command' in g]:
 command=g.get('command',[])
 if not command:continue
 def arg(flag):return command[command.index(flag)+1]
 check(g['session']+' selected range bound',arg('--range-bound')=='200')
 check(g['session']+' default bootstrap', '--bootstrap' not in command)
 if g['tag'].startswith('rq1_'):check(g['session']+' sequential-R2000',arg('--strategy')=='sequential' and arg('--max-iter')=='2000')
 else:check(g['session']+' batch-R100',arg('--strategy')=='batch' and arg('--max-iter')=='100')
 if g['tag'].startswith('kill_'):check(g['session']+' kill W4',arg('--workers')=='4')
 directory=Path(g['result_dir']);events=[json.loads(x) for x in (directory/'run_log.jsonl').read_text().splitlines()] if (directory/'run_log.jsonl').exists() else []
 if g['status']=='completed':
  check(g['session']+' fresh completed evidence',sum(x.get('event')=='run_start' for x in events)==1 and any(x.get('event')=='cct_full' for x in events) and (directory/'testcases.json').exists())
for m in mutants:
 loc=m['localization']
 if loc['status']=='evaluated':
  g=m['modes']['expanded'];folder=Path(g['folder']);check(m['mutant_id']+' detected expanded evidence',g['status']=='completed' and g['verification']['status']=='completed' and g['verification']['killed'])
  check(m['mutant_id']+' paper scoring',loc['scoring_strategy']=='coverage_x_purity')
  check(m['mutant_id']+' all five equal-budget comparisons',all(f'top{k}_{method}_hit' in loc for k in [1,2,3] for method in ['folded','ochiai','dstar','tarantula','barinel','op2']))
  sfl=read(folder/'sfl_localization.json');check(m['mutant_id']+' full SBFL rankings',all(len(r)==sfl['summary']['entities'] for r in sfl['rankings'].values()))
  check(m['mutant_id']+' same local evidence paths',str(Path(g['result_dir'])) in json.dumps(g['verification']['command']) and Path(g['command'][2]).stem==m['mutant_id'])
check('summary confirms full requested record scope',summary['all_cells_recorded'])
check('plan, config, report, per-subject ledger and exception ledger saved',all((OUT/p).exists() for p in ['PLAN.md','config.json','RESULTS.md','subject_results.csv','rq1_completion.csv','rq1_structural_summary.csv','rq1_mutant_killing.csv','rq2_runs.csv','rq3_mutants.csv','exceptions.csv']))
write(OUT/'completion_audit.json',dict(status='passed',checks=len(checks),requirements=checks));print('Completion audit passed:',len(checks),'checks')
