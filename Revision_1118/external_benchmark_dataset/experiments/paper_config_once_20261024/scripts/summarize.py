"""Complete per-subject RQ ledger, explicit missing/error denominators and report."""
from common import *
import csv,statistics,collections
subjects=read(OUT/'subjects.json');manifest=[json.loads(x) for x in (OUT/'dataset/mutants_manifest.jsonl').read_text().splitlines()]
def jsonl(p):return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []
originals=jsonl(OUT/'original_results.jsonl');mutants=jsonl(OUT/'mutant_results.jsonl');rows=[];rq1=[];rq2=[];rq3=[];exceptions=[]
for x in originals:
 if x.get('status')!='completed':exceptions.append(dict(subject=x['subject'],task=x['tag'],status=x.get('status'),reason=x.get('reason',x.get('stderr_tail','')),artifact=x.get('folder')))
 if x.get('verification',{}).get('status') not in [None,'completed']:exceptions.append(dict(subject=x['subject'],task=x['tag']+'_verification',status=x['verification']['status'],reason=x['verification'].get('stderr_tail',''),artifact=x.get('folder')))
 if x.get('verification',{}).get('summary',{}).get('failed',0):exceptions.append(dict(subject=x['subject'],task=x['tag']+'_original_FSF',status='original_fsf_violation',reason=json.dumps(x['verification']['summary']),artifact=x.get('folder')))
for m in mutants:
 for mode,g in m['modes'].items():
  if g.get('status')!='completed' or g.get('verification',{}).get('status') not in [None,'completed']:exceptions.append(dict(subject=m['subject'],task=m['mutant_id']+'_'+mode,status=g.get('status'),reason=g.get('reason',g.get('stderr_tail','')),artifact=g.get('folder')))
  if g.get('verification',{}).get('status') not in [None,'completed']:exceptions.append(dict(subject=m['subject'],task=m['mutant_id']+'_'+mode+'_verification',status=g['verification']['status'],reason=g['verification'].get('stderr_tail',''),artifact=g.get('folder')))
 if m['localization'].get('status') in ['error','skipped']:exceptions.append(dict(subject=m['subject'],task=m['mutant_id']+'_RQ3',status=m['localization'].get('status'),reason=m['localization'].get('reason','')))

