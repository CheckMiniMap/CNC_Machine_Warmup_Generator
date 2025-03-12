"""
CNC Machine Warmup Generator - Configuration Script
Author: John Germing
Date: 2025-03-08
Description: Stores the configuration/default settings for the CNC machine parameters.
"""

# Created dictionary for machine # configuration settings for X and Y axis travel limits.
MACHINES = {
    "1": {"X": 762, "Y": 508},
    "2": {"X": 1016, "Y": 660},
    "3": {"X": 1270, "Y": 508}
}

# Created dictionary for machine configuration for spindle RPM, feedrate mm/min, and flood coolant activation.
DEFAULT_SETTINGS = {
    "start_rpm": 500,
    "finish_rpm": 3000,
    "start_feedrate": 200,
    "finish_feedrate": 800,
    "coolant": True,
    "tool_call_num": 1,
    "increment_steps": 15,
}