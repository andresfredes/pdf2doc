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
from PyQt5.QtCore import QObject, pyqtSignal

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
            print(e)
            self.warning.emit(e)
        else:
            self.finished.emit()

    def convert(self, path):
        """Performs conversion using PyMuPdf and -----------

        Args:
            path (str): full system path to pdf file to convert
        """
        pass
