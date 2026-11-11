from pathlib import Path
import json,hashlib,itertools
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'sources';items=[]
SV='sv-benchmarks/java/';JR=SV+'java-ranger-regression/'
REPOS={'sv':('https://github.com/sosy-lab/sv-benchmarks','2e1723fde6aa65a250dcb677efa45edaa4b6b631','SV-Benchmarks Java'),'lang':('https://github.com/apache/commons-lang','d1a45e9738de5b3e299bb51e987565dcce55fee6','Defects4J Lang-1f project snapshot'),'math':('https://github.com/apache/commons-math','86545dab3ed57872ad98b23e46924d67ddad03fc','Defects4J Math-1f project snapshot')}
def add(name,repo,source,method,params,body,bad,cases,domain,note,bootstrap,max_iter=500):
 p=ROOT/'subjects'/name;(p/'FSF').mkdir(parents=True,exist_ok=True)
 original=(SRC/source).read_text();header='// Derived from '+source+'; see provenance.md and sources for licenses.\n'
 if original.startswith('/*'):header=original[:original.index('*/')+2]+'\n'
 if 'BellmanFord' in source:header=original[original.index('/**'):original.index('public class Main')]+'\n'
 (p/(name+'.java')).write_text(header+'// Modified: bounded scalar core; original source retained separately.\npublic class '+name+' {\n public static int test('+params+') {\n'+f'if ({bad}) {{ return -99; }}\n'+body+'\n }\n}\n')
 cases=[(bad,'-99')]+[(f'!({bad}) && ({t})',d) for t,d in cases]
 (p/'FSF'/(name+'_FSF.txt')).write_text('\n\n'.join(f'[fsf_{i}]\nT: {t}\nD: return_value == {d}' for i,(t,d) in enumerate(cases,1))+'\n')
 url,commit,suite=REPOS[repo];entry=dict(name=name,repository=url,commit=commit,suite=suite,source=source,source_method=method,domain=domain,adaptation=note,bootstrap=bootstrap,max_iter=max_iter,source_sha256=hashlib.sha256((SRC/source).read_bytes()).hexdigest(),status='unvalidated');items.append(entry)
 (p/'provenance.md').write_text(f'# {name}\n\nSource: {suite}; {url}, commit `{commit}`.\n\nSnapshot: `{source}`; selected method(s): {method}.\n\nDomain and mapping: {domain}\n\nAdaptations and retained observable: {note}\n\nInput outside the domain returns -99. This is a core slice, not a verification of the entire upstream program. Defects4J labels identify the checked-out project revision, not ten different bugs or reproduction of the benchmark bug. Upstream source/license notices are retained under sources/.\n')
def bounds(names,lo,hi):return ' || '.join(f'{x} < {lo} || {x} > {hi}' for x in names.split())
# MinePump product64: one step, all previous-state combinations.
body='''int level = water;
boolean pump = running;
if (pump) {
 if (level == 2) { level = 1; } else { if (level == 1) { level = 0; } }
}
if (active) {
 if (pump && methane) { pump = false; }
 else {
  if (pump && level != 0) { pump = false; }
  else {
   if (!pump && level == 2) { if (!methane) { pump = true; } }
  }
 }
}
int state = 0;
if (pump) { state = 10; }
return state + level;'''
cases=[]
for w,r,a,m in itertools.product(range(3),[False,True],[False,True],[False,True]):
 level=max(0,w-int(r));pump=r if not a else ((not m and level==0) if r else (not m and level==2))
 t=f'water == {w} && '+ ' && '.join(('' if flag else '!')+n for n,flag in [('running',r),('active',a),('methane',m)])
 cases.append((t,str(10*int(pump)+level)))
