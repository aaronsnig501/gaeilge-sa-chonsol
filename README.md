# Cluichi Gaeilge - Irish Language ROM Hacks

Irish language patches for retro games, created to normalise Irish in digital
spaces and meet language learners through games they have nostalgia for.

![Gaeilge sa Chonsol](./logo.svg)

## Games

### PS1
- **Spyro the Dragon** (PAL, SCES-01438) - In progress

## Structure
ps1/
spyro/
spyro1/
scripts/   - Patching, mounting, WAD tools
data/      - Translation CSV and Python data structures
patches/   - Generated BPS patch files
notes/     - Technical documentation and offset discoveries

## Approach
- Text patches applied directly to BIN file using verified sector offset formula
- Fada characters encoded as two-byte sequences (Á=Aa, É=Ea, Í=Ia, Ó=Oa, Ú=Ua)
- All strings sourced from main executable SCES_014.38
- Distributable as BPS patch files (apply with Flips)

## Tools Required
- Python 3
- Flips (for BPS patch generation)
- DuckStation or similar PS1 emulator for testing

## CLI

The repository now includes a Typer-based CLI scaffold under [`cli/`](/home/aaronsinnott/Documents/projects/romhacks/gaeilge-sa-chonsol/cli).

### Install
```bash
python3 -m pip install -e .
```

This installs the `gsc` console script and the initial dependencies:
- `typer`
- `rich`
- `pillow`

### Usage
```bash
gsc --help
gsc extract --help
gsc patch --help
gsc validate image ps1.spyro1 original.bin
```

Current command groups are scaffolded for:
- `extract`
- `patch`
- `mount`
- `wad`
- `validate`
- `release`

The first registered game is `ps1.spyro1`, defined in [`cli/games/ps1/spyro1.py`](/home/aaronsinnott/Documents/projects/romhacks/gaeilge-sa-chonsol/cli/games/ps1/spyro1.py).
