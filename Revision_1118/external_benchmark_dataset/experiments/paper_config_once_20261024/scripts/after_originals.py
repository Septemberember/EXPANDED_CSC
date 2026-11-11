"""Start mutant work only after the original-run process has exited successfully."""
from common import *
original_pid=int(sys.argv[1]);print('Waiting for original process',original_pid,flush=True)
while True:
 progress=read(OUT/'originals_progress.json',{})
 if progress.get('status')=='completed':break
 try:os.kill(original_pid,0)
 except ProcessLookupError:raise SystemExit('Original process disappeared before completion; no mutant run started')
 time.sleep(10)
raise SystemExit(subprocess.call([sys.executable,str(OUT/'scripts/run_mutants.py')],cwd=TOOL))
