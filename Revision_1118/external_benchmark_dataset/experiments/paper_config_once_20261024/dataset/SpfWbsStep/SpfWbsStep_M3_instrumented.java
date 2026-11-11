public class SpfWbsStep_M3 {

    public static int test(int PedalPos, boolean AutoBrake, boolean Skid, int prevMode, int prevCommand, int prevPressure) {
        System.out.println("Function input int parameter prevPressure = " + (prevPressure));
        System.out.println("Function input int parameter prevCommand = " + (prevCommand));
        System.out.println("Function input int parameter prevMode = " + (prevMode));
        System.out.println("Function input boolean parameter Skid = " + (Skid));
        System.out.println("Function input boolean parameter AutoBrake = " + (AutoBrake));
        System.out.println("Function input int parameter PedalPos = " + (PedalPos));
        if (csc.bridge.CSCTrace.cond(21, "if", 1, "PedalPos < 0", PedalPos < 0) || csc.bridge.CSCTrace.cond(21, "if", 2, "PedalPos > 4", PedalPos > 4) || csc.bridge.CSCTrace.cond(21, "if", 3, "prevMode < 0", prevMode < 0) || csc.bridge.CSCTrace.cond(21, "if", 4, "prevMode > 1", prevMode > 1) || csc.bridge.CSCTrace.cond(21, "if", 5, "prevCommand < 0", prevCommand < 0) || csc.bridge.CSCTrace.cond(21, "if", 6, "prevCommand > 4", prevCommand > 4) || csc.bridge.CSCTrace.cond(21, "if", 7, "prevPressure < 0", prevPressure < 0) || csc.bridge.CSCTrace.cond(21, "if", 8, "prevPressure > 5", prevPressure > 5)) {
            return csc.bridge.CSCTrace.retObject(21, "return_value", "-1", -1);
        }
        int Nor_Pressure = csc.bridge.CSCTrace.assignObject(22, "var_decl", "Nor_Pressure", "0", 0);
        int Alt_Pressure = csc.bridge.CSCTrace.assignObject(22, "var_decl", "Alt_Pressure", "0", 0);
        int Sys_Mode = csc.bridge.CSCTrace.assignObject(22, "var_decl", "Sys_Mode", "0", 0);
        int WBS_Node_WBS_AS_MeterValve_Switch;
        int WBS_Node_WBS_AccumulatorValve_Switch;
        int WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch;
        boolean WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator;
        int WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1;
        int WBS_Node_WBS_BSCU_Command_Switch;
        boolean WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6;
        int WBS_Node_WBS_BSCU_SystemModeSelCmd_Unit_Delay;
        int WBS_Node_WBS_BSCU_Switch2;
        int WBS_Node_WBS_BSCU_Switch3;
        int WBS_Node_WBS_BSCU_Unit_Delay1;
        int WBS_Node_WBS_Green_Pump_IsolationValve_Switch;
        int WBS_Node_WBS_SelectorValve_Switch;
        int WBS_Node_WBS_SelectorValve_Switch1;
        int WBS_Node_WBS_Unit_Delay2;
        WBS_Node_WBS_Unit_Delay2 = csc.bridge.CSCTrace.assignObject(40, "assign", "WBS_Node_WBS_Unit_Delay2", "prevPressure", prevPressure);
        WBS_Node_WBS_BSCU_Unit_Delay1 = csc.bridge.CSCTrace.assignObject(41, "assign", "WBS_Node_WBS_BSCU_Unit_Delay1", "prevCommand", prevCommand);
        WBS_Node_WBS_BSCU_SystemModeSelCmd_Unit_Delay = csc.bridge.CSCTrace.assignObject(42, "assign", "WBS_Node_WBS_BSCU_SystemModeSelCmd_Unit_Delay", "prevMode", prevMode);
        WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator = csc.bridge.CSCTrace.assignObject(44, "assign", "WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator", "(WBS_Node_WBS_BSCU_SystemModeSelCmd_Unit_Delay == 0)", (WBS_Node_WBS_BSCU_SystemModeSelCmd_Unit_Delay == 0));
        if ((csc.bridge.CSCTrace.cond(46, "if", 1, "PedalPos == 0", PedalPos == 0))) {
            WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 = csc.bridge.CSCTrace.assignObject(47, "assign", "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1", "0", 0);
        } else {
            if ((csc.bridge.CSCTrace.cond(49, "if", 1, "PedalPos == 1", PedalPos == 1))) {
                WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 = csc.bridge.CSCTrace.assignObject(50, "assign", "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1", "1", 1);
            } else {
                if ((csc.bridge.CSCTrace.cond(52, "if", 1, "PedalPos == 2", PedalPos == 2))) {
                    WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 = csc.bridge.CSCTrace.assignObject(53, "assign", "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1", "2", 2);
                } else {
                    if ((csc.bridge.CSCTrace.cond(55, "if", 1, "PedalPos == 3", PedalPos == 3))) {
                        WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 = csc.bridge.CSCTrace.assignObject(56, "assign", "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1", "3", 3);
                    } else {
                        if ((csc.bridge.CSCTrace.cond(58, "if", 1, "PedalPos == 4", PedalPos == 4))) {
                            WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 = csc.bridge.CSCTrace.assignObject(59, "assign", "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1", "4", 4);
                        } else {
                            WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 = csc.bridge.CSCTrace.assignObject(61, "assign", "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1", "0", 0);
                        }
                    }
                }
            }
        }
        if ((csc.bridge.CSCTrace.cond(68, "if", 1, "AutoBrake", AutoBrake) || csc.bridge.CSCTrace.cond(69, "if", 2, "WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator", WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator))) {
            WBS_Node_WBS_BSCU_Command_Switch = csc.bridge.CSCTrace.assignObject(70, "assign", "WBS_Node_WBS_BSCU_Command_Switch", "1", 1);
        } else {
            WBS_Node_WBS_BSCU_Command_Switch = csc.bridge.CSCTrace.assignObject(72, "assign", "WBS_Node_WBS_BSCU_Command_Switch", "0", 0);
        }
        WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6 = csc.bridge.CSCTrace.assignObject(75, "assign", "WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6", "((((!(WBS_Node_WBS_BSCU_Unit_Delay1 == 0)) && (WBS_Node_WBS_Unit_Delay2 <= 0)) && WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator) || (!WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator))", ((((!(WBS_Node_WBS_BSCU_Unit_Delay1 == 0)) && (WBS_Node_WBS_Unit_Delay2 <= 0)) && WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator) || (!WBS_Node_WBS_BSCU_Command_Is_Normal_Relational_Operator)));
        if (csc.bridge.CSCTrace.cond(80, "if", 1, "WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6", WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6)) {
            if (csc.bridge.CSCTrace.cond(81, "if", 1, "Skid", Skid))
                WBS_Node_WBS_BSCU_Switch3 = csc.bridge.CSCTrace.assignObject(82, "assign", "WBS_Node_WBS_BSCU_Switch3", "0", 0);
            else
                WBS_Node_WBS_BSCU_Switch3 = csc.bridge.CSCTrace.assignObject(84, "assign", "WBS_Node_WBS_BSCU_Switch3", "4", 4);
        } else {
            WBS_Node_WBS_BSCU_Switch3 = csc.bridge.CSCTrace.assignObject(87, "assign", "WBS_Node_WBS_BSCU_Switch3", "4", 4);
        }
        if (csc.bridge.CSCTrace.cond(90, "if", 1, "WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6", WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6)) {
            WBS_Node_WBS_Green_Pump_IsolationValve_Switch = csc.bridge.CSCTrace.assignObject(91, "assign", "WBS_Node_WBS_Green_Pump_IsolationValve_Switch", "0", 0);
        } else {
            WBS_Node_WBS_Green_Pump_IsolationValve_Switch = csc.bridge.CSCTrace.assignObject(93, "assign", "WBS_Node_WBS_Green_Pump_IsolationValve_Switch", "5", 5);
        }
        if ((csc.bridge.CSCTrace.cond(96, "if", 1, "WBS_Node_WBS_Green_Pump_IsolationValve_Switch >= 1", WBS_Node_WBS_Green_Pump_IsolationValve_Switch >= 1))) {
            WBS_Node_WBS_SelectorValve_Switch1 = csc.bridge.CSCTrace.assignObject(97, "assign", "WBS_Node_WBS_SelectorValve_Switch1", "0", 0);
        } else {
            WBS_Node_WBS_SelectorValve_Switch1 = csc.bridge.CSCTrace.assignObject(100, "assign", "WBS_Node_WBS_SelectorValve_Switch1", "5", 5);
        }
        if ((!csc.bridge.CSCTrace.cond(103, "if", 1, "WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6", WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6))) {
            WBS_Node_WBS_AccumulatorValve_Switch = csc.bridge.CSCTrace.assignObject(104, "assign", "WBS_Node_WBS_AccumulatorValve_Switch", "0", 0);
        } else {
            if ((csc.bridge.CSCTrace.cond(106, "if", 1, "WBS_Node_WBS_SelectorValve_Switch1 >= 1", WBS_Node_WBS_SelectorValve_Switch1 >= 1))) {
                WBS_Node_WBS_AccumulatorValve_Switch = csc.bridge.CSCTrace.assignObject(107, "assign", "WBS_Node_WBS_AccumulatorValve_Switch", "WBS_Node_WBS_SelectorValve_Switch1", WBS_Node_WBS_SelectorValve_Switch1);
            } else {
                WBS_Node_WBS_AccumulatorValve_Switch = csc.bridge.CSCTrace.assignObject(110, "assign", "WBS_Node_WBS_AccumulatorValve_Switch", "5", 5);
            }
        }
        if ((csc.bridge.CSCTrace.cond(114, "if", 1, "WBS_Node_WBS_BSCU_Switch3 == 0", WBS_Node_WBS_BSCU_Switch3 == 0))) {
            WBS_Node_WBS_AS_MeterValve_Switch = csc.bridge.CSCTrace.assignObject(115, "assign", "WBS_Node_WBS_AS_MeterValve_Switch", "0", 0);
        } else {
            if ((csc.bridge.CSCTrace.cond(117, "if", 1, "WBS_Node_WBS_BSCU_Switch3 == 1", WBS_Node_WBS_BSCU_Switch3 == 1))) {
                WBS_Node_WBS_AS_MeterValve_Switch = csc.bridge.CSCTrace.assignObject(118, "assign", "WBS_Node_WBS_AS_MeterValve_Switch", "(WBS_Node_WBS_AccumulatorValve_Switch / 4)", (WBS_Node_WBS_AccumulatorValve_Switch / 4));
            } else {
                if ((csc.bridge.CSCTrace.cond(120, "if", 1, "WBS_Node_WBS_BSCU_Switch3 == 2", WBS_Node_WBS_BSCU_Switch3 == 2))) {
                    WBS_Node_WBS_AS_MeterValve_Switch = csc.bridge.CSCTrace.assignObject(121, "assign", "WBS_Node_WBS_AS_MeterValve_Switch", "(WBS_Node_WBS_AccumulatorValve_Switch / 2)", (WBS_Node_WBS_AccumulatorValve_Switch / 2));
                } else {
                    if ((csc.bridge.CSCTrace.cond(123, "if", 1, "WBS_Node_WBS_BSCU_Switch3 == 3", WBS_Node_WBS_BSCU_Switch3 == 3))) {
                        WBS_Node_WBS_AS_MeterValve_Switch = csc.bridge.CSCTrace.assignObject(124, "assign", "WBS_Node_WBS_AS_MeterValve_Switch", "((WBS_Node_WBS_AccumulatorValve_Switch / 4) * 3)", ((WBS_Node_WBS_AccumulatorValve_Switch / 4) * 3));
                    } else {
                        if ((csc.bridge.CSCTrace.cond(126, "if", 1, "WBS_Node_WBS_BSCU_Switch3 == 4", WBS_Node_WBS_BSCU_Switch3 == 4))) {
                            WBS_Node_WBS_AS_MeterValve_Switch = csc.bridge.CSCTrace.assignObject(127, "assign", "WBS_Node_WBS_AS_MeterValve_Switch", "WBS_Node_WBS_AccumulatorValve_Switch", WBS_Node_WBS_AccumulatorValve_Switch);
                        } else {
                            WBS_Node_WBS_AS_MeterValve_Switch = csc.bridge.CSCTrace.assignObject(129, "assign", "WBS_Node_WBS_AS_MeterValve_Switch", "0", 0);
                        }
                    }
                }
            }
        }
        if (csc.bridge.CSCTrace.cond(136, "if", 1, "Skid", Skid)) {
            WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch = csc.bridge.CSCTrace.assignObject(137, "assign", "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch", "0", 0);
        } else {
            WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch = csc.bridge.CSCTrace.assignObject(139, "assign", "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch", "(WBS_Node_WBS_BSCU_Command_Switch + WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1)", (WBS_Node_WBS_BSCU_Command_Switch + WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1));
        }
        if (csc.bridge.CSCTrace.cond(142, "if", 1, "WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6", WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6)) {
            Sys_Mode = csc.bridge.CSCTrace.assignObject(143, "assign", "Sys_Mode", "1", 1);
        } else {
            Sys_Mode = csc.bridge.CSCTrace.assignObject(145, "assign", "Sys_Mode", "0", 0);
        }
        if (csc.bridge.CSCTrace.cond(148, "if", 1, "WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6", WBS_Node_WBS_BSCU_SystemModeSelCmd_Logical_Operator6)) {
            WBS_Node_WBS_BSCU_Switch2 = csc.bridge.CSCTrace.assignObject(149, "assign", "WBS_Node_WBS_BSCU_Switch2", "0", 0);
        } else {
            if (((csc.bridge.CSCTrace.cond(151, "if", 1, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 0", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 0)) && (csc.bridge.CSCTrace.cond(152, "if", 2, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 1", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 1)))) {
                WBS_Node_WBS_BSCU_Switch2 = csc.bridge.CSCTrace.assignObject(153, "assign", "WBS_Node_WBS_BSCU_Switch2", "0", 0);
            } else {
                if (((csc.bridge.CSCTrace.cond(155, "if", 1, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 1", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 1)) && (csc.bridge.CSCTrace.cond(156, "if", 2, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 2", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 2)))) {
                    WBS_Node_WBS_BSCU_Switch2 = csc.bridge.CSCTrace.assignObject(157, "assign", "WBS_Node_WBS_BSCU_Switch2", "1", 1);
                } else {
                    if (((csc.bridge.CSCTrace.cond(159, "if", 1, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 2", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 2)) && (csc.bridge.CSCTrace.cond(160, "if", 2, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 3", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 3)))) {
                        WBS_Node_WBS_BSCU_Switch2 = csc.bridge.CSCTrace.assignObject(161, "assign", "WBS_Node_WBS_BSCU_Switch2", "2", 2);
                    } else {
                        if (((csc.bridge.CSCTrace.cond(163, "if", 1, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 3", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch >= 3)) && (csc.bridge.CSCTrace.cond(164, "if", 2, "WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 4", WBS_Node_WBS_BSCU_Command_AntiSkidCommand_Normal_Switch < 4)))) {
                            WBS_Node_WBS_BSCU_Switch2 = csc.bridge.CSCTrace.assignObject(165, "assign", "WBS_Node_WBS_BSCU_Switch2", "3", 3);
                        } else {
                            WBS_Node_WBS_BSCU_Switch2 = csc.bridge.CSCTrace.assignObject(167, "assign", "WBS_Node_WBS_BSCU_Switch2", "4", 4);
                        }
                    }
                }
            }
        }
        if ((csc.bridge.CSCTrace.cond(174, "if", 1, "WBS_Node_WBS_Green_Pump_IsolationValve_Switch >= 1", WBS_Node_WBS_Green_Pump_IsolationValve_Switch >= 1))) {
            WBS_Node_WBS_SelectorValve_Switch = csc.bridge.CSCTrace.assignObject(175, "assign", "WBS_Node_WBS_SelectorValve_Switch", "WBS_Node_WBS_Green_Pump_IsolationValve_Switch", WBS_Node_WBS_Green_Pump_IsolationValve_Switch);
        } else {
            WBS_Node_WBS_SelectorValve_Switch = csc.bridge.CSCTrace.assignObject(177, "assign", "WBS_Node_WBS_SelectorValve_Switch", "0", 0);
        }
        if ((csc.bridge.CSCTrace.cond(180, "if", 1, "WBS_Node_WBS_BSCU_Switch2 == 0", WBS_Node_WBS_BSCU_Switch2 == 0))) {
            Nor_Pressure = csc.bridge.CSCTrace.assignObject(181, "assign", "Nor_Pressure", "0", 0);
        } else {
            if ((csc.bridge.CSCTrace.cond(183, "if", 1, "WBS_Node_WBS_BSCU_Switch2 == 1", WBS_Node_WBS_BSCU_Switch2 == 1))) {
                Nor_Pressure = csc.bridge.CSCTrace.assignObject(184, "assign", "Nor_Pressure", "(WBS_Node_WBS_SelectorValve_Switch / 4)", (WBS_Node_WBS_SelectorValve_Switch / 4));
            } else {
                if ((csc.bridge.CSCTrace.cond(186, "if", 1, "WBS_Node_WBS_BSCU_Switch2 == 2", WBS_Node_WBS_BSCU_Switch2 == 2))) {
                    Nor_Pressure = csc.bridge.CSCTrace.assignObject(187, "assign", "Nor_Pressure", "(WBS_Node_WBS_SelectorValve_Switch / 2)", (WBS_Node_WBS_SelectorValve_Switch / 2));
                } else {
                    if ((csc.bridge.CSCTrace.cond(189, "if", 1, "WBS_Node_WBS_BSCU_Switch2 == 3", WBS_Node_WBS_BSCU_Switch2 == 3))) {
                        Nor_Pressure = csc.bridge.CSCTrace.assignObject(190, "assign", "Nor_Pressure", "((WBS_Node_WBS_SelectorValve_Switch / 4) * 3)", ((WBS_Node_WBS_SelectorValve_Switch / 4) * 3));
                    } else {
                        if ((csc.bridge.CSCTrace.cond(192, "if", 1, "WBS_Node_WBS_BSCU_Switch2 == 4", WBS_Node_WBS_BSCU_Switch2 == 4))) {
                            Nor_Pressure = csc.bridge.CSCTrace.assignObject(193, "assign", "Nor_Pressure", "WBS_Node_WBS_SelectorValve_Switch", WBS_Node_WBS_SelectorValve_Switch);
                        } else {
                            Nor_Pressure = csc.bridge.CSCTrace.assignObject(195, "assign", "Nor_Pressure", "0", 0);
                        }
                    }
                }
            }
        }
        if ((csc.bridge.CSCTrace.cond(202, "if", 1, "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 0", WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 0))) {
            Alt_Pressure = csc.bridge.CSCTrace.assignObject(203, "assign", "Alt_Pressure", "0", 0);
        } else {
            if ((csc.bridge.CSCTrace.cond(205, "if", 1, "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 1", WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 1))) {
                Alt_Pressure = csc.bridge.CSCTrace.assignObject(206, "assign", "Alt_Pressure", "(WBS_Node_WBS_AS_MeterValve_Switch / 4)", (WBS_Node_WBS_AS_MeterValve_Switch / 4));
            } else {
                if ((csc.bridge.CSCTrace.cond(208, "if", 1, "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 2", WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 2))) {
                    Alt_Pressure = csc.bridge.CSCTrace.assignObject(209, "assign", "Alt_Pressure", "(WBS_Node_WBS_AS_MeterValve_Switch / 2)", (WBS_Node_WBS_AS_MeterValve_Switch / 2));
                } else {
                    if ((csc.bridge.CSCTrace.cond(211, "if", 1, "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 3", WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 3))) {
                        Alt_Pressure = csc.bridge.CSCTrace.assignObject(212, "assign", "Alt_Pressure", "((WBS_Node_WBS_AS_MeterValve_Switch / 4) * 3)", ((WBS_Node_WBS_AS_MeterValve_Switch / 4) * 3));
                    } else {
                        if ((csc.bridge.CSCTrace.cond(214, "if", 1, "WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 4", WBS_Node_WBS_BSCU_Command_PedalCommand_Switch1 == 4))) {
                            Alt_Pressure = csc.bridge.CSCTrace.assignObject(215, "assign", "Alt_Pressure", "WBS_Node_WBS_AS_MeterValve_Switch", WBS_Node_WBS_AS_MeterValve_Switch);
                        } else {
                            Alt_Pressure = csc.bridge.CSCTrace.assignObject(217, "assign", "Alt_Pressure", "0", 0);
                        }
                    }
                }
            }
        }
        prevPressure = csc.bridge.CSCTrace.assignObject(224, "assign", "prevPressure", "Nor_Pressure", Nor_Pressure);
        prevCommand = csc.bridge.CSCTrace.assignObject(226, "assign", "prevCommand", "WBS_Node_WBS_BSCU_Switch2", WBS_Node_WBS_BSCU_Switch2);
        prevMode = csc.bridge.CSCTrace.assignObject(228, "assign", "prevMode", "Sys_Mode", Sys_Mode);
        return csc.bridge.CSCTrace.retObject(231, "return_value", "Nor_Pressure + 10 * Alt_Pressure + 100 * Sys_Mode", Nor_Pressure + 10 * Alt_Pressure + 100 * Sys_Mode);
    }
}
