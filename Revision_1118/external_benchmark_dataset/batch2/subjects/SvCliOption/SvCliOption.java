/**
 * Validates an Option string.
 *
 * @author John Keyes ( john at integralsource.com )
 * @version $Revision: 680644 $, $Date: 2008-07-29 01:13:48 -0700 (Tue, 29 Jul 2008) $
 * @since 1.1
 */
// Modified: bounded scalar core; original source retained separately.
public class SvCliOption {
 public static int test(int code) {
if (code < 0 || code > 127) { return -99; }
boolean valid = false;
if ((code >= 97 && code <= 122) || (code >= 65 && code <= 90) || code == 95 || code == 46) { valid = true; }
boolean option = false;
if (valid || code == 32 || code == 63 || code == 64) { option = true; }
if (!option) { return -1; }
return 1;
 }
}
