public class SvCliOption_M1 {

    public static int test(int code) {
        System.out.println("Function input int parameter code = " + (code));
        if (csc.bridge.CSCTrace.cond(11, "if", 1, "code <= 0", code <= 0) || csc.bridge.CSCTrace.cond(11, "if", 2, "code > 127", code > 127)) {
            return csc.bridge.CSCTrace.retObject(11, "return_value", "-99", -99);
        }
        boolean valid = csc.bridge.CSCTrace.assignObject(12, "var_decl", "valid", "false", false);
        if ((csc.bridge.CSCTrace.cond(13, "if", 1, "code >= 97", code >= 97) && csc.bridge.CSCTrace.cond(13, "if", 2, "code <= 122", code <= 122)) || (csc.bridge.CSCTrace.cond(13, "if", 3, "code >= 65", code >= 65) && csc.bridge.CSCTrace.cond(13, "if", 4, "code <= 90", code <= 90)) || csc.bridge.CSCTrace.cond(13, "if", 5, "code == 95", code == 95) || csc.bridge.CSCTrace.cond(13, "if", 6, "code == 46", code == 46)) {
            valid = csc.bridge.CSCTrace.assignObject(13, "assign", "valid", "true", true);
        }
        boolean option = csc.bridge.CSCTrace.assignObject(14, "var_decl", "option", "false", false);
        if (csc.bridge.CSCTrace.cond(15, "if", 1, "valid", valid) || csc.bridge.CSCTrace.cond(15, "if", 2, "code == 32", code == 32) || csc.bridge.CSCTrace.cond(15, "if", 3, "code == 63", code == 63) || csc.bridge.CSCTrace.cond(15, "if", 4, "code == 64", code == 64)) {
            option = csc.bridge.CSCTrace.assignObject(15, "assign", "option", "true", true);
        }
        if (!csc.bridge.CSCTrace.cond(16, "if", 1, "option", option)) {
            return csc.bridge.CSCTrace.retObject(16, "return_value", "-1", -1);
        }
        return csc.bridge.CSCTrace.retObject(17, "return_value", "1", 1);
    }
}
