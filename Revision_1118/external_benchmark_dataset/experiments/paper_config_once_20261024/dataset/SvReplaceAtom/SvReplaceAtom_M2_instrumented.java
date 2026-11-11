public class SvReplaceAtom_M2 {

    public static int test(int kind, int ch, int a, int b, int index) {
        System.out.println("Function input int parameter index = " + (index));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        System.out.println("Function input int parameter ch = " + (ch));
        System.out.println("Function input int parameter kind = " + (kind));
        if (csc.bridge.CSCTrace.cond(5, "if", 1, "kind < 0", kind < 0) || csc.bridge.CSCTrace.cond(5, "if", 2, "kind > 3", kind > 3) || csc.bridge.CSCTrace.cond(5, "if", 3, "ch < 0", ch < 0) || csc.bridge.CSCTrace.cond(5, "if", 4, "ch > 10", ch > 10) || csc.bridge.CSCTrace.cond(5, "if", 5, "a < 0", a < 0) || csc.bridge.CSCTrace.cond(5, "if", 6, "a > 10", a > 10) || csc.bridge.CSCTrace.cond(5, "if", 7, "b < 0", b < 0) || csc.bridge.CSCTrace.cond(5, "if", 8, "b > 10", b > 10) || csc.bridge.CSCTrace.cond(5, "if", 9, "index < 0", index < 0) || csc.bridge.CSCTrace.cond(5, "if", 10, "index > 1", index > 1)) {
            return csc.bridge.CSCTrace.retObject(5, "return_value", "-99", -99);
        }
        int advance = csc.bridge.CSCTrace.assignObject(6, "var_decl", "advance", "-1", -1);
        if (csc.bridge.CSCTrace.cond(7, "if", 1, "ch == 0", ch == 0)) {
            if (csc.bridge.CSCTrace.cond(8, "if", 1, "kind == 0", kind == 0)) {
                if (csc.bridge.CSCTrace.cond(8, "if", 1, "ch == a", ch == a)) {
                    advance = csc.bridge.CSCTrace.assignObject(8, "assign", "advance", "1", 1);
                }
            } else {
                if (csc.bridge.CSCTrace.cond(9, "if", 1, "kind == 1", kind == 1)) {
                    if (csc.bridge.CSCTrace.cond(9, "if", 1, "ch != 10", ch != 10)) {
                        advance = csc.bridge.CSCTrace.assignObject(9, "assign", "advance", "1", 1);
                    }
                } else {
                    boolean found = csc.bridge.CSCTrace.assignObject(11, "var_decl", "found", "false", false);
                    int i = csc.bridge.CSCTrace.assignObject(12, "var_decl", "i", "2", 2);
                    while (csc.bridge.CSCTrace.cond(13, "while", 1, "i > 0", i > 0)) {
                        int value = csc.bridge.CSCTrace.assignObject(14, "var_decl", "value", "a", a);
                        if (csc.bridge.CSCTrace.cond(15, "if", 1, "i == 2", i == 2)) {
                            value = csc.bridge.CSCTrace.assignObject(15, "assign", "value", "b", b);
                        }
                        if (csc.bridge.CSCTrace.cond(16, "if", 1, "ch == value", ch == value)) {
                            found = csc.bridge.CSCTrace.assignObject(16, "assign", "found", "true", true);
                            i = csc.bridge.CSCTrace.assignObject(16, "assign", "i", "0", 0);
                        } else {
                            i = csc.bridge.CSCTrace.assignObject(16, "assign", "i", "i - 1", i - 1);
                        }
                    }
                    if (csc.bridge.CSCTrace.cond(18, "if", 1, "kind == 2", kind == 2)) {
                        if (csc.bridge.CSCTrace.cond(18, "if", 1, "found", found)) {
                            advance = csc.bridge.CSCTrace.assignObject(18, "assign", "advance", "1", 1);
                        }
                    } else {
                        if (csc.bridge.CSCTrace.cond(19, "if", 1, "ch != 10", ch != 10) && !csc.bridge.CSCTrace.cond(19, "if", 2, "found", found)) {
                            advance = csc.bridge.CSCTrace.assignObject(19, "assign", "advance", "1", 1);
                        }
                    }
                }
            }
        }
        if (csc.bridge.CSCTrace.cond(23, "if", 1, "advance >= 0", advance >= 0)) {
            return csc.bridge.CSCTrace.retObject(23, "return_value", "index + advance", index + advance);
        }
        return csc.bridge.CSCTrace.retObject(24, "return_value", "-1", -1);
    }
}
