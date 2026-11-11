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
public class SpfAbortDecision_M2 {
    public static int test(int altitudeOffset, boolean fired) {
        if (altitudeOffset < -1000 || altitudeOffset > 1000) { return -1; }
int failure = 0;
int state = 0;
boolean selected = false;
if ((!fired) == false) { failure = 10; }
if (altitudeOffset <= 0) {
 if (fired) { state = 1; } else { state = 2; }
 selected = true;
}
if (altitudeOffset >= 0) {
 if (selected) { return -2; }
 state = 3;
 selected = true;
}
return failure + state;
    }
}
