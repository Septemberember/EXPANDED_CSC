// Derived from SymbolicPathFinder/jpf-symbc; repository Apache-2.0 license.
// Modified: controlled scalar adaptation; see provenance.md.
public class SpfSubstringCount_M4 {
    public static int test(int a, int b, int c, int d, int p, int q) {
        if (a < 0 || a > 9 || b < 0 || b > 9 || c < 0 || c > 9 || d < 0 || d > 9 || p < 0 || p > 9 || q < 0 || q > 9) { return -1; }
int count = 0;
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
return (count) + 1;
    }
}
