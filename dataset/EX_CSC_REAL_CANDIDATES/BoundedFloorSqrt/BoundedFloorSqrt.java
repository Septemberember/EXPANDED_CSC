public class BoundedFloorSqrt {
    public static int floorSqrt(int number) {
        if (number < 0 || number > 120) {
            return -1;
        }
        if (number == 0 || number == 1) {
            return number;
        }

        int left = 1;
        int right = number;
        int answer = 0;
        while (left <= right) {
            int mid = left + (right - left) / 2;
            if (mid == number / mid) {
                return mid;
            }
            if (mid < number / mid) {
                answer = mid;
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return answer;
    }
}
