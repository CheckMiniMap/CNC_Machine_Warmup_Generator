"""
CNC Machine Warmup Generator - Generator Script
Author: John Germing
Date: 2025-03-08
Description: Function(s) for generating Heidenhain TNC640 and Fanuc 31i 
             controller CNC warmup G-code.
"""

def generate_gcode_heidenhain(machine, start_rpm, finish_rpm, start_feed, finish_feed, coolant, tool_call_num):
    """ Generates Heidenhain-compatible G-code using Q-parameters with optimized coolant activation. """
    gcode = []
    gcode.append("; Heidenhain CNC Warmup Program")
    gcode.append("; =================================")
    gcode.append("; Editable Warmup Parameters:")
    gcode.append(f"Q78 = {machine['X']} ; X-Axis Travel Limit")
    gcode.append(f"Q79 = {machine['Y']} ; Y-Axis Travel Limit")
    gcode.append(f"Q80 = {start_rpm} ; Start Spindle RPM")
    gcode.append(f"Q81 = {finish_rpm} ; Finish Spindle RPM")
    gcode.append(f"Q82 = {start_feed} ; Start Feedrate (mm/min)")
    gcode.append(f"Q83 = {finish_feed} ; Finish Feedrate (mm/min)")
    gcode.append(f"Q84 = {1 if coolant else 0} ; Coolant (1 = ON, 0 = OFF)")
    gcode.append("Q85 = 15 ; Feedrate/spindle RPM ramp-up per move. Increase for more gradual ramp-up.")
    gcode.append(f"Q96 = {tool_call_num} ; Tool Call Number")
    gcode.append("; =================================")
    gcode.append("; Uneditable Warmup Variables For Program:")
    gcode.append("Q86 = (Q81 - Q80) / 5 ; Spindle RPM divided into # of moves")
    gcode.append("Q87 = (Q83 - Q82) / 5 ; Feedrate divided into # of moves")
    
    gcode.append("Q88 = Q78 / Q85 ; X-Axis increment per step")
    gcode.append("Q89 = Q79 / Q85 ; Y-Axis increment per step")
    gcode.append("Q90 = (Q81 - Q80) / Q85 ; Spindle RPM increment per step")
    gcode.append("Q91 = (Q83 - Q82) / Q85 ; Feedrate increment per step")

    gcode.append("Q92 = 0 ; Current X position")
    gcode.append("Q93 = 0 ; Current Y position")
    gcode.append("Q94 = Q80 ; Current Spindle RPM")
    gcode.append("Q95 = Q82 ; Current Feedrate")
    gcode.append("; =================================\n")

    # Start Warmup Program
    gcode.append("BEGIN PGM WARMUP MM")

    # Ensure origin table and tool offsets are reset before starting
    gcode.append("; Safe startup regardless of current position, origin table, or tool offsets")
    gcode.append("TOOL CALL Q96 Z S+Q80 ; Call defined tool #")
    gcode.append("L R0 ; Reset tool radius compensation")

    # Spindle Warmup (Start at low RPM)
    gcode.append("S+0 M3 ; Start spindle at Q80 RPM")
    gcode.append("L Z+200 F+Q82 ; Retract the tool. Move to safe Z height")
    gcode.append("CYCL DEF 7.0 DATUM SHIFT ; Reset active datum shift")
    gcode.append("CYCL DEF 7.1 X+0 ; Reset X datum to 0")
    gcode.append("CYCL DEF 7.2 Y+0 ; Reset Y datum to 0")
    gcode.append("CYCL DEF 7.3 Z+0 ; Reset Z datum to 0")
    gcode.append("TRANS DATUM RESET ; Reset any active datum shifts/origin tables")

    # Move to origin (without coolant, start spindle RPM, and start feedrate)
    gcode.append(f"S+Q80 M3 ; Start spindle at Q80 RPM")
    gcode.append("L X+0 Y+0 R0 F+Q82 ; Move to origin")

    # Enable coolant BEFORE gradually ramping up spindle RPM/feedrate
    gcode.append("IF Q84 == 1 THEN M8 ; Coolant ON before spindle ramp-up")

    # Gradually start increasing spindle RPM/feedrate (X+0 -> X+Q78)
    gcode.append("LBL 1 ; Move from X+0 -> X+Q78")
    gcode.append("Q92 = Q92 + Q88 ; Increment X-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+Q92 Y+0 R0 F+Q95 ; Move to incremented X while ramping up feedrate")
    gcode.append("IF Q92 = Q78 GOTO LBL2 ; If X-axis reaches Q78, end incrementing")
    gcode.append("CALL LBL 1 REP Q85 ; Repeat incrementing loop Q85 times")
    gcode.append("LBL 2 ; End incrementing from X+0 -> X+Q78")

    # Gradually continue increasing spindle RPM/feedrate (Y+0 -> Y+Q79)
    gcode.append("LBL 3 ; Move from Y+0 -> Y+Q79")
    gcode.append("Q93 = Q93 + Q89 ; Increment Y-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+Q78 Y+Q93 R0 F+Q95 ; Move to incremented Y while ramping up feedrate")
    gcode.append("IF Q93 = Q79 GOTO LBL4 ; If Y-axis reaches Q79, end incrementing")
    gcode.append("CALL LBL 3 REP Q85 ; Repeat incrementing loop Q85 times")
    gcode.append("LBL 4 ; End incrementing from Y+0 -> Y+Q79")

    # Gradually continue increasing spindle RPM/feedrate (X+Q78 -> Y+0)
    gcode.append("LBL 5 ; Move from X+Q78 -> X+0")
    gcode.append("Q92 = Q92 - Q88 ; Decrement X-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+Q92 Y+Q79 R0 F+Q95; Return to X0 with Y max")
    gcode.append("IF Q92 = 0 GOTO LBL6 ; If X-axis reaches 0, end incrementing")
    gcode.append("CALL LBL 5 REP Q85; Repeat incrementing loop Q85 times")
    gcode.append("LBL 6 ; End incrementing from X+Q78 -> X+0")

    # Gradually continue increasing spindle RPM/feedrate (Y+Q79 -> Y+0)
    gcode.append("LBL 7 ; Move from Y+Q79 -> Y+0")
    gcode.append("Q93 = Q93 - Q89 ; Decrement Y-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+0 Y+Q93 R0 F+Q95 ; Return to Y0 with X0")
    gcode.append("IF Q93 LT 1 GOTO LBL8 ; If Y-axis reaches 0, end incrementing")
    gcode.append("CALL LBL 7 REP Q85 ; Repeat incrementing loop Q85 times")
    gcode.append("LBL 8 ; End incrementing from Y+Q79 -> Y+0")

    # Final origin position (X0 Y0) with finish feedrate and spindle RPM
    gcode.append("L X0 Y0 R0 F+Q83 ; Return to origin")
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