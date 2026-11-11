public class SpfDelimiterSearch_M4 {

    public static int test(int a, int b, int c, int d, int e) {
        System.out.println("Function input int parameter e = " + (e));
        System.out.println("Function input int parameter d = " + (d));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(5, "if", 1, "a < 0", a < 0) || csc.bridge.CSCTrace.cond(5, "if", 2, "a > 9", a > 9) || csc.bridge.CSCTrace.cond(5, "if", 3, "b < 0", b < 0) || csc.bridge.CSCTrace.cond(5, "if", 4, "b > 9", b > 9) || csc.bridge.CSCTrace.cond(5, "if", 5, "c < 0", c < 0) || csc.bridge.CSCTrace.cond(5, "if", 6, "c > 9", c > 9) || csc.bridge.CSCTrace.cond(5, "if", 7, "d < 0", d < 0) || csc.bridge.CSCTrace.cond(5, "if", 8, "d > 9", d > 9) || csc.bridge.CSCTrace.cond(5, "if", 9, "e < 0", e < 0) || csc.bridge.CSCTrace.cond(5, "if", 10, "e > 9", e > 9)) {
            return csc.bridge.CSCTrace.retObject(5, "return_value", "-1", -1);
        }
        int i = csc.bridge.CSCTrace.assignObject(6, "var_decl", "i", "0", 0);
        while (csc.bridge.CSCTrace.cond(7, "while", 1, "i < 3", i < 3)) {
            int ch = csc.bridge.CSCTrace.assignObject(8, "var_decl", "ch", "a", a);
            if (csc.bridge.CSCTrace.cond(9, "if", 1, "i == 1", i == 1)) {
                ch = csc.bridge.CSCTrace.assignObject(9, "assign", "ch", "b", b);
            }
            if (csc.bridge.CSCTrace.cond(10, "if", 1, "i == 2", i == 2)) {
                ch = csc.bridge.CSCTrace.assignObject(10, "assign", "ch", "c", c);
            }
            int j = csc.bridge.CSCTrace.assignObject(11, "var_decl", "j", "0", 0);
            while (csc.bridge.CSCTrace.cond(12, "while", 1, "j < 2", j < 2)) {
                int delim = csc.bridge.CSCTrace.assignObject(13, "var_decl", "delim", "d", d);
                if (csc.bridge.CSCTrace.cond(14, "if", 1, "j == 1", j == 1)) {
                    delim = csc.bridge.CSCTrace.assignObject(14, "assign", "delim", "e", e);
                }
                if (csc.bridge.CSCTrace.cond(15, "if", 1, "ch == delim", ch == delim)) {
                    return csc.bridge.CSCTrace.retObject(15, "return_value", "i", i);
                }
                j = csc.bridge.CSCTrace.assignObject(16, "assign", "j", "j + 1", j + 1);
            }
            i = csc.bridge.CSCTrace.assignObject(18, "assign", "i", "i + 1", i + 1);
        }
        return csc.bridge.CSCTrace.retObject(20, "return_value", "(3) + 1", (3) + 1);
    }
}
