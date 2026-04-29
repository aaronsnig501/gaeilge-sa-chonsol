#!/usr/bin/env python3
"""
WAD.WAD archive unpacker for Spyro PS1.
Usage: python3 wad_unpack.py <path/to/WAD.WAD> [subfile_number]
       subfile_number: 0 = extract all (default), N = extract specific subfile
"""

import argparse
import os
import struct

parser = argparse.ArgumentParser(description='Unpacker for WAD.WAD archive.')
parser.add_argument('filepath', type=str, help='Path to WAD.WAD.')
parser.add_argument('subfile', type=int, nargs='?', default=0,
                    help='Subfile number. 0 = extract all (default).')
args = parser.parse_args()

def extractSubfile(sfNum):
    ofile = open('sf_' + str(sfNum) + '.bin', 'wb')
    sfAddr = subfiles[(sfNum-1)*2]
    sfSize = subfiles[(sfNum-1)*2+1]
    ifile.seek(sfAddr)
    ofile.write(ifile.read(sfSize))
    ofile.close()
    print(f'Extracted sf_{sfNum}.bin ({sfSize} bytes)')

ifile = open(args.filepath, 'rb')
headerFmt = '<' + 'I'*512
subfiles = struct.unpack(headerFmt, ifile.read(struct.calcsize(headerFmt)))
sfCount = 0
for x in range(int(len(subfiles)/2)):
    if not subfiles[x*2+1] == 0:
        sfCount = x+1

if args.subfile > 0:
    extractSubfile(args.subfile)
else:
    for n in range(sfCount):
        extractSubfile(n+1)

ifile.close()
print(f'Extraction completed. {sfCount} subfiles.')
