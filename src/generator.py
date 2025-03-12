"""
CNC Machine Warmup Generator - Generator Script
Author: John Germing
Date: 2025-03-08
Description: Function(s) for generating Heidenhain TNC640 and Fanuc 31i 
             controller CNC warmup G-code.
"""

def generate_gcode_heidenhain(machine, start_rpm, finish_rpm, start_feed, finish_feed, coolant, tool_call_num, increment_steps):
    """ Generates Heidenhain TNC640-compatible G-code using variables for machine warmup. """
    gcode = []
    
    # Start Warmup Program
    gcode.append("BEGIN PGM WARMUP MM")

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
    gcode.append(f"Q85 = {increment_steps} ; Feedrate/spindle RPM ramp-up per move. Increase for more gradual ramp-up.")
    gcode.append(f"Q96 = {tool_call_num} ; Tool Call Number")
    gcode.append("; =================================")
    gcode.append("; Uneditable Warmup Variables For Program:")
    gcode.append("Q86 = (Q81 - Q80) / 4 ; Spindle RPM divided into # of moves")
    gcode.append("Q87 = (Q83 - Q82) / 4 ; Feedrate divided into # of moves")
    
    gcode.append("Q88 = Q78 / Q85 ; X-Axis increment per step")
    gcode.append("Q89 = Q79 / Q85 ; Y-Axis increment per step")
    gcode.append("Q90 = Q86 / Q85 ; Spindle RPM increment per step")
    gcode.append("Q91 = Q87 / Q85 ; Feedrate increment per step")

    gcode.append("Q92 = 0 ; Current X position")
    gcode.append("Q93 = 0 ; Current Y position")
    gcode.append("Q94 = Q80 ; Current Spindle RPM")
    gcode.append("Q95 = Q82 ; Current Feedrate")
    gcode.append("; =================================\n")

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
    gcode.append("L X+Q92 Y+0 R0 F+Q95 ; Move to X max and Y 0 while ramping up feedrate")
    gcode.append("IF Q92 = Q78 GOTO LBL2 ; If X-axis reaches Q78, end incrementing")
    gcode.append("CALL LBL 1 REP Q85 ; Repeat incrementing loop Q85 times")
    gcode.append("LBL 2 ; End incrementing from X+0 -> X+Q78")

    # Gradually continue increasing spindle RPM/feedrate (Y+0 -> Y+Q79)
    gcode.append("LBL 3 ; Move from Y+0 -> Y+Q79")
    gcode.append("Q93 = Q93 + Q89 ; Increment Y-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+Q78 Y+Q93 R0 F+Q95 ; Move to X max and Y max while ramping up feedrate")
    gcode.append("IF Q93 = Q79 GOTO LBL4 ; If Y-axis reaches Q79, end incrementing")
    gcode.append("CALL LBL 3 REP Q85 ; Repeat incrementing loop Q85 times")
    gcode.append("LBL 4 ; End incrementing from Y+0 -> Y+Q79")

    # Gradually continue increasing spindle RPM/feedrate (X+Q78 -> Y+0)
    gcode.append("LBL 5 ; Move from X+Q78 -> X+0")
    gcode.append("Q92 = Q92 - Q88 ; Decrement X-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+Q92 Y+Q79 R0 F+Q95; Return to X0 with Y max while ramping up feedrate")
    gcode.append("IF Q92 = 0 GOTO LBL6 ; If X-axis reaches 0, end incrementing")
    gcode.append("CALL LBL 5 REP Q85; Repeat incrementing loop Q85 times")
    gcode.append("LBL 6 ; End incrementing from X+Q78 -> X+0")

    # Gradually continue increasing spindle RPM/feedrate (Y+Q79 -> Y+0)
    gcode.append("LBL 7 ; Move from Y+Q79 -> Y+0")
    gcode.append("Q93 = Q93 - Q89 ; Decrement Y-axis")
    gcode.append("Q94 = Q94 + Q90 ; Increment Spindle RPM")
    gcode.append("Q95 = Q95 + Q91 ; Increment Feedrate")

    gcode.append("S+Q94 M3 ; Gradually increasing spindle RPM")
    gcode.append("L X+0 Y+Q93 R0 F+Q95 ; Return to Y0 with X0 while ramping up feedrate")
    gcode.append("IF Q93 LT 1 GOTO LBL8 ; If Y-axis reaches 0, end incrementing")
    gcode.append("CALL LBL 7 REP Q85 ; Repeat incrementing loop Q85 times")
    gcode.append("LBL 8 ; End incrementing from Y+Q79 -> Y+0")

    # Final origin position (X0 Y0) with finish feedrate and spindle RPM
    gcode.append("L X0 Y0 R0 F+Q83 ; Return to origin")
    gcode.append("S+Q81 M3 ; Final spindle speed Q81 RPM")
    
    # Stop Spindle
    gcode.append("M5 ; Spindle OFF")

    # Turn OFF Coolant AFTER Stopping the Spindle
    gcode.append("M9 ; Coolant OFF")

    # End program
    gcode.append("END PGM WARMUP MM")

    return "\n".join(gcode)

