public class CampusMealPlan {
    public static int recommendPlan(int mealsPerWeek, int diningDollars, int age, int commuteMiles,
            boolean athlete, boolean vegetarian, boolean lateNight, boolean scholarship) {
        if (mealsPerWeek < 0) {
            return -1;
        }
        if (mealsPerWeek > 21) {
            return -1;
        }
        if (diningDollars < 0) {
            return -1;
        }
        if (diningDollars > 500) {
            return -1;
        }
        if (age < 16) {
            return -1;
        }
        if (age > 80) {
            return -1;
        }
        if (commuteMiles < 0) {
            return -1;
        }
        if (commuteMiles > 100) {
            return -1;
        }

        int score = 0;
        int meals = 0;
        int dollars = 0;
        int access = 0;
        int profile = 0;
        int discount = 0;

        if (mealsPerWeek >= 17) {
            meals = 4;
            score += 38;
            access += 3;
        } else if (mealsPerWeek >= 12) {
            meals = 3;
            score += 29;
            access += 2;
        } else if (mealsPerWeek >= 6) {
            meals = 2;
            score += 18;
            access += 1;
        } else {
            meals = 1;
            score += 7;
        }

        if (diningDollars >= 350) {
            dollars = 4;
            score += 21;
            access += 2;
        } else if (diningDollars >= 200) {
            dollars = 3;
            score += 15;
            access += 1;
        } else if (diningDollars >= 80) {
            dollars = 2;
            score += 8;
        } else {
            dollars = 1;
            score += 2;
        }

        if (age <= 18) {
            profile += 2;
            score += 4;
        } else if (age <= 24) {
            profile += 1;
            score += 2;
        } else if (age >= 40) {
            profile -= 1;
            score -= 2;
        } else {
            score += 1;
        }

        if (commuteMiles >= 40) {
            score += 8;
            access += 2;
        } else if (commuteMiles >= 15) {
            score += 5;
            access += 1;
        } else if (commuteMiles <= 2) {
            score -= 2;
        } else {
            score += 1;
        }

        if (athlete) {
            score += 11;
            profile += 3;
        } else {
            score += 1;
        }
        if (vegetarian) {
            score += 4;
            profile += 1;
        }
        if (lateNight) {
            score += 6;
            access += 1;
        }
        if (scholarship) {
            score -= 5;
            discount += 2;
        }

        if (meals == 4 && dollars >= 3) {
            score += 4;
        } else if (meals == 1 && dollars == 1) {
            score -= 4;
        }
        if (access >= 5 && lateNight) {
            score += 3;
        } else if (access <= 1 && commuteMiles <= 2) {
            score -= 2;
        }
        if (profile >= 4 && athlete) {
            score += 2;
        } else if (profile < 0 && scholarship) {
            score -= 2;
        }
        if (discount >= 2 && score > 60) {
            score -= 3;
        }

        if (score >= 70) {
            return 4;
        }
        if (score >= 50) {
            return 3;
        }
        if (score >= 28) {
            return 2;
        }
        return 1;
    }
}
