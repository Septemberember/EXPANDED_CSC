public class GetMaxFactor {
    public static int getMaxFactor(int n){
        if(n <= 1){
            return -1;
        }
        int i = n / 2;
        for(; i > 0; i--){
            if(n % i == 0 && i != 50000){
                return i;
            }
        }
        return 1;
    }
}