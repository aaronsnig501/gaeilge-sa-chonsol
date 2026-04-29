#!/usr/bin/env python3
"""
WAD.WAD archive packer for Spyro PS1.
Usage: python3 wad_pack.py <folder_with_subfiles> [--output new_WAD.WAD]
       Files must be named sf_1.bin, sf_2.bin, etc.
"""

import argparse
import struct
import os

parser = argparse.ArgumentParser(description='Packer for WAD.WAD archive.')
parser.add_argument('filepath', type=str,
                    help='Path to folder with subfiles.')
parser.add_argument('--output', type=str, default='new_WAD.WAD',
                    help='Output file name.')
args = parser.parse_args()

fpath = args.filepath.strip('"\'')
filelist = os.listdir(fpath)

wad = open(args.output, 'wb')
offset = 2048
counter = 0

for x in range(len(filelist)):
    sf_path = os.path.join(fpath, f'sf_{x+1}.bin')
    subfile = open(sf_path, 'rb')
    bytes0 = subfile.read()
    sfsize = len(bytes0)
    wad.seek(counter * 8)
    wad.write(offset.to_bytes(4, byteorder='little'))
    wad.seek(counter * 8 + 4)
    wad.write(sfsize.to_bytes(4, byteorder='little'))
    counter += 1
    wad.seek(offset)
    wad.write(bytes0)
    offset += sfsize
    subfile.close()
    print(f'Packed sf_{x+1}.bin ({sfsize} bytes)')

wad.close()
print(f'WAD file created: {args.output}')
