public class BoundaryStressQuota {
    public static int quotaScore(int rounds, int quota, int reserve) {
        if (rounds < 0 || rounds > 500) {
            return -1;
        }
        if (quota < 0 || quota > 500) {
            return -1;
        }
        if (reserve < 0 || reserve > 500) {
            return -1;
        }

        int score = 0;
        int count = rounds;
        while (count > 0) {
            if (quota > 200) {
                score = score + 8;
            } else {
                score = score + 1;
            }

            if (rounds > 200) {
                score = score + 2;
            }

            if (reserve > 200) {
                score = score + 3;
            }

            if (score > 220) {
                return 220;
            }

            count = count - 3;
        }

        if (score < 0) {
            return 0;
        }
        return score;
    }
}
