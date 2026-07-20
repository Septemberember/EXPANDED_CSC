public class BoundedGCD {
    public static int boundedGcd(int a, int b) {
        if (a < 0 || a > 12 || b < 0 || b > 12) {
            return -1;
        }
        if (a == 0 || b == 0) {
            if (a > b) {
                return a;
            }
            return b;
        }

        while (a % b != 0) {
            int remainder = a % b;
            a = b;
            b = remainder;
        }
        return b;
    }
}
