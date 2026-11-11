public class SpfFlapMotion_M1 {

    public static int test(int goal, int position, boolean emergency) {
        System.out.println("Function input boolean parameter emergency = " + (emergency));
        System.out.println("Function input int parameter position = " + (position));
        System.out.println("Function input int parameter goal = " + (goal));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "goal <= 0", goal <= 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "goal > 40", goal > 40) || csc.bridge.CSCTrace.cond(21, "if", 3, "position < 0", position < 0) || csc.bridge.CSCTrace.cond(21, "if", 4, "position > 40", position > 40)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        if (csc.bridge.CSCTrace.cond(22, "if", 1, "emergency", emergency)) {
            goal = csc.bridge.CSCTrace.assignObject(22, "assign", "goal", "30", 30);
        }
        int time = csc.bridge.CSCTrace.assignObject(23, "var_decl", "time", "0", 0);
        while (csc.bridge.CSCTrace.cond(24, "while", 1, "position != goal", position != goal)) {
            if (csc.bridge.CSCTrace.cond(25, "if", 1, "emergency", emergency)) {
                if (csc.bridge.CSCTrace.cond(26, "if", 1, "goal > position", goal > position)) {
                    position = csc.bridge.CSCTrace.assignObject(26, "assign", "position", "position + 10", position + 10);
                } else {
                    position = csc.bridge.CSCTrace.assignObject(26, "assign", "position", "position - 10", position - 10);
                }
            } else {
                if (csc.bridge.CSCTrace.cond(28, "if", 1, "goal > position", goal > position)) {
                    position = csc.bridge.CSCTrace.assignObject(28, "assign", "position", "position + 1", position + 1);
                } else {
                    position = csc.bridge.CSCTrace.assignObject(28, "assign", "position", "position - 1", position - 1);
                }
            }
            time = csc.bridge.CSCTrace.assignObject(30, "assign", "time", "time + 1", time + 1);
            if (csc.bridge.CSCTrace.cond(31, "if", 1, "time > 1", time > 1)) {
                return csc.bridge.CSCTrace.retObject(31, "return_value", "-2", -2);
            }
        }
        return csc.bridge.CSCTrace.retObject(33, "return_value", "position", position);
    }
}
