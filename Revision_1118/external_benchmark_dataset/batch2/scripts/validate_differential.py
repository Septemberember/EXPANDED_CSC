"""Compile original methods, not rewritten reference algorithms; exhaustive mapped domains."""
from pathlib import Path
import json,re,subprocess,hashlib,os,shutil
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'sources';OUT=ROOT/'validation/differential';REF=OUT/'reference';REF.mkdir(parents=True,exist_ok=True)
fallback=Path('/Users/jiazedong/Library/Java/JavaVirtualMachines/ms-17.0.15/Contents/Home/bin');JAVA=Path(os.environ['JAVA_HOME'])/'bin' if os.environ.get('JAVA_HOME') else fallback if fallback.exists() else Path(shutil.which('javac')).parent
files=[];records=[]
def write(path,text,source=None,edit='none'):
 p=REF/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);files.append(str(p))
 records.append(dict(reference=path,source=source,edit=edit,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
def copy(source,path=None):write(path or Path(source).name,(SRC/source).read_text(),source)
def extract(source,signature):
 text=(SRC/source).read_text();start=text.index(signature);brace=text.index('{',start);depth=1;end=brace+1
 while depth:
  if text[end]=='{':depth+=1
  elif text[end]=='}':depth-=1
  end+=1
 method=text[start:end]
 records.append(dict(source=source,signature=signature,method_sha256=hashlib.sha256(method.encode()).hexdigest(),edit='method text extracted unchanged'))
 return method
SV='sv-benchmarks/java/';JR=SV+'java-ranger-regression/'
for f in ['Environment.java','MinePump.java']:copy(SV+'MinePump/spec1-5_product64/MinePumpSystem/'+f,'MinePumpSystem/'+f)
for source,name in [(JR+'TCAS_prop1/Main.java','RefTcas'),(SV+'algorithms/BellmanFord-FunSat01/Main.java','RefBellman')]:
 write(name+'.java',(SRC/source).read_text().replace('public class Main','public class '+name),source,'rename top-level class only; original methods unchanged')
write('org/sosy_lab/sv_benchmarks/Verifier.java','package org.sosy_lab.sv_benchmarks; public class Verifier { public static int nondetInt(){throw new UnsupportedOperationException("unused driver");} public static void assume(boolean b){throw new UnsupportedOperationException("unused driver");}}',edit='compile-only stub; neither driver nor stub called')
for group in ['printtokens_eqchk/impl','replace5_eqchk/impl']:
 for f in sorted((SRC/JR/group).glob('*.java')):copy(str(f.relative_to(SRC)))
copy(JR+'apachecli_eqchk/OptionValidator.java')
source='commons-lang/StringUtils.java';methods=[extract(source,sig) for sig in ['public static int getLevenshteinDistance(CharSequence s, CharSequence t) {','public static boolean isEmpty(final CharSequence cs) {','public static boolean isNotEmpty(final CharSequence cs) {']]
write('org/apache/commons/lang3/StringUtils.java','package org.apache.commons.lang3; public class StringUtils { public static final String EMPTY="";\n'+'\n'.join(methods)+'\n}',source,'selected original methods unchanged; omit unrelated methods to avoid unrelated dependencies')
for f in ['CharSet.java','CharRange.java','CharSetUtils.java']:copy('commons-lang/'+f,'org/apache/commons/lang3/'+f)
method=extract('commons-lang/ArrayUtils.java','public static int lastIndexOf(final int[] array, final int valueToFind, int startIndex) {')
write('RefArray.java','public class RefArray { public static final int INDEX_NOT_FOUND=-1;\n'+method+'\n}','commons-lang/ArrayUtils.java','selected original method unchanged with original constant')
method=extract('commons-math/MathArrays.java','public static boolean checkOrder(double[] val, OrderDirection dir,')
write('RefMath.java','public class RefMath { public enum OrderDirection {INCREASING, DECREASING}\n'+method+'\n}\nclass MathInternalError extends RuntimeException {}\nclass NonMonotonicSequenceException extends RuntimeException { NonMonotonicSequenceException(double v,double p,int i,RefMath.OrderDirection d,boolean s){} }\n','commons-math/MathArrays.java','original method unchanged; compile-only exception classes never instantiated (abort=false; valid enums)')
files+= [str(p) for p in sorted((ROOT/'subjects').glob('*/*.java'))]+[str(ROOT/'scripts/DifferentialHarness.java')]
classes=OUT/'classes';classes.mkdir(exist_ok=True)
r=subprocess.run([str(JAVA/'javac'),'-d',str(classes)]+files,capture_output=True,text=True);(OUT/'compile.log').write_text(r.stdout+r.stderr)
if r.returncode:raise SystemExit(r.stderr)
r=subprocess.run([str(JAVA/'java'),'-ea','-cp',str(classes),'DifferentialHarness'],capture_output=True,text=True,timeout=120);(OUT/'run.log').write_text(r.stdout+r.stderr);print(r.stdout+r.stderr)
results={}
for line in r.stdout.splitlines():
 name,count,status=line.split();results[name]=dict(cases=int(count),status=status,scope='selected invalid inputs' if name=='guard_checks' else 'exhaustive declared mapped domain')
(OUT/'report.json').write_text(json.dumps(dict(exit_code=r.returncode,assertions_enabled=True,reference_build=records,results=results),indent=2)+'\n');raise SystemExit(r.returncode)
