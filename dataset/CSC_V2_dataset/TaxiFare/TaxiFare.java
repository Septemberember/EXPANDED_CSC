public class TaxiFare {
    public static int calcFare(int distance, int waitMinutes, boolean night) {
        if (distance <= 0) {
            return 0;
        }
        if (distance > 30 || waitMinutes < 0 || waitMinutes > 60) {
            return -1;
        }

        int fare = 12;
        if (distance > 3) {
            int extraDistance = distance - 3;
            while (extraDistance > 0) {
                if (extraDistance <= 5) {
                    fare += 2;
                } else {
                    fare += 3;
                }
                extraDistance--;
            }
        }

        if (waitMinutes > 0) {
            if (waitMinutes <= 10) {
                fare += waitMinutes / 2;
            } else {
                fare += 5 + (waitMinutes - 10);
            }
        }

        if (night && fare > 0) {
            fare += 5;
        }
        return fare;
    }
}
