# Copyright 2021, Andres Fredes, <andres.hector.fredes@gmail.com>
# 
# This file is part of pdf2doc.
# 
#     pdf2doc is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     pdf2doc is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with pdf2doc.  If not, see <https://www.gnu.org/licenses/>.

WINDOW = {
    "XPOS":0,
    "YPOS":0,
    "WIDTH":500,
    "HEIGHT":100,
}

IMG_DIR = 'images'
FONT_DIR = 'fonts'

# PyMuPDF constants and their relative values
XY_LIMIT = 0  # 100  # each image side must be greater than this
REL_RATIO = 0  # 0.05  # image : image size ratio must be larger than this (5%)
ABS_SIZE = 0  # 2048  # absolute image size limit 2 KB: ignore if smaller