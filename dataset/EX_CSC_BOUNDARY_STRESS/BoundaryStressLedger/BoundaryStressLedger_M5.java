public class BoundaryStressLedger {
    public static int ledgerScore(int periods, int reserve, int audit) {
        if (periods < 0 || periods > 500) {
            return -1;
        }
        if (reserve < 0 || reserve > 500) {
            return -1;
        }
        if (audit < 0 || audit > 500) {
            return -1;
        }

        int score = 0;
        int cursor = periods;
        while (cursor > 0) {
            if (reserve > 200) {
                score = score + 7;
            } else {
                score = score + 1;
            }

            if (periods > 200) {
                score = score + 2;
            }

            if (audit > 200) {
                score = score + 3;
            }

            if (score > 220) {
                return 220;
            }

            cursor = cursor - 4;
        }

        if (score > 180 && audit == 0) {
            return 180;
        }
        return score;
    }
}
