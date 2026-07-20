public class LoanRisk {
    public static int classifyRisk(int income, int debt, boolean stableJob) {
        if (income < 0 || income > 200) {
            return -1;
        }
        if (debt < 0 || debt > 200) {
            return -1;
        }

        int risk = 50;
        if (income >= 100) {
            risk -= 20;
        } else if (income >= 50) {
            risk -= 10;
        } else {
            risk += 10;
        }

        int debtLeft = debt;
        while (debtLeft > 0) {
            if (debtLeft >= 50) {
                risk += 8;
                debtLeft -= 50;
            } else {
                risk += 3;
                debtLeft = 0;
            }
        }

        if (stableJob && risk > 10) {
            risk -= 10;
        }
        if (risk < 0) {
            return 0;
        }
        if (risk > 100) {
            return 100;
        }
        return risk;
    }
}
