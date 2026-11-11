public class SpfAbortDecision_M5 {

    public static int test(int altitudeOffset, boolean fired) {
        System.out.println("Function input boolean parameter fired = " + (fired));
        System.out.println("Function input int parameter altitudeOffset = " + (altitudeOffset));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "altitudeOffset < -1000", altitudeOffset < -1000) || csc.bridge.CSCTrace.cond(21, "if", 2, "altitudeOffset > 1000", altitudeOffset > 1000)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int failure = csc.bridge.CSCTrace.assignObject(22, "var_decl", "failure", "0", 0);
        int state = csc.bridge.CSCTrace.assignObject(23, "var_decl", "state", "0", 0);
        boolean selected = csc.bridge.CSCTrace.assignObject(24, "var_decl", "selected", "false", false);
        if (!csc.bridge.CSCTrace.cond(25, "if", 1, "fired", fired)) {
            failure = csc.bridge.CSCTrace.assignObject(25, "assign", "failure", "10", 10);
        }
        if (csc.bridge.CSCTrace.cond(26, "if", 1, "altitudeOffset <= 0", altitudeOffset <= 0)) {
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "fired", fired)) {
                state = csc.bridge.CSCTrace.assignObject(27, "assign", "state", "1", 1);
            } else {
                state = csc.bridge.CSCTrace.assignObject(27, "assign", "state", "2", 2);
            }
            selected = csc.bridge.CSCTrace.assignObject(28, "assign", "selected", "true", true);
        }
        if (csc.bridge.CSCTrace.cond(30, "if", 1, "altitudeOffset >= 0", altitudeOffset >= 0)) {
            if (csc.bridge.CSCTrace.cond(31, "if", 1, "selected", selected)) {
                return csc.bridge.CSCTrace.retObject(31, "return_value", "(-2) + 1", (-2) + 1);
            }
            state = csc.bridge.CSCTrace.assignObject(32, "assign", "state", "3", 3);
            selected = csc.bridge.CSCTrace.assignObject(33, "assign", "selected", "true", true);
        }
        return csc.bridge.CSCTrace.retObject(35, "return_value", "failure + state", failure + state);
    }
}
