public class BoundedIntPower {
    public static int boundedPow(int base, int exponent, boolean signedMode) {
        if (base < -3 || base > 3) {
            return -1;
        }
        if (exponent < 0 || exponent > 6) {
            return -1;
        }

        if (exponent == 0) {
            return 1;
        }
        if (base == 0) {
            return 0;
        }

        int factor = base;
        if (!signedMode && factor < 0) {
            factor = -factor;
        }

        int result = 1;
        int remaining = exponent;
        while (remaining > 0) {
            result = result * factor;
            remaining = remaining - 1;
        }
        return result;
    }
}
