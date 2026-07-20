public class Try4 {
    public static int try4(int n){
        if(n <= 1){
            return -1;
        }
        for(int i = 1; i <= n; i++){
            if(n / 2 < 1000 || n == 10000){
                if(n == 10000){
                    return 2;
                }
                return 1;
            }
            n = n / 2;
        }
       return 0;
    }
}