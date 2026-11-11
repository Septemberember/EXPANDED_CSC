// Derived from sv-benchmarks/java/MinePump/spec1-5_product64/MinePumpSystem/MinePump.java; see provenance.md and sources for licenses.
// Modified: bounded scalar core; original source retained separately.
public class SvMinePumpStep_M6 {
 public static int test(int water, boolean running, boolean active, boolean methane) {
if (water < 0 || water > 2) { return -99; }
int level = water;
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
if (pump) { state = 11; }
return state + level;
 }
}
