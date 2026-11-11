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
public class D4jArrayLastIndex_M1 {
 public static int test(int a, int b, int c, int key, int startIndex) {
if (a <= 0 || a > 4 || b < 0 || b > 4 || c < 0 || c > 4 || key < 0 || key > 4 || startIndex < -1 || startIndex > 4) { return -99; }
int start = startIndex;
if (start < 0) { return -1; } else { if (start >= 3) { start = 2; } }
int i = start;
while (i >= 0) {
 int value = a;
 if (i == 1) { value = b; }
 if (i == 2) { value = c; }
 if (key == value) { return i; }
 i = i - 1;
}
return -1;
 }
}
