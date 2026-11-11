"""Rebuild controlled adaptations and behavioral specifications from pinned sources."""
from pathlib import Path
import json,hashlib,itertools
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'sources/jpf-symbc/src/examples'
items=[]
def add(name,source,method,params,body,cases,domain,note,bootstrap):
 p=ROOT/'subjects'/name;p.mkdir(parents=True,exist_ok=True);(p/'FSF').mkdir(exist_ok=True)
 original=(SRC/source).read_text()
 header=original[:original.index('*/')+2]+'\n' if original.lstrip().startswith('/*') else '// Derived from SymbolicPathFinder/jpf-symbc; repository Apache-2.0 license.\n'
 (p/(name+'.java')).write_text(header+'// Modified: controlled scalar adaptation; see provenance.md.\npublic class '+name+' {\n    public static int test('+params+') {\n'+body+'\n    }\n}\n')
 (p/'FSF'/(name+'_FSF.txt')).write_text('\n\n'.join(f'[fsf_{i}]\nT: {t}\nD: return_value == {d}' for i,(t,d) in enumerate(cases,1))+'\n')
 entry=dict(name=name,source=source,source_method=method,domain=domain,adaptation=note,bootstrap=bootstrap,source_sha256=hashlib.sha256((SRC/source).read_bytes()).hexdigest(),status='unvalidated')
 items.append(entry)
 (p/'provenance.md').write_text(f'# {name}\n\nSource: SymbolicPathFinder/jpf-symbc, commit `c98bfae2969e51923006e4c922c0f4e4a1cfbdfb`, `src/examples/{source}`, {method}.\n\nLicense: Apache-2.0 (retained in sources).\n\nDomain: {domain}\n\nAdaptation: {note}\n\nThis is a bounded core, not verification of the complete upstream program. FSF describes the retained observable, not upstream correctness in general.\n')
def guard(cond):return f'        if ({cond}) {{ return -1; }}\n'
def specguard(cond,cases):return [(cond,'-1')]+[(f'!({cond}) && ({t})',d) for t,d in cases]
# Full one-step WBS, retaining original branching and arithmetic.
s=(SRC/'WBS.java').read_text();body=s.split('boolean Skid) {',1)[1].split('\n\tpublic static void launch',1)[0].rsplit('}',1)[0]
repl={'WBS_Node_WBS_BSCU_SystemModeSelCmd_rlt_PRE':'prevMode','WBS_Node_WBS_BSCU_rlt_PRE1':'prevCommand','WBS_Node_WBS_rlt_PRE2':'prevPressure'}
for a,b in repl.items():body=body.replace(a,b)
bad='PedalPos < 0 || PedalPos > 4 || prevMode < 0 || prevMode > 1 || prevCommand < 0 || prevCommand > 4 || prevPressure < 0 || prevPressure > 5'
f='(prevMode != 0 || (prevCommand != 0 && prevPressure <= 0))'
cases=[]
for pedal,auto,skid in itertools.product(range(5),[False,True],[False,True]):
 cmd=0 if skid else min(4,pedal+int(auto));press=[0,1,2,3,5]
 base=f'PedalPos == {pedal} && '+('AutoBrake' if auto else '!AutoBrake')+' && '+('Skid' if skid else '!Skid')
 cases.extend([(f'{base} && !{f}',str(press[cmd])),(f'{base} && {f}',str(100+10*(0 if skid else press[pedal])))])
add('SpfWbsStep','WBS.java','update','int PedalPos, boolean AutoBrake, boolean Skid, int prevMode, int prevCommand, int prevPressure',guard(bad)+'int Nor_Pressure = 0; int Alt_Pressure = 0; int Sys_Mode = 0;\n'+body+'\nreturn Nor_Pressure + 10 * Alt_Pressure + 100 * Sys_Mode;',specguard(bad,cases),'pedal 0..4; previous mode 0..1, command 0..4, pressure 0..5; all flags; other inputs return -1','Expose previous state as inputs; retain complete update control flow; encode outputs normal + 10*alternate + 100*mode. Does not model multi-step reachability.','PedalPos=0,AutoBrake=false,Skid=false,prevMode=0,prevCommand=0,prevPressure=5')
bad='goal < 0 || goal > 40 || position < 0 || position > 40'
body=guard(bad)+'''if (emergency) { goal = 30; }
int time = 0;
while (position != goal) {
 if (emergency) {
  if (goal > position) { position = position + 10; } else { position = position - 10; }
 } else {
  if (goal > position) { position = position + 1; } else { position = position - 1; }
 }
 time = time + 1;
 if (time > 1) { return -2; }
}
return position;'''
ok='(emergency && (position == 20 || position == 30 || position == 40))'
normal='(!emergency && (position == goal || position + 1 == goal || position - 1 == goal))'
add('SpfFlapMotion','FlapController.java','EmergencySensor.run; FlapMovement.run','int goal, int position, boolean emergency',body,specguard(bad,[(ok,'30'),(normal,'goal'),(f'!{ok} && !{normal}','-2')]),'goal and initial position 0..40; emergency flag','Execute sensor before motion; preserve movement and time>1 assertion as -2; -1 rejects domain. No interleavings or concurrency claim.','goal=1,position=0,emergency=false')
bad='balance < 0 || balance > 20 || deposit < -5 || deposit > 10 || amount < -5 || amount > 30 || withdrawals < 0 || withdrawals > 5'
body=guard(bad)+'''int currentBalance = balance;
if (deposit > 0) { currentBalance = currentBalance + deposit; }
if (amount > currentBalance) { return currentBalance; }
if (withdrawals >= 5) { return -2; }
currentBalance = currentBalance - amount;
int nextWithdrawals = withdrawals + 1;
return currentBalance;'''
cases=[]
for t,b in [('deposit > 0','(balance + deposit)'),('deposit <= 0','balance')]:
 cases += [(f'{t} && amount > {b}',b),(f'{t} && amount <= {b} && withdrawals >= 5','-2'),(f'{t} && amount <= {b} && withdrawals < 5',f'{b} - amount')]
