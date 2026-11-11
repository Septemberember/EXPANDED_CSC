// Derived from sv-benchmarks/java/java-ranger-regression/TCAS_prop1/Main.java; see provenance.md and sources for licenses.
// Modified: bounded scalar core; original source retained separately.
public class SvTcasClimb_M6 {
 public static int test(int layer, int upDelta, int downDelta, int separation, boolean above, boolean inhibit) {
if (layer < 0 || layer > 3 || upDelta < -2 || upDelta > 2 || downDelta < -2 || downDelta > 2 || separation < 0 || separation > 2) { return -99; }
int alim = 740;
if (layer == 0) { alim = 400; } else { if (layer == 1) { alim = 500; } else { if (layer == 2) { alim = 640; } } }
int up = alim + upDelta * 100;
int down = alim + downDelta * 100;
int sep = 500 + separation * 100;
int biased = up;
if (inhibit) { biased = up + 100; }
int preferred = 0;
if (biased > down) { preferred = 2; }
if (preferred != 0) {
 if (!(down >= alim)) { return 1; } else { return 0; }
} else {
 if (!(sep >= 600)) { return 0; }
 else {
  if (!(up >= alim)) { return 0; }
  else { if (!above) { return 0; } else { return 1; } }
 }
}
 }
}
