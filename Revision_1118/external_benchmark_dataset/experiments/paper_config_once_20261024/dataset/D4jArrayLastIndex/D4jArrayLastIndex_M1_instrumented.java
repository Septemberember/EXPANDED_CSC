public class D4jArrayLastIndex_M1 {

    public static int test(int a, int b, int c, int key, int startIndex) {
        System.out.println("Function input int parameter startIndex = " + (startIndex));
        System.out.println("Function input int parameter key = " + (key));
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(20, "if", 1, "a <= 0", a <= 0) || csc.bridge.CSCTrace.cond(20, "if", 2, "a > 4", a > 4) || csc.bridge.CSCTrace.cond(20, "if", 3, "b < 0", b < 0) || csc.bridge.CSCTrace.cond(20, "if", 4, "b > 4", b > 4) || csc.bridge.CSCTrace.cond(20, "if", 5, "c < 0", c < 0) || csc.bridge.CSCTrace.cond(20, "if", 6, "c > 4", c > 4) || csc.bridge.CSCTrace.cond(20, "if", 7, "key < 0", key < 0) || csc.bridge.CSCTrace.cond(20, "if", 8, "key > 4", key > 4) || csc.bridge.CSCTrace.cond(20, "if", 9, "startIndex < -1", startIndex < -1) || csc.bridge.CSCTrace.cond(20, "if", 10, "startIndex > 4", startIndex > 4)) {
            return csc.bridge.CSCTrace.retObject(20, "return_value", "-99", -99);
        }
        int start = csc.bridge.CSCTrace.assignObject(21, "var_decl", "start", "startIndex", startIndex);
        if (csc.bridge.CSCTrace.cond(22, "if", 1, "start < 0", start < 0)) {
            return csc.bridge.CSCTrace.retObject(22, "return_value", "-1", -1);
        } else {
            if (csc.bridge.CSCTrace.cond(22, "if", 1, "start >= 3", start >= 3)) {
                start = csc.bridge.CSCTrace.assignObject(22, "assign", "start", "2", 2);
            }
        }
        int i = csc.bridge.CSCTrace.assignObject(23, "var_decl", "i", "start", start);
        while (csc.bridge.CSCTrace.cond(24, "while", 1, "i >= 0", i >= 0)) {
            int value = csc.bridge.CSCTrace.assignObject(25, "var_decl", "value", "a", a);
            if (csc.bridge.CSCTrace.cond(26, "if", 1, "i == 1", i == 1)) {
                value = csc.bridge.CSCTrace.assignObject(26, "assign", "value", "b", b);
            }
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "i == 2", i == 2)) {
                value = csc.bridge.CSCTrace.assignObject(27, "assign", "value", "c", c);
            }
            if (csc.bridge.CSCTrace.cond(28, "if", 1, "key == value", key == value)) {
                return csc.bridge.CSCTrace.retObject(28, "return_value", "i", i);
            }
            i = csc.bridge.CSCTrace.assignObject(29, "assign", "i", "i - 1", i - 1);
        }
        return csc.bridge.CSCTrace.retObject(31, "return_value", "-1", -1);
    }
}
