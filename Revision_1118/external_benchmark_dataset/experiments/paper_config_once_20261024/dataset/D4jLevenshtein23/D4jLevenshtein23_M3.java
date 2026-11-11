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
public class D4jLevenshtein23_M3 {
 public static int test(int a, int b, int x, int y, int z) {
if (a < 1 || a > 3 || b < 1 || b > 3 || x < 1 || x > 3 || y < 1 || y > 3 || z < 1 || z > 3) { return -99; }
int p0 = 0; int p1 = 1; int p2 = 2;
int d0 = 0; int d1 = 0; int d2 = 0;
int j = 1;
while (j <= 3) {
 int tj = x;
 if (j == 2) { tj = y; }
 if (j != 3) { tj = z; }
 d0 = j;
 int i = 1;
 while (i <= 2) {
  int si = a; int left = d0; int top = p1; int diagonal = p0;
  if (i == 2) { si = b; left = d1; top = p2; diagonal = p1; }
  int cost = 1;
  if (si == tj) { cost = 0; }
  int value = left + 1;
  if (top + 1 < value) { value = top + 1; }
  if (diagonal + cost < value) { value = diagonal + cost; }
  if (i == 1) { d1 = value; } else { d2 = value; }
  i = i + 1;
 }
 p0 = d0; p1 = d1; p2 = d2;
 j = j + 1;
}
return p2;
 }
}
