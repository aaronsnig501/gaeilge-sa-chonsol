"""Text encoding helpers for ROM strings."""

FADA_REPLACEMENTS = {
    "Á": "Aa",
    "É": "Ea",
    "Í": "Ia",
    "Ó": "Oa",
    "Ú": "Ua",
    "á": "aa",
    "é": "ea",
    "í": "ia",
    "ó": "oa",
    "ú": "ua",
}


def encode_rom_text(text: str) -> str:
    """Convert Irish text with fadas into the ROM's ASCII-safe encoding."""
    for original, replacement in FADA_REPLACEMENTS.items():
        text = text.replace(original, replacement)
    return text
