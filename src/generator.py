"""
CNC Machine Warmup Generator - Generator Script
Author: John Germing
Date: 2025-03-08
Description: This script will include function(s) for Heidenhain-compatible 
             CNC warmup G-code.
"""

def generate_gcode(machine, start_rpm, finish_rpm, start_feed, finish_feed, coolant):
    """ Generates Heidenhain-compatible G-code using Q-parameters with optimized coolant activation. """
    gcode = []
    gcode.append("; Heidenhain CNC Warmup Program")
    gcode.append("; =================================")
    gcode.append(f"; Machine Travel: X{machine['X']} Y{machine['Y']}")
    gcode.append("; Editable Warmup Parameters:")
    gcode.append(f"Q80 = {start_rpm} ; Start Spindle RPM")
    gcode.append(f"Q81 = {finish_rpm} ; Finish Spindle RPM")
    gcode.append(f"Q82 = {start_feed} ; Start Feedrate (mm/min)")
    gcode.append(f"Q83 = {finish_feed} ; Finish Feedrate (mm/min)")
    gcode.append(f"Q84 = {1 if coolant else 0} ; Coolant (1 = ON, 0 = OFF)")
    gcode.append("; =================================\n")

    # Start Program
    gcode.append("BEGIN PGM WARMUP MM")
    
    # Spindle Warmup (Start at low RPM)
    gcode.append("S+Q80 M3 ; Start spindle at Q80 RPM")
    gcode.append("L Z50 F+Q82 ; Move to safe Z height")

    # Move through machine travel limits (without coolant)
    gcode.append("L X0 Y0 F+Q82 ; Move to origin")
    gcode.append(f"L X{machine['X']} Y0 F+Q83 ; Move to max X")
    gcode.append(f"L X{machine['X']} Y{machine['Y']} ; Move to max Y")
    gcode.append(f"L X0 Y{machine['Y']} ; Return to Y max at X0")
    gcode.append("L X0 Y0 ; Return to origin")
    
    # Enable Coolant BEFORE Full-Speed Spindle Operation
    gcode.append("IF Q84 == 1 THEN M8 ; Coolant ON before spindle ramp-up")

    # Ramp spindle speed to final value
    gcode.append("S+Q81 M3 ; Ramp spindle to Q81 RPM")

    # Keep Coolant ON for Full-Speed Operation
    gcode.append("L X0 Y0 F+Q83 ; Final movement with full spindle speed")

    # Turn OFF Coolant BEFORE Stopping the Spindle
    gcode.append("M9 ; Coolant OFF before spindle stop")
    
    # Stop Spindle
    gcode.append("M5 ; Spindle OFF")

    # End program
    gcode.append("END PGM WARMUP MM")

    return "\n".join(gcode)
