public class BoundedRightmostSetBit {
    public static int rightmostSetBitIndex(int number) {
        if (number < 0 || number > 100) {
            return -2;
        }
        if (number == 0) {
            return -1;
        }

        int index = 0;
        int temp = number;
        while (temp % 2 == 0) {
            temp = temp / 2;
            index = index + 1;
        }
        return index;
    }
}
