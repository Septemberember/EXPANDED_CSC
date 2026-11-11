public class SvBellmanFord3 {

    public static int test(int w01, int w02, int w12, int w21) {
        System.out.println("Function input int parameter w21 = " + (w21));
        System.out.println("Function input int parameter w12 = " + (w12));
        System.out.println("Function input int parameter w02 = " + (w02));
        System.out.println("Function input int parameter w01 = " + (w01));
        if (csc.bridge.CSCTrace.cond(43, "if", 1, "w01 < 0", w01 < 0) || csc.bridge.CSCTrace.cond(43, "if", 2, "w01 > 4", w01 > 4) || csc.bridge.CSCTrace.cond(43, "if", 3, "w02 < 0", w02 < 0) || csc.bridge.CSCTrace.cond(43, "if", 4, "w02 > 4", w02 > 4) || csc.bridge.CSCTrace.cond(43, "if", 5, "w12 < 0", w12 < 0) || csc.bridge.CSCTrace.cond(43, "if", 6, "w12 > 4", w12 > 4) || csc.bridge.CSCTrace.cond(43, "if", 7, "w21 < 0", w21 < 0) || csc.bridge.CSCTrace.cond(43, "if", 8, "w21 > 4", w21 > 4)) {
            return csc.bridge.CSCTrace.retObject(43, "return_value", "-99", -99);
        }
        int d0 = csc.bridge.CSCTrace.assignObject(44, "var_decl", "d0", "0", 0);
        int d1 = csc.bridge.CSCTrace.assignObject(45, "var_decl", "d1", "2147483647", 2147483647);
        int d2 = csc.bridge.CSCTrace.assignObject(46, "var_decl", "d2", "2147483647", 2147483647);
        int k = csc.bridge.CSCTrace.assignObject(47, "var_decl", "k", "0", 0);
        while (csc.bridge.CSCTrace.cond(48, "while", 1, "k < 3", k < 3)) {
            boolean relaxed = csc.bridge.CSCTrace.assignObject(49, "var_decl", "relaxed", "false", false);
            if (csc.bridge.CSCTrace.cond(50, "if", 1, "d1 > d0 + w01", d1 > d0 + w01)) {
                d1 = csc.bridge.CSCTrace.assignObject(50, "assign", "d1", "d0 + w01", d0 + w01);
                relaxed = csc.bridge.CSCTrace.assignObject(50, "assign", "relaxed", "true", true);
            }
            if (csc.bridge.CSCTrace.cond(51, "if", 1, "d2 > d0 + w02", d2 > d0 + w02)) {
                d2 = csc.bridge.CSCTrace.assignObject(51, "assign", "d2", "d0 + w02", d0 + w02);
                relaxed = csc.bridge.CSCTrace.assignObject(51, "assign", "relaxed", "true", true);
            }
            if (csc.bridge.CSCTrace.cond(52, "if", 1, "d0 > d1 + 4", d0 > d1 + 4)) {
                d0 = csc.bridge.CSCTrace.assignObject(52, "assign", "d0", "d1 + 4", d1 + 4);
                relaxed = csc.bridge.CSCTrace.assignObject(52, "assign", "relaxed", "true", true);
            }
            if (csc.bridge.CSCTrace.cond(53, "if", 1, "d2 > d1 + w12", d2 > d1 + w12)) {
                d2 = csc.bridge.CSCTrace.assignObject(53, "assign", "d2", "d1 + w12", d1 + w12);
                relaxed = csc.bridge.CSCTrace.assignObject(53, "assign", "relaxed", "true", true);
            }
            if (csc.bridge.CSCTrace.cond(54, "if", 1, "d0 > d2 + 4", d0 > d2 + 4)) {
                d0 = csc.bridge.CSCTrace.assignObject(54, "assign", "d0", "d2 + 4", d2 + 4);
                relaxed = csc.bridge.CSCTrace.assignObject(54, "assign", "relaxed", "true", true);
            }
            if (csc.bridge.CSCTrace.cond(55, "if", 1, "d1 > d2 + w21", d1 > d2 + w21)) {
                d1 = csc.bridge.CSCTrace.assignObject(55, "assign", "d1", "d2 + w21", d2 + w21);
                relaxed = csc.bridge.CSCTrace.assignObject(55, "assign", "relaxed", "true", true);
            }
            if (!csc.bridge.CSCTrace.cond(56, "if", 1, "relaxed", relaxed)) {
                return csc.bridge.CSCTrace.retObject(56, "return_value", "d1 * 10 + d2", d1 * 10 + d2);
            }
            k = csc.bridge.CSCTrace.assignObject(57, "assign", "k", "k + 1", k + 1);
        }
        return csc.bridge.CSCTrace.retObject(59, "return_value", "d1 * 10 + d2", d1 * 10 + d2);
    }
}
