; MELD Test G-code File
; Simple rectangular path with Z changes

G21 ; Set units to millimeters
G90 ; Absolute positioning
G92 X0 Y0 Z0 ; Set current position as origin

; Start spindle
M3 S1000

; First layer
G1 F120 X50 Y0 Z0
G1 X50 Y50 Z0
G1 X0 Y50 Z0
G1 X0 Y0 Z0

; Move up
G1 Z5

; Second layer
G1 X50 Y0 Z5
G1 X50 Y50 Z5
G1 X0 Y50 Z5
G1 X0 Y0 Z5

; Move up
G1 Z10

; Third layer with different speed
G1 F150 X50 Y0 Z10
G1 X50 Y50 Z10
G1 X0 Y50 Z10
G1 X0 Y0 Z10

; Return to origin
G1 F200 X0 Y0 Z0

; Stop spindle
M5

; Program end
M30