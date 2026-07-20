public class GuardedQuotient {
    public static int classifyQuotient(int value) {
        if (value != 7) {
            return 0;
        }

        int quotient = 84 / (value - 7);
        if (quotient > 0) {
            return 1;
        }
        return -1;
    }
}
