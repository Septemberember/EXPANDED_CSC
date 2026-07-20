public class GetLowCaseLoop {
    public static char getLowCase(char c) {
        char t = 'z';
        while(t >= 'f' && t != c - 'A' + 'a') {
            if(c < 'F' || c > 'Z') {
                return '0';
            }
            t--;
        }
        return t;
    }
}