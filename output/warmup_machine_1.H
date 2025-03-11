; Heidenhain CNC Warmup Program
; =================================
; Editable Warmup Parameters:
Q78 = 762 ; X-Axis Travel Limit
Q79 = 508 ; Y-Axis Travel Limit
Q80 = 500 ; Start Spindle RPM
Q81 = 3000 ; Finish Spindle RPM
Q82 = 200 ; Start Feedrate (mm/min)
Q83 = 800 ; Finish Feedrate (mm/min)
Q84 = 1 ; Coolant (1 = ON, 0 = OFF)
Q85 = 15 ; Feedrate/spindle RPM ramp-up per move. Increase for more gradual ramp-up.
Q96 = 1 ; Tool Call Number
; =================================
; Uneditable Warmup Variables For Program:
Q86 = (Q81 - Q80) / 5 ; Spindle RPM divided into # of moves
Q87 = (Q83 - Q82) / 5 ; Feedrate divided into # of moves
Q88 = Q78 / Q85 ; X-Axis increment per step
Q89 = Q79 / Q85 ; Y-Axis increment per step
Q90 = (Q81 - Q80) / Q85 ; Spindle RPM increment per step
Q91 = (Q83 - Q82) / Q85 ; Feedrate increment per step
Q92 = 0 ; Current X position
Q93 = 0 ; Current Y position
Q94 = Q80 ; Current Spindle RPM
Q95 = Q82 ; Current Feedrate
; =================================

BEGIN PGM WARMUP MM
; Safe startup regardless of current position, origin table, or tool offsets
TOOL CALL Q96 Z S+Q80 ; Call defined tool #
L R0 ; Reset tool radius compensation
S+0 M3 ; Start spindle at Q80 RPM
L Z+200 F+Q82 ; Retract the tool. Move to safe Z height
CYCL DEF 7.0 DATUM SHIFT ; Reset active datum shift
CYCL DEF 7.1 X+0 ; Reset X datum to 0
CYCL DEF 7.2 Y+0 ; Reset Y datum to 0
CYCL DEF 7.3 Z+0 ; Reset Z datum to 0
TRANS DATUM RESET ; Reset any active datum shifts/origin tables
S+Q80 M3 ; Start spindle at Q80 RPM
L X+0 Y+0 R0 F+Q82 ; Move to origin
IF Q84 == 1 THEN M8 ; Coolant ON before spindle ramp-up
LBL 1 ; Move from X+0 -> X+Q78
Q92 = Q92 + Q88 ; Increment X-axis
Q94 = Q94 + Q90 ; Increment Spindle RPM
Q95 = Q95 + Q91 ; Increment Feedrate
S+Q94 M3 ; Gradually increasing spindle RPM
L X+Q92 Y+0 R0 F+Q95 ; Move to incremented X while ramping up feedrate
IF Q92 = Q78 GOTO LBL2 ; If X-axis reaches Q78, end incrementing
CALL LBL 1 REP Q85 ; Repeat incrementing loop Q85 times
LBL 2 ; End incrementing from X+0 -> X+Q78
LBL 3 ; Move from Y+0 -> Y+Q79
Q93 = Q93 + Q89 ; Increment Y-axis
Q94 = Q94 + Q90 ; Increment Spindle RPM
Q95 = Q95 + Q91 ; Increment Feedrate
S+Q94 M3 ; Gradually increasing spindle RPM
L X+Q78 Y+Q93 R0 F+Q95 ; Move to incremented Y while ramping up feedrate
IF Q93 = Q79 GOTO LBL4 ; If Y-axis reaches Q79, end incrementing
CALL LBL 3 REP Q85 ; Repeat incrementing loop Q85 times
LBL 4 ; End incrementing from Y+0 -> Y+Q79
LBL 5 ; Move from X+Q78 -> X+0
Q92 = Q92 - Q88 ; Decrement X-axis
Q94 = Q94 + Q90 ; Increment Spindle RPM
Q95 = Q95 + Q91 ; Increment Feedrate
S+Q94 M3 ; Gradually increasing spindle RPM
L X+Q92 Y+Q79 R0 F+Q95; Return to X0 with Y max
IF Q92 = 0 GOTO LBL6 ; If X-axis reaches 0, end incrementing
CALL LBL 5 REP Q85; Repeat incrementing loop Q85 times
LBL 6 ; End incrementing from X+Q78 -> X+0
LBL 7 ; Move from Y+Q79 -> Y+0
Q93 = Q93 - Q89 ; Decrement Y-axis
Q94 = Q94 + Q90 ; Increment Spindle RPM
Q95 = Q95 + Q91 ; Increment Feedrate
S+Q94 M3 ; Gradually increasing spindle RPM
L X+0 Y+Q93 R0 F+Q95 ; Return to Y0 with X0
IF Q93 LT 1 GOTO LBL8 ; If Y-axis reaches 0, end incrementing
CALL LBL 7 REP Q85 ; Repeat incrementing loop Q85 times
LBL 8 ; End incrementing from Y+Q79 -> Y+0
L X0 Y0 R0 F+Q83 ; Return to origin
S+Q81 M3 ; Final spindle speed Q81 RPM
M9 ; Coolant OFF before spindle stop
M5 ; Spindle OFF
END PGM WARMUP MM