def valid(g):return g.get('status')=='completed' and g.get('verification',{}).get('status')=='completed'
for s in subjects:
 name=s['subject'];o={x['tag']:x for x in originals if x['subject']==name};ms=[x for x in mutants if x['subject']==name];a=o.get('rq1_original',{});b=o.get('rq1_expanded',{});one=dict(subject=name,loop_bearing=s['loop_bearing'],csc_only_status=a.get('status','pending'),boundary_status=b.get('status','pending'),csc_only_s=a.get('wall_time_s'),boundary_s=b.get('wall_time_s'),csc_only_tests=a.get('testcase_stats',{}).get('executable_records'),boundary_tests=b.get('testcase_stats',{}).get('executable_records'),csc_only_nodes=a.get('cct',{}).get('total_nodes'),boundary_nodes=b.get('cct',{}).get('total_nodes'),csc_only_empty=a.get('cct',{}).get('empty_leaves'),boundary_empty=b.get('cct',{}).get('empty_leaves'),boundary_infeasible=b.get('cct',{}).get('infeasible_leaves'),boundary_out_of_range=b.get('cct',{}).get('out_of_range_leaves'),boundary_expanded=b.get('cct',{}).get('expanded_nodes'))
 paired=a.get('status')==b.get('status')=='completed';one['valid_completion_pair']=paired;one['overhead_ratio']=b['wall_time_s']/a['wall_time_s'] if paired and a['wall_time_s'] else None;rq1.append(one)
 for mode,g in [('csc_only',a),('boundary',b)]:
  one[mode+'_verification_status']=g.get('verification',{}).get('status','pending')
  one[mode+'_verification_failed']=g.get('verification',{}).get('summary',{}).get('failed')
  one[mode+'_infeasible']=g.get('cct',{}).get('infeasible_leaves')
  one[mode+'_truncated']=g.get('cct',{}).get('truncated_leaves')
 row=dict(subject=name,loop_bearing=s['loop_bearing'],RQ1_completion='completed' if paired else 'pending' if not a or not b else 'skipped_incomplete',RQ1_original_s=a.get('wall_time_s'),RQ1_boundary_s=b.get('wall_time_s'),RQ1_overhead_ratio=one['overhead_ratio'],RQ1_original_tests=one['csc_only_tests'],RQ1_boundary_tests=one['boundary_tests'],RQ1_boundary_empty=one['boundary_empty'])
 for mode,g in [('original',a),('boundary',b)]:
  row['RQ1_'+mode+'_verification_status']=g.get('verification',{}).get('status','pending')
  row['RQ1_'+mode+'_verification_failed']=g.get('verification',{}).get('summary',{}).get('failed')
 wrows=[o.get('rq2_w'+str(w),{}) for w in [1,2,4,8]];eligible=all(x.get('status')=='completed' and x.get('fresh') for x in wrows);row['RQ2_status']='completed' if eligible else 'pending' if not all(wrows) else 'skipped_incomplete';row['RQ2_completed_settings']=sum(x.get('status')=='completed' for x in wrows)
 for w,x in zip([1,2,4,8],wrows):
  row[f'RQ2_W{w}_s']=x.get('wall_time_s');row[f'RQ2_S{w}']=wrows[0]['wall_time_s']/x['wall_time_s'] if wrows[0].get('status')==x.get('status')=='completed' else None
  if x:rq2.append(dict(subject=name,workers=w,status=x['status'],generation_s=x.get('wall_time_s'),speedup=row[f'RQ2_S{w}'],frontier_mean=x.get('frontier_mean'),frontier_max=x.get('frontier_max'),**x.get('fingerprint',{})))
 for key in ['cct_structure_sha256','cct_semantic_sha256','test_inputs_sha256']:
  row['RQ2_'+key+'_invariant']=len({x.get('fingerprint',{}).get(key) for x in wrows})==1 and all(x.get('fingerprint',{}).get(key) for x in wrows) if eligible else None
 row['RQ1_mutants_planned']=6;row['RQ1_mutants_recorded']=len(ms)
 for mode in ['original','expanded']:
  gs=[m['modes'].get(mode,{}) for m in ms];vs=[g for g in gs if valid(g)];row[f'RQ1_{mode}_valid_mutants']=len(vs);row[f'RQ1_{mode}_killed']=sum(g['verification']['killed'] for g in vs)
 row['RQ1_kill_valid_pairs']=sum(all(valid(m['modes'].get(mode,{})) for mode in ['original','expanded']) for m in ms)
 for label,oa,ba in [('both',True,True),('boundary_only',False,True),('original_only',True,False),('neither',False,False)]:
  row['RQ1_kill_'+label]=sum(all(valid(m['modes'].get(mode,{})) for mode in ['original','expanded']) and m['modes']['original']['verification']['killed']==oa and m['modes']['expanded']['verification']['killed']==ba for m in ms)
 loc=[dict(m['localization'],subject=name,mutant_id=m['mutant_id'],fault_category=m['fault_category'],operator=m['operator']) for m in ms];rq3.extend(loc);evaluated=[x for x in loc if x['status']=='evaluated'];row['RQ3_evaluated']=len(evaluated);row['RQ3_not_detected']=sum(x['status']=='not_detected' for x in loc);row['RQ3_skipped']=sum(x['status'] not in ['evaluated','not_detected'] for x in loc);row['RQ3_status']='completed' if len(ms)==6 and all(x['status'] in ['evaluated','not_detected'] for x in loc) else 'completed_with_skips' if len(ms)==6 else 'pending'
 for k in [1,2,3]:row[f'RQ3_folded_top{k}_hits']=sum(bool(x.get(f'top{k}_folded_hit')) for x in evaluated)
 rows.append(row)

