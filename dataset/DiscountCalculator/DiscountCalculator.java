public class DiscountCalculator {
    public static int computeDiscount(int price, int customerYears, boolean coupon) {
        if (price < 0 || price > 1000) {
            return -1;
        }
        if (customerYears < 0 || customerYears > 30) {
            return -1;
        }

        int discount = 0;
        if (price >= 500) {
            discount += 50;
        } else if (price >= 200) {
            discount += 20;
        }

        int yearsLeft = customerYears;
        while (yearsLeft > 0) {
            if (yearsLeft >= 5) {
                discount += 2;
                yearsLeft -= 5;
            } else {
                discount += 1;
                yearsLeft = 0;
            }
        }

        if (coupon && price >= 100) {
            discount += 15;
        }
        if (discount > 100) {
            return 100;
        }
        return discount;
    }
}
