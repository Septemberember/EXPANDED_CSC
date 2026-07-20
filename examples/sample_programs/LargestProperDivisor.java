/**
 * LargestProperDivisor — sample program for CSC test generation.
 *
 * Returns the largest proper divisor of n (the largest integer d < n such that n % d == 0).
 * Returns -1 if n <= 1 (no proper divisor exists).
 *
 * The println statements match the format expected by csc_engine's execution path parser.
 */
public class LargestProperDivisor {

    public static int largestProperDivisor(int n) {
        System.out.println("Function input int parameter n = " + n);
        int return_value;
        int i;
        int result;

        System.out.println("Evaluating if condition: n <= 1 is evaluated as: " + (n <= 1));
        if (n <= 1) {
            return -1;
        }

        i = n - 1;
        System.out.println("i = " + i + ", current value of i: " + i);
        System.out.println("Evaluating if condition: i > 1 is evaluated as: " + (i > 1));
        while (i > 1) {
            System.out.println("Entering loop with condition: i > 1 is evaluated as: true");

            System.out.println("Evaluating if condition: n % i == 0 is evaluated as: " + (n % i == 0));
            if (n % i == 0) {
                return_value = i;
                System.out.println("return_value = " + return_value + ", current value of return_value: " + return_value);
                System.out.println("Return statement executed, current value of return_value: " + return_value);
                return i;
            }

            i = i - 1;
            System.out.println("i = " + i + ", current value of i: " + i);
            System.out.println("Evaluating if condition: i > 1 is evaluated as: " + (i > 1));
        }
        System.out.println("Exiting loop, condition no longer holds: i > 1 is evaluated as: false");

        return_value = -1;
        System.out.println("return_value = " + return_value + ", current value of return_value: " + return_value);
        return return_value;
    }

    public static void main(String[] args) {
        int result = largestProperDivisor(10);
        System.out.println("RETURN_VALUE: largestProperDivisor() = " + result);
    }
}
