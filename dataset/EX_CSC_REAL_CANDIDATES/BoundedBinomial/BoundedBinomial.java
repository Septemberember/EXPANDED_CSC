public class BoundedBinomial {
    public static int boundedChoose(int n, int k) {
        if (n < 0 || n > 8) {
            return -1;
        }
        if (k < 0 || k > 4) {
            return -1;
        }
        if (k > n) {
            return 0;
        }

        int result = 1;
        int i = 1;
        while (i <= k) {
            result = result * (n - i + 1);
            result = result / i;
            i = i + 1;
        }
        return result;
    }
}
