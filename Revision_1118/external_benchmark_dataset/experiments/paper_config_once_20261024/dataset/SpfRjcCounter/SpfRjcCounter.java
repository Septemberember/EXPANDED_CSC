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
public class SpfRjcCounter {
    public static int test(int steps) {
        if (steps < 0 || steps > 8) { return -1; }
int active = 1;
int initialized = 0;
int counter = 0;
int i = 0;
while (i < steps) {
 if (initialized == 1) {
  if (active == 1) {
   counter = counter + 1;
   active = -1;
   active = 1;
  }
 }
 initialized = 1;
 i = i + 1;
}
return counter;
    }
}
