"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/maya-coop
#                           ___  _
#     ___ ___   ___  _ __  / _ \| |_
#    / __/ _ \ / _ \| '_ \| | | | __|
#   | (_| (_) | (_) | |_) | |_| | |_
#    \___\___/ \___/| .__/ \__\_\\__|
#                   |_|
@summary:       Maya cooperative qt library
@run:           import coopQt as qt (suggested)
"""
from __future__ import print_function
import logging, time, threading
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMayaUI as omUI
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance

try:
    long        # Python 2
except NameError:
    long = int  # Python 3

# LOGGING
logging.basicConfig()  # errors and everything else (2 separate log groups)
logger = logging.getLogger("coopQt")  # create a logger for this file
logger.setLevel(logging.DEBUG)  # defines the logging level (INFO for releases)


# STYLES
fontHeader = QtGui.QFont('MS Shell dlg 2', 15);
fontFooter = QtGui.QFont('MS Shell dlg 2', 8);
# button.setStyleSheet("background-color: rgb(0,210,255); color: rgb(0,0,0);")
# imagePath = cmds.internalVar(upd = True) + 'icons/background.png')
# button.setStyleSheet("background-image: url(" + imagePath + "); border:solid black 1px;")
# self.setStyleSheet("QLabel { color: rgb(50, 50, 50); font-size: 11px; background-color: rgba(188, 188, 188, 50); border: 1px solid rgba(188, 188, 188, 250); } QSpinBox { color: rgb(50, 50, 50); font-size: 11px; background-color: rgba(255, 188, 20, 50); }")

PPI = 1
if cmds.about(mac=True):
    PPI = 1
else:
    PPI = cmds.mayaDpiSetting(systemDpi=True, q=True)/96.0

# WINDOW
def getMayaWindow():
    """
    Get the pointer to a maya window and wrap the instance as a QWidget
    Returns:
        Maya Window as a QWidget instance
    """
    ptr = omUI.MQtUtil.mainWindow()  # pointer to main window
    return wrapInstance(long(ptr), QtWidgets.QWidget)  # wrapper


def getDock(name=''):
    """
    Get pointer to a dock pane
    Args:
        name: Name of the dock

    Returns:
        ptr: pointer to the created dock
    """
    if not name:
        cmds.error("No name for dock was specified")
    deleteDock(name)
    # used to be called dockControl
    # ctrl = cmds.workspaceControl(name, dockToMainWindow=('left', True), label=name)
    ctrl = cmds.dockControl(name, con=name, area='left', label=name)
    qtCtrl = omUI.MQtUtil.findControl(ctrl)
    ptr = wrapInstance(long(qtCtrl), QtWidgets.QWidget)
    return ptr


def deleteDock(name=''):
    """
    Deletes a docked UI
    Args:
        name: Name of the dock to delete
    """
    if cmds.dockControl(name, query=True, exists=True):  # workspaceControl on 2017
        logger.debug("The dock should be deleted next")
        cmds.deleteUI(name)


class MayaUI(QtWidgets.QDialog):
    """
    DEPRECATED - USE CoopMayaUI instead
    Creates a QDialog and parents it to the main Maya window
    """
    def __init__(self, parent=getMayaWindow()):
        super(MayaUI, self).__init__(parent)


class CoopMayaUI(QtWidgets.QDialog):

    def __init__(self, title, dock=False, rebuild=False, brand="studio.coop", tooltip="", show=True, parent=getMayaWindow()):

        super(CoopMayaUI, self).__init__(parent)
        # check if window exists
        if cmds.window(title, exists=True):
            if not rebuild:
                cmds.showWindow(title)
                return
            cmds.deleteUI(title, wnd=True)  # delete old window

        # create window
        self.setWindowTitle(title)
        self.setObjectName(title)
        self.setWindowFlags(QtCore.Qt.Tool)  # always on top (multiplatform)
        if cmds.about(mac=True):
            self.dpiS = 1
        else:
            self.dpiS = cmds.mayaDpiSetting(systemDpi=True, q=True)/96.0

        # check if the ui is dockable
        if cmds.dockControl(title, query=True, exists=True):
            print("dock under this name exists")
            cmds.deleteUI("watercolorFX", ctl=True)
            cmds.deleteUI("watercolorFX", lay=True)
        if dock:
            cmds.dockControl(title, con=title, area='left', label=title)

        # default UI elements (keeping it simple)
        self.layout = QtWidgets.QVBoxLayout(self)  # self -> apply to QDialog
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        headerMargin = 10 * self.dpiS
        self.header = QtWidgets.QLabel(title)
        self.header.setAlignment(QtCore.Qt.AlignHCenter)
        self.header.setFont(fontHeader)
        self.header.setContentsMargins(headerMargin, headerMargin, headerMargin, headerMargin)

        self.brand = QtWidgets.QLabel(brand)
        self.brand.setAlignment(QtCore.Qt.AlignHCenter)
        self.brand.setToolTip(tooltip)
        self.brand.setStyleSheet("background-color: rgb(40,40,40); color: rgb(180,180,180); border:solid black 1px")
        self.brand.setFont(fontFooter)

        self.buildUI()
        self.populateUI()
        if not dock and show:
            self.show()
            #parent.show()

        logger.debug("A coopMayaUI was successfully generated")

    def buildUI(self):
        pass

    def populateUI(self):
        pass


def createMayaWindow(title, rebuild=False, brand='studio.coop', tooltip='introduction to the UI'):
    """
    Creates a default Maya window
    Args:
        title (str): The title of the Maya window
        rebuild (bool): If the window is destroyed and rebuild with each call
        brand (str): The brand of your company
        tooltip (str): Help tooltip for the UI

    Returns:
        window (QDialog): the QDialog instance
        existed (bool): if the window existed before or not
    """
    if cmds.window(title, exists=True):
        if not rebuild:
            cmds.showWindow(title)
            return None, True
        cmds.deleteUI(title, wnd=True)  # delete old window
    mWindow = MayaUI()
    mWindow.setWindowTitle(title)
    mWindow.setObjectName(title)
    mWindow.setWindowFlags(QtCore.Qt.Tool)  # always on top (multiplatform)

    if cmds.about(mac=True):
        mWindow.dpiS = 1
    else:
        mWindow.dpiS = cmds.mayaDpiSetting(systemDpi=True, q=True)/96.0

    # Default UI elements (keeping it simple)
    mWindow.header = QtWidgets.QLabel(title)
    mWindow.header.setAlignment(QtCore.Qt.AlignHCenter)
    mWindow.header.setFont(fontHeader)
    mWindow.header.setContentsMargins(10, 10, 10, 10)

    mWindow.brand = QtWidgets.QLabel(brand)
    mWindow.brand.setToolTip(tooltip)
    mWindow.brand.setStyleSheet("background-color: rgb(40,40,40); color: rgb(180,180,180); border:solid black 1px")
    mWindow.brand.setAlignment(QtCore.Qt.AlignHCenter)
    mWindow.brand.setGeometry(10, 10, 20, 20)
    mWindow.brand.setFont(fontFooter)

    logger.debug("Window successfully created")
    return mWindow, False


def getCoopIconPath():
    """
    Get the coop icon path
    Returns:
        iconPath (str): the coop icon path
    """
    iconPaths = mel.eval('getenv("XBMLANGPATH")')
    for iconPath in iconPaths.split(';'):
        if "coop/maya/icons" in iconPath:
            return iconPath


def labeledComboBox(label, options):
    """
    Creates and returns a labeled combobox
    Args:
        label (str): String containing label text
        options (lst): List of options to display in combo box e.g. ['.png', '.jpg', '.tif']

    Returns:
        labeledComboBox (QWidget): QWidget with the labeled combo box
    TODO:
        Convert to CLASS
    """
    w = QtWidgets.QWidget()
    wLayout = QtWidgets.QHBoxLayout()
    labelW = QtWidgets.QLabel(label)
    comboW = QtWidgets.QComboBox()
    comboW.addItems(options)
    wLayout.addWidget(labelW)
    wLayout.addWidget(comboW)
    w.setLayout(wLayout)
    return w


class IconButton(QtWidgets.QLabel):
    """
    Icon Button class object
    """
    clicked = QtCore.Signal(str)

    def __init__(self, image, tooltip='', size=[25, 25], parent=None, bColor=(50, 50, 50), hColor=(200, 200, 200)):
        """
        Icon Button constructor
        Args:
            image (str): relative image path ("images/butIcon.png")
            tooltip (str): tooltip of button (default -> "")
            size {lst): List of unsigned integers -> size of button in pixels (default -> [25, 25])
            parent (QWidget): Parent widget (default -> None)
        """
        super(IconButton, self).__init__(parent)
        self.setFixedSize(size[0], size[1])
        self.setScaledContents(True)
        self.setToolTip(tooltip)
        self.setPixmap(image)
        styleSheet = "QLabel{background-color: rgb" + "{0}".format(bColor) + \
                     ";} QLabel:hover{background-color: rgb" + "{0}".format(hColor) + ";}"
        self.setStyleSheet(styleSheet)

    def mouseReleaseEvent(self, event):
        self.clicked.emit("emit the signal")

    def changeIcon(self, image):
        self.setPixmap(image)


class HLine(QtWidgets.QFrame):
    """
    Horizontal line class object
    """
    def __init__(self, width=0, height=5*PPI):
        """
        Horizontal line constructor
        Args:
            width (int):  Width of horizontal line
            height (int): Height of widget (line thickness won't change)
        """
        super(HLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.height = height
        self.width = width


    def sizeHint(self):
        return QtCore.QSize(self.width, self.height)


class RelativeSlider(QtWidgets.QSlider):
    """
    Relative slider class object
    A slider that slides back to it's 0 position after sliding, giving relative values to it's previous position
    """
    def __init__(self, direction=QtCore.Qt.Horizontal):
        """
        Relative slider constructor
        Args:
            direction: QtCore.Qt.Horizontal or QtCore.Qt.Vertical
        """
        super(RelativeSlider, self).__init__(direction)
        self.prevValue = 0
        self.sliderReleased.connect(self.release)

    def release(self):
        self.prevValue = 0
        self.slideBack(time.time()+0.05)

    def relValue(self):
        """
        Get the relative value
        Returns:
            (int): relative value
        """
        relValue = self.value() - self.prevValue
        self.prevValue = self.value()
        return relValue

    def slideBack(self, endTime):
        self.blockSignals(True)
        if time.time() < endTime:
            self.setValue(self.value() * 0.9)
            threading.Timer(0.01, self.slideBack, [endTime]).start()
        else:
            self.setValue(0)
        self.blockSignals(False)


class WidgetGroup(QtWidgets.QWidget):
    """
    Simple widget group class object with embedded layout and batch widget assignment
    """

    def __init__(self, qWidgets=[], qLayout=None, parent=None, margins=0):
        """
        Widget Group constructor
        Args:
            qWidgets (lst): List of QWidgets to group (default -> [])
            qLayout: QtWidgets Layout object -> layout of group (default -> QtWidgets.QVBoxLayout())
            parent: QtWidgets object -> parent QtWidgets object (default -> None)
        """
        super(WidgetGroup, self).__init__(parent)
        if not qLayout:
            qLayout = QtWidgets.QVBoxLayout()
        self.groupLayout = qLayout
        self.setLayout(self.groupLayout)
        self.groupLayout.setContentsMargins(margins, margins, margins, margins)
        for widget in qWidgets:
            self.groupLayout.addWidget(widget)

    def addWidget(self, widget):
        """
        Add a single widget to the group
        Args:
            widget (QWidget): Widget to be added
        """
        self.groupLayout.addWidget(widget)

    def addWidget(self, widget, row, column):
        """
        Add a single widget into (row, column) of the group (has to be a QGridLayout)
        Args:
            widget (QWidget): Widget to be added
            row (int): row to insert into
            column (int): column to insert into
        """
        self.groupLayout.addWidget(widget, row, column)

    def addWidgets(self, widgets):
        """
        Adds a list of widgets to the group
        Args:
            widgets (lst): List of QWidgets to be added
        """
        for widget in widgets:
            self.groupLayout.addWidget(widget)
