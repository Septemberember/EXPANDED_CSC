public class SpfRjcCounter_M6 {

    public static int test(int steps) {
        System.out.println("Function input int parameter steps = " + (steps));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "steps < 0", steps < 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "steps > 8", steps > 8)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int active = csc.bridge.CSCTrace.assignObject(22, "var_decl", "active", "1", 1);
        int initialized = csc.bridge.CSCTrace.assignObject(23, "var_decl", "initialized", "0", 0);
        int counter = csc.bridge.CSCTrace.assignObject(24, "var_decl", "counter", "0", 0);
        int i = csc.bridge.CSCTrace.assignObject(25, "var_decl", "i", "0", 0);
        while (csc.bridge.CSCTrace.cond(26, "while", 1, "i < steps", i < steps)) {
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "initialized == 1", initialized == 1)) {
                if (csc.bridge.CSCTrace.cond(28, "if", 1, "active == 1", active == 1)) {
                    counter = csc.bridge.CSCTrace.assignObject(29, "assign", "counter", "counter + 1", counter + 1);
                    active = csc.bridge.CSCTrace.assignObject(30, "assign", "active", "-1", -1);
                    active = csc.bridge.CSCTrace.assignObject(31, "assign", "active", "1", 1);
                }
            }
            initialized = csc.bridge.CSCTrace.assignObject(34, "assign", "initialized", "2", 2);
            i = csc.bridge.CSCTrace.assignObject(35, "assign", "i", "i + 1", i + 1);
        }
        return csc.bridge.CSCTrace.retObject(37, "return_value", "counter", counter);
    }
}
