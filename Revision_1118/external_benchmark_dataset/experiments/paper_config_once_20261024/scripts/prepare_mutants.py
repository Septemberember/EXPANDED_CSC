"""Six pre-registered atomic edits per subject; no replacement based on outcomes."""
from common import *
import re
subjects=read(OUT/'subjects.json');manifest=[];selection=[]
def mask_java(code):
 pattern=r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
 return re.sub(pattern,lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),code)
def paren_end(text,start):
 depth=1;i=start+1
 while depth:
  if text[i]=='(':depth+=1
  elif text[i]==')':depth-=1
  i+=1
 return i-1
for s in subjects:
 name=s['subject'];java=Path(s['java_file']);code=java.read_text();masked=mask_java(code);start=masked.index('public static int test');predicates=[];loopvars=set()
 for m in re.finditer(r'\b(if|while|for)\s*\(',masked[start:]):
  begin=start+m.end()-1;end=paren_end(masked,begin);expr=masked[begin+1:end]
  if m.group(1)!='if':loopvars.update(re.findall(r'\b[a-zA-Z_]\w*\b',expr));continue
  if not re.search(r'<=|>=|==|!=|&&|\|\||<|>',expr):
   a=begin+1;b=end;predicates.append(dict(a=a,b=b,old=code[a:b],new='('+code[a:b]+') == false',operator='ROR',site=begin,category='condition'))
  for op in re.finditer(r'<=|>=|==|!=|&&|\|\||<|>',expr):
   a=begin+1+op.start();b=begin+1+op.end();old=code[a:b];new={'<':'<=','>':'>=','<=':'<','>=':'>','==':'!=','!=':'==','&&':'||','||':'&&'}[old]
   operator='LOR' if old in ['&&','||'] else 'ROR' if old in ['==','!='] else 'BOR'
   predicates.append(dict(a=a,b=b,old=old,new=new,operator=operator,site=begin,category='condition'))
 chosen=[];usedsites=set()
 # One boundary, then an internal relational predicate, then an internal connector/next predicate.
 for preference in [lambda p:p['operator']=='BOR',lambda p:p['operator']=='ROR',lambda p:p['operator']=='LOR' and p['site']!=min(x['site'] for x in predicates)]:
  options=[p for p in predicates if p['site'] not in usedsites and preference(p)]
  if not options:options=[p for p in predicates if p['site'] not in usedsites]
  if not options:break
  p=options[0];chosen.append(p);usedsites.add(p['site'])
 if len(chosen)<3:raise RuntimeError(name+' insufficient distinct condition sites')
 returns=list(re.finditer(r'\breturn\s+([^;]+);',masked[start:]));ret=returns[-1];a=start+ret.start(1);b=start+ret.end(1);old=code[a:b].strip()
 chosen.append(dict(a=a,b=b,old=code[a:b],new='('+old+') + 1',operator='RVR',category='statement'))
 assignments=[]
 for m in re.finditer(r'\b(\w+)\s*=\s*([^;=]+);',masked[start:]):
  var=m.group(1);a=start+m.start(2);b=start+m.end(2);expr=code[a:b]
  if var in loopvars or var in {'time','depth','cursor','current','index','i','j','k','start'}:continue
  # Ignore condition fragments and assignments spanning control statements.
  if any(c in expr for c in '{}') or '\n' in expr or expr.strip() in ['true','false']:continue
  assignments.append((var,a,b,expr))
 # Arithmetic operator mutation in a state update, favor a later algorithmic update.
 arithmetic=[]
 for var,a,b,expr in assignments:
  for m in re.finditer(r'(?<=[\w\s)])([+*/-])(?=[\s\w(])',expr):
   op=m.group(1);arithmetic.append(dict(a=a+m.start(1),b=a+m.end(1),old=op,new={'+':'-','-':'+','*':'+','/':'*'}[op],operator='AOR',category='statement',var=var))
 if arithmetic:chosen.append(arithmetic[-1])
 else:
  choices=[m for m in returns[:-1] if code[start+m.start(1):start+m.end(1)].strip() not in ['-1','-99']]
  rr=choices[-1] if choices else returns[0];a=start+rr.start(1);b=start+rr.end(1);chosen.append(dict(a=a,b=b,old=code[a:b],new='('+code[a:b].strip()+') + 1',operator='RVR',category='statement'))
 constants=[]
 for var,a,b,expr in assignments:
  for m in re.finditer(r'(?<![\w.])\d+(?![\w.])',expr):
   old=m.group();value=int(old)
   if value>10000:continue
   constants.append(dict(a=a+m.start(),b=a+m.end(),old=old,new=str(value+1),operator='CR',category='statement',var=var))
 if constants:chosen.append(constants[-1])
 else:
  chosen.append(dict(a=start+ret.start(1),b=start+ret.end(1),old=code[start+ret.start(1):start+ret.end(1)],new='('+code[start+ret.start(1):start+ret.end(1)].strip()+') - 1',operator='RVR',category='statement'))
 assert len(chosen)==6,name
 for i,m in enumerate(chosen,1):
  mutant=name+f'_M{i}';mutpath=java.with_name(mutant+'.java');a,b=m['a'],m['b'];assert code[a:b]==m['old']
  changed=code[:a]+m['new']+code[b:];changed=changed.replace('public class '+name+' {','public class '+mutant+' {',1);mutpath.write_text(changed)
  line=code.count('\n',0,a)+1;original_line=code.splitlines()[line-1];mutant_line=changed.splitlines()[line-1];category=m['category'];relative=str(mutpath.relative_to(OUT/'dataset'))
  record=dict(mutant_id=mutant,subject=name,operator=m['operator'],fault_kind='control-flow' if category=='condition' else 'data-flow',fault_category=category,original_file=str(java.relative_to(OUT/'dataset')),mutant_file=relative,original_location=dict(line=line,code=original_line),mutant_location=dict(line=line,code=mutant_line),change=dict(type='single-token-or-expression-replacement',original_span=[a,b],from_text=m['old'],to_text=m['new'],description='Pre-registered atomic mutation; class-name change is only packaging'),ground_truth=dict(primary_file=relative,primary_line=line,acceptable_files=[relative],acceptable_lines=[line],acceptable_line_window=dict(start=line,end=line),operator=m['operator'],fault_category=category),bound_fsf=str(Path(s['fsf']).relative_to(OUT/'dataset')),validation=dict(compiles=None,instrumentable=None,terminates=None,detected=None),original_sha256=hashlib.sha256(code.encode()).hexdigest(),mutant_sha256=hashlib.sha256(changed.encode()).hexdigest())
  manifest.append(record)
 selection.append(dict(subject=name,candidates=6,condition=3,statement=3,loop_bearing=s['loop_bearing']))
p=OUT/'dataset/mutants_manifest.jsonl';p.write_text(''.join(json.dumps(x)+'\n' for x in manifest));write(OUT/'mutation_selection.json',dict(policy='fixed before execution; no outcome-driven replacement; every candidate reported even if compilation/generation fails',subjects=selection,candidate_count=len(manifest)))
print('Prepared',len(manifest),'mutants')
