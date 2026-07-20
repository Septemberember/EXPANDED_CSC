public class ApplianceWarranty {
    public static int decideClaim(int monthsOwned, int repairCost, int deviceTier, int incidents,
            boolean express, boolean refurbished, boolean member, boolean accidental) {
        if (monthsOwned < 0 || monthsOwned > 120) {
            return -1;
        }
        if (repairCost < 0 || repairCost > 5000) {
            return -1;
        }
        if (deviceTier < 1 || deviceTier > 4) {
            return -1;
        }
        if (incidents < 0 || incidents > 8) {
            return -1;
        }

        int score = 20;
        int ageCredit = 0;
        int costPressure = 0;
        int risk = 0;
        int service = 0;
        int finalScore = 0;

        if (monthsOwned <= 24) {
            ageCredit = 18;
            service = 2;
        } else if (monthsOwned <= 60) {
            ageCredit = 8;
            risk = 1;
        } else {
            ageCredit = 2;
            risk = 3;
        }

        score += ageCredit;
        score += service;
        score -= risk;

        if (repairCost >= 1500) {
            costPressure = 16;
            risk += 3;
        } else if (repairCost >= 400) {
            costPressure = 7;
            risk += 1;
        } else {
            costPressure = 2;
            service += 1;
        }

        score -= costPressure;
        score += repairCost / 250;
        score -= repairCost / 700;

        if (deviceTier >= 3) {
            score += 14;
            service += 2;
        } else {
            score += 4;
        }

        if (incidents >= 4) {
            score -= 14;
            risk += 3;
        } else if (incidents == 0) {
            score += 6;
            service += 1;
        }

        score += deviceTier * 2;
        score -= incidents * 2;
        score += monthsOwned / 30;

        if (member && !refurbished) {
            score += 8;
            service += 1;
        }
        if (express || accidental) {
            score -= 4;
            risk += 1;
        }

        finalScore = score;
        finalScore += service * 2;
        finalScore -= risk * 3;
        finalScore += ageCredit / 3;
        finalScore -= costPressure / 4;
        finalScore += deviceTier;
        finalScore -= incidents;

        if (finalScore >= 50) {
            return 4;
        }
        if (finalScore >= 32) {
            return 3;
        }
        if (finalScore >= 14) {
            return 2;
        }
        return 1;
    }
}
