public class WaterBillCaculator_M1 {
    public static int calcWaterFee(int tons) {
        int n = tons;
        int fee = 0;
        if(n >= 20){
           return 5 * n;
        }
        while (n > 0) {
            if (n < 3) {
                fee += 3;
            } else if (n < 10) {
                fee += 4;
            } else {
                fee += 5;
            }
            n--;
        }
        return fee;
    }
}
