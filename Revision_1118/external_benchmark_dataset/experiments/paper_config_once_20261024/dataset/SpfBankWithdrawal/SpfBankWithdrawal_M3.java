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
public class SpfBankWithdrawal_M3 {
    public static int test(int balance, int deposit, int amount, int withdrawals) {
        if (balance < 0 || balance > 20 || deposit < -5 || deposit > 10 || amount < -5 || amount > 30 || withdrawals < 0 || withdrawals > 5) { return -1; }
int currentBalance = balance;
if (deposit > 0) { currentBalance = currentBalance + deposit; }
if (amount >= currentBalance) { return currentBalance; }
if (withdrawals >= 5) { return -2; }
currentBalance = currentBalance - amount;
int nextWithdrawals = withdrawals + 1;
return currentBalance;
    }
}
