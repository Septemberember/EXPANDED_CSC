// Derived from SymbolicPathFinder/jpf-symbc; repository Apache-2.0 license.
// Modified: controlled scalar adaptation; see provenance.md.
public class SpfDelimiterSearch_M5 {
    public static int test(int a, int b, int c, int d, int e) {
        if (a < 0 || a > 9 || b < 0 || b > 9 || c < 0 || c > 9 || d < 0 || d > 9 || e < 0 || e > 9) { return -1; }
int i = 0;
while (i < 3) {
 int ch = a;
 if (i == 1) { ch = b; }
 if (i == 2) { ch = c; }
 int j = 0;
 while (j < 2) {
  int delim = d;
  if (j == 1) { delim = e; }
  if (ch == delim) { return (i) + 1; }
  j = j + 1;
 }
 i = i + 1;
}
return 3;
    }
}
