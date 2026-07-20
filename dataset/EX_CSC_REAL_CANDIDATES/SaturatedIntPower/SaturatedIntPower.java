public class SaturatedIntPower {
    public static int saturatedPow(int base, int exponent, boolean highCap) {
        if (base < -4 || base > 4) {
            return -999;
        }
        if (exponent < 0 || exponent > 6) {
            return -999;
        }

        int limit = 60;
        if (highCap) {
            limit = 120;
        }
        int floor = -limit;

        if (exponent == 0) {
            return 1;
        }
        if (base == 0) {
            return 0;
        }

        int result = 1;
        int n = exponent;
        while (n > 0) {
            result = result * base;
            n = n - 1;
        }
        if (result > limit) {
            return limit;
        }
        if (result < floor) {
            return floor;
        }
        return result;
    }
}
