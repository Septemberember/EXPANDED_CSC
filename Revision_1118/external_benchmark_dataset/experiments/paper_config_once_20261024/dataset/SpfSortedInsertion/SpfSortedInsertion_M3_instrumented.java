public class SpfSortedInsertion_M3 {

    public static int test(int a, int b, int c, int value) {
        System.out.println("Function input int parameter value = " + (value));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "a < 0", a < 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "a > 9", a > 9) || csc.bridge.CSCTrace.cond(21, "if", 3, "b < a", b < a) || csc.bridge.CSCTrace.cond(21, "if", 4, "b > 9", b > 9) || csc.bridge.CSCTrace.cond(21, "if", 5, "c < b", c < b) || csc.bridge.CSCTrace.cond(21, "if", 6, "c > 9", c > 9) || csc.bridge.CSCTrace.cond(21, "if", 7, "value < 0", value < 0) || csc.bridge.CSCTrace.cond(21, "if", 8, "value > 9", value > 9)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int first = csc.bridge.CSCTrace.assignObject(22, "var_decl", "first", "a", a);
        if (csc.bridge.CSCTrace.cond(23, "if", 1, "value < first", value < first)) {
            return csc.bridge.CSCTrace.retObject(23, "return_value", "value * 1000 + a * 100 + b * 10 + c", value * 1000 + a * 100 + b * 10 + c);
        }
        int cursor = csc.bridge.CSCTrace.assignObject(24, "var_decl", "cursor", "1", 1);
        int following = csc.bridge.CSCTrace.assignObject(25, "var_decl", "following", "b", b);
        while (csc.bridge.CSCTrace.cond(26, "while", 1, "cursor < 3", cursor < 3) && csc.bridge.CSCTrace.cond(26, "while", 2, "following < value", following < value)) {
            cursor = csc.bridge.CSCTrace.assignObject(27, "assign", "cursor", "cursor + 1", cursor + 1);
            if (csc.bridge.CSCTrace.cond(28, "if", 1, "cursor == 2", cursor == 2)) {
                following = csc.bridge.CSCTrace.assignObject(28, "assign", "following", "c", c);
            }
        }
        if (csc.bridge.CSCTrace.cond(30, "if", 1, "cursor == 1", cursor == 1)) {
            return csc.bridge.CSCTrace.retObject(30, "return_value", "a * 1000 + value * 100 + b * 10 + c", a * 1000 + value * 100 + b * 10 + c);
        }
        if (csc.bridge.CSCTrace.cond(31, "if", 1, "cursor == 2", cursor == 2)) {
            return csc.bridge.CSCTrace.retObject(31, "return_value", "a * 1000 + b * 100 + value * 10 + c", a * 1000 + b * 100 + value * 10 + c);
        }
        return csc.bridge.CSCTrace.retObject(32, "return_value", "a * 1000 + b * 100 + c * 10 + value", a * 1000 + b * 100 + c * 10 + value);
    }
}
