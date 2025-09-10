# MELD Programming Concepts Summary

## File Structure & Format
- **Storage**: ASCII text, LF line endings only (no CRLF)
- **Structure**: `%ProgramName` → blocks → `M30` (with mandatory `G04 X0.5` before)
- **Blocks**: `N<line> <words>` separated by spaces/tabs
- **Words**: Letter + optional parameters (case insensitive, uppercase recommended)

## Block Execution & Look-Ahead
- **Look-ahead**: Analyzes 128 geometry entries ahead for velocity optimization
- **Without look-ahead**: Velocity reduces to 0 at each transition (G60)
- **Velocity transitions**: Lower velocity applied at segment start, higher velocity at transition
- **Dynamic optimization**: Maintains highest possible velocity through segment transitions

## Block Skipping (Conditional Execution)
```gcode
/N20 G01 X100                   # Skip if "Skip Line 0" disabled
/1N30 G01 Y100                  # Skip if "Skip Line 1" disabled
```
- Use `/` or `/0` through `/3` for conditional blocks
- Enable/disable in traverse settings page

## Feed Interpolation Modes
- **FCONST** (default): Apply programmed velocity immediately
- **FLIN**: Linear velocity transition from v_start to v_end over path length

## Smoothing & Blending Systems

### Path Smoothing Types
1. **Circular**: `#set paramCircularSmoothing(<radius>)#` - Arc between straight lines
2. **Parabola**: `#set paramVertexSmoothing(2; <subtype>; <radius>)#` - Steady velocity transition  
3. **Biquadratic**: `#set paramVertexSmoothing(3; <subtype>; <radius>)#` - No acceleration steps
4. **Bezier 3rd/5th**: `#set paramVertexSmoothing(4/5; <subtype>; <radius>)#` - Advanced smoothing

### Smoothing Subtypes
- **1**: Constant tolerance radius (RTB)
- **2**: Distance between intersection and vertex
- **3**: Adaptive tolerance radius (velocity-dependent)

### Auto Accurate Stop
`#set paramAutoAccurateStop(<angle>)#` - Automatic stops at sharp corners (>angle threshold)

## Advanced Features

### Mathematical Functions (@6xx)
- **@610**: Absolute value | **@613**: Square root | **@614**: Pythagorean (√(a²+b²))
- **@620/621**: Increment/decrement | **@622**: Integer part
- **@630-636**: Trig functions (sin, cos, tan, cot, asin, acos, atan) - all in degrees

### Flow Control
- **@714**: Decoder stop (wait for external event)
- **Mutual exclusion**: Some G-codes cannot be in same block (G00-03, G70-71, G90-91, etc.)

## Units & Coordinate Systems
- **Default state**: G00, G17 (XY plane), G53 (no offset), G70 (inch/mm·min⁻¹), G90 (absolute)
- **Unit changes**: Include `G04 X0.5` if no movement command for HMI update
- **Working planes**: G17 (XY), G18 (ZX), G19 (YZ) affect arc interpolation (I,J,K parameters)

## Programming Best Practices

### Error Prevention
- Match block numbers to line numbers for proper HMI display
- Include `G04 X0.5` before all program end commands (M30)
- Use only LF line endings (not CRLF)
- Validate mathematical expressions (left-to-right evaluation)

### Modal State Management
- Track modal states: interpolation mode, coordinate system, units, plane selection
- Modal commands remain active until explicitly changed
- Reset with opposing commands (G00↔G01↔G02↔G03, G90↔G91, etc.)

### Subroutine Organization
- **Local subroutines**: Same file, use label `L<number>`
- **External subroutines**: Separate files in CNC directory
- **Parameter passing**: Via R-parameters (no automatic save/restore)
- **Nesting limit**: 20 levels maximum

## Arc Programming Methods
1. **Center point**: `I<x_offset> J<y_offset> K<z_offset>` (relative to start)
2. **Radius**: `U<radius>` (positive=shorter arc, negative=longer arc)
3. **Full circles**: Start and end points must be equal in working plane

## System Integration Notes
- **PLC integration**: M-functions interface with machine PLC
- **Data recording**: M60/M61 control CSV logging at configurable rates (1-20Hz)
- **Temperature monitoring**: Multiple K-type thermocouples and spindle sensors
- **Force feedback**: Actuator force monitoring and PID control integration