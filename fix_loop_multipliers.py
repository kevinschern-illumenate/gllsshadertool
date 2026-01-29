"""
Fix non-integer time multipliers in shaders to ensure perfect looping.

This script finds patterns like sin(... * time * 0.5) or time * 0.123
and rounds the multipliers to integers.
"""

import os
import re
from pathlib import Path

SHADERS_DIR = Path("src/looplab/shaders/examples")

# Skip audio shaders
SKIP_PATTERNS = [".audio.frag", ".thumb.", ".png", ".vert"]

def should_skip(filename: str) -> bool:
    return any(p in filename.lower() for p in SKIP_PATTERNS)


def fix_time_multipliers(content: str, filename: str) -> str:
    """
    Fix non-integer time multipliers to ensure perfect looping.
    
    Patterns to fix:
    - time * 0.5 -> time * 1.0
    - 0.5 * time -> 1.0 * time  
    - sin(time * 0.123) -> sin(time * 1.0)
    - time/i1 where i1 varies -> need special handling
    """
    
    original = content
    
    # Pattern 1: number * time (where number is a decimal)
    def fix_mult_before(match):
        num_str = match.group(1)
        try:
            val = float(num_str)
            # Round to nearest integer, minimum 1
            int_val = max(1, round(val))
            return f"{int_val}.0*time"
        except:
            return match.group(0)
    
    # Pattern 2: time * number (where number is a decimal)
    def fix_mult_after(match):
        num_str = match.group(1)
        try:
            val = float(num_str)
            int_val = max(1, round(val))
            return f"time*{int_val}.0"
        except:
            return match.group(0)
    
    # Pattern 3: time/number -> time * (1/rounded)
    def fix_div(match):
        num_str = match.group(1)
        try:
            val = float(num_str)
            # For division, we want time/N to loop, so keep as time/int
            int_val = max(1, round(val))
            return f"time/{int_val}.0"
        except:
            return match.group(0)
    
    # Fix: 0.123*time patterns (decimal before time)
    content = re.sub(r'(\d+\.\d+)\s*\*\s*time\b', fix_mult_before, content)
    
    # Fix: time*0.123 patterns (decimal after time)
    content = re.sub(r'\btime\s*\*\s*(\d+\.\d+)', fix_mult_after, content)
    
    # Fix: time/0.123 patterns
    content = re.sub(r'\btime\s*/\s*(\d+\.\d+)', fix_div, content)
    
    # Also handle LOOP_TIME directly
    content = re.sub(r'(\d+\.\d+)\s*\*\s*LOOP_TIME\b', 
                     lambda m: f"{max(1, round(float(m.group(1))))}.0*LOOP_TIME", content)
    content = re.sub(r'\bLOOP_TIME\s*\*\s*(\d+\.\d+)', 
                     lambda m: f"LOOP_TIME*{max(1, round(float(m.group(1))))}.0", content)
    
    if content != original:
        print(f"  [FIXED] Time multipliers adjusted")
        return content
    else:
        print(f"  [OK] No problematic multipliers found")
        return content


def analyze_shader(content: str, filename: str) -> list:
    """Analyze shader for potential loop-breaking patterns."""
    issues = []
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Check for time accumulation patterns (i4 += ... * time)
        if re.search(r'\+\s*=.*time', line, re.IGNORECASE):
            issues.append(f"  Line {i}: Accumulating time - may break loop: {line.strip()[:60]}")
        
        # Check for time in non-trig context that's not a simple multiply
        # These are harder to auto-fix
        
    return issues


def main():
    shader_dir = SHADERS_DIR
    
    if not shader_dir.exists():
        print(f"Error: {shader_dir} not found")
        return
    
    frag_files = list(shader_dir.glob("*.frag"))
    
    fixed = 0
    issues_found = []
    
    for frag_file in sorted(frag_files):
        filename = frag_file.name
        
        if should_skip(filename):
            continue
        
        print(f"[CHECK] {filename}")
        
        try:
            content = frag_file.read_text(encoding='utf-8')
            
            # Analyze for issues that can't be auto-fixed
            issues = analyze_shader(content, filename)
            if issues:
                issues_found.append((filename, issues))
            
            # Fix what we can
            new_content = fix_time_multipliers(content, filename)
            
            if new_content != content:
                frag_file.write_text(new_content, encoding='utf-8')
                fixed += 1
                
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print(f"\n=== Summary ===")
    print(f"Fixed multipliers in: {fixed} files")
    
    if issues_found:
        print(f"\n=== Manual Review Needed ===")
        for filename, issues in issues_found:
            print(f"\n{filename}:")
            for issue in issues:
                print(issue)


if __name__ == "__main__":
    main()
