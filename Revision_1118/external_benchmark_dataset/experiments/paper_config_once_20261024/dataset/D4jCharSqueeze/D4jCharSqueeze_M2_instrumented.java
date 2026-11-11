public class D4jCharSqueeze_M2 {

    public static int test(int a, int b, int c, int d, int low, int high) {
        System.out.println("Function input int parameter high = " + (high));
        System.out.println("Function input int parameter low = " + (low));
        System.out.println("Function input int parameter d = " + (d));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(20, "if", 1, "a < 1", a < 1) || csc.bridge.CSCTrace.cond(20, "if", 2, "a > 3", a > 3) || csc.bridge.CSCTrace.cond(20, "if", 3, "b < 1", b < 1) || csc.bridge.CSCTrace.cond(20, "if", 4, "b > 3", b > 3) || csc.bridge.CSCTrace.cond(20, "if", 5, "c < 1", c < 1) || csc.bridge.CSCTrace.cond(20, "if", 6, "c > 3", c > 3) || csc.bridge.CSCTrace.cond(20, "if", 7, "d < 1", d < 1) || csc.bridge.CSCTrace.cond(20, "if", 8, "d > 3", d > 3) || csc.bridge.CSCTrace.cond(20, "if", 9, "low < 1", low < 1) || csc.bridge.CSCTrace.cond(20, "if", 10, "low > 3", low > 3) || csc.bridge.CSCTrace.cond(20, "if", 11, "high < 1", high < 1) || csc.bridge.CSCTrace.cond(20, "if", 12, "high > 3", high > 3) || csc.bridge.CSCTrace.cond(20, "if", 13, "low > high", low > high)) {
            return csc.bridge.CSCTrace.retObject(20, "return_value", "-99", -99);
        }
        int result = csc.bridge.CSCTrace.assignObject(21, "var_decl", "result", "0", 0);
        int last = csc.bridge.CSCTrace.assignObject(22, "var_decl", "last", "32", 32);
        int i = csc.bridge.CSCTrace.assignObject(23, "var_decl", "i", "0", 0);
        while (csc.bridge.CSCTrace.cond(24, "while", 1, "i < 4", i < 4)) {
            int ch = csc.bridge.CSCTrace.assignObject(25, "var_decl", "ch", "a", a);
            if (csc.bridge.CSCTrace.cond(26, "if", 1, "i != 1", i != 1)) {
                ch = csc.bridge.CSCTrace.assignObject(26, "assign", "ch", "b", b);
            }
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "i == 2", i == 2)) {
                ch = csc.bridge.CSCTrace.assignObject(27, "assign", "ch", "c", c);
            }
            if (csc.bridge.CSCTrace.cond(28, "if", 1, "i == 3", i == 3)) {
                ch = csc.bridge.CSCTrace.assignObject(28, "assign", "ch", "d", d);
            }
            if (!(csc.bridge.CSCTrace.cond(29, "if", 1, "ch == last", ch == last) && csc.bridge.CSCTrace.cond(29, "if", 2, "i != 0", i != 0) && csc.bridge.CSCTrace.cond(29, "if", 3, "ch >= low", ch >= low) && csc.bridge.CSCTrace.cond(29, "if", 4, "ch <= high", ch <= high))) {
                result = csc.bridge.CSCTrace.assignObject(30, "assign", "result", "result * 10 + ch", result * 10 + ch);
                last = csc.bridge.CSCTrace.assignObject(31, "assign", "last", "ch", ch);
            }
            i = csc.bridge.CSCTrace.assignObject(33, "assign", "i", "i + 1", i + 1);
        }
        return csc.bridge.CSCTrace.retObject(35, "return_value", "result", result);
    }
}
