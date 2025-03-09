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
    gcode.append("Q85 = (Q81 - Q80) / 6 ; Spindle speed increment per step")
    gcode.append("; =================================\n")

    # Start Program
    gcode.append("BEGIN PGM WARMUP MM")
    
    # Spindle Warmup (Start at low RPM)
    gcode.append(f"S+Q80 M3 ; Start spindle at Q80 RPM")
    gcode.append("L Z200 F+Q82 ; Move to safe Z height")
    
    # Move through travel limits (without coolant + incrementing spindle speed)
    gcode.append("S+(Q80 + Q85) M3 ; Increase by Q85 step 1")
    gcode.append("L X0 Y0 F+Q82 ; Move to origin")

    # Enable Coolant BEFORE Full-Speed Spindle Operation
    gcode.append("IF Q84 == 1 THEN M8 ; Coolant ON before spindle ramp-up")

    # Continue navigating travel limits while increasing spindle speed
    gcode.append("S+(Q80 + (Q85 * 2)) M3 ; Increase by Q85 step 2")
    gcode.append(f"L X{machine['X']} Y0 F+Q83 ; Move to max X")
    gcode.append("S+(Q80 + (Q85 * 3)) M3 ; Increase by Q85 step 3")
    gcode.append(f"L X{machine['X']} Y{machine['Y']} ; Move to max Y")
    gcode.append("S+(Q80 + (Q85 * 4)) M3 ; Increase by Q85 step 4")
    gcode.append(f"L X0 Y{machine['Y']} ; Return to Y max at X0")
    gcode.append("S+(Q80 + (Q85 * 5)) M3 ; Increase by Q85 step 5")
    gcode.append("L X0 Y0 F+Q83 ; Return to origin")
    gcode.append("S+Q81 M3 ; Final spindle speed Q81 RPM")

    # Turn OFF Coolant BEFORE Stopping the Spindle
    gcode.append("M9 ; Coolant OFF before spindle stop")
    
    # Stop Spindle
    gcode.append("M5 ; Spindle OFF")

    # End program
    gcode.append("END PGM WARMUP MM")

    return "\n".join(gcode)


def generate_gcode_fanuc(machine, start_rpm, finish_rpm, start_feed, finish_feed, coolant):
    """ Generates Fanuc 31i-compatible G-code using variable storage and coolant activation. """
    gcode = []
    gcode.append("( Fanuc CNC Warmup Program )")
    gcode.append("( ============================= )")
    gcode.append(f"( Machine Travel: X{machine['X']} Y{machine['Y']} )")
    gcode.append("( Editable Warmup Parameters )")
    gcode.append(f"#80 = {start_rpm}   ( Start Spindle RPM )")
    gcode.append(f"#81 = {finish_rpm}   ( Finish Spindle RPM )")
    gcode.append(f"#82 = {start_feed}   ( Start Feedrate (mm/min) )")
    gcode.append(f"#83 = {finish_feed}   ( Finish Feedrate (mm/min) )")
    gcode.append(f"#84 = {1 if coolant else 0}   ( Coolant (1 = ON, 0 = OFF) )")
    gcode.append("#85 = (#81 - #80) / 6   ( Spindle speed increment per step )")
    gcode.append("( ============================= )\n")

    # Start Program
    gcode.append("O1000 ( Warmup Program )")
    gcode.append("G21 G17 G90 ( Set to metric, XY plane, absolute positioning )")

    # Spindle Warmup
    gcode.append("S#80 M3 ( Start spindle at #80 RPM )")
    gcode.append("G0 Z200 ( Move to safe Z height )")

    # Move through travel limits (without coolant + incrementing spindle speed)
    gcode.append("S[#80 + #85] M3 ( Increase by #85 step 1 )")
    gcode.append("G1 X0 Y0 F#82 ( Move to origin )")

    # Enable Coolant BEFORE Full-Speed Spindle Operation
    gcode.append("IF [#84 EQ 1] THEN M8 ( Coolant ON before spindle ramp-up )")

    # Continue navigating travel limits while increasing spindle speed
    gcode.append("S[#80 + (#85 * 2)] M3 ( Increase by #85 step 2 )")
    gcode.append(f"G1 X{machine['X']} Y0 F#83 ( Move to max X )")
    gcode.append("S[#80 + (#85 * 3)] M3 ( Increase by #85 step 3 )")
    gcode.append(f"G1 X{machine['X']} Y{machine['Y']} ( Move to max Y )")
    gcode.append("S[#80 + (#85 * 4)] M3 ( Increase by #85 step 4 )")
    gcode.append(f"G1 X0 Y{machine['Y']} ( Return to Y max at X0 )")
    gcode.append("S[#80 + (#85 * 5)] M3 ( Increase by #85 step 5 )")
    gcode.append("G1 X0 Y0 F#83 ( Return to origin )")
    gcode.append("S#81 M3 ( Final spindle speed #81 RPM )")

    # Turn OFF Coolant BEFORE Stopping the Spindle
    gcode.append("M9 ( Coolant OFF before spindle stop )")

    # Stop Spindle
    gcode.append("M5 ( Spindle OFF )")

    # End Program
    gcode.append("M30 ( End of Program )")

    return "\n".join(gcode)