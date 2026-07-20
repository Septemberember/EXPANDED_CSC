public class BoundedAutomorphicNumber {
    public static int classifyAutomorphic(int number) {
        if (number < 0 || number > 99) {
            return -1;
        }

        int square = number * number;
        int temp = number;
        int place = 1;
        if (temp == 0) {
            return 1;
        }

        while (temp > 0) {
            place = place * 10;
            temp = temp / 10;
        }

        int lastDigits = square % place;
        if (lastDigits == number) {
            return 1;
        }
        return 0;
    }
}
