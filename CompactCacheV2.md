# ESRI Imagery Compact Cache V2 Technical Description
---
An ESRI White Paper

Compact Cache V2 is an Esri tile storage format introduced with the ArcGIS 10.2 release, offering improved performance over the original Compact Cache.  The purpose of this white paper is to document the internal structure of the Compact Cache V2 as used for map and imagery storage, to allow programmers to read and write data in Compact Cache V2.

## Why Compact Cache V2

Storing pre-rendered map tiles for later use is a well-established method of improving GIS system performance.  The Esri Exploded Cache implementation stored each such tile as an individual file in a specific folder, using a simple naming convention to map a specific tile to a given map location and resolution.  While efficient and simple, this approach relies heavily on the file system, which leads to poor performance, especially for very large caches.  Since many map tiles are much smaller than the allocation size on a modern storage system, Exploded Caches also tend to waste storage space.

As a solution to the Exploded Cache scalability problems, the original Esri Compact Cache stored all the tiles for a larger map area in a single file called a bundle, file which follows a similar naming convention to the one used for Exploded Cache.  Compact Cache bundle files store an area of 128 by 128 tiles.  Since most map access focuses on a specific location at a time, only one or a couple of bundle files are in use, greatly reducing the file system load and improving performance.  To locate a given tile within the larger bundle file, a spatial index table is used.  In the original Compact Cache, this index held only the offsets for all the tiles within a bundle.  The index file was stored independently from the tile bundle, with a matching file name but different extension.

The Compact Cache V2 is similar to the original Compact Cache, with two primary differences: the Compact Cache V2 index table contains both the offset and size of each tile, and the index table is stored within the bundle file.  These two changes further improve the application performance, reducing the number of input/output operations needed to access the tiles.  While originally used only to store image tiles in JPEG or PNG format, the Compact Cache V2 structure lends itself to other uses, for example storing terrain data or vector tiles.  This document will mostly be concerned with the naming and structure of the Compact Cache V2 bundle files when used to store map images.  The internal tile format or the exact cache metadata format may vary with the use, and indeed are the current subject of technology development within Esri.

## Disk Structure
The Compact Cache V2 disk structure (illustrated in Figure 1) consists of a main folder containing a configuration file named conf.xml, an envelope file named conf.cdi, and a _\_alllayers_ folder, which itself contains level subfolders.  Each level folder contains all the bundles with tiles rendered for a specific scale or level of detail (LOD).

The conf.xml file contains most metadata properties of the cache in XML format.  These properties include identification of the cache as a Compact Cache, spatial reference, top-left origin, tile size in pixels, tile image format, target screen resolution, the set of predefined LOD scales at which the tiles exist, and the size of the bundle measured in tiles.  Each scale defined in the conf.xml represents an LOD level, counted up from zero in order of decreasing scale.  Two successive level scales differ by a factor of two.  The content of the conf.xml is sufficient to determine the tile grid used by the cache and establish the mapping between the map coordinates and tiles within specific bundles.  Every tile within a cache is uniquely identified by the level, row and column numbers.  The row and column are measured from the top left origin of the cache, which itself is defined in the conf.xml file.

The conf.cdi file contains the envelope of the extent of data in the cache, also in XML format.  It is used to eliminate slow file search operations for non-existing tile, mostly an Exploded Cache problem.

### Configuration File
A Compact Cache V2 configuration file called conf.xml resides in the main cache folder (See Appendix A for an example).  This XML file describes various properties of the cache.  There are three main objects: __TileCacheInfo__, __TileImageInfo__ and __CacheStorageInfo__.

The __TileCacheInfo__ object contains metadata properties of the cache as a whole.  The principal fields are:

| Element | Description |
| --- | --- |
| SpatialReference | Spatial reference of the cache |
| TileOrigin | X and Y coordinates of the top left corner in the cache spatial reference system |
| TileCols | Tile width in pixels. Usually 256 or 512 |
| TileRows | Tile height in pixels. Usually 256 or 512 |
| DPI | The dots per inch value used in rendering the tiles |
| LODInfos | A list of LODInfo elements, each one containing the level number, pixel resolution and the map scale |

The __Resolution__ field in the list of __LODInfos__ elements provides the accurate conversion between the pixel location and map coordinates.  The __Resolution__ value should agree with the __DPI__ and the __Scale__ fields, which are advisory only and might not provide full accuracy.  The __DPI__ value may be used to scale the cache tiles to the actual screen resolution to ensure readability of labels and other features.

The __TileImageInfo__ object describes the tile encoding and parameters used when creating tiles in the cache. The principal components are:

| Element | Description |
| --- | --- |
| CacheTileFormat | The internal format of the tiles.  For images the possible values are JPEG, PNG8, PNG24, PNG32 and MIXED |
| CompressionQuality | JPEG Q setting used during tile generation, if the format is JPEG |
| Antialiasing | *True* if antialiasing is on during tile generation |

The __CacheStorageInfo__ object defines the storage format and parameters of bundles. The fixed value of the __StorageFormat__ element defines a Compact Cache V2 cache.  The elements of the *CacheStorageInfo* object are:

| Element | Description |
| --- | --- |
| StorageFormat | *esriMapCacheStorageModeCompactV2* |
| PacketSize | 128, meaning that each bundle covers 128 by 128 tiles |

## Bundle File Naming

