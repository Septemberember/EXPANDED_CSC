"""Paper's existing Fold-the-Tree and all five SBFL formulas; no generation."""
from common import *
from baseline.SFL.sfl_runner import run_sfl_localization
from folded_composite_budget_compare_sfl import MutantRecord,_compare_one_mutant
record=read(Path(sys.argv[1]));g=read(Path(sys.argv[2]));folder=Path(g['folder']);directory=Path(g['result_dir']);mutant=record['mutant_id']
# Entire ranking, so inspection budgets cannot silently exceed saved top-10.
sfl=run_sfl_localization(directory,folder/'verification.json',top_k=None);write(folder/'sfl_localization.json',sfl)
rec=MutantRecord(mutant_id=mutant,result_dir=directory,sfl_report=folder/'sfl_localization.json',ground_truth=record['ground_truth'],subject=record['subject'],operator=record['operator'],fault_kind=record['fault_kind'],fault_category=record['fault_category'])
row=_compare_one_mutant(rec,OUT/'rq3','ochiai',[1,2,3],'coverage_x_purity')
if row['status']=='evaluated':
 aggregated=read(OUT/'rq3/artifacts'/mutant/'cct_folded_localization_aggregated.json',{})
 conditions=aggregated.get('aggregated_condition_node_ranking',[]);edges=aggregated.get('aggregated_interval_rankings',{}).get('folded_edge_partition',[]);target=record['ground_truth']['primary_line']
 for k in [1,2,3]:
  lines={int(x['line']) for x in conditions[:k] if x.get('line') is not None}
  edge_lines={int(line) for x in edges[:k] for line in (x.get('statement_lines') or [])}
  row[f'top{k}_condition_hit']=target in lines;row[f'top{k}_edge_partition_hit']=target in edge_lines;row[f'top{k}_folded_region_lines']=sorted(lines|edge_lines)
  budget=row[f'top{k}_budget']
  for formula,ranking in sfl['rankings'].items():
   checked=[]
   for item in ranking:
    if len(checked)>=budget:break
    if int(item['line']) not in checked:checked.append(int(item['line']))
   row[f'top{k}_{formula}_hit']=target in checked;row[f'top{k}_{formula}_region_lines']=checked
write(folder/'localization.json',row);print(mutant,row['status'],flush=True)
