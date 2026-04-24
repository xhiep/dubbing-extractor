#!/usr/bin/env python3
"""Quick verification that all 4 tabs are properly added to notebook"""

import sys
from pathlib import Path

HERE = Path(__file__).parent.parent

def verify_tabs():
    """Check that all 4 tabs are added to notebook in main.py"""

    with open(HERE / "main.py", "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split('\n')

    print("Checking tab additions in main.py...")
    print("=" * 60)

    tabs_found = []

    # Find all notebook.add() and notebook.insert() calls
    for i, line in enumerate(lines, 1):
        if ('notebook.add(' in line or 'notebook.insert(' in line) and 'text=' in line:
            # Extract tab name
            if 'Nguon' in line or 'Source' in line:
                tabs_found.append(('Source', i, line.strip()))
            elif 'Can Chinh' in line or 'Adjust' in line or 'Dieu Chinh' in line:
                tabs_found.append(('Adjust', i, line.strip()))
            elif 'Long Tieng' in line or 'Dub' in line or 'Lồng Tiếng' in line:
                tabs_found.append(('Dub', i, line.strip()))
            elif 'Nhat Ky' in line or 'Log' in line or 'Nhật Ký' in line:
                tabs_found.append(('Log', i, line.strip()))

    # Report findings
    expected_tabs = ['Source', 'Adjust', 'Dub', 'Log']
    found_names = [name for name, _, _ in tabs_found]

    print(f"\nExpected tabs: {', '.join(expected_tabs)}")
    print(f"Found tabs: {', '.join(found_names)}")
    print()

    for name, line_num, code in tabs_found:
        print(f"[OK] {name:8} tab at line {line_num:4}: {code}")

    missing = set(expected_tabs) - set(found_names)
    if missing:
        print(f"\n[ERROR] Missing tabs: {', '.join(missing)}")
        return False

    print("\n" + "=" * 60)
    print("[SUCCESS] All 4 tabs are properly added to notebook!")
    return True

if __name__ == "__main__":
    success = verify_tabs()
    sys.exit(0 if success else 1)