add('SvMinePumpStep','sv',SV+'MinePump/spec1-5_product64/MinePumpSystem/MinePump.java','timeShift; processEnvironment; Environment.lowerWaterLevel','int water, boolean running, boolean active, boolean methane',body,bounds('water',0,2),cases,'water enum 0/1/2=low/normal/high, all state flags; explicit arbitrary prior state','Inline feature-wrapper calls and enum switches; preserve water lowering before environment processing and the counterintuitive original !isLowWaterSensorDry test (water!=low); encode pump*10+water. No reachability claim.','water=2,running=false,active=true,methane=false')
# TCAS non-crossing climb; map offsets to original thresholds, retain ALIM and preference branching.
body='''int alim = 740;
if (layer == 0) { alim = 400; } else { if (layer == 1) { alim = 500; } else { if (layer == 2) { alim = 640; } } }
int up = alim + upDelta * 100;
int down = alim + downDelta * 100;
int sep = 500 + separation * 100;
int biased = up;
if (inhibit) { biased = up + 100; }
int preferred = 0;
if (biased > down) { preferred = 1; }
if (preferred != 0) {
 if (!(down >= alim)) { return 1; } else { return 0; }
} else {
 if (!(sep >= 600)) { return 0; }
 else {
  if (!(up >= alim)) { return 0; }
  else { if (!above) { return 0; } else { return 1; } }
 }
}'''
pref='((inhibit && upDelta + 1 > downDelta) || (!inhibit && upDelta > downDelta))';ok=f'(({pref} && downDelta < 0) || (!{pref} && separation >= 1 && upDelta >= 0 && above))'
add('SvTcasClimb','sv',JR+'TCAS_prop1/Main.java','Non_Crossing_Biased_Climb; ALIM; Inhibit_Biased_Climb; Own_Above_Threat','int layer, int upDelta, int downDelta, int separation, boolean above, boolean inhibit',body,bounds('layer',0,3)+' || '+bounds('upDelta downDelta',-2,2)+' || '+bounds('separation',0,2),[(ok,'1'),('!'+ok,'0')],'four altitude layers; up/down = ALIM(layer)+100*delta, delta -2..2; vertical separation 500/600/700; own/other altitude 1/0 if above else 0/0; inhibit bool','Extract non-crossing climb predicate (not full advisory); inline helpers and expose fields. Preserve original comparison order and return boolean encoded 0/1.','layer=0,upDelta=0,downDelta=-1,separation=1,above=true,inhibit=false')
# Fixed three-node complete nonnegative graph; exact unfolding of fixed i,j scan.
body='''int d0 = 0;
int d1 = 2147483647;
int d2 = 2147483647;
int k = 0;
while (k < 3) {
 boolean relaxed = false;
 if (d1 > d0 + w01) { d1 = d0 + w01; relaxed = true; }
 if (d2 > d0 + w02) { d2 = d0 + w02; relaxed = true; }
 if (d0 > d1 + 4) { d0 = d1 + 4; relaxed = true; }
 if (d2 > d1 + w12) { d2 = d1 + w12; relaxed = true; }
 if (d0 > d2 + 4) { d0 = d2 + 4; relaxed = true; }
 if (d1 > d2 + w21) { d1 = d2 + w21; relaxed = true; }
 if (!relaxed) { return d1 * 10 + d2; }
 k = k + 1;
}
return d1 * 10 + d2;'''
cases=[]
for x,y in itertools.product([False,True],repeat=2):
 c1='w01 <= w02 + w21';c2='w02 <= w01 + w12';a='w01' if x else '(w02 + w21)';b='w02' if y else '(w01 + w12)'
 cases.append((('' if x else '!')+'('+c1+') && '+('' if y else '!')+'('+c2+')',a+' * 10 + '+b))
