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
public class SpfTreeSearch {
    public static int test(int left, int root, int right, int key) {
        if (left < 0 || root <= left || right <= root || right > 9 || key < 0 || key > 9) { return -1; }
int current = 0;
while (current >= 0) {
 int value = root;
 if (current == 1) { value = left; }
 if (current == 2) { value = right; }
 if (value == key) { return 1; }
 if (key < value) {
  if (current == 0) { current = 1; } else { current = -1; }
 } else {
  if (current == 0) { current = 2; } else { current = -1; }
 }
}
return 0;
    }
}
