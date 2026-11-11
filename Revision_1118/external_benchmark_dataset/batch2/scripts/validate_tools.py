"""Reuse the established runner with batch-local paths and per-subject budgets."""
from pathlib import Path
import importlib.util,json,concurrent.futures,sys
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runner',ROOT.parent/'scripts/validate_tools.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.ROOT=ROOT
subjects=json.loads((ROOT/'manifest.json').read_text())['subjects']
subjects=[s for s in subjects if len(sys.argv)==1 or s['name'] in sys.argv[1:]]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(runner.run,subjects))
(ROOT/'validation/latest_run.json').write_text(json.dumps(results,indent=2)+'\n')