# Both indirect paths strictly shorter is impossible for nonnegative weights.
cases=cases[1:]
add('SvBellmanFord3','sv',SV+'algorithms/BellmanFord-FunSat01/Main.java','runBellmanFord','int w01, int w02, int w12, int w21',body,bounds('w01 w02 w12 w21',0,4),cases,'N=3, source=0; edges 1->0 and 2->0 fixed to 4; other four weights 0..4; diagonal ignored','Scalarize distances; unfold fixed 3x3 edge scans in original order; retain pass loop and early exit. All nodes become finite in first row so infinite guards are provably true at subsequent edges. Encode distances to nodes1/2 as 10*d1+d2; d0 remains0. No negative cycles.','w01=4,w02=1,w12=2,w21=1',1000)
# Token identifier: 3 chars + terminating NUL; full printable ASCII.
alpha=lambda x:f'(({x} >= 65 && {x} <= 90) || ({x} >= 97 && {x} <= 122))'
digit=lambda x:f'({x} >= 48 && {x} <= 57)'
body=f'''int i = 1;
boolean letter = {alpha('a')};
if (letter) {{
 while (i < 3) {{
  int ch = b;
  if (i == 2) {{ ch = c; }}
  letter = {alpha('ch')};
  if (letter) {{ i = i + 1; }}
  else {{
   boolean number = {digit('ch')};
   if (number) {{ i = i + 1; }} else {{ return 0; }}
  }}
 }}
 return 1;
}} else {{ return 0; }}'''
ok=f'{alpha("a")} && ({alpha("b")} || {digit("b")}) && ({alpha("c")} || {digit("c")})'
add('SvTokenIdentifier','sv',JR+'printtokens_eqchk/impl/PrintTokens2.java','isIdentifier; isalpha; isdigit','int a, int b, int c',body,bounds('a b c',32,126),[(ok,'1'),(f'!({ok})','0')],'exactly three printable ASCII characters followed by NUL','Flatten token array and inline character classification; preserve scan and early rejection. Does not tokenize streams or recognize other token classes.','a=65,b=48,c=97',1000)
# Single atom regex matcher: four atom kinds selected, two class members.
body='''int advance = -1;
if (ch != 0) {
 if (kind == 0) { if (ch == a) { advance = 1; } }
 else { if (kind == 1) { if (ch != 10) { advance = 1; } }
 else {
  boolean found = false;
  int i = 2;
  while (i > 0) {
   int value = a;
   if (i == 2) { value = b; }
   if (ch == value) { found = true; i = 0; } else { i = i - 1; }
  }
  if (kind == 2) { if (found) { advance = 1; } }
  else { if (ch != 10 && !found) { advance = 1; } }
 }
 }
}
if (advance >= 0) { return index + advance; }
return -1;'''
ok='(ch != 0 && ((kind == 0 && ch == a) || (kind == 1 && ch != 10) || (kind == 2 && (ch == a || ch == b)) || (kind == 3 && ch != 10 && ch != a && ch != b)))'
add('SvReplaceAtom','sv',JR+'replace5_eqchk/impl/Replace.java','omatch; locate','int kind, int ch, int a, int b, int index',body,bounds('kind',0,3)+' || '+bounds('ch a b',0,10)+' || '+bounds('index',0,1),[(ok,'index + 1'),('!'+ok,'-1')],'kind 0 literal,1 any,2 two-member class,3 negated class; codes 0..10, index0/1','Scalarize one pattern atom and class contents; inline locate reverse scan; return updated index on match, -1 on failure. Exclude anchors/closure and complete replace pipeline.','kind=2,ch=3,a=2,b=3,index=0')
body='''boolean valid = false;
if ((code >= 97 && code <= 122) || (code >= 65 && code <= 90) || code == 95 || code == 46) { valid = true; }
boolean option = false;
if (valid || code == 32 || code == 63 || code == 64) { option = true; }
if (!option) { return -1; }
return 1;'''
ok='((code >= 97 && code <= 122) || (code >= 65 && code <= 90) || code == 95 || code == 46 || code == 32 || code == 63 || code == 64)'
add('SvCliOption','sv',JR+'apachecli_eqchk/OptionValidator.java','validateOption; isValidOpt; isValidChar','int code',body,bounds('code',0,127),[(ok,'1'),('!'+ok,'-1')],'ASCII codes0..127','Inline option validation helper chain; exception -> -1 and success ->1. Preserve dot/underscore acceptance present in implementation despite narrower prose comments. Small reserve subject; not full CLI parsing.','code=65')
# Levenshtein fixed 2 vs 3, scalar rows and helper min; retain both loops.
body='''int p0 = 0; int p1 = 1; int p2 = 2;
int d0 = 0; int d1 = 0; int d2 = 0;
int j = 1;
while (j <= 3) {
 int tj = x;
 if (j == 2) { tj = y; }
 if (j == 3) { tj = z; }
 d0 = j;
 int i = 1;
 while (i <= 2) {
  int si = a; int left = d0; int top = p1; int diagonal = p0;
  if (i == 2) { si = b; left = d1; top = p2; diagonal = p1; }
  int cost = 1;
  if (si == tj) { cost = 0; }
  int value = left + 1;
  if (top + 1 < value) { value = top + 1; }
  if (diagonal + cost < value) { value = diagonal + cost; }
  if (i == 1) { d1 = value; } else { d2 = value; }
  i = i + 1;
 }
 p0 = d0; p1 = d1; p2 = d2;
 j = j + 1;
}
return p2;'''
one='((a == x && b == y) || (a == x && b == z) || (a == y && b == z))';two='(a == x || a == y || b == y || b == z)'
add('D4jLevenshtein23','lang','commons-lang/StringUtils.java','getLevenshteinDistance(CharSequence, CharSequence)','int a, int b, int x, int y, int z',body,bounds('a b x y z',1,3),[(one,'1'),(f'!{one} && {two}','2'),('!'+two,'3')],'strings length2 and3 over codes1..3; non-null','Scalarize two working distance arrays, inline Math.min and ternary; retain nested dynamic-programming loops and recurrence. Fixed nonempty dimensions remove null/empty/swap branches. Return edit distance.','a=1,b=2,x=1,y=3,z=2',1500)
# squeeze full output, four digits and range charset.
body='''int result = 0;
int last = 32;
int i = 0;
while (i < 4) {
 int ch = a;
 if (i == 1) { ch = b; }
 if (i == 2) { ch = c; }
 if (i == 3) { ch = d; }
 if (!(ch == last && i != 0 && ch >= low && ch <= high)) {
  result = result * 10 + ch;
  last = ch;
 }
 i = i + 1;
}
return result;'''
m=['(b == a && b >= low && b <= high)','(c == b && c >= low && c <= high)','(d == c && d >= low && d <= high)'];cases=[]
for flags in itertools.product([False,True],repeat=3):
 chars=['a']+[x for x,f in zip(['b','c','d'],flags) if not f]
 expr=' + '.join(f'{x} * {10**(len(chars)-i-1)}' for i,x in enumerate(chars))
 cases.append((' && '.join(('' if f else '!')+m for f,m in zip(flags,m)),expr))
