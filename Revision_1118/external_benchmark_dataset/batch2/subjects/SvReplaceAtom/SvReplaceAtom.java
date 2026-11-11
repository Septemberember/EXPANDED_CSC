// Derived from sv-benchmarks/java/java-ranger-regression/replace5_eqchk/impl/Replace.java; see provenance.md and sources for licenses.
// Modified: bounded scalar core; original source retained separately.
public class SvReplaceAtom {
 public static int test(int kind, int ch, int a, int b, int index) {
if (kind < 0 || kind > 3 || ch < 0 || ch > 10 || a < 0 || a > 10 || b < 0 || b > 10 || index < 0 || index > 1) { return -99; }
int advance = -1;
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
return -1;
 }
}
