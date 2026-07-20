public class Try2{
    public static int try2(int x){
        if(x < 0){
            return -1;
        }
        if(x >= 521){
            return 9;
        }
        for(;x > 0; x--){
            if(x > 10){
                x = x / 2;
                x = x - 10;
            }else{
                x = x - 3;
            }
        }
        return x;
    }
}