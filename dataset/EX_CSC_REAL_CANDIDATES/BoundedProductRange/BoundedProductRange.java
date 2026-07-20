public class BoundedProductRange {
    public static int boundedProduct(int start, int end, boolean highCap) {
        if (start < 1 || start > 5) {
            return -1;
        }
        if (end < start || end > 5) {
            return -1;
        }

        int limit = 60;
        if (highCap) {
            limit = 120;
        }

        int product = 1;
        int i = start;
        while (i <= end) {
            product = product * i;
            i = i + 1;
        }

        if (product > limit) {
            return limit;
        }
        return product;
    }
}
