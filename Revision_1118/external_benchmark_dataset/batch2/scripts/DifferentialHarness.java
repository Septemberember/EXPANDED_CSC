import java.lang.reflect.*;
import java.util.*;
public class DifferentialHarness {
 static Map<String,Integer> counts=new LinkedHashMap<>();
 static void check(String name,int actual,int expected){if(actual!=expected)throw new AssertionError(name+" case="+counts.get(name)+" actual="+actual+" expected="+expected);counts.put(name,counts.getOrDefault(name,0)+1);}
 static Field field(Class<?> c,String name)throws Exception{Field f=c.getDeclaredField(name);f.setAccessible(true);return f;}
 public static void main(String[] args)throws Exception{
  Field water=field(MinePumpSystem.Environment.class,"waterLevel"),running=field(MinePumpSystem.MinePump.class,"pumpRunning"),active=field(MinePumpSystem.MinePump.class,"systemActive");
  for(int w=0;w<=2;w++)for(boolean r:new boolean[]{false,true})for(boolean a:new boolean[]{false,true})for(boolean m:new boolean[]{false,true}){
   MinePumpSystem.Environment env=new MinePumpSystem.Environment();water.set(env,MinePumpSystem.Environment.WaterLevelEnum.values()[w]);if(m)env.changeMethaneLevel();
   MinePumpSystem.MinePump pump=new MinePumpSystem.MinePump(env);running.setBoolean(pump,r);active.setBoolean(pump,a);pump.timeShift();
   check("SvMinePumpStep",SvMinePumpStep.test(w,r,a,m),(pump.isPumpRunning()?10:0)+env.getWaterLevel().ordinal());
  }
  for(int l=0;l<=3;l++)for(int u=-2;u<=2;u++)for(int d=-2;d<=2;d++)for(int s=0;s<=2;s++)for(boolean a:new boolean[]{false,true})for(boolean i:new boolean[]{false,true}){
   RefTcas.initialize();RefTcas.Alt_Layer_Value=l;int alim=RefTcas.ALIM();RefTcas.Up_Separation=alim+100*u;RefTcas.Down_Separation=alim+100*d;RefTcas.Cur_Vertical_Sep=500+100*s;RefTcas.Own_Tracked_Alt=a?1:0;RefTcas.Other_Tracked_Alt=0;RefTcas.Climb_Inhibit=i?1:0;
   check("SvTcasClimb",SvTcasClimb.test(l,u,d,s,a,i),RefTcas.Non_Crossing_Biased_Climb()?1:0);
  }
  for(int a=0;a<=4;a++)for(int b=0;b<=4;b++)for(int c=0;c<=4;c++)for(int d=0;d<=4;d++){
   int[] dist=RefBellman.runBellmanFord(3,new int[]{0,a,b,4,0,c,4,d,0},0);
   if(dist[0]!=0)throw new AssertionError("Unexpected source distance");
   check("SvBellmanFord3",SvBellmanFord3.test(a,b,c,d),10*dist[1]+dist[2]);
  }
  Method identifier=PrintTokens2.class.getDeclaredMethod("isIdentifier",char[].class);identifier.setAccessible(true);
  for(int a=32;a<=126;a++)for(int b=32;b<=126;b++)for(int c=32;c<=126;c++){
   check("SvTokenIdentifier",SvTokenIdentifier.test(a,b,c),(Boolean)identifier.invoke(null,(Object)new char[]{(char)a,(char)b,(char)c,0})?1:0);
  }
  Method omatch=Replace.class.getDeclaredMethod("omatch",char[].class,char[].class,int.class);omatch.setAccessible(true);
  for(int k=0;k<=3;k++)for(int ch=0;ch<=10;ch++)for(int a=0;a<=10;a++)for(int b=0;b<=10;b++)for(int index=0;index<=1;index++){
   char kind=new char[]{'c','?','[','!'}[k];char[] pat=k<2?new char[]{kind,(char)a}:new char[]{kind,2,(char)a,(char)b};char[] line={0,0};line[index]=(char)ch;Replace.tempIndex=index;
   boolean ok=(Boolean)omatch.invoke(null,line,pat,0);
   check("SvReplaceAtom",SvReplaceAtom.test(k,ch,a,b,index),ok?Replace.tempIndex:-1);
  }
  for(int c=0;c<=127;c++){
   int expected=1;try{OptionValidator.validateOption((char)c);}catch(IllegalArgumentException e){expected=-1;}
   check("SvCliOption",SvCliOption.test(c),expected);
  }
  for(int a=1;a<=3;a++)for(int b=1;b<=3;b++)for(int x=1;x<=3;x++)for(int y=1;y<=3;y++)for(int z=1;z<=3;z++){
   String s=new String(new char[]{(char)a,(char)b}),t=new String(new char[]{(char)x,(char)y,(char)z});
   check("D4jLevenshtein23",D4jLevenshtein23.test(a,b,x,y,z),org.apache.commons.lang3.StringUtils.getLevenshteinDistance(s,t));
  }
  for(int a=1;a<=3;a++)for(int b=1;b<=3;b++)for(int c=1;c<=3;c++)for(int d=1;d<=3;d++)for(int l=1;l<=3;l++)for(int h=l;h<=3;h++){
   String s=new String(new char[]{(char)a,(char)b,(char)c,(char)d}),set=new String(new char[]{(char)l,'-',(char)h});
   String result=org.apache.commons.lang3.CharSetUtils.squeeze(s,set);int encoded=0;for(char v:result.toCharArray())encoded=encoded*10+v;
   check("D4jCharSqueeze",D4jCharSqueeze.test(a,b,c,d,l,h),encoded);
  }
  for(int a=0;a<=4;a++)for(int b=0;b<=4;b++)for(int c=0;c<=4;c++)for(int k=0;k<=4;k++)for(int s=-1;s<=4;s++){
   check("D4jArrayLastIndex",D4jArrayLastIndex.test(a,b,c,k,s),RefArray.lastIndexOf(new int[]{a,b,c},k,s));
  }
  for(int a=-3;a<=3;a++)for(int b=-3;b<=3;b++)for(int c=-3;c<=3;c++)for(boolean i:new boolean[]{false,true})for(boolean s:new boolean[]{false,true}){
   check("D4jMonotonicOrder",D4jMonotonicOrder.test(a,b,c,i,s),RefMath.checkOrder(new double[]{a,b,c},i?RefMath.OrderDirection.INCREASING:RefMath.OrderDirection.DECREASING,s,false)?1:0);
  }
  check("guard_checks",SvMinePumpStep.test(-1,false,false,false),-99);
  check("guard_checks",SvTcasClimb.test(4,0,0,0,false,false),-99);
  check("guard_checks",SvBellmanFord3.test(-1,0,0,0),-99);
  check("guard_checks",SvTokenIdentifier.test(0,65,65),-99);
  check("guard_checks",SvReplaceAtom.test(4,1,1,1,0),-99);
  check("guard_checks",SvCliOption.test(128),-99);
  check("guard_checks",D4jLevenshtein23.test(0,1,1,1,1),-99);
  check("guard_checks",D4jCharSqueeze.test(1,1,1,1,2,1),-99);
  check("guard_checks",D4jArrayLastIndex.test(0,0,0,0,5),-99);
  check("guard_checks",D4jMonotonicOrder.test(4,0,0,true,true),-99);
  for(Map.Entry<String,Integer> e:counts.entrySet())System.out.println(e.getKey()+" "+e.getValue()+" PASS");
 }
}
