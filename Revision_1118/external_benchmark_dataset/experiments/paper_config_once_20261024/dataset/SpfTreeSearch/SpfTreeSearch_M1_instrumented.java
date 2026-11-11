public class SpfTreeSearch_M1 {

    public static int test(int left, int root, int right, int key) {
        System.out.println("Function input int parameter key = " + (key));
        System.out.println("Function input int parameter right = " + (right));
        System.out.println("Function input int parameter root = " + (root));
        System.out.println("Function input int parameter left = " + (left));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "left <= 0", left <= 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "root <= left", root <= left) || csc.bridge.CSCTrace.cond(21, "if", 3, "right <= root", right <= root) || csc.bridge.CSCTrace.cond(21, "if", 4, "right > 9", right > 9) || csc.bridge.CSCTrace.cond(21, "if", 5, "key < 0", key < 0) || csc.bridge.CSCTrace.cond(21, "if", 6, "key > 9", key > 9)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int current = csc.bridge.CSCTrace.assignObject(22, "var_decl", "current", "0", 0);
        while (csc.bridge.CSCTrace.cond(23, "while", 1, "current >= 0", current >= 0)) {
            int value = csc.bridge.CSCTrace.assignObject(24, "var_decl", "value", "root", root);
            if (csc.bridge.CSCTrace.cond(25, "if", 1, "current == 1", current == 1)) {
                value = csc.bridge.CSCTrace.assignObject(25, "assign", "value", "left", left);
            }
            if (csc.bridge.CSCTrace.cond(26, "if", 1, "current == 2", current == 2)) {
                value = csc.bridge.CSCTrace.assignObject(26, "assign", "value", "right", right);
            }
            if (csc.bridge.CSCTrace.cond(27, "if", 1, "value == key", value == key)) {
                return csc.bridge.CSCTrace.retObject(27, "return_value", "1", 1);
            }
            if (csc.bridge.CSCTrace.cond(28, "if", 1, "key < value", key < value)) {
                if (csc.bridge.CSCTrace.cond(29, "if", 1, "current == 0", current == 0)) {
                    current = csc.bridge.CSCTrace.assignObject(29, "assign", "current", "1", 1);
                } else {
                    current = csc.bridge.CSCTrace.assignObject(29, "assign", "current", "-1", -1);
                }
            } else {
                if (csc.bridge.CSCTrace.cond(31, "if", 1, "current == 0", current == 0)) {
                    current = csc.bridge.CSCTrace.assignObject(31, "assign", "current", "2", 2);
                } else {
                    current = csc.bridge.CSCTrace.assignObject(31, "assign", "current", "-1", -1);
                }
            }
        }
        return csc.bridge.CSCTrace.retObject(34, "return_value", "0", 0);
    }
}
