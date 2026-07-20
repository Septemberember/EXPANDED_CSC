public class BoundedSqrtBinarySearch {
    public static int floorSqrt(int num) {
        if (num < 0 || num > 80) {
            return -1;
        }
        if (num == 0 || num == 1) {
            return num;
        }

        int left = 1;
        int right = num;
        int answer = 0;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (mid == num / mid) {
                return mid;
            } else if (mid < num / mid) {
                answer = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return answer;
    }
}
