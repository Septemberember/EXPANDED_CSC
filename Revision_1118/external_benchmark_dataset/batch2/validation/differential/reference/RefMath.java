public class RefMath { public enum OrderDirection {INCREASING, DECREASING}
public static boolean checkOrder(double[] val, OrderDirection dir,
                                     boolean strict, boolean abort)
        throws NonMonotonicSequenceException {
        double previous = val[0];
        final int max = val.length;

        int index;
        ITEM:
        for (index = 1; index < max; index++) {
            switch (dir) {
            case INCREASING:
                if (strict) {
                    if (val[index] <= previous) {
                        break ITEM;
                    }
                } else {
                    if (val[index] < previous) {
                        break ITEM;
                    }
                }
                break;
            case DECREASING:
                if (strict) {
                    if (val[index] >= previous) {
                        break ITEM;
                    }
                } else {
                    if (val[index] > previous) {
                        break ITEM;
                    }
                }
                break;
            default:
                // Should never happen.
                throw new MathInternalError();
            }

            previous = val[index];
        }

        if (index == max) {
            // Loop completed.
            return true;
        }

        // Loop early exit means wrong ordering.
        if (abort) {
            throw new NonMonotonicSequenceException(val[index], previous, index, dir, strict);
        } else {
            return false;
        }
    }
}
class MathInternalError extends RuntimeException {}
class NonMonotonicSequenceException extends RuntimeException { NonMonotonicSequenceException(double v,double p,int i,RefMath.OrderDirection d,boolean s){} }
