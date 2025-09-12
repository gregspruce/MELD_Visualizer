# MELD Manufacturing G-Code/M-Code Reference

## Core Syntax Rules
- Program: `% ProgramName` (optional) → blocks → `G04 X0.5` → `M30`
- Block: `N<num> <commands>` (N should equal line number)
- Comments: `(text)`
- Variables: `R0-R999` (R10-R128 reserved by system)
- Line endings: LF only (no CRLF)

## G-Commands (Motion/Setup)

### Motion (Modal)
- **G00** `X<> Y<> Z<>`: Rapid traverse (max velocity, non-MELD)
- **G01** `X<> Y<> Z<> F<>`: Linear interpolation at feedrate
- **G02** `X<> Y<> {I<> J<> | U<radius>} F<>`: Clockwise arc
- **G03** `X<> Y<> {I<> J<> | U<radius>} F<>`: Counterclockwise arc

### Control (Non-Modal)
- **G04** `{X<sec> | F<sec>}`: Dwell/pause
- **G09**: Accurate stop (current block)
- **G60**: Modal accurate stop

### Coordinate Systems (Modal)
- **G17**: XY plane (default) | **G18**: ZX plane | **G19**: YZ plane
- **G53**: No offset (default) | **G54-G57**: Work coordinate offsets
- **G90**: Absolute coords (default) | **G91**: Incremental coords

### Units (Modal)
- **G70**: inch/mm·min⁻¹ | **G71**: mm/mm·min⁻¹ | **G700**: inch/inch·min⁻¹ | **G710**: mm/inch·min⁻¹
- Add `G04 X0.5` when changing units without movement

## M-Commands (Machine Functions)

### Timing Types
- **Handshake**: Blocks until complete (max 1 per line)
- **Fast bit**: Immediate execution (max 10 per line)

### Spindle Control (Handshake)
- **M04** `S<rpm>`: Start CCW, wait for setpoint | **M05**: Stop | **M06** `S<rpm>`: Start CCW, no wait

### Coolant/Gas (Fast bit)
- **M08/M09**: Tool cooling on/off | **M10/M11**: Shield gas on/off | **M12/M13**: Table cooling on/off

### Actuator Control (Handshake, units: mil/min or mm/min×10)
- **M20** `S<vel>`: Set position velocity | **M21** `S<pos>`: Set soft limit
- **M22** `S<%>`: Set FRO | **M23** `S<pos>`: Position start | **M24** `S<vel>`: Velocity start | **M25**: Stop

### Advanced Spindle (Handshake)
- **M40** `S<mode>`: PID mode (0=torque, 1=force, 2=K-type, 3=tool temp)
- **M41** `S<val>`: Enable PID with setpoint | **M42** `S<torque>`: Hold until torque | **M43** `S<temp>`: Hold until temp

### Program Control (Handshake)
- **M50/M51**: Save Z/XY coordinates | **M54**: Hold | **M55**: Hold + message | **M56**: Hold + message + unlock
- **M30**: Program end (requires preceding `G04 X0.5`)

## Parameter System

### Variable Operations
```gcode
R<n>=<value>                    # Assignment
R<n>=R<m>+R<p>-<const>*R<q>/<const>  # Math (left-to-right)
@610 R<dest> R<src>             # Absolute value
@620/621 R<n>                   # Increment/decrement
@630-636 R<dest> R<angle>       # Trig functions (degrees)
```

### Reserved Parameters (Read-only)
- **R50-R52**: Last Z,X,Y positions
- **R100-R104**: Spindle (speed cmd, torque, actual speed, power, PID setpoint)
- **R105-R118**: Feed/traverse data (velocity, position, torque, FRO)
- **R119-R128**: Temperatures (spindle upper/lower, K-type 1-4)

## Control Flow

### Jumps
- **@100** `K<±line>`: Unconditional jump
- **@121-126** `R<val1> {K<val2>|R<val2>} K<±line>`: Conditional (≠,=,≤,<,≥,>)

### Loops
- **@131-136** `R<val1> {K<val2>|R<val2>} K<exitline>`: While loops (=,≠,>,≥,<,≤)
- **@141-146** `R<val1> {K<val2>|R<val2>} K<startline>`: Repeat until loops
- **@151/161** `R<counter> {K<limit>|R<limit>} K<startline>`: For/for-down loops

### Subroutines
```gcode
L<number> [P<count>]            # Call subroutine
L=R<param>                      # Dynamic call
L<number>                       # Subroutine label
M17                             # Return
```

## Execution Order (Fixed Sequence)
1. Reference (N*, G17-19, G70-71, G90-91)
2. Configuration (G53-57, F*)
3. M-functions (pre)
4. Parameters (S*)
5. Movement (G00-03)
6. Wait (G04)
7. M-functions (post)

## Example Program Structure
```gcode
% ProgramName
N10 G71 G90 G17                # Setup: mm units, absolute, XY plane
N20 M04 S350                   # Start spindle at 350 RPM
N30 G01 X100 Y50 F6000         # Linear move
N40 G02 X150 Y100 I25 J25 F6000 # Arc move
N50 M05                        # Stop spindle
N60 G04 X0.5                   # Mandatory pause
N70 M30                        # End program
```

## Critical Rules
- One handshake M-function max per line
- Always `G04 X0.5` before `M30`
- Block numbers should match line numbers for HMI
- Math operations process left-to-right
- Trig functions use degrees
- Arc center (I,J,K) relative to start point
