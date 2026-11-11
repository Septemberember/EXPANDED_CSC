public class SpfSubstringCount_M2 {

    public static int test(int a, int b, int c, int d, int p, int q) {
        System.out.println("Function input int parameter q = " + (q));
        System.out.println("Function input int parameter p = " + (p));
        System.out.println("Function input int parameter d = " + (d));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(5, "if", 1, "a < 0", a < 0) || csc.bridge.CSCTrace.cond(5, "if", 2, "a > 9", a > 9) || csc.bridge.CSCTrace.cond(5, "if", 3, "b < 0", b < 0) || csc.bridge.CSCTrace.cond(5, "if", 4, "b > 9", b > 9) || csc.bridge.CSCTrace.cond(5, "if", 5, "c < 0", c < 0) || csc.bridge.CSCTrace.cond(5, "if", 6, "c > 9", c > 9) || csc.bridge.CSCTrace.cond(5, "if", 7, "d < 0", d < 0) || csc.bridge.CSCTrace.cond(5, "if", 8, "d > 9", d > 9) || csc.bridge.CSCTrace.cond(5, "if", 9, "p < 0", p < 0) || csc.bridge.CSCTrace.cond(5, "if", 10, "p > 9", p > 9) || csc.bridge.CSCTrace.cond(5, "if", 11, "q < 0", q < 0) || csc.bridge.CSCTrace.cond(5, "if", 12, "q > 9", q > 9)) {
            return csc.bridge.CSCTrace.retObject(5, "return_value", "-1", -1);
        }
        int count = csc.bridge.CSCTrace.assignObject(6, "var_decl", "count", "0", 0);
        int i = csc.bridge.CSCTrace.assignObject(7, "var_decl", "i", "0", 0);
        while (csc.bridge.CSCTrace.cond(8, "while", 1, "i < 3", i < 3)) {
            boolean found = csc.bridge.CSCTrace.assignObject(9, "var_decl", "found", "true", true);
            int j = csc.bridge.CSCTrace.assignObject(10, "var_decl", "j", "0", 0);
            while (csc.bridge.CSCTrace.cond(11, "while", 1, "j < 2", j < 2)) {
                int index = csc.bridge.CSCTrace.assignObject(12, "var_decl", "index", "i + j", i + j);
                int ch = csc.bridge.CSCTrace.assignObject(13, "var_decl", "ch", "a", a);
                if (csc.bridge.CSCTrace.cond(14, "if", 1, "index != 1", index != 1)) {
                    ch = csc.bridge.CSCTrace.assignObject(14, "assign", "ch", "b", b);
                }
                if (csc.bridge.CSCTrace.cond(15, "if", 1, "index == 2", index == 2)) {
                    ch = csc.bridge.CSCTrace.assignObject(15, "assign", "ch", "c", c);
                }
                if (csc.bridge.CSCTrace.cond(16, "if", 1, "index == 3", index == 3)) {
                    ch = csc.bridge.CSCTrace.assignObject(16, "assign", "ch", "d", d);
                }
                int needle = csc.bridge.CSCTrace.assignObject(17, "var_decl", "needle", "p", p);
                if (csc.bridge.CSCTrace.cond(18, "if", 1, "j == 1", j == 1)) {
                    needle = csc.bridge.CSCTrace.assignObject(18, "assign", "needle", "q", q);
                }
                found = csc.bridge.CSCTrace.assignObject(19, "assign", "found", "found && ch == needle", found && ch == needle);
                j = csc.bridge.CSCTrace.assignObject(20, "assign", "j", "j + 1", j + 1);
            }
            if (csc.bridge.CSCTrace.cond(22, "if", 1, "found", found)) {
                count = csc.bridge.CSCTrace.assignObject(22, "assign", "count", "count + 1", count + 1);
            }
            i = csc.bridge.CSCTrace.assignObject(23, "assign", "i", "i + 1", i + 1);
        }
        return csc.bridge.CSCTrace.retObject(25, "return_value", "count", count);
    }
}
