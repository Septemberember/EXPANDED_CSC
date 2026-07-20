public class ShippingCost {
    public static int calculateShipping(int weight, int distance, boolean express) {
        if (weight <= 0 || distance <= 0) {
            return -1;
        }
        if (weight > 20 || distance > 500) {
            return -1;
        }

        int cost = 5;
        int extraWeight = weight - 1;
        while (extraWeight > 0) {
            if (extraWeight <= 5) {
                cost += 2;
            } else {
                cost += 3;
            }
            extraWeight--;
        }

        int remainingDistance = distance;
        while (remainingDistance > 100) {
            cost += 4;
            remainingDistance -= 100;
        }

        if (express && cost > 0) {
            cost += 8;
        }
        if (cost > 100) {
            return 100;
        }
        return cost;
    }
}
