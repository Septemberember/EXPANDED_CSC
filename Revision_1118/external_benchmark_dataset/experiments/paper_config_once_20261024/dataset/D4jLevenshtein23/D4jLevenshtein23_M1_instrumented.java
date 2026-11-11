public class D4jLevenshtein23_M1 {

    public static int test(int a, int b, int x, int y, int z) {
        System.out.println("Function input int parameter z = " + (z));
        System.out.println("Function input int parameter y = " + (y));
        System.out.println("Function input int parameter x = " + (x));
        System.out.println("Function input int parameter b = " + (b));
        System.out.println("Function input int parameter a = " + (a));
        if (csc.bridge.CSCTrace.cond(20, "if", 1, "a <= 1", a <= 1) || csc.bridge.CSCTrace.cond(20, "if", 2, "a > 3", a > 3) || csc.bridge.CSCTrace.cond(20, "if", 3, "b < 1", b < 1) || csc.bridge.CSCTrace.cond(20, "if", 4, "b > 3", b > 3) || csc.bridge.CSCTrace.cond(20, "if", 5, "x < 1", x < 1) || csc.bridge.CSCTrace.cond(20, "if", 6, "x > 3", x > 3) || csc.bridge.CSCTrace.cond(20, "if", 7, "y < 1", y < 1) || csc.bridge.CSCTrace.cond(20, "if", 8, "y > 3", y > 3) || csc.bridge.CSCTrace.cond(20, "if", 9, "z < 1", z < 1) || csc.bridge.CSCTrace.cond(20, "if", 10, "z > 3", z > 3)) {
            return csc.bridge.CSCTrace.retObject(20, "return_value", "-99", -99);
        }
        int p0 = csc.bridge.CSCTrace.assignObject(21, "var_decl", "p0", "0", 0);
        int p1 = csc.bridge.CSCTrace.assignObject(21, "var_decl", "p1", "1", 1);
        int p2 = csc.bridge.CSCTrace.assignObject(21, "var_decl", "p2", "2", 2);
        int d0 = csc.bridge.CSCTrace.assignObject(22, "var_decl", "d0", "0", 0);
        int d1 = csc.bridge.CSCTrace.assignObject(22, "var_decl", "d1", "0", 0);
        int d2 = csc.bridge.CSCTrace.assignObject(22, "var_decl", "d2", "0", 0);
        int j = csc.bridge.CSCTrace.assignObject(23, "var_decl", "j", "1", 1);
        while (csc.bridge.CSCTrace.cond(24, "while", 1, "j <= 3", j <= 3)) {
            int tj = csc.bridge.CSCTrace.assignObject(25, "var_decl", "tj", "x", x);
            if (csc.bridge.CSCTrace.cond(26, "if", 1, "j == 2", j == 2)) {
                tj = csc.bridge.CSCTrace.assignObject(26, "assign", "tj", "y", y);
            }
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "j == 3", j == 3)) {
                tj = csc.bridge.CSCTrace.assignObject(27, "assign", "tj", "z", z);
            }
            d0 = csc.bridge.CSCTrace.assignObject(28, "assign", "d0", "j", j);
            int i = csc.bridge.CSCTrace.assignObject(29, "var_decl", "i", "1", 1);
            while (csc.bridge.CSCTrace.cond(30, "while", 1, "i <= 2", i <= 2)) {
                int si = csc.bridge.CSCTrace.assignObject(31, "var_decl", "si", "a", a);
                int left = csc.bridge.CSCTrace.assignObject(31, "var_decl", "left", "d0", d0);
                int top = csc.bridge.CSCTrace.assignObject(31, "var_decl", "top", "p1", p1);
                int diagonal = csc.bridge.CSCTrace.assignObject(31, "var_decl", "diagonal", "p0", p0);
                if (csc.bridge.CSCTrace.cond(32, "if", 1, "i == 2", i == 2)) {
                    si = csc.bridge.CSCTrace.assignObject(32, "assign", "si", "b", b);
                    left = csc.bridge.CSCTrace.assignObject(32, "assign", "left", "d1", d1);
                    top = csc.bridge.CSCTrace.assignObject(32, "assign", "top", "p2", p2);
                    diagonal = csc.bridge.CSCTrace.assignObject(32, "assign", "diagonal", "p1", p1);
                }
                int cost = csc.bridge.CSCTrace.assignObject(33, "var_decl", "cost", "1", 1);
                if (csc.bridge.CSCTrace.cond(34, "if", 1, "si == tj", si == tj)) {
                    cost = csc.bridge.CSCTrace.assignObject(34, "assign", "cost", "0", 0);
                }
                int value = csc.bridge.CSCTrace.assignObject(35, "var_decl", "value", "left + 1", left + 1);
                if (csc.bridge.CSCTrace.cond(36, "if", 1, "top + 1 < value", top + 1 < value)) {
                    value = csc.bridge.CSCTrace.assignObject(36, "assign", "value", "top + 1", top + 1);
                }
                if (csc.bridge.CSCTrace.cond(37, "if", 1, "diagonal + cost < value", diagonal + cost < value)) {
                    value = csc.bridge.CSCTrace.assignObject(37, "assign", "value", "diagonal + cost", diagonal + cost);
                }
                if (csc.bridge.CSCTrace.cond(38, "if", 1, "i == 1", i == 1)) {
                    d1 = csc.bridge.CSCTrace.assignObject(38, "assign", "d1", "value", value);
                } else {
                    d2 = csc.bridge.CSCTrace.assignObject(38, "assign", "d2", "value", value);
                }
                i = csc.bridge.CSCTrace.assignObject(39, "assign", "i", "i + 1", i + 1);
            }
            p0 = csc.bridge.CSCTrace.assignObject(41, "assign", "p0", "d0", d0);
            p1 = csc.bridge.CSCTrace.assignObject(41, "assign", "p1", "d1", d1);
            p2 = csc.bridge.CSCTrace.assignObject(41, "assign", "p2", "d2", d2);
            j = csc.bridge.CSCTrace.assignObject(42, "assign", "j", "j + 1", j + 1);
        }
        return csc.bridge.CSCTrace.retObject(44, "return_value", "p2", p2);
    }
}
