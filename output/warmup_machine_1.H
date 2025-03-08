; Heidenhain CNC Warmup Program
; =================================
; Machine Travel: X762 Y508
; Editable Warmup Parameters:
Q80 = 500 ; Start Spindle RPM
Q81 = 3000 ; Finish Spindle RPM
Q82 = 200 ; Start Feedrate (mm/min)
Q83 = 800 ; Finish Feedrate (mm/min)
Q84 = 1 ; Coolant (1 = ON, 0 = OFF)
; =================================

BEGIN PGM WARMUP MM
S+Q80 M3 ; Start spindle at Q80 RPM
L Z50 F+Q82 ; Move to safe Z height
L X0 Y0 F+Q82 ; Move to origin
L X762 Y0 F+Q83 ; Move to max X
L X762 Y508 ; Move to max Y
L X0 Y508 ; Return to Y max at X0
L X0 Y0 ; Return to origin
S+Q81 M3 ; Ramp spindle to Q81 RPM
IF Q84 == 1 THEN M8 ; Coolant ON
M5 ; Spindle OFF
M9 ; Coolant OFF
END PGM WARMUP MM