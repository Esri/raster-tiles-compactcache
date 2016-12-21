#-------------------------------------------------------------------------------
# Name:        Vundler
# Purpose:     Build compact cache V2 bundles from individual tiles
#
# Author:      luci6974
#
# Created:     20/09/2016
#
#  Copyright 2016 Esri
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.?
#
#-------------------------------------------------------------------------------
#
# Converts individual tile files to the esri Compact Cache V2 format
#
# Takes two arguments, the first one is the input level folder
# the second one being the output level folder for the bundles
# This script operates on a single level
#
# Assumes that the input folder structure is .../Level/Row/Col.ext
#
# Loops over columns and then row, in the order given by os.walk
# Keeps one bundle open in case the next tile fits in the same bundle
# In most cases this combination results in good performance
#
# It does not check the input tile format, and assumes that all
# the files and folders under the source contain valid tiles.  In other
# words, make sure there are no spurious files and folders under the input
# path, otherwise the output bundles might have strange content.
#

import sys
import string
import os.path
import struct

#Bundle linear size in tiles
BSZ = 128
# Tiles per bundle
BSZ2 = BSZ ** 2
# Index size in bytes
IDXSZ = BSZ2 * 8


#Output path
opath = None

# The curr_* variable are used for caching of open output bundles
# current bundle is kept open to reduce overhead
# TODO: Eliminate global variables
curr_bundle = None
# A bundle index list
# Array would be better, but it lacks 8 byte int support
curr_index = None
# Bundle file name without path or extension
curr_bname = None
# Current size of bundle file
curr_offset = long(0)
# max size of a tile in the current bundle
curr_max = 0

def init_bundle(fname):
    '''Create an empty V2 bundle file'''
    fd = open(fname,"wb")
    # Empty bundle file header, lots of magic numbers
    header = struct.pack("<4I3Q6I",
        3,          # Version
        BSZ2,       # numRecords
        0,          # maxRecord Size
        5,          # Offset Size
        0,          # Slack Space
        64 + IDXSZ, # File Size
        40,         # User Header Offset
        20 + IDXSZ, # User Header Size
        3,          # Legacy 1
        16,         # Legacy 2
        BSZ2,       # Legacy 3
        5,          # Legacy 4
        IDXSZ       # Index Size
    )
    fd.write(header)
    # Write empty index.
    fd.write(struct.pack("<{}Q".format(BSZ2), *((0,) * BSZ2)))
    fd.close()

def cleanup():
    '''Updates header and closes the current bundle'''
    global curr_bundle, curr_bname, curr_index, curr_max, curr_offset
    curr_bname = None

    # Update the max rec size and file size, then close the file
    if curr_bundle != None:
        curr_bundle.seek(8)
        curr_bundle.write(struct.pack("<I", curr_max))
        curr_bundle.seek(24)
        curr_bundle.write(struct.pack("<Q", curr_offset))
        curr_bundle.seek(64)
        curr_bundle.write(struct.pack("<{}Q".format(BSZ2), *curr_index))
        curr_bundle.close()

def openbundle(row, col):
    '''Make the bundle corresponding to the row and col current'''
    global curr_bname, curr_bundle, curr_index, curr_offset, opath, curr_max
    # row and column of top-left tile in the output bundle
    start_row = (row / BSZ ) * BSZ
    start_col = (col / BSZ ) * BSZ
    bname = "R{:04x}C{:04x}".format(start_row, start_col)
#    bname = "R%(r)04xC%(c)04x" % {"r": start_row, "c": start_col}

    # If the name matches the current bundle, nothing to do
    if bname == curr_bname:
        return

    # Close the current bundle, if it exists
    cleanup()

    # Make the new bundle current
    curr_bname = bname
    # Open or create it, seek to end of bundle file
    fname = os.path.join(opath, bname + ".bundle")

    # Create the bundle file if it didn't exist already
    if not os.path.exists(fname):
        init_bundle(fname)

    # Open the bundle
    curr_bundle = open(fname,"r+b")
    # Read the current max record size
    curr_bundle.seek(8)
    curr_max = int(struct.unpack("<I", curr_bundle.read(4))[0])
    # Read the index as longs in a list
    curr_bundle.seek(64)
    curr_index = list(struct.unpack("<{}Q".format(BSZ2),
                        curr_bundle.read(IDXSZ)))
    # Go to end
    curr_bundle.seek(0, os.SEEK_END)
    curr_offset = curr_bundle.tell()

def add_tile(fname, row):
    '''Add this tile to the output cache'''
    global BSZ, curr_bundle, curr_max, curr_offset
    col = int(os.path.splitext(os.path.basename(fname))[0])

    # Read the tile data
    tile = open(fname, "rb").read()
    tsize = len(tile)

    # Write the tile at the end of the bundle, prefixed by size
    openbundle(row, col)
    curr_bundle.write(struct.pack("<I", tsize))
    curr_bundle.write(tile)
    # Skip the size
    curr_offset += 4

    # Update the index, row major
    curr_index[(row % BSZ ) * BSZ + col % BSZ] = curr_offset + (tsize << 40)
    curr_offset += tsize

    # Update the current bundle max tile size
    curr_max = max(curr_max, tsize)

def dorow(folder, row):
    '''Adds the tiles from one row folder'''
    r = int(row)
    for root, dirs, files in os.walk(os.path.join(folder,row)):
        for f in (os.path.join(folder, row, fn) for fn in files):
            add_tile(f, r)
        break

def main():
    global opath
    opath = sys.argv[2]
    # Process each row folder
    for root, dirs, files in os.walk(sys.argv[1]):
        for d in dirs:
            dorow(root, d)
        break
    cleanup()

if __name__ == '__main__':
    main()
