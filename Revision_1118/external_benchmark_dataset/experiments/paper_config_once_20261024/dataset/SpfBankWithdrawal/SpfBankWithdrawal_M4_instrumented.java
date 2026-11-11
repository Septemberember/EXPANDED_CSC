public class SpfBankWithdrawal_M4 {

    public static int test(int balance, int deposit, int amount, int withdrawals) {
        System.out.println("Function input int parameter withdrawals = " + (withdrawals));
        System.out.println("Function input int parameter amount = " + (amount));
        System.out.println("Function input int parameter deposit = " + (deposit));
        System.out.println("Function input int parameter balance = " + (balance));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "balance < 0", balance < 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "balance > 20", balance > 20) || csc.bridge.CSCTrace.cond(21, "if", 3, "deposit < -5", deposit < -5) || csc.bridge.CSCTrace.cond(21, "if", 4, "deposit > 10", deposit > 10) || csc.bridge.CSCTrace.cond(21, "if", 5, "amount < -5", amount < -5) || csc.bridge.CSCTrace.cond(21, "if", 6, "amount > 30", amount > 30) || csc.bridge.CSCTrace.cond(21, "if", 7, "withdrawals < 0", withdrawals < 0) || csc.bridge.CSCTrace.cond(21, "if", 8, "withdrawals > 5", withdrawals > 5)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int currentBalance = csc.bridge.CSCTrace.assignObject(22, "var_decl", "currentBalance", "balance", balance);
        if (csc.bridge.CSCTrace.cond(23, "if", 1, "deposit > 0", deposit > 0)) {
            currentBalance = csc.bridge.CSCTrace.assignObject(23, "assign", "currentBalance", "currentBalance + deposit", currentBalance + deposit);
        }
        if (csc.bridge.CSCTrace.cond(24, "if", 1, "amount > currentBalance", amount > currentBalance)) {
            return csc.bridge.CSCTrace.retObject(24, "return_value", "currentBalance", currentBalance);
        }
        if (csc.bridge.CSCTrace.cond(25, "if", 1, "withdrawals >= 5", withdrawals >= 5)) {
            return csc.bridge.CSCTrace.retObject(25, "return_value", "-2", -2);
        }
        currentBalance = csc.bridge.CSCTrace.assignObject(26, "assign", "currentBalance", "currentBalance - amount", currentBalance - amount);
        int nextWithdrawals = csc.bridge.CSCTrace.assignObject(27, "var_decl", "nextWithdrawals", "withdrawals + 1", withdrawals + 1);
        return csc.bridge.CSCTrace.retObject(28, "return_value", "(currentBalance) + 1", (currentBalance) + 1);
    }
}
