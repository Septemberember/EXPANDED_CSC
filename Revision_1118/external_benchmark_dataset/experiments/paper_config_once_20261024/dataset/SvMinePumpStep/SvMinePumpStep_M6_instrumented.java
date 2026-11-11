public class SvMinePumpStep_M6 {

    public static int test(int water, boolean running, boolean active, boolean methane) {
        System.out.println("Function input boolean parameter methane = " + (methane));
        System.out.println("Function input boolean parameter active = " + (active));
        System.out.println("Function input boolean parameter running = " + (running));
        System.out.println("Function input int parameter water = " + (water));
        if (csc.bridge.CSCTrace.cond(5, "if", 1, "water < 0", water < 0) || csc.bridge.CSCTrace.cond(5, "if", 2, "water > 2", water > 2)) {
            return csc.bridge.CSCTrace.retObject(5, "return_value", "-99", -99);
        }
        int level = csc.bridge.CSCTrace.assignObject(6, "var_decl", "level", "water", water);
        boolean pump = csc.bridge.CSCTrace.assignObject(7, "var_decl", "pump", "running", running);
        if (csc.bridge.CSCTrace.cond(8, "if", 1, "pump", pump)) {
            if (csc.bridge.CSCTrace.cond(9, "if", 1, "level == 2", level == 2)) {
                level = csc.bridge.CSCTrace.assignObject(9, "assign", "level", "1", 1);
            } else {
                if (csc.bridge.CSCTrace.cond(9, "if", 1, "level == 1", level == 1)) {
                    level = csc.bridge.CSCTrace.assignObject(9, "assign", "level", "0", 0);
                }
            }
        }
        if (csc.bridge.CSCTrace.cond(11, "if", 1, "active", active)) {
            if (csc.bridge.CSCTrace.cond(12, "if", 1, "pump", pump) && csc.bridge.CSCTrace.cond(12, "if", 2, "methane", methane)) {
                pump = csc.bridge.CSCTrace.assignObject(12, "assign", "pump", "false", false);
            } else {
                if (csc.bridge.CSCTrace.cond(14, "if", 1, "pump", pump) && csc.bridge.CSCTrace.cond(14, "if", 2, "level != 0", level != 0)) {
                    pump = csc.bridge.CSCTrace.assignObject(14, "assign", "pump", "false", false);
                } else {
                    if (!csc.bridge.CSCTrace.cond(16, "if", 1, "pump", pump) && csc.bridge.CSCTrace.cond(16, "if", 2, "level == 2", level == 2)) {
                        if (!csc.bridge.CSCTrace.cond(16, "if", 1, "methane", methane)) {
                            pump = csc.bridge.CSCTrace.assignObject(16, "assign", "pump", "true", true);
                        }
                    }
                }
            }
        }
        int state = csc.bridge.CSCTrace.assignObject(20, "var_decl", "state", "0", 0);
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "pump", pump)) {
            state = csc.bridge.CSCTrace.assignObject(21, "assign", "state", "11", 11);
        }
        return csc.bridge.CSCTrace.retObject(22, "return_value", "state + level", state + level);
    }
}
