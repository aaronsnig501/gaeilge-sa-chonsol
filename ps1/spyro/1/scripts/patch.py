#!/usr/bin/env python3
"""
Spyro the Dragon (PS1 PAL) - Irish Language Patch
Applies translations from data/translations.py to original.bin
Usage: python3 patch.py <path_to_original.bin> [output.bin]
"""

import csv
import shutil
import re
import sys
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
CSV_PATH = os.path.join(DATA_DIR, 'translations.csv')

INPUT_BIN = sys.argv[1] if len(sys.argv) > 1 else 'original.bin'
OUTPUT_BIN = sys.argv[2] if len(sys.argv) > 2 else 'spyro_gaeilge.bin'

# Build sector map from sync headers
with open(INPUT_BIN, 'rb') as f:
    bin_data = f.read()

syncs = [m.start() for m in re.finditer(
    b'\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00', bin_data)]

def iso_to_bin(iso_offset):
    """Convert ISO offset to bin offset using sync header map."""
    iso_sector = iso_offset // 2048
    byte_in_sector = iso_offset % 2048
    return syncs[iso_sector] + byte_in_sector + 24

# Verify formula with known offsets
assert iso_to_bin(0xc000 + 0x10b0) == 0xefa8, "Formula check failed: CONTINUE"
assert iso_to_bin(0xc000 + 0x2430) == 0x10588, "Formula check failed: STONE HILL"
print("Sector formula verified ✓")

# Strings in 0x6c*** region use fixed-width slots with metadata after
# Value = original string length (pad only up to this, preserve bytes after)
preserve_metadata = {
    0x6c17c: 5,   # WORLD
    0x6c1a4: 6,   # PAUSED
    0x6c1cc: 7,   # OPTIONS
    0x6c264: 6,   # CAMERA
    0x6c2a4: 4,   # DONE
    0x6c2ec: 6,   # ACTIVE
    0x6c30c: 7,   # PASSIVE
    0x6c38c: 5,   # RETRY
    0x6c3e4: 5,   # GO TO
    0x6c3f4: 7,   # RESCUED
    0x6bfa0: 4,   # QUIT
    0x6bfa8: 7,   # CRASHED
    0x6bfc0: 5,   # TOTAL
    0x6bff4: 7,   # COPTERS
    0x6c01c: 5,   # BOATS
    0x6c05c: 6,   # LIGHTS
    0x6c064: 5,   # RINGS
    0x6c0cc: 6,   # CHESTS
    0x6c0d4: 6,   # PLANES
    0x6c0dc: 6,   # ARCHES
    0x6c0e4: 7,   # BARRELS
    0x6bfe0: 3,   # YES
    0x6bff0: 2,   # NO
    0x6c6a8: 4,   # HOME
}

# Load translations
patches = []
skipped = []
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['irish'].strip():
            offset = int(row['offset'], 16)
            english = row['english']
            irish = row['irish']
            budget = int(row['budget'])
            encoded = irish.encode('ascii')
            if len(encoded) > budget:
                skipped.append((irish, len(encoded), budget))
                continue
            patches.append((offset, budget, english, irish, encoded))

if skipped:
    print(f"\nSkipped ({len(skipped)} strings exceed budget):")
    for irish, size, budget in skipped:
        print(f"  {irish}: {size} bytes, budget {budget}")

# Apply patches
shutil.copy(INPUT_BIN, OUTPUT_BIN)
with open(OUTPUT_BIN, 'r+b') as f:
    for offset, budget, english, irish, encoded in patches:
        iso_offset = 0xc000 + offset
        bin_offset = iso_to_bin(iso_offset)
        f.seek(bin_offset)
        f.write(encoded)
        if offset in preserve_metadata:
            original_len = preserve_metadata[offset]
            pad = original_len - len(encoded)
            if pad > 0:
                f.write(b'\x00' * pad)
        else:
            f.write(b'\x00' * (budget - len(encoded)))

print(f"\nDone. Applied {len(patches)} patches to {OUTPUT_BIN}")