add('D4jCharSqueeze','lang','commons-lang/CharSetUtils.java','squeeze; CharSet.contains','int a, int b, int c, int d, int low, int high',body,bounds('a b c d low high',1,3)+' || low > high',cases,'four digits1..3 mapped to Java characters 1..3; charset inclusive range low..high within1..3','Flatten text and replace charset range lookup with integer comparison; retain suppression loop and last-character state; encode complete output as nonzero decimal digits (injective).','a=1,b=1,c=2,d=2,low=1,high=2',1000)
body='''int start = startIndex;
if (start < 0) { return -1; } else { if (start >= 3) { start = 2; } }
int i = start;
while (i >= 0) {
 int value = a;
 if (i == 1) { value = b; }
 if (i == 2) { value = c; }
 if (key == value) { return i; }
 i = i - 1;
}
return -1;'''
r2='(startIndex >= 2 && key == c)';r1=f'(startIndex >= 1 && key == b && !{r2})';r0=f'(startIndex >= 0 && key == a && !{r2} && !{r1})'
add('D4jArrayLastIndex','lang','commons-lang/ArrayUtils.java','lastIndexOf(int[], int, int)','int a, int b, int c, int key, int startIndex',body,bounds('a b c key',0,4)+' || '+bounds('startIndex',-1,4),[(r2,'2'),(r1,'1'),(r0,'0'),(f'!{r2} && !{r1} && !{r0}','-1')],'three-element non-null int array, values/key0..4; startIndex -1..4','Flatten array, preserve backward scan and start-index clamping. Distinct from prior delimiter earliest-match scan.','a=1,b=2,c=1,key=1,startIndex=4')
body='''int previous = a;
int i = 1;
while (i < 3) {
 int value = b;
 if (i == 2) { value = c; }
 if (increasing) {
  if (strict) { if (value <= previous) { return 0; } }
  else { if (value < previous) { return 0; } }
 } else {
  if (strict) { if (value >= previous) { return 0; } }
  else { if (value > previous) { return 0; } }
 }
 previous = value;
 i = i + 1;
}
return 1;'''
ok='((increasing && strict && a < b && b < c) || (increasing && !strict && a <= b && b <= c) || (!increasing && strict && a > b && b > c) || (!increasing && !strict && a >= b && b >= c))'
add('D4jMonotonicOrder','math','commons-math/MathArrays.java','checkOrder(double[], OrderDirection, boolean, boolean)','int a, int b, int c, boolean increasing, boolean strict',body,bounds('a b c',-3,3),[(ok,'1'),('!'+ok,'0')],'three exact integer-valued doubles -3..3; both directions/strictness; abort=false','Flatten array and enum, specialize abort=false, replace labeled early-break with equivalent return. Integer mapping exact on finite domain; no claim for NaN, infinities or rounding.','a=1,b=2,c=3,increasing=true,strict=true')
(ROOT/'manifest.json').write_text(json.dumps({'batch':2,'defects4j_index_commit':'8c16da8230843cdc918eaf4ddb449637f02b83c6','subjects':items},indent=2)+'\n')
print('Built',len(items),'subjects')