def generate_gcode_fanuc(machine, start_rpm, finish_rpm, start_feed, finish_feed, coolant, tool_call_num, increment_steps):
    """ Generates Fanuc R31i-compatible G-code using variables for machine warmup. """
    gcode = []
    # Start Warmup Program
    gcode.append("% ( Fanuc CNC Warmup Program - START )")
    gcode.append("O4321 ( Program Number )")

    gcode.append("( ============================= )")
    gcode.append("( Editable Warmup Parameters )")
    
    gcode.append(f"#78 = {machine['X']} ( X-Axis Travel Limit )")
    gcode.append(f"#79 = {machine['Y']} ( Y-Axis Travel Limit )")
    gcode.append(f"#80 = {start_rpm} ( Start Spindle RPM )")
    gcode.append(f"#81 = {finish_rpm} ( Finish Spindle RPM )")
    gcode.append(f"#82 = {start_feed} ( Start Feedrate (mm/min) )")
    gcode.append(f"#83 = {finish_feed} ( Finish Feedrate (mm/min) )")
    gcode.append(f"#84 = {1 if coolant else 0} ( Coolant (1 = ON, 0 = OFF) )")
    gcode.append(f"#85 = {increment_steps} ( Feedrate/spindle RPM ramp-up per move )")
    gcode.append(f"#96 = {tool_call_num} ( Tool Call Number )")
    gcode.append("( ============================= )")

    gcode.append("( Uneditable Warmup Variables )")
    gcode.append("#86 = (#81 - #80) / 4 ( Spindle RPM divided into # of moves )")
    gcode.append("#87 = (#83 - #82) / 4 ( Feedrate divided into # of moves )")

    gcode.append("#88 = #78 / #85 ( X-Axis increment per step )")
    gcode.append("#89 = #79 / #85 ( Y-Axis increment per step )")
    gcode.append("#90 = #86 / #85 ( Spindle RPM increment per step )")
    gcode.append("#91 = #87 / #85 ( Feedrate increment per step )")

    gcode.append("#92 = 0 ( Current X position )")
    gcode.append("#93 = 0 ( Current Y position )")
    gcode.append("#94 = #80 ( Current Spindle RPM )")
    gcode.append("#95 = #82 ( Current Feedrate )")

    gcode.append("( ============================= )")

    # Safety Block
    gcode.append("G21 G17 G90 ( Metric Mode, XY Plane, Absolute Positioning )")

    # Define tool and start Spindle
    gcode.append("T#96 M06 ( Call defined tool )")
    gcode.append("S#80 M3 ( Start spindle at #80 RPM )")

    # Move to safe Z height before resetting offsets
    gcode.append("G43 Z200 H#96 ( Move to safe Z height )")

    # Reset offsets to 0
    gcode.append("G92 X0 Y0 Z0 ( Set program zero offsets )")

    # Enable Coolant BEFORE spindle ramp-up
    gcode.append("IF [#84 EQ 1] THEN M8 ( Coolant ON before spindle ramp-up )")

    # Gradual X-Axis Movement & Feedrate/Spindle Speed Ramp-Up (X0 -> X#92)
    gcode.append("( Gradually ramp-up feedrate/spindle rpm while traveling Z-Axis )")
    gcode.append("WHILE [#92 LT #78] DO1 ( Loop till #92 >= #78 )")
    gcode.append("  #92 = #92 + #88 ( Increment X-axis )")
    gcode.append("  #94 = #94 + #90 ( Increment Spindle RPM )")
    gcode.append("  #95 = #95 + #91 ( Increment Feedrate )")
    gcode.append("  S#94 M3 ( Gradually increase Spindle RPM )")
    gcode.append("  G1 X#92 Y0 F#95 ( Move from X0 to X#78 while ramping up feedrate )")
    gcode.append("END1 ( End of loop )")

    # Gradual Y-Axis Movement & Feedrate/Spindle Speed Ramp-Up (Y0 -> Y#93)
    gcode.append("( Gradually ramp-up feedrate/spindle rpm while traveling Y-Axis )")
    gcode.append("WHILE [#93 LT #79] DO1 ( Loop till #93 >= #79 )")
    gcode.append("  #93 = #93 + #89 ( Increment Y-axis )")
    gcode.append("  #94 = #94 + #90 ( Increment Spindle RPM )")
    gcode.append("  #95 = #95 + #91 ( Increment Feedrate )")
    gcode.append("  S#94 M3 ( Gradually increase Spindle RPM )")
    gcode.append("  G1 X#78 Y#93 F#95 ( Move from Y0 to Y#79 while ramping up feedrate )")
    gcode.append("END1 ( End of loop )")

    # Gradual X-Axis Movement & Feedrate/Spindle Speed Ramp-Up (X#92 -> X0)
    gcode.append("( Gradually ramp-up feedrate/spindle rpm while traveling Z-Axis )")
    gcode.append("WHILE [#92 GT 0] DO1 ( Loop till #92 <= 0 )")
    gcode.append("  #92 = #92 - #88 ( Decrement X-axis )")
    gcode.append("  #94 = #94 + #90 ( Increment Spindle RPM )")
    gcode.append("  #95 = #95 + #91 ( Increment Feedrate )")
    gcode.append("  S#94 M3 ( Gradually increase Spindle RPM )")
    gcode.append("  G1 X#92 Y#79 F#95 ( Move from X#78 to X0 while ramping up feedrate )")
    gcode.append("END1 ( End of loop )")

    # Gradual Y-Axis Movement & Feedrate/Spindle Speed Ramp-Up (Y#93 -> Y0)
    gcode.append("( Gradually ramp-up feedrate/spindle rpm while traveling Y-Axis )")
    gcode.append("WHILE [#93 GT 0] DO1 ( Loop till #93 <= 0 )")
    gcode.append("  #93 = #93 - #89 ( Decrement Y-axis )")
    gcode.append("  #94 = #94 + #90 ( Increment Spindle RPM )")
    gcode.append("  #95 = #95 + #91 ( Increment Feedrate )")
    gcode.append("  S#94 M3 ( Gradually increase Spindle RPM )")
    gcode.append("  G1 X0 Y#93 F#95 ( Move from Y#79 to Y0 while ramping up feedrate )")
    gcode.append("END1 ( End of loop )")

    # Final Move to Origin
    gcode.append("G1 X0 Y0 F#83 ( Final origin position with max feedrate )")
    gcode.append("S#81 M3 ( Final spindle RPM )")

    # Turn OFF Coolant & Spindle
    gcode.append("M5 ( Spindle OFF )")
    gcode.append("M9 ( Coolant OFF )")
    
    # End Program
    gcode.append("M30 ( End Program - Restart )")

    gcode.append("% ( Fanuc CNC Warmup Program - END )")

    return "\n".join(gcode)