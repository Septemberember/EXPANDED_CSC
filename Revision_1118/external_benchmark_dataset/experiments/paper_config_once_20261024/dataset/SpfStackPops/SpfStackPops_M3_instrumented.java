public class SpfStackPops_M3 {

    public static int test(int a, int b, int c, int pops) {
        System.out.println("Function input int parameter pops = " + (pops));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "a < 0", a < 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "a > 9", a > 9) || csc.bridge.CSCTrace.cond(21, "if", 3, "b < 0", b < 0) || csc.bridge.CSCTrace.cond(21, "if", 4, "b > 9", b > 9) || csc.bridge.CSCTrace.cond(21, "if", 5, "c < 0", c < 0) || csc.bridge.CSCTrace.cond(21, "if", 6, "c > 9", c > 9) || csc.bridge.CSCTrace.cond(21, "if", 7, "pops < 0", pops < 0) || csc.bridge.CSCTrace.cond(21, "if", 8, "pops > 4", pops > 4)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int depth = csc.bridge.CSCTrace.assignObject(22, "var_decl", "depth", "3", 3);
        int value = csc.bridge.CSCTrace.assignObject(23, "var_decl", "value", "-3", -3);
        int i = csc.bridge.CSCTrace.assignObject(24, "var_decl", "i", "0", 0);
        while (csc.bridge.CSCTrace.cond(25, "while", 1, "i < pops", i < pops)) {
            if (csc.bridge.CSCTrace.cond(26, "if", 1, "depth == 0", depth == 0)) {
                return csc.bridge.CSCTrace.retObject(26, "return_value", "-2", -2);
            }
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "depth != 3", depth != 3)) {
                value = csc.bridge.CSCTrace.assignObject(27, "assign", "value", "c", c);
            }
            if (csc.bridge.CSCTrace.cond(28, "if", 1, "depth == 2", depth == 2)) {
                value = csc.bridge.CSCTrace.assignObject(28, "assign", "value", "b", b);
            }
            if (csc.bridge.CSCTrace.cond(29, "if", 1, "depth == 1", depth == 1)) {
                value = csc.bridge.CSCTrace.assignObject(29, "assign", "value", "a", a);
            }
            depth = csc.bridge.CSCTrace.assignObject(30, "assign", "depth", "depth - 1", depth - 1);
            i = csc.bridge.CSCTrace.assignObject(31, "assign", "i", "i + 1", i + 1);
        }
        return csc.bridge.CSCTrace.retObject(33, "return_value", "value", value);
    }
}
