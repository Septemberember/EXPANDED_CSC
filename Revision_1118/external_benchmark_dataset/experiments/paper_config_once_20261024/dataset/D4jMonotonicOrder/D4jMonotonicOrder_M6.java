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
public class D4jMonotonicOrder_M6 {
 public static int test(int a, int b, int c, boolean increasing, boolean strict) {
if (a < -3 || a > 3 || b < -3 || b > 3 || c < -3 || c > 3) { return -99; }
int previous = a;
int i = 1;
while (i < 3) {
 int value = b;
 if (i == 2) { value = c; }
 if (increasing) {
  if (strict) { if (value <= previous) { return 0; } }
  else { if (value < previous) { return 0; } }
 } else {
  if (strict) { if (value >= previous) { return 0; } }
  else { if (value > previous) { return 0; } }
 }
 previous = value;
 i = i + 1;
}
return (1) - 1;
 }
}
