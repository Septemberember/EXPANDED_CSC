public class D4jMonotonicOrder_M1 {

    public static int test(int a, int b, int c, boolean increasing, boolean strict) {
        System.out.println("Function input boolean parameter strict = " + (strict));
        System.out.println("Function input boolean parameter increasing = " + (increasing));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(20, "if", 1, "a <= -3", a <= -3) || csc.bridge.CSCTrace.cond(20, "if", 2, "a > 3", a > 3) || csc.bridge.CSCTrace.cond(20, "if", 3, "b < -3", b < -3) || csc.bridge.CSCTrace.cond(20, "if", 4, "b > 3", b > 3) || csc.bridge.CSCTrace.cond(20, "if", 5, "c < -3", c < -3) || csc.bridge.CSCTrace.cond(20, "if", 6, "c > 3", c > 3)) {
            return csc.bridge.CSCTrace.retObject(20, "return_value", "-99", -99);
        }
        int previous = csc.bridge.CSCTrace.assignObject(21, "var_decl", "previous", "a", a);
        int i = csc.bridge.CSCTrace.assignObject(22, "var_decl", "i", "1", 1);
        while (csc.bridge.CSCTrace.cond(23, "while", 1, "i < 3", i < 3)) {
            int value = csc.bridge.CSCTrace.assignObject(24, "var_decl", "value", "b", b);
            if (csc.bridge.CSCTrace.cond(25, "if", 1, "i == 2", i == 2)) {
                value = csc.bridge.CSCTrace.assignObject(25, "assign", "value", "c", c);
            }
            if (csc.bridge.CSCTrace.cond(26, "if", 1, "increasing", increasing)) {
                if (csc.bridge.CSCTrace.cond(27, "if", 1, "strict", strict)) {
                    if (csc.bridge.CSCTrace.cond(27, "if", 1, "value <= previous", value <= previous)) {
                        return csc.bridge.CSCTrace.retObject(27, "return_value", "0", 0);
                    }
                } else {
                    if (csc.bridge.CSCTrace.cond(28, "if", 1, "value < previous", value < previous)) {
                        return csc.bridge.CSCTrace.retObject(28, "return_value", "0", 0);
                    }
                }
            } else {
                if (csc.bridge.CSCTrace.cond(30, "if", 1, "strict", strict)) {
                    if (csc.bridge.CSCTrace.cond(30, "if", 1, "value >= previous", value >= previous)) {
                        return csc.bridge.CSCTrace.retObject(30, "return_value", "0", 0);
                    }
                } else {
                    if (csc.bridge.CSCTrace.cond(31, "if", 1, "value > previous", value > previous)) {
                        return csc.bridge.CSCTrace.retObject(31, "return_value", "0", 0);
                    }
                }
            }
            previous = csc.bridge.CSCTrace.assignObject(33, "assign", "previous", "value", value);
            i = csc.bridge.CSCTrace.assignObject(34, "assign", "i", "i + 1", i + 1);
        }
        return csc.bridge.CSCTrace.retObject(36, "return_value", "1", 1);
    }
}
