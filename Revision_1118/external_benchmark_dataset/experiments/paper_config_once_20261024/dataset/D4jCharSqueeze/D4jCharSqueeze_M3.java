/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
// Modified: bounded scalar core; original source retained separately.
public class D4jCharSqueeze_M3 {
 public static int test(int a, int b, int c, int d, int low, int high) {
if (a < 1 || a > 3 || b < 1 || b > 3 || c < 1 || c > 3 || d < 1 || d > 3 || low < 1 || low > 3 || high < 1 || high > 3 || low > high) { return -99; }
int result = 0;
int last = 32;
int i = 0;
while (i < 4) {
 int ch = a;
 if (i == 1) { ch = b; }
 if (i == 2) { ch = c; }
 if (i == 3) { ch = d; }
 if (!(ch == last || i != 0 && ch >= low && ch <= high)) {
  result = result * 10 + ch;
  last = ch;
 }
 i = i + 1;
}
return result;
 }
}
