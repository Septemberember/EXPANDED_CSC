public class AddLoop_M2 {
    public static int AddLoop(int x, int y) {
        if(x < -30 || x > 30 || y < -30 || y > 30) {
            return -1;
        }
        int sum = x;
        if (y > 0) {
            int n = y;
            while (n > 0) {
                sum = sum + 1;
                n = n - 1;
            }
        } else {
            int n = -y;
            while (n > 0) {
                sum = sum - 1;
                n = n - 2;
            }
        }
        return sum;
    }
}