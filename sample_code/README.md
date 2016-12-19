# Compact Cache V2 sample code

## Vundler.py

Convert individual tile files to the [Esri Compact Cache V2](../CompactCacheV2.md) format bundles.  It only builds individual bundles, not a completely functional cache.

While operational, this code is only provided as an example.  It takes two arguments, the input level folder and the output level folder. Assumes that the input folder structure is of the form \<input_path>/\<row#>/\<col#>.\*

The script does not check the input tile format, and assumes that all the files and folders under the source contain valid tiles. The output might not be valid if non-tile files are present under the input folder.
The algorithm loops over files in a row folder, inserting each tile in the appropriate bundle. It keeps one bundle open in case the next tile fits in the same bundle.  In most cases this combination results in good performance.
Optionally, if the global variable USEGZ is True, compresses every input
tile with gzip before storing it into the bundle.

The [sample_tiles] (../sample_tiles) folder contains individual jpeg tiles for the first three level of a cache in Web Mercator projection.  The [sample_cache] (../sample_cache) folder contains a Compact Cache V2 cache produced from these individual tiles 
using the Vundler.py script.  The commands used to generate the bundles for each level are:

```
python sample_code\Vundler.py sample_tiles\L00 sample_cache\_alllayers/L00
python sample_code\Vundler.py sample_tiles\L01 sample_cache\_alllayers/L01
python sample_code\Vundler.py sample_tiles\L02 sample_cache\_alllayers/L02
```

## Licensing

Copyright 2016 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

[](Esri Tags: raster, image, cache)
[](Esri Language: Python)

