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

"""gui.py: module to build/manage all gui elements. Built using PyQt5.

This is the core of the program which calls on a Converter object to do the
business logic.
"""

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QMainWindow, QMessageBox,
    QVBoxLayout, QWidget)
import re
from config import WINDOW
from custom_widgets import Action, Button, Label
from converter import Converter

class UI(QMainWindow):
    """The main window object for the Graphical User Interface.

    Created by subclassing the Qt object QMainWindow.
    """
    def __init__(self):
        super().__init__()
        self.title = "Andy Fred's PDF to DOC converter"
        self._init_UI()

    def _init_UI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(
            WINDOW["XPOS"],
            WINDOW["YPOS"],
            WINDOW["WIDTH"],
            WINDOW["HEIGHT"]
        )
        self._add_menu()
        self._add_widgets()

    def _add_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("File")
        exit_option = Action(
            name='Exit',
            window=self,
            shortcut='Ctrl+Q',
            tip='Exit Program',
            func=self._close
        )
        file_menu.addAction(exit_option)

    def _add_widgets(self):
        central = QWidget()
        layout = QVBoxLayout()
        
        self.label = Label(text="")
        layout.addWidget(self.label)
        hbox = QHBoxLayout()
        self.choose_button = Button(
            text="Choose pdf",
            func=self.select,
            active=True,
        )
        hbox.addWidget(self.choose_button)
        self.convert_button = Button(
            text="Convert to doc",
            func=self.convert,
            active=False,
        )
        hbox.addWidget(self.convert_button)
        layout.addLayout(hbox)

        footer = Label(
            text="Send feedback to andres.hector.fredes@gmail.com",
            size=12,
        )
        layout.addWidget(footer)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _close(self):
        super().close()

    def select(self):
        """Generates file selector, specifically to choose PDF files for
        conversion.

        Uses the QFileDialog to manage the file selection and then additional
        code to manage safe usage of the GUI.
        """
        file_picker = QFileDialog()
        self.path = file_picker.getOpenFileName(
            None,
            "Select File",
            "",
        )[0]
        if self.path != "":
            if self.path.endswith(".pdf"):
                self.convert_button.enable()
                pattern = "/"
                filename = re.split(pattern, self.path)[-1:][0]
                self.label.setText(filename)
            else:
                self.label.setText("Invalid file type")
        else:
            self.label.setText("No file specified")

    def convert(self):
        """Primary function for the application.

        Creates a worker in a new thread to generate the converted file without
        locking the GUI. All interaction is disabled during the conversion to
        avoid user error. Helpful notices are generated while converting and on
        recieving the finished signal from the worker thread.
        """
        self.choose_button.disable()
        self.convert_button.disable()
        self.label.setText("Converting...")
        
        self.thread = QThread()
        self.worker = Converter(self.path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.choose_button.enable)
        self.worker.finished.connect(
            lambda: self.label.setText("Conversion complete!")
        )
        
        self.worker.warning.connect(self.warning)
        self.worker.warning.connect(self.choose_button.enable)
        self.worker.warning.connect(
            lambda: self.label.setText("Conversion failed.")
        )

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        


    def warning(self):
        """Generates a pop-up warning that the conversion failed.

        Triggered by an incoming signal from the secondary thread.
        """
        title = "Conversion error"
        message = f"Unable to convert file."
        warning = QMessageBox.warning(
            None,
            title,
            message,
            QMessageBox.Ok,
            QMessageBox.Ok
        )
