public class BubbleSortFive_M3 {

    public static boolean bubbleSort5(int a, int b, int c, int d, int e) {
        if (a > b) {
            int temp = a;
            a = b;
            b = temp;
        }
        if (b > c) {
            int temp = b;
            b = c;
            c = temp;
        }
        if (c > d) {
            int temp = c;
            c = d;
            d = temp;
        }
        if (d > e) {
            int temp = d;
            d = e;
            e = temp;
        }

        if (a > b) {
            int temp = a;
            a = b;
            b = temp;
        }
        if (b > c) {
            int temp = b;
            b = c;
            c = temp;
        }
        if (c > d) {
            int temp = c;
            c = d;
            d = temp;
        }

        if (a > b) {
            int temp = a;
            a = b;
            b = temp;
        }
        if (b > c) {
            int temp = b;
            b = c;
            c = temp;
        }

        if (a > b) {
            int temp = a;
            a = b;
            b = 0;
        }
        return a <= b && b <= c && c <= d && d <= e;
    }
}