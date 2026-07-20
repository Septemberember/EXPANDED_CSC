public class WaterBillCaculator_M4 {
    public static int calcWaterFee(int tons) {
        int n = tons;
        int fee = 0;
        if(tons <= 0){
            return 0;
        }
        if(n >= 30){
           return 5 * n;
        }
        if (n < 3) {
            fee = fee * 3;
        } else if (n < 10) {
            fee = 6 + 4 * (tons - 1);
        } else {
            fee = 34 + 5 * (tons - 9);
        }

        return fee;
    }
}
