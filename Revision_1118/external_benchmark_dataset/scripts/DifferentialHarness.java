import java.lang.reflect.*;
import java.util.*;
import java.io.*;
public class DifferentialHarness {
 static Map<String,Integer> counts=new LinkedHashMap<>();
 static void check(String name,int actual,int expected) {
  if(actual!=expected) throw new AssertionError(name+" actual="+actual+" expected="+expected+" case="+counts.get(name));
  counts.put(name,counts.getOrDefault(name,0)+1);
 }
 static Field field(Class<?> c,String n)throws Exception{Field f=c.getDeclaredField(n);f.setAccessible(true);return f;}
 public static void main(String[] args)throws Exception{
  PrintStream report=System.out;System.setOut(new PrintStream(OutputStream.nullOutputStream()));
  Field wm=field(WBS.class,"WBS_Node_WBS_BSCU_SystemModeSelCmd_rlt_PRE"),wc=field(WBS.class,"WBS_Node_WBS_BSCU_rlt_PRE1"),wp=field(WBS.class,"WBS_Node_WBS_rlt_PRE2");
  Field wn=field(WBS.class,"Nor_Pressure"),wa=field(WBS.class,"Alt_Pressure"),ws=field(WBS.class,"Sys_Mode");
  for(int p=0;p<=4;p++)for(int m=0;m<=1;m++)for(int c=0;c<=4;c++)for(int v=0;v<=5;v++)for(boolean a:new boolean[]{false,true})for(boolean k:new boolean[]{false,true}){
   WBS w=new WBS();wm.setInt(w,m);wc.setInt(w,c);wp.setInt(w,v);w.update(p,a,k);
   check("SpfWbsStep",SpfWbsStep.test(p,a,k,m,c,v),wn.getInt(w)+10*wa.getInt(w)+100*ws.getInt(w));
  }
  Field fg=field(FlapController.class,"goal"),fp=field(FlapController.class,"currentPosition");
  for(int g=0;g<=40;g++)for(int p=0;p<=40;p++)for(boolean e:new boolean[]{false,true}){
   fg.setInt(null,g);FlapController.FlapMovement motion=new FlapController.FlapMovement(p);
   new FlapController.EmergencySensor(e).run();int expected;
   try{motion.run();expected=fp.getInt(null);}catch(AssertionError ex){expected=-2;}
   check("SpfFlapMotion",SpfFlapMotion.test(g,p,e),expected);
  }
  Field bb=field(sequences.BankAccount.class,"balance"),bw=field(sequences.BankAccount.class,"numberOfWithdrawals");
  for(int b=0;b<=20;b++)for(int d=-5;d<=10;d++)for(int a=-5;a<=30;a++)for(int w=0;w<=5;w++){
   sequences.BankAccount bank=new sequences.BankAccount(b);bw.setInt(bank,w);bank.deposit(d);int expected;
   try{bank.withdraw(a);expected=bb.getInt(bank);}catch(AssertionError ex){expected=-2;}
   check("SpfBankWithdrawal",SpfBankWithdrawal.test(b,d,a,w),expected);
  }
  strings.DelimSearch ds=new strings.DelimSearch();
  for(int a=0;a<=9;a++)for(int b=0;b<=9;b++)for(int c=0;c<=9;c++)for(int d=0;d<=9;d++)for(int e=0;e<=9;e++){
   check("SpfDelimiterSearch",SpfDelimiterSearch.test(a,b,c,d,e),ds.search(new String(new char[]{(char)a,(char)b,(char)c}),new String(new char[]{(char)d,(char)e})));
  }
  for(int a=0;a<=9;a++)for(int b=0;b<=9;b++)for(int c=0;c<=9;c++)for(int d=0;d<=9;d++)for(int p=0;p<=9;p++)for(int q=0;q<=9;q++){
   check("SpfSubstringCount",SpfSubstringCount.test(a,b,c,d,p,q),strings.StringSearch.search_1(new String(new char[]{(char)p,(char)q}),new String(new char[]{(char)a,(char)b,(char)c,(char)d})));
  }
  for(int a=0;a<=9;a++)for(int b=a;b<=9;b++)for(int c=b;c<=9;c++)for(int v=0;v<=9;v++){
   compositional.SortedListInt list=new compositional.SortedListInt();list.insert(a);list.insert(b);list.insert(c);list.insert(v);
   String[] digits=list.toString().replace("[","").replace("]","").split(",");int expected=0;for(String digit:digits)expected=expected*10+Integer.parseInt(digit);
   check("SpfSortedInsertion",SpfSortedInsertion.test(a,b,c,v),expected);
  }
  for(int l=0;l<=9;l++)for(int r=l+1;r<=9;r++)for(int h=r+1;h<=9;h++)for(int k=0;k<=9;k++){
   sequences.BinTree tree=new sequences.BinTree();tree.add(r);tree.add(l);tree.add(h);
   check("SpfTreeSearch",SpfTreeSearch.test(l,r,h,k),tree.find(k)?1:0);
  }
  // Observe state names at the original virtual call boundary while retaining its assertion.
  class AbortObserver extends ExampleAbort{
   int state;
   public void setNextState(String s){super.setNextState(s);state=s.equals("abortLowActiveLAS")?1:s.equals("abortPassiveLAS")?2:3;}
  }
  for(int offset=-1000;offset<=1000;offset++)for(boolean fired:new boolean[]{false,true}){
   int alt = 120000 + offset;
   AbortObserver abort=new AbortObserver();int expected;
   try{abort.abort(alt,fired);expected=abort.state+(abort.failures.contains(ExampleAbort.Failure.LAS_CNTRL)?10:0);}catch(AssertionError e){expected=-2;}
   check("SpfAbortDecision",SpfAbortDecision.test(offset,fired),expected);
  }
  for(int ticks=0;ticks<=8;ticks++){
   rjc.SimpleCounter counter=new rjc.SimpleCounter();counter.Init();int[] result={0};for(int i=0;i<ticks;i++)counter.Main(result);
   check("SpfRjcCounter",SpfRjcCounter.test(ticks),result[0]);
  }
  for(int a=0;a<=9;a++)for(int b=0;b<=9;b++)for(int c=0;c<=9;c++)for(int pops=0;pops<=4;pops++){
   sequences.Stack stack=new sequences.Stack();stack.push(a);stack.push(b);stack.push(c);int expected=-3;
   try{for(int i=0;i<pops;i++)expected=stack.pop(1);}catch(RuntimeException ex){expected=-2;}
   check("SpfStackPops",SpfStackPops.test(a,b,c,pops),expected);
  }
  // Added guard behavior is tested separately; no upstream equivalence claimed outside domain.
  check("guard_checks",SpfAbortDecision.test(1001,false),-1);
  check("guard_checks",SpfWbsStep.test(-1,false,false,0,0,0),-1);
  check("guard_checks",SpfFlapMotion.test(-1,0,false),-1);
  check("guard_checks",SpfBankWithdrawal.test(-1,0,0,0),-1);
  check("guard_checks",SpfDelimiterSearch.test(10,0,0,0,0),-1);
  check("guard_checks",SpfSubstringCount.test(0,0,0,0,-1,0),-1);
  check("guard_checks",SpfSortedInsertion.test(2,1,3,0),-1);
  check("guard_checks",SpfTreeSearch.test(1,1,2,0),-1);
  check("guard_checks",SpfRjcCounter.test(9),-1);
  check("guard_checks",SpfStackPops.test(0,0,0,5),-1);
  for(Map.Entry<String,Integer> entry:counts.entrySet())report.println(entry.getKey()+" "+entry.getValue()+" PASS");
 }
}
