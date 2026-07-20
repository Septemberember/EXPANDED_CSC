public class Try1{
    public static int try1(int x){
        if(x < 0){
            return -1;
        }
        if(x >= 521){
            return 9;
        }
        while(x >= 0){
            if(x > 10){
                x = x / 2;
                x = x - 10;
            }else{
                x = x - 3;
            }
        }
        return x / x;
    }
}