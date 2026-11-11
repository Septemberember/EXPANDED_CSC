public class SvTcasClimb_M4 {

    public static int test(int layer, int upDelta, int downDelta, int separation, boolean above, boolean inhibit) {
        System.out.println("Function input boolean parameter inhibit = " + (inhibit));
        System.out.println("Function input boolean parameter above = " + (above));
        System.out.println("Function input int parameter separation = " + (separation));
        System.out.println("Function input int parameter downDelta = " + (downDelta));
        System.out.println("Function input int parameter upDelta = " + (upDelta));
        System.out.println("Function input int parameter layer = " + (layer));
        if (csc.bridge.CSCTrace.cond(5, "if", 1, "layer < 0", layer < 0) || csc.bridge.CSCTrace.cond(5, "if", 2, "layer > 3", layer > 3) || csc.bridge.CSCTrace.cond(5, "if", 3, "upDelta < -2", upDelta < -2) || csc.bridge.CSCTrace.cond(5, "if", 4, "upDelta > 2", upDelta > 2) || csc.bridge.CSCTrace.cond(5, "if", 5, "downDelta < -2", downDelta < -2) || csc.bridge.CSCTrace.cond(5, "if", 6, "downDelta > 2", downDelta > 2) || csc.bridge.CSCTrace.cond(5, "if", 7, "separation < 0", separation < 0) || csc.bridge.CSCTrace.cond(5, "if", 8, "separation > 2", separation > 2)) {
            return csc.bridge.CSCTrace.retObject(5, "return_value", "-99", -99);
        }
        int alim = csc.bridge.CSCTrace.assignObject(6, "var_decl", "alim", "740", 740);
        if (csc.bridge.CSCTrace.cond(7, "if", 1, "layer == 0", layer == 0)) {
            alim = csc.bridge.CSCTrace.assignObject(7, "assign", "alim", "400", 400);
        } else {
            if (csc.bridge.CSCTrace.cond(7, "if", 1, "layer == 1", layer == 1)) {
                alim = csc.bridge.CSCTrace.assignObject(7, "assign", "alim", "500", 500);
            } else {
                if (csc.bridge.CSCTrace.cond(7, "if", 1, "layer == 2", layer == 2)) {
                    alim = csc.bridge.CSCTrace.assignObject(7, "assign", "alim", "640", 640);
                }
            }
        }
        int up = csc.bridge.CSCTrace.assignObject(8, "var_decl", "up", "alim + upDelta * 100", alim + upDelta * 100);
        int down = csc.bridge.CSCTrace.assignObject(9, "var_decl", "down", "alim + downDelta * 100", alim + downDelta * 100);
        int sep = csc.bridge.CSCTrace.assignObject(10, "var_decl", "sep", "500 + separation * 100", 500 + separation * 100);
        int biased = csc.bridge.CSCTrace.assignObject(11, "var_decl", "biased", "up", up);
        if (csc.bridge.CSCTrace.cond(12, "if", 1, "inhibit", inhibit)) {
            biased = csc.bridge.CSCTrace.assignObject(12, "assign", "biased", "up + 100", up + 100);
        }
        int preferred = csc.bridge.CSCTrace.assignObject(13, "var_decl", "preferred", "0", 0);
        if (csc.bridge.CSCTrace.cond(14, "if", 1, "biased > down", biased > down)) {
            preferred = csc.bridge.CSCTrace.assignObject(14, "assign", "preferred", "1", 1);
        }
        if (csc.bridge.CSCTrace.cond(15, "if", 1, "preferred != 0", preferred != 0)) {
            if (!(csc.bridge.CSCTrace.cond(16, "if", 1, "down >= alim", down >= alim))) {
                return csc.bridge.CSCTrace.retObject(16, "return_value", "1", 1);
            } else {
                return csc.bridge.CSCTrace.retObject(16, "return_value", "0", 0);
            }
        } else {
            if (!(csc.bridge.CSCTrace.cond(18, "if", 1, "sep >= 600", sep >= 600))) {
                return csc.bridge.CSCTrace.retObject(18, "return_value", "0", 0);
            } else {
                if (!(csc.bridge.CSCTrace.cond(20, "if", 1, "up >= alim", up >= alim))) {
                    return csc.bridge.CSCTrace.retObject(20, "return_value", "0", 0);
                } else {
                    if (!csc.bridge.CSCTrace.cond(21, "if", 1, "above", above)) {
                        return csc.bridge.CSCTrace.retObject(21, "return_value", "0", 0);
                    } else {
                        return csc.bridge.CSCTrace.retObject(21, "return_value", "(1) + 1", (1) + 1);
                    }
                }
            }
        }
    }
}
