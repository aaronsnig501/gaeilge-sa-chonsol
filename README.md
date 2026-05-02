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
gsc init --console ps1 --game spyro1 --rom ~/roms/spyro.bin
gsc extract
gsc extract --output custom.csv
gsc validate
gsc validate --csv custom.csv
gsc patch
gsc patch --output spyro_gaeilge.bin
gsc patch --dry-run
gsc release --mode fast
gsc release --mode compact --version 1.0 --output patches/spyro1_gaeilge_v1.0.bps
gsc mount
gsc umount
gsc wad list
gsc wad extract
gsc wad extract --subfile 1
gsc wad pack ./wad_subfiles
gsc status
gsc status --game spyro1
```

The `init` command validates the ROM path, checks it matches the expected game,
and writes a local `.gsc/config.toml` file in the repository root.

The `extract` command reads the configured ROM, extracts the game's registered
string table, and writes `offset,budget,english,irish` rows while preserving any
existing Irish translations already present in the target CSV.

The `validate` command reads the translations CSV, encodes Irish text using the
ROM's fada scheme, and reports translation progress plus any rows that exceed
their byte budgets.

The `patch` command validates the configured CSV, skips any over-budget rows,
copies the configured ROM to a new BIN, and applies valid translations using the
verified PS1 sector mapping and preserve-metadata rules.

The `release` command validates all strings, generates a patched BIN, and calls
Flips to produce a distributable BPS patch file. You must choose `--mode fast`
for quicker creation with a larger patch, or `--mode compact` for slower,
smaller output.

The `mount` and `umount` commands strip PS1 BIN sectors into a temporary ISO
and mount or unmount it using the configured mount point from `.gsc/config.toml`.

The `wad` commands list, extract, and repack WAD subfiles using the mounted disc
and the registered game's WAD metadata.

The `status` command summarizes translation progress by category and overall,
using the registered string table layout and highlighting any over-budget rows.

Current command groups are scaffolded for:
- `init`
- `extract`
- `patch`
- `release`
- `status`
- `mount`
- `umount`
- `wad`
- `validate`
- `release`

The first registered game is `ps1.spyro1`, defined in [`cli/games/ps1/spyro1.py`](/home/aaronsinnott/Documents/projects/romhacks/gaeilge-sa-chonsol/cli/games/ps1/spyro1.py).

## Supabase

The repository now includes an initial Supabase migration at
[`supabase/migrations/20260502113000_initial_schema.sql`](/home/aaronsinnott/Documents/projects/romhacks/gaeilge-sa-chonsol/supabase/migrations/20260502113000_initial_schema.sql:1)
covering:

- `strings`
- `suggestions`
- `verifications`
- `contributors`

The `strings` table uses the current repo model:
- `verified` boolean for in-game confirmation
- `compromised` boolean for constrained-but-best-available translations
- `note` for translator context

Environment variable placeholders live in
[.env.example](/home/aaronsinnott/Documents/projects/romhacks/gaeilge-sa-chonsol/.env.example:1).

Because the current site is deployed as a static SvelteKit build on GitHub Pages,
the deployed frontend should only use public client-side Supabase values:

- `PUBLIC_SUPABASE_URL`
- `PUBLIC_SUPABASE_PUBLISHABLE_KEY`

The non-public variables are only for future CI or backend work:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`

Recommended Supabase dashboard security settings:
- Data API: enabled
- Automatically expose new tables and functions: disabled
- Automatic RLS on new public tables: enabled

Repo-side setup covered here:
- schema migration
- environment variable placeholders

Still manual outside the repo:
- create the Supabase project
- apply the migration in your project
- add `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_KEY` to GitHub Actions secrets when CI/server-side Supabase access is needed

To sync verified or updated Supabase string data back into the repo CSVs, use:

```bash
python3 -m pip install supabase
SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 scripts/sync_from_supabase.py
python3 scripts/generate_status.py
```

The repository also includes a GitHub Actions workflow at
[`sync-supabase-strings.yml`](/home/aaronsinnott/Documents/projects/romhacks/gaeilge-sa-chonsol/.github/workflows/sync-supabase-strings.yml:1)
for manual or API-triggered syncs.
