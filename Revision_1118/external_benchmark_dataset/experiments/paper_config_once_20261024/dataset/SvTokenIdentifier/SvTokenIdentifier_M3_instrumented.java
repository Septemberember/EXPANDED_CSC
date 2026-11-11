public class SvTokenIdentifier_M3 {

    public static int test(int a, int b, int c) {
        System.out.println("Function input int parameter c = " + (c));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(5, "if", 1, "a < 32", a < 32) || csc.bridge.CSCTrace.cond(5, "if", 2, "a > 126", a > 126) || csc.bridge.CSCTrace.cond(5, "if", 3, "b < 32", b < 32) || csc.bridge.CSCTrace.cond(5, "if", 4, "b > 126", b > 126) || csc.bridge.CSCTrace.cond(5, "if", 5, "c < 32", c < 32) || csc.bridge.CSCTrace.cond(5, "if", 6, "c > 126", c > 126)) {
            return csc.bridge.CSCTrace.retObject(5, "return_value", "-99", -99);
        }
        int i = csc.bridge.CSCTrace.assignObject(6, "var_decl", "i", "1", 1);
        boolean letter = csc.bridge.CSCTrace.assignObject(7, "var_decl", "letter", "((a >= 65 && a <= 90) || (a >= 97 && a <= 122))", ((a >= 65 && a <= 90) || (a >= 97 && a <= 122)));
        if (csc.bridge.CSCTrace.cond(8, "if", 1, "letter", letter)) {
            while (csc.bridge.CSCTrace.cond(9, "while", 1, "i < 3", i < 3)) {
                int ch = csc.bridge.CSCTrace.assignObject(10, "var_decl", "ch", "b", b);
                if (csc.bridge.CSCTrace.cond(11, "if", 1, "i != 2", i != 2)) {
                    ch = csc.bridge.CSCTrace.assignObject(11, "assign", "ch", "c", c);
                }
                letter = csc.bridge.CSCTrace.assignObject(12, "assign", "letter", "((ch >= 65 && ch <= 90) || (ch >= 97 && ch <= 122))", ((ch >= 65 && ch <= 90) || (ch >= 97 && ch <= 122)));
                if (csc.bridge.CSCTrace.cond(13, "if", 1, "letter", letter)) {
                    i = csc.bridge.CSCTrace.assignObject(13, "assign", "i", "i + 1", i + 1);
                } else {
                    boolean number = csc.bridge.CSCTrace.assignObject(15, "var_decl", "number", "(ch >= 48 && ch <= 57)", (ch >= 48 && ch <= 57));
                    if (csc.bridge.CSCTrace.cond(16, "if", 1, "number", number)) {
                        i = csc.bridge.CSCTrace.assignObject(16, "assign", "i", "i + 1", i + 1);
                    } else {
                        return csc.bridge.CSCTrace.retObject(16, "return_value", "0", 0);
                    }
                }
            }
            return csc.bridge.CSCTrace.retObject(19, "return_value", "1", 1);
        } else {
            return csc.bridge.CSCTrace.retObject(20, "return_value", "0", 0);
        }
    }
}
