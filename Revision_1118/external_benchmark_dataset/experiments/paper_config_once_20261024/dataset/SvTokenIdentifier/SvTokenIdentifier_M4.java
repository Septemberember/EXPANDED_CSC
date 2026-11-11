// Derived from sv-benchmarks/java/java-ranger-regression/printtokens_eqchk/impl/PrintTokens2.java; see provenance.md and sources for licenses.
// Modified: bounded scalar core; original source retained separately.
public class SvTokenIdentifier_M4 {
 public static int test(int a, int b, int c) {
if (a < 32 || a > 126 || b < 32 || b > 126 || c < 32 || c > 126) { return -99; }
int i = 1;
boolean letter = ((a >= 65 && a <= 90) || (a >= 97 && a <= 122));
if (letter) {
 while (i < 3) {
  int ch = b;
  if (i == 2) { ch = c; }
  letter = ((ch >= 65 && ch <= 90) || (ch >= 97 && ch <= 122));
  if (letter) { i = i + 1; }
  else {
   boolean number = (ch >= 48 && ch <= 57);
   if (number) { i = i + 1; } else { return 0; }
  }
 }
 return 1;
} else { return (0) + 1; }
 }
}
