from pathlib import Path
import json,subprocess,re,shutil,hashlib,os
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'sources/jpf-symbc/src/examples';OUT=ROOT/'validation/differential';OUT.mkdir(parents=True,exist_ok=True)
fallback=Path('/Users/jiazedong/Library/Java/JavaVirtualMachines/ms-17.0.15/Contents/Home/bin')
JAVA=Path(os.environ['JAVA_HOME'])/'bin' if os.environ.get('JAVA_HOME') else fallback if fallback.exists() else Path(shutil.which('javac')).parent
files=[];edits=[]
for subject in json.loads((ROOT/'manifest.json').read_text())['subjects']:
 path=subject['source'];text=(SRC/path).read_text()
 # Reference compatibility edits do not alter retained method computations.
 text=re.sub(r'^import gov\.nasa\.jpf\.[^;]+;\s*','',text,flags=re.M)
 text=re.sub(r'^\s*@Preconditions\([^\n]*\)\s*','\n',text,flags=re.M)
 text=text.replace('Debug.printPC("\\n Path Condition: ");','/* omitted diagnostic only */')
 text=text.replace('Verify.randomBool()','false /* unused main driver */')
 target=OUT/'reference'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text);files.append(str(target))
 edits.append({'source':path,'original_sha256':hashlib.sha256((SRC/path).read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
 files.append(str(ROOT/'subjects'/subject['name']/(subject['name']+'.java')))
files.append(str(ROOT/'scripts/DifferentialHarness.java'));classes=OUT/'classes';classes.mkdir(exist_ok=True)
r=subprocess.run([str(JAVA/'javac'),'-d',str(classes)]+files,capture_output=True,text=True)
(OUT/'compile.log').write_text(r.stdout+r.stderr)
if r.returncode:raise SystemExit(r.stderr)
r=subprocess.run([str(JAVA/'java'),'-ea','-cp',str(classes),'DifferentialHarness'],capture_output=True,text=True,timeout=90)
(OUT/'run.log').write_text(r.stdout+r.stderr);print(r.stdout+r.stderr)
results={}
for line in r.stdout.splitlines():
 name,count,status=line.split();results[name]={'cases':int(count),'status':status,'scope':'exhaustive declared domain' if name!='guard_checks' else 'selected invalid inputs'}
(OUT/'report.json').write_text(json.dumps({'exit_code':r.returncode,'assertions_enabled':True,'reference_edits':'Remove JPF imports/annotations and diagnostic print; replace Verify.randomBool only in unused main. All selected original methods retain computations, assertions, strings and objects.','sources':edits,'results':results},indent=2)+'\n')
raise SystemExit(r.returncode)
