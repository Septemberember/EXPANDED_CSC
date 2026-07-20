public class ShiftBandClassifier {
    public static int classifyShiftBand(int value) {
        if (value < 0 || value > 20) {
            return -1;
        }
        if ((value << 1) > 12) {
            return 1;
        }
        return 0;
    }
}