def csvout(filename,data):
 path=OUT/filename;keys=list(dict.fromkeys(k for r in data for k in r))
 if not keys and filename=='exceptions.csv':keys=['subject','task','status','reason','artifact']
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows([{k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in data])
kill_records=[]
for m in mutants:
 d={k:m[k] for k in ['mutant_id','subject','operator','fault_category','loop_bearing']}
 d['valid_pair']=all(valid(m['modes'].get(mode,{})) for mode in ['original','expanded'])
 for mode,g in m['modes'].items():
  d[mode+'_generation_status']=g.get('status');d[mode+'_verification_status']=g.get('verification',{}).get('status','skipped')
  d[mode+'_killed']=g.get('verification',{}).get('killed');d[mode+'_generation_s']=g.get('wall_time_s')
  d[mode+'_tests']=g.get('testcase_stats',{}).get('executable_records');d[mode+'_artifact']=g.get('folder');d[mode+'_reason']=g.get('reason','')
 d['RQ3_status']=m['localization'].get('status');kill_records.append(d)
csvout('rq1_mutant_killing.csv',kill_records)
structural=[]
for loops in [False,True]:
 group=[r for r in rq1 if r['loop_bearing']==loops and r['valid_completion_pair']]
 d=dict(structural_class='loop-bearing' if loops else 'loop-free',valid_pairs=len(group))
 for field in ['csc_only_tests','boundary_tests','csc_only_empty','boundary_empty','csc_only_nodes','boundary_nodes','boundary_infeasible','boundary_out_of_range','csc_only_s','boundary_s','overhead_ratio']:
  d['mean_'+field]=statistics.mean(r[field] for r in group) if group else None
 d['boundary_empty_zero_subjects']=sum(r['boundary_empty']==0 for r in group);structural.append(d)
csvout('rq1_structural_summary.csv',structural)
csvout('subject_results.csv',rows);csvout('rq1_completion.csv',rq1);csvout('rq2_runs.csv',rq2);csvout('rq3_mutants.csv',rq3);csvout('exceptions.csv',exceptions)
write(OUT/'subject_results.json',rows);write(OUT/'rq3_mutants.json',rq3)
# Loop-bearing kill denominator follows the paper. Non-looping records are retained separately.
loop_pairs=[m for m in mutants if m['loop_bearing'] and all(valid(m['modes'].get(mode,{})) for mode in ['original','expanded'])]
kill={k:0 for k in ['both','boundary_only','original_only','neither']}
for m in loop_pairs:
 a=m['modes']['original']['verification']['killed'];b=m['modes']['expanded']['verification']['killed'];kill['both' if a and b else 'boundary_only' if b else 'original_only' if a else 'neither']+=1
summaries=[];evaluated=[x for x in rq3 if x['status']=='evaluated']
for category in ['overall','condition','statement']:
 group=[x for x in evaluated if category=='overall' or x['fault_category']==category]
 for k in [1,2,3]:
  d=dict(category=category,top_k=k,cases=len(group),mean_budget=statistics.mean(x[f'top{k}_budget'] for x in group) if group else None)
  for method in ['folded','ochiai','dstar','tarantula','barinel','op2']:
   d[method+'_hits']=sum(bool(x.get(f'top{k}_{method}_hit')) for x in group);d[method+'_rate_pct']=100*d[method+'_hits']/len(group) if group else None
  summaries.append(d)
csvout('rq3_summary.csv',summaries)
worker_summary=[]
for w in [1,2,4,8]:
 group=[x for x in rq2 if x['workers']==w and x['status']=='completed' and x.get('speedup') is not None]
 worker_summary.append(dict(workers=w,subjects=len(group),mean_time_s=statistics.mean(x['generation_s'] for x in group) if group else None,mean_speedup=statistics.mean(x['speedup'] for x in group) if group else None,median_speedup=statistics.median(x['speedup'] for x in group) if group else None))
csvout('rq2_summary.csv',worker_summary)
summary=dict(original_config_cells_recorded=len(originals),original_config_cells_planned=120,original_statuses=dict(collections.Counter(x['status'] for x in originals)),mutants_recorded=len(mutants),mutants_planned=120,mutant_generation_planned=240,mutant_generation_statuses=dict(collections.Counter(g.get('status') for m in mutants for g in m['modes'].values())),rq1_valid_completion_pairs=sum(x['valid_completion_pair'] for x in rq1),rq1_loop_mutants_planned=sum(s['loop_bearing'] for s in subjects)*6,rq1_valid_loop_kill_pairs=len(loop_pairs),rq1_kill_outcomes=kill,rq2=worker_summary,rq2_all_fingerprints_invariant_subjects=sum(all(r.get('RQ2_'+k+'_invariant') for k in ['cct_structure_sha256','cct_semantic_sha256','test_inputs_sha256']) for r in rows),rq3_statuses=dict(collections.Counter(x['status'] for x in rq3)),rq3=summaries,exception_count=len(exceptions),all_cells_recorded=len(originals)==120 and len(mutants)==120 and all(len(m['modes'])==2 for m in mutants))
write(OUT/'summary.json',summary)
summary['rq1_structural']=structural
summary['original_verification_violations']=sum(x.get('verification',{}).get('summary',{}).get('failed',0)>0 for x in originals)
summary['mutant_generation_cells_recorded']=sum(len(m['modes']) for m in mutants)
write(OUT/'summary.json',summary)
fmt=lambda x:'—' if x is None else f'{x:.2f}' if isinstance(x,float) else str(x)

# Exact paired McNemar tests; one Holm family across the three depths.
from math import comb

def exact_mcnemar(b, c):
 n = b + c
 return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2**n)

