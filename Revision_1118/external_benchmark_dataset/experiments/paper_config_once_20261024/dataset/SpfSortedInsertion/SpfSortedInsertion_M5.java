/*
 * Copyright (C) 2014, United States Government, as represented by the
 * Administrator of the National Aeronautics and Space Administration.
 * All rights reserved.
 *
 * Symbolic Pathfinder (jpf-symbc) is licensed under the Apache License, 
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 * 
 *        http://www.apache.org/licenses/LICENSE-2.0. 
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 */
// Modified: controlled scalar adaptation; see provenance.md.
public class SpfSortedInsertion_M5 {
    public static int test(int a, int b, int c, int value) {
        if (a < 0 || a > 9 || b < a || b > 9 || c < b || c > 9 || value < 0 || value > 9) { return -1; }
int first = a;
if (value <= first) { return value * 1000 + a * 100 + b * 10 + c; }
int cursor = 1;
int following = b;
while (cursor < 3 && following < value) {
 cursor = cursor + 1;
 if (cursor == 2) { following = c; }
}
if (cursor == 1) { return a * 1000 + value * 100 + b * 10 + c; }
if (cursor == 2) { return (a * 1000 + b * 100 + value * 10 + c) + 1; }
return a * 1000 + b * 100 + c * 10 + value;
    }
}
