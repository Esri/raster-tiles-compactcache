# Compact Cache V2 sample code

## Vundler.py

Convert individual tile files to the esri Compact Cache V2 format bundles.  It does not build a complete Compact Cache V2, only individual bundles.  
Takes two arguments, the input level folder and the output level folder
Assumes that the input folder structure is <input_path>/Row/Col.ext

It does not check the input tile format, and assumes that all the files and folders under the source contain valid tiles. It might fail if non-tile files are present under the input folder.

The algorithm loops over files in a row folder, inserting each tile in the appropriate bundle. It keeps one bundle open in case the next tile fits in the same bundle.  In most cases this combination results in good performance.

Optionally, if the global variable USEGZ is True, compresses every input
tile with gzip before storing it into the bundle.


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

