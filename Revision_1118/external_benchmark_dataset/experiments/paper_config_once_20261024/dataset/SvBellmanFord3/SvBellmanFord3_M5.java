/**
 * Type : Functional Safety Expected Verdict : True Last modified by : Zafer Esen
 * <zafer.esen@it.uu.se> Date : 9 October 2019
 *
 * <p>Original license follows.
 */

/**
 * Copyright (c) 2011, Regents of the University of California All rights reserved.
 *
 * <p>Redistribution and use in source and binary forms, with or without modification, are permitted
 * provided that the following conditions are met:
 *
 * <p>1. Redistributions of source code must retain the above copyright notice, this list of
 * conditions and the following disclaimer.
 *
 * <p>2. Redistributions in binary form must reproduce the above copyright notice, this list of
 * conditions and the following disclaimer in the documentation and/or other materials provided with
 * the distribution.
 *
 * <p>3. Neither the name of the University of California, Berkeley nor the names of its
 * contributors may be used to endorse or promote products derived from this software without
 * specific prior written permission.
 *
 * <p>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
 * WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * @author Sudeep Juvekar <sjuvekar@cs.berkeley.edu>
 * @author Jacob Burnim <jburnim@cs.berkeley.edu>
 */

// Modified: bounded scalar core; original source retained separately.
public class SvBellmanFord3_M5 {
 public static int test(int w01, int w02, int w12, int w21) {
if (w01 < 0 || w01 > 4 || w02 < 0 || w02 > 4 || w12 < 0 || w12 > 4 || w21 < 0 || w21 > 4) { return -99; }
int d0 = 0;
int d1 = 2147483647;
int d2 = 2147483647;
int k = 0;
while (k < 3) {
 boolean relaxed = false;
 if (d1 > d0 + w01) { d1 = d0 + w01; relaxed = true; }
 if (d2 > d0 + w02) { d2 = d0 + w02; relaxed = true; }
 if (d0 > d1 + 4) { d0 = d1 + 4; relaxed = true; }
 if (d2 > d1 + w12) { d2 = d1 + w12; relaxed = true; }
 if (d0 > d2 + 4) { d0 = d2 + 4; relaxed = true; }
 if (d1 > d2 + w21) { d1 = d2 - w21; relaxed = true; }
 if (!relaxed) { return d1 * 10 + d2; }
 k = k + 1;
}
return d1 * 10 + d2;
 }
}
