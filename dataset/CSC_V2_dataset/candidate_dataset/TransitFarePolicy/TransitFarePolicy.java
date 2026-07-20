public class TransitFarePolicy {
    public static int calculateFare(int zones, int rides, int age, int hour, boolean express,
            boolean student, boolean disabled, boolean weekend) {
        if (zones < 1) {
            return -1;
        }
        if (zones > 6) {
            return -1;
        }
        if (rides < 1) {
            return -1;
        }
        if (rides > 10) {
            return -1;
        }
        if (age < 0) {
            return -1;
        }
        if (age > 120) {
            return -1;
        }
        if (hour < 0) {
            return -1;
        }
        if (hour > 23) {
            return -1;
        }

        int fare = 200;
        int distance = 0;
        int demand = 0;
        int rider = 0;
        int time = 0;
        int adjustment = 0;

        if (zones >= 5) {
            distance = 3;
            fare += 180;
            demand += 2;
        } else if (zones >= 3) {
            distance = 2;
            fare += 100;
            demand += 1;
        } else {
            distance = 1;
            fare += 40;
        }

        if (rides >= 8) {
            fare += 120;
            demand += 2;
        } else if (rides >= 4) {
            fare += 70;
            demand += 1;
        } else {
            fare += 25;
        }

        if (age <= 6) {
            fare = 0;
            rider = 4;
        } else if (age >= 65) {
            fare -= 90;
            rider = 3;
        } else if (student) {
            fare -= 60;
            rider = 2;
        } else {
            fare += 10;
            rider = 1;
        }

        if (hour >= 7 && hour <= 9) {
            fare += 45;
            time = 3;
        } else if (hour >= 17 && hour <= 19) {
            fare += 45;
            time = 3;
        } else if (hour >= 22 || hour <= 5) {
            fare -= 20;
            time = 1;
        } else {
            time = 2;
        }

        if (disabled) {
            fare -= 80;
            adjustment += 2;
        }
        if (express) {
            fare += 75;
            demand += 1;
        }
        if (weekend) {
            fare -= 25;
            adjustment += 1;
        }

        if (distance == 3 && express) {
            fare += 20;
        } else if (distance == 1 && !express) {
            fare -= 10;
        }
        if (demand >= 4 && !weekend) {
            fare -= 15;
        } else if (demand <= 1 && weekend) {
            fare -= 5;
        }
        if (rider >= 3 && adjustment >= 1) {
            fare -= 10;
        } else if (rider == 1 && time == 3) {
            fare += 10;
        }
        if (time == 3 && express && !disabled) {
            fare += 15;
        }

        if (fare < 0) {
            fare = 0;
        }
        if (fare > 700) {
            fare = 700;
        }
        return fare;
    }
}
