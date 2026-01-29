"""
Convert library shaders to use u_phase for perfect looping.

This script transforms iTime-based shaders to use u_phase (0.0 to 1.0)
multiplied by integer constants, ensuring seamless loops.
"""

import os
import re
from pathlib import Path

SHADERS_DIR = Path("src/looplab/shaders/examples")

# Skip audio shaders - they need special handling and real-time input
SKIP_PATTERNS = [".audio.frag", ".thumb.", ".png", ".vert"]

def should_skip(filename: str) -> bool:
    """Check if file should be skipped."""
    return any(p in filename.lower() for p in SKIP_PATTERNS)


def convert_shader(content: str, filename: str) -> str:
    """
    Convert a shader from iTime to u_phase for perfect looping.
    
    Strategy:
    1. Add a LOOP_SPEED constant at the top
    2. Replace iTime with (u_phase * TAU * LOOP_SPEED) for cyclic animations
    3. Handle #define time patterns
    """
    
    # Check if uses iTime at all
    if "iTime" not in content:
        print(f"  [SKIP] No iTime reference: {filename}")
        return content
    
    lines = content.split('\n')
    new_lines = []
    
    # Track if we've added our header
    header_added = False
    has_loop_header = "LOOP_SPEED" in content and "u_phase" in content
    
    # The core loop time definition - using TAU (2*PI) ensures smooth cycling
    loop_header = """
// === PERFECT LOOP CONVERSION ===
// LOOP_SPEED controls animation speed (integer for seamless loops)
#define LOOP_SPEED 2.0
#define LOOP_TIME (u_phase * 6.283185307 * LOOP_SPEED)
// ================================
"""
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Add header after initial comments/blank lines (if not already present)
        if not header_added and not has_loop_header and stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
            # Check if we're still in a block comment
            in_block = False
            for prev_line in lines[:i]:
                if '/*' in prev_line:
                    in_block = True
                if '*/' in prev_line:
                    in_block = False
            
            if not in_block:
                new_lines.append(loop_header)
                header_added = True
        
        # Handle various time definition patterns
        
        # Pattern: #define time (iTime*X) or #define time iTime*X or complex iTime expressions
        if stripped.startswith('#define') and 'iTime' in stripped:
            # Extract the macro name
            define_match = re.match(r'#define\s+(\w+)\s+(.+)', stripped)
            if define_match:
                macro_name = define_match.group(1)
                macro_body = define_match.group(2)
                
                # Try to extract a multiplier from simple patterns
                mult_match = re.search(r'iTime\s*\*\s*([\d.]+)', macro_body)
                if mult_match:
                    try:
                        mult_val = float(mult_match.group(1))
                        int_mult = max(1, round(mult_val))
                    except:
                        int_mult = 2
                    new_lines.append(f"#define {macro_name} (LOOP_TIME * {int_mult}.0)")
                else:
                    # Just replace iTime with LOOP_TIME in the macro
                    new_body = macro_body.replace('iTime', 'LOOP_TIME')
                    new_lines.append(f"#define {macro_name} {new_body}")
                continue
        
        # Pattern: float time = iTime * X;
        time_var_match = re.match(r'(\s*)float\s+time\s*=\s*iTime\s*\*?\s*([\d.]+)?;', line)
        if time_var_match:
            indent = time_var_match.group(1)
            multiplier = time_var_match.group(2) or "1.0"
            try:
                mult_val = float(multiplier)
                int_mult = max(1, round(mult_val))
            except:
                int_mult = 2
            new_lines.append(f"{indent}float time = LOOP_TIME * {int_mult}.0;")
            continue
        
        # Replace direct iTime usage (not in defines - already handled above)
        if 'iTime' in line and not stripped.startswith('#define'):
            # Replace iTime * number with LOOP_TIME * rounded_number
            def replace_itime_mult(match):
                multiplier = match.group(1) or "1.0"
                try:
                    mult_val = float(multiplier)
                    int_mult = max(1, round(mult_val))
                except:
                    int_mult = 2
                return f"LOOP_TIME * {int_mult}.0"
            
            # iTime * 0.05 -> LOOP_TIME * 1.0
            line = re.sub(r'iTime\s*\*\s*([\d.]+)', replace_itime_mult, line)
            
            # Remaining bare iTime
            line = line.replace('iTime', 'LOOP_TIME')
        
        new_lines.append(line)
    
    # If header wasn't added (e.g., file starts with code), prepend it
    if not header_added and not has_loop_header:
        return loop_header + '\n'.join(new_lines)
    
    return '\n'.join(new_lines)


def main():
    """Process all shader files."""
    shader_dir = SHADERS_DIR
    
    if not shader_dir.exists():
        print(f"Error: {shader_dir} not found")
        return
    
    # Get all .frag files
    frag_files = list(shader_dir.glob("*.frag"))
    
    converted = 0
    skipped = 0
    errors = 0
    
    for frag_file in sorted(frag_files):
        filename = frag_file.name
        
        if should_skip(filename):
            print(f"[SKIP] {filename} (audio/excluded)")
            skipped += 1
            continue
        
        print(f"[PROCESS] {filename}")
        
        try:
            content = frag_file.read_text(encoding='utf-8')
            new_content = convert_shader(content, filename)
            
            if new_content != content:
                frag_file.write_text(new_content, encoding='utf-8')
                print(f"  [OK] Converted")
                converted += 1
            else:
                skipped += 1
                
        except Exception as e:
            print(f"  [ERROR] {e}")
            errors += 1
    
    print(f"\n=== Summary ===")
    print(f"Converted: {converted}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()