In the main cache folder, in addition to the conf.xml and conf.cdi files, there is a subfolder named _\_alllayers_.  Within this folder there are subfolders matching each of the cache LOD levels.  The folder names for the LOD levels begin with the uppercase letter __L__, followed by the level number as two decimal digits, prefixed by zero if necessary:
```
Layers\_alllayers\L08
```
All the bundle files for a given level are stored in the respective level folder.  Each bundle file stores the tiles for a 128 by 128 tile region of the cache, where 128 is the value of the __PacketSize__ field of the __CacheStorageInfo__ object stored in the cache configuration file.

The name of each bundle file is of the form **R\<rrrr>C\<cccc>.bundle**.  The \<rrrr> and \<cccc> fields are the row and column number of the top- and left-most tile location covered by the respective bundle, expressed in hexadecimal.  The row and column fields in the bundle file name have at least four lower case hexadecimal digits, prefixed by 0 if necessary.  Use of lower case hexadecimal digits ensures that the uppercase **C** character used as the separator between the row and column digits can be distinguished from the hexadecimal digit **c**.  The row and column fields in the bundle name are always multiples of the **PacketSize**, which means that the row and column fields of the bundle file names will always end in 00 or in 80.
For example, the top-left four bundles at level 8, if they exist, will be stored as:
```
Layers\_alllayers\L08\R0000C0000.bundle
Layers\_alllayers\L08\R0000C0080.bundle
Layers\_alllayers\L08\R0080C0000.bundle
Layers\_alllayers\L08\R0080C0080.bundle
```

## Bundle File Structure
Compact Cache uses bundle files for storing image tiles.  A bundle file has a small header, followed by the tile index table, followed by the tile data.  A bundle stores all the existing tiles for a geographical 128-by-128-tile area, for a maximum of 16384 individual tiles.  Internal to the bundle, the tiles are indexed by row and column.  Each tile index record consists in tile size and tile offset within the bundle file.  The index records for all 16,384 tiles within the bundle are stored in a row major array.  A tile index with a size of zero means that the tile does not exist, regardless of the offset value.


## Bundle Header
The bundle header is a 64-byte structure located at the beginning of the bundle file.  It consists of unsigned integers of 4 or 8 bytes, in lower-endian representation

| Offset | Size | Field Name | Value |
| --- | --- | --- | --- |
| 0 |	4	| Version	| 3 |
| 4	| 4	| Record Count | 16384 |
| 8 |	4	| Maximum Tile Size	| |
| 12 | 4 | Offset Byte Count | 5 |
| 16 | 8 | Slack Space | |
| 24 | 8 | File Size | |
| 32 | 8 | User Header Offset	| 40 |
| 40 | 4 | User Header Size	| 20 + 131072 |
| 44 | 4 | Legacy | 3 |
| 48 | 4 | Legacy | 16 |
| 52 | 4 | Legacy | 16384 |
| 56 | 4 | Legacy	| 5 |
| 60 | 4 | Index Size | 131072 |

The Slack Space value is a rough measure of the amount of bytes that are part of the bundle but are not used.  It is used and updated by the ArcGIS cache editing tools.  The value contained here is not always accurate and should be left as zero.  The __Legacy__ fields are there to ease the transition from the earlier version of Compact Cache, they should always have the listed values.

## Tile Index

The tile index immediately follows the bundle header, starting at file offset 64.  The index is a 128-by-128 array of tile index records, each one 8 bytes long, one such record per tile.  The total tile index size is 131,072 bytes.  This value is stored at file offset 60 within the bundle header.  The index records are stored in row major order in top-left orientation.  This means that the first tile index record corresponds to the top left tile within the bundle, whose absolute row and column are also used to name the bundle file.  The next index record is located immediately to the right of the first one.  The formula to compute the offset of the index record for a specific tile is:
```
TileIndexOffset = 64 + 8 * (128 * row + column)
```
where row and column numbers are relative to the row and column of the top-leftmost tile of the bundle.  Alternatively, a formula using the modulo operation % and the absolute row and column numbers relative to the top-leftmost tile within a level can be used:
```
TileIndexOffset = 64 + 8 * (128 * (row % 128) + (column % 128))
```
The fixed part of a Compact Cache V2 bundle consists of the header and the tile index, and is 131072 + 64 bytes in size.

## Tile Index Record
To find the content of a tile located at a specific row and tile location, first locate and read the tile index record matching the row and location as described above.  The tile offset and size can then be extracted from the tile index record and used to read the tile content itself.  Each tile data is contigous, but the order of the tiles within the bundle file is not defined.  It is possible to have unused space between tiles in the bundle file.
A tile index record is an 8-byte, low-endian unsigned integer which contains both the starting tile offset within the file and the size of a tile.  The tile offset is stored in bits 0 to 39, while the tile size is located in bits 40 to 63. Bit 0 is the least significant bit, and both offset and size are stored in little-endian format.
If IDX is the tile index value for a particular tile, and M is 2 to the power of 40, then the offset and size can be calculated as:
```
TileOffset = IDX % M
TileSize = Floor(IDX / M)
```
All values used in the calculation above have to be 8-byte-or-larger integers.  The __TileOffset__ is an absolute offset within the bundle file indicating the location where the tile data starts.  The __TileSize__ is the size of the tile in bytes.  If a decoded index has a TileSize of zero, then the tile is not stored in the bundle, regardless of the TileOffset value.

## Tile Record

The original Compact Cache bundles stored the tile data prefixed by a 4 byte little endian integer field which stored the size of the tile.  To ease the transition to Compact Cache V2, this size field is retained.  Note that the file offset stored in the tile index record is the offset of the first byte of the tile, not the offset of the size record, which will start at _offset_ - 4.
 
