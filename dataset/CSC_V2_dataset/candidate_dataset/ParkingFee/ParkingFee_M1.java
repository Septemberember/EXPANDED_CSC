public class ParkingFee {
    public static int computeFee(int hours, int entryHour, boolean weekend) {
        if (hours <= 0 || hours > 24) {
            return -1;
        }
        if (entryHour < 0 || entryHour >= 23) {
            return -1;
        }

        int fee = 4;
        int extraHours = hours - 1;
        while (extraHours > 0) {
            if (entryHour >= 18 || weekend) {
                fee += 3;
            } else {
                fee += 2;
            }
            extraHours--;
        }

        if (weekend && hours >= 6) {
            fee += 5;
        }
        if (fee > 60) {
            return 60;
        }
        return fee;
    }
}
