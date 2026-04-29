#!/bin/bash
# Mount Spyro 1 disc image for exploration
# Usage: ./mount.sh <path_to_original.bin>

BIN=${1:-original.bin}
ISO=spyro_stripped.iso

echo "Stripping sectors from $BIN..."
python3 - << PYEOF
with open('$BIN', 'rb') as f_in, open('$ISO', 'wb') as f_out:
    sector_size = 2336
    header_size = 24
    data_size = 2048
    while True:
        sector = f_in.read(sector_size)
        if len(sector) < sector_size:
            break
        f_out.write(sector[header_size:header_size + data_size])
print("Done stripping sectors")
PYEOF

sudo mkdir -p /mnt/spyro
sudo mount -o loop $ISO /mnt/spyro
echo "Mounted at /mnt/spyro"
echo "Unmount with: sudo umount /mnt/spyro"
