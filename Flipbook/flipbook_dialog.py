# ~/houdini19.5/PythonScripts/Flipbook/flipbook_dialog.py
## Flipbook ##

# import data
import hou
import os
import subprocess
import re
import json

from PySide2.QtWidgets import QDialog, QGridLayout, QPushButton
from PySide2.QtWidgets import QLabel, QLineEdit, QComboBox
from PySide2.QtWidgets import QApplication, QCheckBox, QScrollArea
from PySide2.QtWidgets import QTextEdit, QHBoxLayout, QVBoxLayout


class Flipbook(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.command = ""
        self.command_json = {}

        # Widget
        self.setMinimumSize(600, 600)
        self.setWindowTitle("Flipbook")
        self.renderbutton = QPushButton("Render")
        self.renderbutton.resize(80, 40)
        self.resolution_combobox = QComboBox()
        self.resolution_combobox_label = QLabel("Resolution")
        self.camera_combobox = QComboBox()
        self.camera_combobox_label = QLabel("Cameras")
        self.textedit = QTextEdit()
        self.lineedit_label = QLabel("comment")
        self.movbutton = QPushButton("MOV")
        self.explorebutton = QPushButton("Flipbook Explore")
        self.textedit.setMaximumSize(300, 100)

        # get current path
        self.filepath = hou.hipFile.path()
        self.filename = os.path.basename(self.filepath).split(".")[0]
        self.dirname = os.path.dirname(self.filepath)

        # Layout
        self.gridlayout = QGridLayout()
        self.gridlayout.addWidget(self.textedit, 0, 1, 1, 2)


        self.gridlayout.addWidget(self.camera_combobox_label,1, 0, 1, 1)
        self.gridlayout.addWidget(self.camera_combobox,1, 1, 1, 2)
        self.gridlayout.addWidget(self.lineedit_label, 0, 0, 1, 1)
        self.gridlayout.addWidget(self.resolution_combobox_label,2,0)
        self.gridlayout.addWidget(self.resolution_combobox, 2, 1, 1, 2)

        self.gridlayout.addWidget(self.movbutton, 3, 0)
        self.gridlayout.addWidget(self.explorebutton, 3, 1)
        self.gridlayout.addWidget(self.renderbutton, 3, 2)
        self.gridlayout.setVerticalSpacing(170)
        self.setLayout(self.gridlayout)

        # Set
        self.create_camera_combobox()
        self.create_resolution_combobox()

        # Event
        self.renderbutton.clicked.connect(self.render_flipbook)
        self.explorebutton.clicked.connect(self.open_explore)
        self.movbutton.clicked.connect(self.play_flipbook_mov)
        self.camera_combobox.activated.connect(self.create_resolution_combobox)

    def render_flipbook(self):
        cur_desktop = hou.ui.curDesktop()
        scene = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer) #return hou.SceneViewer
        cur_view = scene.curViewport()

        # Set Current Camera

        if self.camera_combobox.currentText() == "current_view":
            cur_camera = cur_view.defaultCamera()
        else:
            cur_camera = hou.node(f"/obj/{self.camera_combobox.currentText()}")
        cur_view.setCamera(cur_camera)




        # flipbook Setting
        if not os.path.exists(self.flipbook_path):
            os.makedirs(self.flipbook_path)

        scene.flipbookSettings().stash()
        flipbook_options = scene.flipbookSettings()
        flipbook_options.output(f"{self.flipbook_path}/{self.filename}.$F4.jpeg")

        # framerange
        framerange = self.get_current_frame()
        flipbook_options.frameRange((framerange.x(), framerange.y()))
        flipbook_options.useResolution(1)  # use

        # resolution
        resolution = self.get_current_resolution()
        if resolution == "camera_resolution":
            res_x = int(cur_camera.parm("resx").eval())
            res_y = int(cur_camera.parm("resy").eval())
        else:
            res_x = int(resolution.split(":")[0])
            res_y = int(resolution.split(":")[1])


        flipbook_options.resolution((res_x, res_y))

        scene.flipbook(scene.curViewport(), flipbook_options)
        self.make_json_file(res_x,res_y)

    @property
    def flipbook_path(self):
        return f"{self.dirname}/{self.filename}_flipbook"

    def get_current_frame(self):
        return hou.playbar.frameRange()  # return Vector2 Class

    def create_resolution_combobox(self):
        self.resolution_combobox.clear()
        resolustion_list = ["1920:1080", "1280:720"]
        for resolution in resolustion_list:
            self.resolution_combobox.addItem(resolution)
        self.add_camera_resolution()

    def get_current_resolution(self):
        return self.resolution_combobox.currentText()

    def add_camera_resolution(self):
        if self.camera_combobox.currentText() == "current_view":
            return
        self.resolution_combobox.addItem(f"camera_resolution")

    def open_explore(self):
        path = self.flipbook_path.replace("/", "\\")
        subprocess.Popen(f"explorer {path}", shell=True)

    def get_flipbook_first_image(self):
        if os.path.exists(self.flipbook_path):
            files = os.listdir(self.flipbook_path)
            self.convert_image_name(files[0])

    def convert_image_name(self, file):
        pattern = re.compile(r"\.(\d+)\.")
        match = pattern.findall(file)
        self.start_frame = match[0]
        self._input_name = file.replace(self.start_frame, "%04d")

    def play_flipbook_mov(self):
        self.get_flipbook_first_image()
        self.add_command()
        subprocess.run(f"pwsh -Command {self.command};start {self.flipbook_path}/{self.filename}.mov")

    # TODO ADD CODEC AND RESOLUTION
    def add_command(self):
        # ffmpeg.exe command
        self.command += ' '.join([
            "rez-env", "ffmpeg", "--",
            "ffmpeg.exe", "-f", "image2",
            "-start_number", self.start_frame,
            "-i", f"{self.flipbook_path}/{self._input_name}",
            f"{self.flipbook_path}/{self.filename}.mov"
        ])

    # TODO INSERT OTHER DATA
    def make_json_file(self,res_x,res_y):
        self.command_json["comment"] = self.textedit.toPlainText()
        self.command_json["Resolution"] = f"{res_x}:{res_y}"

        json_path = f"{self.dirname}/{self.filename}.json"

        with open(json_path, "w") as f:  # create json file
            json.dump(self.command_json, f, indent=4, ensure_ascii=True)  # dump json data

    def get_cameras(self):
        return hou.nodeType(hou.objNodeTypeCategory(), "cam").instances()

    def create_camera_combobox(self):
        self.camera_combobox.addItem("current_view")
        cameras = self.get_cameras()
        for camera in cameras:
            self.camera_combobox.addItem(camera.name())