# ~/houdini19.5/PythonScripts/main.py
import hou
from importlib import reload


def OpenFlipbook(kwargs):
    from Flipbook import flipbook_dialog as Flipbook
    reload(Flipbook)
    flipbook = Flipbook.Flipbook(hou.ui.mainQtWindow())
    flipbook.show()
