# Spyro the Dragon - Irish Language Patch
**Spyro the Dragon (PS1 PAL, SCES-01438)**

An Irish language (Gaeilge) patch for the original Spyro the Dragon on PS1.
This patch translates all in-game text to Irish, including level names, 
homeworld names, UI strings, HUD elements, and NPC dialogue.

## Status
Work in progress - v0.1

### Translated
- ✅ All level names
- ✅ All homeworld names (short labels and transition screens)
- ✅ Pause menu
- ✅ Options menu
- ✅ HUD strings (treasure, time, records)
- ✅ Save/load system
- ✅ Balloonist dialogue (partial)
- ✅ Flight level HUD (barrels, planes, arches etc.)
- ✅ Intro cutscene text
- ✅ Demo mode strings

### In Progress
- 🔄 Dragon rescue NPC dialogue
- 🔄 Remaining balloonist dialogue

### Known Limitations
- ❌ Frontend menu (NEW GAME, LOAD GAME, EMPTY etc.) — stored as 
  pre-rendered sprites, requires image editing — planned for v2.0
- ❌ Spyro logo — sprite-based, planned for v2.0
- ❌ Language selection screen — sprite-based

## Technical Notes

### Fada Encoding
The game's font renderer uses a two-byte encoding for accented characters:
| Character | Encoding |
|-----------|----------|
| Á | Aa |
| É | Ea |
| Í | Ia |
| Ó | Oa |
| Ú | Ua |

All in-game text is uppercase only.

### String Tables
Text lives in the main executable `SCES_014.38` in two regions:

**Main region (0x800–0x5100)**
Five language slots per string: Italian, Spanish, German, French, English.
Irish replaces the English slot.

**Extended region (0x6c000+)**
Four language slots with fixed 8-byte slots and rendering metadata.
Must preserve bytes after the null terminator — see `preserve_metadata`
in `scripts/patch.py`.

### Homeworld Transitions
The homeworld entry screens only had French text (no English equivalent).
Irish has been patched directly into the French slots at 0xed0–0xf44.

### ISO to BIN Offset Formula
PS1 BIN files use 2336-byte sectors with 24-byte headers.
Sector positions are looked up from sync header positions rather than
calculated with a fixed stride, as sector boundaries are irregular.

```python
syncs = [positions of 0x00FFFFFFFFFFFFFFFFFFFFFF00 in bin]
def iso_to_bin(iso_offset):
    iso_sector = iso_offset // 2048
    byte_in_sector = iso_offset % 2048
    return syncs[iso_sector] + byte_in_sector + 24
```

## Usage

### Applying the Patch
1. Install [Flips](https://github.com/Alcaro/Flips)
2. Obtain a PAL copy of Spyro the Dragon (SCES-01438)
3. Apply the `.bps` patch file from the `patches/` directory using Flips
4. Load the patched BIN file in a PS1 emulator (DuckStation recommended)

### Building from Source
```bash
# Apply translations to original BIN
python3 scripts/patch.py original.bin spyro_gaeilge.bin

# Generate BPS patch (requires Flips)
flips --create --bps original.bin spyro_gaeilge.bin patches/spyro1_gaeilge.bps
```

### Mounting the Disc Image
```bash
./scripts/mount.sh original.bin
# Files available at /mnt/spyro/
sudo umount /mnt/spyro
```

### Exploring the WAD
```bash
mkdir wad_subfiles
cd wad_subfiles
python3 ../scripts/wad_unpack.py /path/to/WAD.WAD
```

## Credits
- Translation: [Your name]
- ROM hacking research: [Your name]
- Decompilation reference: [Spyro decompilation project]
- Prior art: Bípbúp's Irish SMB1 patch (romhacking.net)

## Disclaimer
This patch is a fan translation for preservation and cultural purposes.
It requires a legally obtained copy of the original game to use.
