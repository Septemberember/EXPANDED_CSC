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
public class SpfFlapMotion_M2 {
    public static int test(int goal, int position, boolean emergency) {
        if (goal < 0 || goal > 40 || position < 0 || position > 40) { return -1; }
if ((emergency) == false) { goal = 30; }
int time = 0;
while (position != goal) {
 if (emergency) {
  if (goal > position) { position = position + 10; } else { position = position - 10; }
 } else {
  if (goal > position) { position = position + 1; } else { position = position - 1; }
 }
 time = time + 1;
 if (time > 1) { return -2; }
}
return position;
    }
}