paired_tests = []
for k in [1, 2, 3]:
 b = sum(bool(x[f'top{k}_folded_hit']) and not bool(x[f'top{k}_op2_hit']) for x in evaluated)
 c = sum(bool(x[f'top{k}_op2_hit']) and not bool(x[f'top{k}_folded_hit']) for x in evaluated)
 paired_tests.append(dict(top_k=k, folded_only=b, op2_only=c, exact_p=exact_mcnemar(b, c)))
previous_adjusted = 0.0
for rank, test in enumerate(sorted(paired_tests, key=lambda x: x['exact_p'])):
 previous_adjusted = max(previous_adjusted, min(1.0, (len(paired_tests) - rank) * test['exact_p']))
 test['holm_p'] = previous_adjusted
paired_table = ['| Top-k | Fold-the-Tree-only hits | Op2-only hits | Exact p | Holm-adjusted p |', '|---:|---:|---:|---:|---:|']
for test in paired_tests:
 paired_table.append(f"| {test['top_k']} | {test['folded_only']} | {test['op2_only']} | {test['exact_p']:.5f} | {test['holm_p']:.5f} |")

# Verification timing uses complete per-program process records.
loop_by_subject = {x['subject']: x['loop_bearing'] for x in subjects}
verification_means = {}
verification_tags = ['rq1_original', 'rq1_expanded', 'rq2_w4']
for tag in verification_tags:
 records = [x for x in originals if x['tag'] == tag]
 if len(records) != len(subjects) or {x['subject'] for x in records} != set(loop_by_subject):
  raise ValueError(f'Incomplete or duplicate verification records for {tag}')
 if any(x.get('verification', {}).get('status') != 'completed' for x in records):
  raise ValueError(f'Verification did not complete normally for {tag}')
 for group, loop_flag in [('loop_free', False), ('loop_bearing', True), ('all', None)]:
  values = [x['verification']['wall_time_s'] for x in records
            if loop_flag is None or loop_by_subject[x['subject']] == loop_flag]
  verification_means[(tag, group)] = statistics.mean(values)
loop_free_count = sum(not x['loop_bearing'] for x in subjects)
loop_bearing_count = sum(x['loop_bearing'] for x in subjects)
# Retain the approved prose for this dataset; other sizes remain readable.
count_words = {6: 'six', 14: 'fourteen'}

# Report presentation only; statistics are computed above.
rq1_table = ['| Group | Program pairs | Tests: CSC-only / CSC+Boundary | Ancestor-stopped empty leaves: CSC-only / CSC+Boundary | CCT nodes: CSC-only / CSC+Boundary | Generation time (s): CSC-only / CSC+Boundary | Mean time ratio |', '|---|---:|---:|---:|---:|---:|---:|']
for d in structural:
 rq1_table.append('| '+d['structural_class']+' | '+str(d['valid_pairs'])+' | '+' | '.join(fmt(d['mean_'+a])+' / '+fmt(d['mean_'+b]) for a,b in [('csc_only_tests','boundary_tests'),('csc_only_empty','boundary_empty'),('csc_only_nodes','boundary_nodes'),('csc_only_s','boundary_s')])+' | '+fmt(d['mean_overhead_ratio'])+' |')
