public class BoundedHarshadNumber {
    public static int classifyHarshad(int number) {
        if (number < 1 || number > 100) {
            return -1;
        }

        int temp = number;
        int digitSum = 0;
        while (temp > 0) {
            int digit = temp % 10;
            digitSum = digitSum + digit;
            temp = temp / 10;
        }

        if (number % digitSum == 0) {
            return 1;
        }
        return 0;
    }
}