add('SpfBankWithdrawal','sequences/BankAccount.java','deposit; withdraw','int balance, int deposit, int amount, int withdrawals',body,specguard(bad,cases),'balance 0..20; deposit -5..10; amount -5..30; count 0..5','Expose object state; keep input values immutable and copy balance to local currentBalance; inline deposit then withdraw; return final balance or -2 assertion. Preserve negative withdrawal behavior rather than silently fixing it.','balance=10,deposit=1,amount=3,withdrawals=0')
bad='a < 0 || a > 9 || b < 0 || b > 9 || c < 0 || c > 9 || d < 0 || d > 9 || e < 0 || e > 9'
body=guard(bad)+'''int i = 0;
while (i < 3) {
 int ch = a;
 if (i == 1) { ch = b; }
 if (i == 2) { ch = c; }
 int j = 0;
 while (j < 2) {
  int delim = d;
  if (j == 1) { delim = e; }
  if (ch == delim) { return i; }
  j = j + 1;
 }
 i = i + 1;
}
return 3;'''
m=['(a == d || a == e)','(b == d || b == e)','(c == d || c == e)']
cases=[(' && '.join(['!'+x for x in m[:i]]+[m[i]]),str(i)) for i in range(3)]+[(' && '.join('!'+x for x in m),'3')]
add('SpfDelimiterSearch','strings/DelimSearch.java','search','int a, int b, int c, int d, int e',body,specguard(bad,cases),'three character text and two delimiters, each code 0..9','Flatten fixed-length strings into scalar character codes, preserve nested search loops and earliest match; replace continue with equivalent fall-through.','a=1,b=2,c=3,d=4,e=5')
bad='a < 0 || a > 9 || b < 0 || b > 9 || c < 0 || c > 9 || d < 0 || d > 9 || p < 0 || p > 9 || q < 0 || q > 9'
body=guard(bad)+'''int count = 0;
int i = 0;
while (i < 3) {
 boolean found = true;
 int j = 0;
 while (j < 2) {
  int index = i + j;
  int ch = a;
  if (index == 1) { ch = b; }
  if (index == 2) { ch = c; }
  if (index == 3) { ch = d; }
  int needle = p;
  if (j == 1) { needle = q; }
  found = found && ch == needle;
  j = j + 1;
 }
 if (found) { count = count + 1; }
 i = i + 1;
}
return count;'''
m=['(a == p && b == q)','(b == p && c == q)','(c == p && d == q)'];cases=[]
for flags in itertools.product([False,True],repeat=3): cases.append((' && '.join(('' if flag else '!')+x for flag,x in zip(flags,m)),str(sum(flags))))
add('SpfSubstringCount','strings/StringSearch.java','search_1','int a, int b, int c, int d, int p, int q',body,specguard(bad,cases),'four-character haystack and two-character needle; codes 0..9','Flatten strings; retain nested search and overlapping occurrences.','a=1,b=2,c=1,d=2,p=1,q=2')
bad='a < 0 || a > 9 || b < a || b > 9 || c < b || c > 9 || value < 0 || value > 9'
body=guard(bad)+'''int first = a;
if (value <= first) { return value * 1000 + a * 100 + b * 10 + c; }
int cursor = 1;
int following = b;
while (cursor < 3 && following < value) {
 cursor = cursor + 1;
 if (cursor == 2) { following = c; }
}
if (cursor == 1) { return a * 1000 + value * 100 + b * 10 + c; }
if (cursor == 2) { return a * 1000 + b * 100 + value * 10 + c; }
return a * 1000 + b * 100 + c * 10 + value;'''
cases=[('value <= a','value * 1000 + a * 100 + b * 10 + c'),('value > a && value <= b','a * 1000 + value * 100 + b * 10 + c'),('value > b && value <= c','a * 1000 + b * 100 + value * 10 + c'),('value > c','a * 1000 + b * 100 + c * 10 + value')]
add('SpfSortedInsertion','compositional/SortedListInt.java','insert','int a, int b, int c, int value',body,specguard(bad,cases),'sorted three-node list with values 0..9; inserted digit 0..9','Replace next pointers by cursor and scalar fields; preserve search for insertion location; encode all four output digits, including leading zeros. Fixed length makes encoding injective.','a=1,b=3,c=5,value=4')
bad='left < 0 || root <= left || right <= root || right > 9 || key < 0 || key > 9'
body=guard(bad)+'''int current = 0;
while (current >= 0) {
 int value = root;
 if (current == 1) { value = left; }
 if (current == 2) { value = right; }
 if (value == key) { return 1; }
 if (key < value) {
  if (current == 0) { current = 1; } else { current = -1; }
 } else {
  if (current == 0) { current = 2; } else { current = -1; }
 }
}
return 0;'''
match='(key == left || key == root || key == right)'
add('SpfTreeSearch','sequences/BinTree.java','find','int left, int root, int right, int key',body,specguard(bad,[(match,'1'),('!'+match,'0')]),'three-node BST with 0<=left<root<right<=9; key 0..9','Fix tree shape to root with two leaves; replace references/null by node indices/-1; preserve traversal.','left=1,root=4,right=7,key=5')
bad='altitudeOffset < -1000 || altitudeOffset > 1000'
body=guard(bad)+"""int failure = 0;
int state = 0;
boolean selected = false;
if (!fired) { failure = 10; }
if (altitudeOffset <= 0) {
 if (fired) { state = 1; } else { state = 2; }
 selected = true;
}
if (altitudeOffset >= 0) {
 if (selected) { return -2; }
 state = 3;
 selected = true;
}
return failure + state;"""
cases=[('altitudeOffset == 0','-2'),('altitudeOffset < 0 && fired','1'),('altitudeOffset < 0 && !fired','12'),('altitudeOffset > 0 && fired','3'),('altitudeOffset > 0 && !fired','13')]
add('SpfAbortDecision','ExampleAbort.java','abort; setNextState','int altitudeOffset, boolean fired',body,specguard(bad,cases),'offset -1000..1000 and flags; original altitude = 120000 + altitudeOffset','Translate altitude around its threshold (no overflow on domain); flatten EnumSet to failure flag, state strings to tags; inline setNextState; preserve ambiguous transition assertion at offset=0 as -2. Original defect is retained and specified, not repaired.','altitudeOffset=0,fired=true')
bad='steps < 0 || steps > 8'
body=guard(bad)+'''int active = 1;
int initialized = 0;
int counter = 0;
int i = 0;
while (i < steps) {
 if (initialized == 1) {
  if (active == 1) {
   counter = counter + 1;
   active = -1;
   active = 1;
  }
 }
 initialized = 1;
 i = i + 1;
}
return counter;'''
add('SpfRjcCounter','rjc/SimpleCounter.java','Init; Main; state entry/exit methods','int steps',body,specguard(bad,[('steps == 0','0'),('steps > 0','steps - 1')]),'0..8 Main calls after Init','Flatten one-element state/output arrays; inline state dispatch and transitions; bound repeated controller ticks.','steps=3')
bad='a < 0 || a > 9 || b < 0 || b > 9 || c < 0 || c > 9 || pops < 0 || pops > 4'
body=guard(bad)+'''int depth = 3;
int value = -3;
int i = 0;
while (i < pops) {
 if (depth == 0) { return -2; }
 if (depth == 3) { value = c; }
 if (depth == 2) { value = b; }
 if (depth == 1) { value = a; }
 depth = depth - 1;
 i = i + 1;
}
return value;'''
add('SpfStackPops','sequences/Stack.java','push; pop; isEmpty','int a, int b, int c, int pops',body,specguard(bad,[('pops == 0','-3'),('pops == 1','c'),('pops == 2','b'),('pops == 3','a'),('pops == 4','-2')]),'push three digits then pop 0..4 times','Flatten three nodes to slots and depth; inline pop/isEmpty; return last popped value, -3 for no pop and -2 for empty-stack exception; remove diagnostic printing. Annotation preconditions are not enforced by ordinary Java; zero values deliberately retained.','a=1,b=2,c=3,pops=2')
(ROOT/'manifest.json').write_text(json.dumps({'repository':'https://github.com/SymbolicPathFinder/jpf-symbc','commit':'c98bfae2969e51923006e4c922c0f4e4a1cfbdfb','subjects':items},indent=2)+'\n')
print('Built',len(items),'subjects')
