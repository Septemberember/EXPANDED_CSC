public class CoursePlacement {
    public static int placeStudent(int examScore, int homeworkScore, int projectScore, int absences,
            boolean honorsRequest, boolean transfer, boolean needsSupport, boolean summerTerm) {
        if (examScore < 0 || examScore > 100) {
            return -1;
        }
        if (homeworkScore < 0 || homeworkScore > 100) {
            return -1;
        }
        if (projectScore < 0 || projectScore > 100) {
            return -1;
        }
        if (absences < 0 || absences > 30) {
            return -1;
        }

        int readiness = 12;
        int academic = 0;
        int consistency = 0;
        int caution = 0;
        int combined = 0;

        if (examScore >= 85) {
            academic = 28;
            readiness += 26;
        } else if (examScore >= 60) {
            academic = 16;
            readiness += 15;
        } else {
            academic = 5;
            readiness += 4;
            caution += 2;
        }

        readiness += academic / 3;
        readiness += examScore / 20;

        if (homeworkScore >= 75) {
            consistency = 15;
            readiness += 14;
        } else if (homeworkScore >= 50) {
            consistency = 8;
            readiness += 7;
        } else {
            consistency = 2;
            readiness += 1;
            caution += 2;
        }

        readiness += consistency / 4;
        readiness += homeworkScore / 25;

        if (projectScore >= 75) {
            academic += 14;
            readiness += 12;
        } else if (projectScore >= 45) {
            academic += 7;
            readiness += 5;
        } else {
            readiness += 1;
            caution += 2;
        }

        readiness += projectScore / 25;
        readiness -= absences / 3;

        if (absences <= 5) {
            readiness += 6;
            consistency += 2;
        } else {
            caution += 2;
        }

        if (honorsRequest && !needsSupport) {
            readiness += 5;
        }
        if (transfer || summerTerm) {
            readiness -= 3;
            caution += 1;
        }

        combined = readiness;
        combined += academic / 5;
        combined += consistency / 5;
        combined -= caution * 4;
        combined += examScore / 25;

        if (combined >= 64) {
            return 4;
        }
        if (combined >= 42) {
            return 3;
        }
        if (combined >= 20) {
            return 2;
        }
        return 1;
    }
}