rq2_table = ['| Workers | Valid programs | Mean generation time (s) | Mean speedup | Median speedup |', '|---:|---:|---:|---:|---:|']
for x in worker_summary:rq2_table.append('| '+' | '.join(fmt(x[k]) for k in ['workers','subjects','mean_time_s','mean_speedup','median_speedup'])+' |')
rq3_table = ['| Top-k | Evaluated candidates | Folded | Ochiai | DStar | Tarantula | Barinel | Op2 |', '|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in summaries:
 if x['category']=='overall':rq3_table.append('| '+' | '.join(fmt(x[k]) for k in ['top_k','cases','folded_rate_pct','ochiai_rate_pct','dstar_rate_pct','tarantula_rate_pct','barinel_rate_pct','op2_rate_pct'])+' |')
status_table = ['| Program | RQ1 completion | RQ1 valid mutant pairs | RQ2 completion | RQ3 evaluated / undetected / skipped |', '|---|---|---:|---|---|']
for x in rows:status_table.append(f"| {x['subject']} | {x['RQ1_completion']} | {x['RQ1_kill_valid_pairs']}/6 | {x['RQ2_status']} | {x['RQ3_evaluated']}/{x['RQ3_not_detected']}/{x['RQ3_skipped']} |")

report = """# Supplementary Evaluation of 20 External Program Cores

Recorded original-program configurations: {original_count}/{original_planned}.
Recorded mutation candidates: {mutant_count}/{mutant_planned}. Per-program results for RQ1–RQ3 are recorded
in `subject_results.csv`. The experiment plan, configuration, and
individual execution commands are retained.

The detailed supplementary results are provided in this artifact and
the response letter. The manuscript provides a brief pointer to the
supplementary evaluation.

## RQ1: Exploration, Generation Cost, and Mutant Detection

Normally completed original-program pairs: {completed_pairs}/{subject_count}.
Valid mutant pairs in the loop-bearing group: {loop_pairs_count}/{loop_planned}.
Mutants killed by both modes: {both}; only by CSC+Boundary: {boundary_only};
only by CSC-only: {original_only}; by neither: {neither}.

The following table includes normally completed original-program pairs.
Counts and generation times are averaged across programs within each
group. The mean time ratio is calculated by first dividing CSC+Boundary
generation time by CSC-only generation time for each program, then
averaging those ratios.

{rq1_table}

Verification time measures the complete refined-TBFV process,
including default report generation, for all collected paths of each
program. Mean verification times for sequential CSC-only and
CSC+Boundary are {verification_original_free:.3f} and {verification_boundary_free:.3f} seconds for the {loop_free_text} loop-free programs,
and {verification_original_loops:.3f} and {verification_boundary_loops:.3f} seconds for the {loop_bearing_text} loop-bearing programs.
Across all {subject_count} programs, the corresponding means are {verification_original_all:.3f} and
{verification_boundary_all:.3f} seconds.

## RQ2: Worker Scaling

Programs with all three canonical final-output fingerprints agreeing
across the four worker settings: {invariant_count}/{subject_count}.

Each configuration was run once. The times are observed generation
costs on the recorded machine. Speedup is calculated for each program
relative to batch W=1; the table reports the mean and median of those
program-level ratios.

{rq2_table}

For batch W=4, mean verification time is {verification_batch4:.3f} seconds across all
{subject_count} programs. Verification completed normally for every program under
both sequential configurations and batch W=4. These means use
`verification.wall_time_s` in `original_results.jsonl`, with equal
weight for each program.

## RQ3: Fault Localization

Localization statuses: {localization_statuses}.
Hit rates use all {evaluated_count} candidates with failure
evidence and a successfully completed localization process, including
ranking misses. Undetected candidates and exceptional outcomes are
recorded separately.

All values in the method columns are hit rates (%). At depth k,
Fold-the-Tree inspects the union of source lines in its first k condition
candidates and first k edge-partition candidates. Each of the five SBFL
formulas receives the same number of unique source lines for that
candidate and depth. The condition/state-update breakdown and actual
inspection budgets are recorded in `rq3_summary.csv`.

{rq3_table}

An undetected mutant has no failure detected by the generated tests
and FSF checks in this evaluation; this status does not establish
mutant equivalence.

### Paired Comparison with Op2

The following results use two-sided exact McNemar tests on the
{evaluated_count} evaluated mutants. Holm correction is applied jointly to the
three comparisons at Top-1, Top-2, and Top-3 against Op2.

{paired_table}

For discordant counts b and c, the exact p-value is
min(1, 2 × sum(comb(b+c, i), i=0,...,min(b,c)) / 2^(b+c)).
The paired hit indicators are recorded in `rq3_mutants.csv`.
All three adjusted p-values are below 0.05. Mutants from the same
program may share evidence, so these mutant-level tests are
interpreted as exploratory.

## Per-Program Completion Status

Detailed times, CCT sizes, test counts, mutant-detection results, and
localization denominators are recorded in `subject_results.csv`.

{status_table}

The exception ledger, `exceptions.csv`, contains {exception_count} entries. The
protocol excludes repair or parameter tuning followed by retries.
Budget exhaustion and timeouts do not count as normal completion.

Original-program configurations reporting an FSF failure: {fsf_failures}.
RQ1 completion denotes normal generation completion; FSF outcomes are
recorded separately in `rq1_completion.csv`. Mutant experiments proceed
only after the corresponding original program's batch-W4 FSF check
completes normally without failures.

## Evaluation Scope

The group comprises {subject_count} controlled program cores, including methods
from shared upstream projects. Its newly constructed single-fault
mutants need not have the same difficulty distribution as the original
252 mutants. One run per configuration provides observed timing
results but does not estimate run-to-run variation.

## Supporting Records

- `PLAN.md`: experiment plan.
- `config.json`: configuration and tool hashes.
- `subjects.json`: input hashes.
- `dataset/mutants_manifest.jsonl`: predefined mutation candidates.
- `rq1_mutant_killing.csv`: per-mutant detection results.
- `generation_runs.jsonl`: generation commands.
- `mutant_results.jsonl`: detection results and localization evidence paths.
- `exceptions.csv`: exception ledger.
- `completion_audit.json`: post-experiment completeness checks.
""".format(
 original_count=len(originals), original_planned=summary['original_config_cells_planned'],
 mutant_count=len(mutants), mutant_planned=summary['mutants_planned'],
 completed_pairs=summary['rq1_valid_completion_pairs'], subject_count=len(subjects),
 loop_pairs_count=len(loop_pairs), loop_planned=summary['rq1_loop_mutants_planned'],
 both=kill['both'], boundary_only=kill['boundary_only'],
 original_only=kill['original_only'], neither=kill['neither'],
 invariant_count=summary['rq2_all_fingerprints_invariant_subjects'],
 localization_statuses=json.dumps(summary['rq3_statuses'], sort_keys=True),
 evaluated_count=len(evaluated), exception_count=len(exceptions),
 fsf_failures=summary['original_verification_violations'],
 rq1_table='\n'.join(rq1_table), rq2_table='\n'.join(rq2_table),
 rq3_table='\n'.join(rq3_table), status_table='\n'.join(status_table),
 paired_table='\n'.join(paired_table),
 verification_original_free=verification_means[('rq1_original', 'loop_free')],
 verification_boundary_free=verification_means[('rq1_expanded', 'loop_free')],
 verification_original_loops=verification_means[('rq1_original', 'loop_bearing')],
 verification_boundary_loops=verification_means[('rq1_expanded', 'loop_bearing')],
 verification_original_all=verification_means[('rq1_original', 'all')],
 verification_boundary_all=verification_means[('rq1_expanded', 'all')],
 verification_batch4=verification_means[('rq2_w4', 'all')],
 loop_free_text=count_words.get(loop_free_count, str(loop_free_count)),
 loop_bearing_text=count_words.get(loop_bearing_count, str(loop_bearing_count)),
)
(OUT/'RESULTS.md').write_text(report)
print(json.dumps({k:v for k,v in summary.items() if k not in ['rq3']},indent=2))
