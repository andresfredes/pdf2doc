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

"""coverter.py: Custom worker object to run conversion on secondary thread.
This avoids locking the gui during file processing.
"""
import fitz
from docx import Document
from PyQt5.QtCore import QObject, pyqtSignal
from config import IMG_DIR, FONT_DIR, XY_LIMIT, REL_RATIO, ABS_SIZE
import os, io, re
from PIL import Image

class Converter(QObject):
    """Simple worker function to handle file conversion in a secondary thread
    to avoid locking the GUI.

    Thread management is done by the GUI itself, but this is the object that
    will be passed to the secondary thread to manage the comparatively slower
    task of converting the files.

    Uses PyMuPDF to pull text from the PDF and then dump the text into a new
    doc file.

    Class variables:
        finished (pyqtSignal): Signal emitted to main thread when task complete.
        warning (pyqtSignal): Signal emitted to main thread when task failed.

    Args:
        path (str): path of file to convert
    """
    finished = pyqtSignal()
    warning = pyqtSignal()

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        """Handles the safe file conversion and ultimate emitting of signals.

        This function is triggered when the object is moved onto the secondary
        thread. It emits a finished signal on success and warning on failure.
        """
        try:
            self.convert(self.path)
        except Exception as e:
            print(f"Error in conversion: {type(e).__name__}:{e}")
            self.warning.emit()
        else:
            self.finished.emit()

    def convert(self, path):
        """Performs conversion using PyMuPdf and python-docx. Any images
        contained within the pdf will also be extracted into an images folder.

        Args:
            path (str): full system path to pdf file to convert
        """

        img_dir = os.path.join(os.path.dirname(path), IMG_DIR)
        font_dir = os.path.join(os.path.dirname(path), FONT_DIR)
        doc = Document()
        with fitz.open(path) as pdf:
            # try:
            #     self.get_images(pdf, img_dir)
            # except Exception as e:
            #     print(f"Error getting images: {type(e).__name__}:{e}")
            # try:
            #     self.get_fonts(pdf, font_dir)
            # except Exception as e:
            #     print(f"Error getting fonts: {type(e).__name__}:{e}")
            for page in pdf.pages():
                text = self.remove_control_characters(page.get_text("block"))
                try:
                    doc.add_paragraph(text)
                except Exception as e:
                    print(f"{text}----------------------")
                    print(f"Error getting text: {type(e).__name__}:{e}")
                doc.add_page_break()
            
        doc_path = f"{path.split('.')[0]}.docx"
        doc.save(doc_path)
            
    def get_images(self, pdf, img_dir):
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        page_count = pdf.page_count
        xreflist = []
        imglist = []
        for pno in range(page_count):
            il = pdf.get_page_images(pno)
            imglist.extend([x[0] for x in il])
            for img in il:
                xref = img[0]
                if xref in xreflist:
                    continue
                width = img[2]
                height = img[3]
                if min(width, height) <= XY_LIMIT:
                    continue
                image = self.recoverpix(pdf, img)
                n = image["colorspace"]
                imgdata = image["image"]

                if len(imgdata) <= ABS_SIZE:
                    continue
                if len(imgdata) / (width * height * n) <= REL_RATIO:
                    continue

                imgfile = os.path.join(
                    img_dir,
                    f"img{xref:05d}.{image['ext']}"
                )
                fout = open(imgfile, "wb")
                fout.write(imgdata)
                fout.close()
                xreflist.append(xref)

    def recoverpix(self, doc, item):
        xref = item[0]  # xref of PDF image
        smask = item[1]  # xref of its /SMask

        # special case: /SMask or /Mask exists
        # use Pillow to recover original image
        if smask > 0:
            fpx = io.BytesIO(  # BytesIO object from image binary
                doc.extract_image(xref)["image"],
            )
            fps = io.BytesIO(  # BytesIO object from smask binary
                doc.extract_image(smask)["image"],
            )
            img0 = Image.open(fpx)  # Pillow Image
            mask = Image.open(fps)  # Pillow Image
            img = Image.new("RGBA", img0.size)  # prepare result Image
            img.paste(img0, None, mask)  # fill in base image and mask
            bf = io.BytesIO()
            img.save(bf, "png")  # save to BytesIO
            return {  # create dictionary expected by caller
                "ext": "png",
                "colorspace": 3,
                "image": bf.getvalue(),
            }
        # special case: /ColorSpace definition exists
        # to be sure, we convert these cases to RGB PNG images
        if "/ColorSpace" in doc.xref_object(xref, compressed=True):
            pix1 = fitz.Pixmap(doc, xref)
            pix2 = fitz.Pixmap(fitz.csRGB, pix1)
            return {  # create dictionary expected by caller
                "ext": "png",
                "colorspace": 3,
                "image": pix2.tobytes("png"),
            }
        return doc.extract_image(xref)

    def get_fonts(self, pdf):
        pass

    def remove_control_characters(self, text):
        def str_to_int(s, default, base=10):
            if int(s, base) < 0x10000:
                return chr(int(s, base))
            return default
        text = re.sub(
            r"&#(\d+);?",
            lambda c: str_to_int(c.group(1), c.group(0)),
            text
        )
        text = re.sub(
            r"&#[xX]([0-9a-fA-F]+);?",
            lambda c: str_to_int(c.group(1), c.group(0), base=16),
            text
        )
        text = re.sub(r"[\x00-\x08\x0b\x0e-\x1f\x7f]", "", text)
        return text