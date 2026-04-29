# Spyro the Dragon (PS1 PAL) - Irish Translation Notes

## ROM Format
- Disc image: BIN/CUE format
- Sector size in BIN: 2336 bytes
- Sector header: 24 bytes
- Data per sector: 2048 bytes
- Sync header pattern: `00 FF FF FF FF FF FF FF FF FF FF 00`

## ISO to BIN offset formula
```pythonsyncs = [positions of sync headers in bin]
def iso_to_bin(iso_offset):
iso_sector = iso_offset // 2048
byte_in_sector = iso_offset % 2048
return syncs[iso_sector] + byte_in_sector + 24
Verified with:
- CONTINUE (exe 0x10b0) → bin 0xefa8
- STONE HILL (exe 0x2430) → bin 0x10588

## Executable
- File: SCES_014.38
- Location in ISO: sector 24 (iso offset 0xc000)
- Size: 444416 bytes
- Contains all game text strings

## String Tables
Two main string tables in the executable:

### Main text region (0x800 - 0x5100)
- Five language slots per string: Italian, Spanish, German, French, English
- Null-separated, variable length
- Patching: write Irish to English slot, null-pad to budget

### Extended region (0x6c000+)
- Four language slots: Italian, Spanish, German, English  
- Fixed 8-byte slots with rendering metadata after string
- CRITICAL: Only null-pad up to original string length, preserve bytes after
- preserve_metadata dict in patch.py tracks original lengths

## Accent Encoding
Fada characters use two-byte encoding:
- Á = Aa (0x41 0x61)
- É = Ea (0x45 0x61)  
- Í = Ia (0x49 0x61)
- Ó = Oa (0x4F 0x61)
- Ú = Ua (0x55 0x61)
All uppercase only - game uses all-caps rendering

## WAD Archive
- File: WAD.WAD (211MB)
- 114 subfiles
- sf_1.bin (108KB) - titlescreen sprite sheet
- Text strings NOT in WAD - all in executable

## Frontend Menu (Known Limitation)
NEW GAME, LOAD GAME, EMPTY, START GAME etc. are SPRITES not text.
Stored as pre-rendered images in sf_1.bin (titlescreen sprite sheet).
Loaded into VRAM at (512, 256) via LoadImage().
See titlescreen.c from decompilation project for sprite indices.
Requires image editing to translate - planned for v2.0.

## Homeworld Transition Screens
French-only slots at 0xed0-0xf44 - no English equivalents.
Game displays these during world entry cutscenes.
Patched Irish into French slots directly.

## Disc StructureSCES_014.38  - Main executable (all text)
WAD.WAD      - Level/asset data
S0/
S000000D.NSF  - Level data
S000003C.NSF  - Level data
WARP.BIN      - Warp data
CRASH.EXE     - Frontend engine
MUSIC1-6.STR  - Music streams
SYSTEM.CNF    - Boot config

## Known Issues / TODO
- [ ] Frontend menu sprites (v2.0)
- [ ] Spyro logo translation (v2.0)  
- [ ] Dragon rescue dialogue (NPC strings)
- [ ] Some save/load multi-line messages may be tight
- [ ] TAIFEAD not yet implemented for flight level RECORD display
