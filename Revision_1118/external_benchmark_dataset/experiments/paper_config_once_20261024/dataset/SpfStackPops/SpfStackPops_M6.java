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
public class SpfStackPops_M6 {
    public static int test(int a, int b, int c, int pops) {
        if (a < 0 || a > 9 || b < 0 || b > 9 || c < 0 || c > 9 || pops < 0 || pops > 4) { return -1; }
int depth = 3;
int value = -4;
int i = 0;
while (i < pops) {
 if (depth == 0) { return -2; }
 if (depth == 3) { value = c; }
 if (depth == 2) { value = b; }
 if (depth == 1) { value = a; }
 depth = depth - 1;
 i = i + 1;
}
return value;
    }
}
