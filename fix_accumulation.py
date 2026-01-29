"""
Fix time accumulation patterns that break perfect loops.

Patterns like:
  var += time * X   -> var += sin(time) * X
  var += X + time   -> var += X + sin(time)
  pos += time * vel -> pos += sin(time) * vel
"""

import re
from pathlib import Path

SHADERS_DIR = Path("src/looplab/shaders/examples")
SKIP_PATTERNS = [".audio.frag", ".thumb.", ".png", ".vert"]

def should_skip(filename: str) -> bool:
    return any(p in filename.lower() for p in SKIP_PATTERNS)


def fix_accumulation(content: str, filename: str) -> tuple[str, list]:
    """
    Fix patterns where time is accumulated rather than used cyclically.
    Returns (new_content, list_of_changes)
    """
    changes = []
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*'):
            new_lines.append(line)
            continue
        
        # Pattern: += ... time * ... (time being multiplied and accumulated)
        # But NOT inside sin/cos already
        if '+=' in line and 'time' in line.lower():
            # Check if time is already wrapped in sin/cos
            if re.search(r'sin\s*\(\s*time', line, re.IGNORECASE) or \
               re.search(r'cos\s*\(\s*time', line, re.IGNORECASE):
                new_lines.append(line)
                continue
            
            # Pattern: += time * X or += X * time (bare time multiplication being accumulated)
            # Replace time with sin(time) to make it cyclic
            
            # += time * something
            if re.search(r'\+=\s*time\s*\*', line, re.IGNORECASE):
                line = re.sub(r'\+=(\s*)time(\s*\*)', r'+=\1sin(time)\2', line, flags=re.IGNORECASE)
                changes.append(f"  Line {i+1}: Wrapped accumulated time in sin()")
            
            # += something * time (at end or followed by semicolon/operator)
            elif re.search(r'\+=.*\*\s*time\s*[;+\-\)]', line, re.IGNORECASE):
                line = re.sub(r'\*(\s*)time(\s*[;+\-\)])', r'*\1sin(time)\2', line, flags=re.IGNORECASE)
                changes.append(f"  Line {i+1}: Wrapped accumulated time in sin()")
            
            # += something + time * X (time term in addition)
            elif re.search(r'\+\s*time\s*\*', line, re.IGNORECASE):
                line = re.sub(r'\+(\s*)time(\s*\*)', r'+\1sin(time)\2', line, flags=re.IGNORECASE)
                changes.append(f"  Line {i+1}: Wrapped accumulated time in sin()")
                
            # += vec2/vec3(...time...) - time inside vector constructor being accumulated
            # This is trickier, skip for now
            
        # Pattern: pos += time * vel  or  pos += LOOP_TIME * something
        if '+=' in line and 'LOOP_TIME' in line:
            if re.search(r'sin\s*\(\s*LOOP_TIME', line) or \
               re.search(r'cos\s*\(\s*LOOP_TIME', line):
                new_lines.append(line)
                continue
                
            # += LOOP_TIME * something
            if re.search(r'\+=\s*LOOP_TIME\s*\*', line):
                line = re.sub(r'\+=(\s*)LOOP_TIME(\s*\*)', r'+=\1sin(LOOP_TIME)\2', line)
                changes.append(f"  Line {i+1}: Wrapped accumulated LOOP_TIME in sin()")
            
            # += something * LOOP_TIME
            elif re.search(r'\+=.*\*\s*LOOP_TIME', line):
                line = re.sub(r'\*(\s*)LOOP_TIME', r'*\1sin(LOOP_TIME)', line)
                changes.append(f"  Line {i+1}: Wrapped accumulated LOOP_TIME in sin()")
            
            # += something + LOOP_TIME * X
            elif re.search(r'\+\s*LOOP_TIME\s*\*', line):
                line = re.sub(r'\+(\s*)LOOP_TIME(\s*\*)', r'+\1sin(LOOP_TIME)\2', line)
                changes.append(f"  Line {i+1}: Wrapped accumulated LOOP_TIME in sin()")
        
        new_lines.append(line)
    
    return '\n'.join(new_lines), changes


def main():
    shader_dir = SHADERS_DIR
    
    if not shader_dir.exists():
        print(f"Error: {shader_dir} not found")
        return
    
    frag_files = list(shader_dir.glob("*.frag"))
    
    fixed = 0
    all_changes = []
    
    for frag_file in sorted(frag_files):
        filename = frag_file.name
        
        if should_skip(filename):
            continue
        
        try:
            content = frag_file.read_text(encoding='utf-8')
            new_content, changes = fix_accumulation(content, filename)
            
            if changes:
                print(f"[FIX] {filename}")
                for change in changes:
                    print(change)
                frag_file.write_text(new_content, encoding='utf-8')
                fixed += 1
                all_changes.extend([(filename, c) for c in changes])
                
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
    
    print(f"\n=== Summary ===")
    print(f"Fixed accumulation patterns in: {fixed} files")
    print(f"Total changes: {len(all_changes)}")


if __name__ == "__main__":
    main()
