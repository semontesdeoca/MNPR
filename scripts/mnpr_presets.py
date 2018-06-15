"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
      _         _                                   _
  ___| |_ _   _| | ___     _ __  _ __ ___  ___  ___| |_ ___
 / __| __| | | | |/ _ \   | '_ \| '__/ _ \/ __|/ _ \ __/ __|
 \__ \ |_| |_| | |  __/   | |_) | | |  __/\__ \  __/ |_\__ \
 |___/\__|\__, |_|\___|   | .__/|_|  \___||___/\___|\__|___/
          |___/           |_|
@summary:       MNPR's style presets interface and implementation
@adapted from:  coopAttrManager.py (https://github.com/semontesdeoca/maya-coop)
"""
from __future__ import print_function
import os, json, logging, pprint, operator, traceback, functools
from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import coopLib as lib
import coopQt as qt
import mnpr_system
import mnpr_runner
import mnpr_info

# LOGGING
logging.basicConfig()  # errors and everything else (2 separate log groups)
logger = logging.getLogger("mnpr_presets")  # create a logger for this file
logger.setLevel(logging.DEBUG)  # defines the logging level (INFO for releases)
# logger.setLevel(logging.INFO)  # defines the logging level (DEBUG for debugging)

PATH = lib.Path(lib.getLibDir()).parent()


#        _         _          _ _ _
#    ___| |_ _   _| | ___    | (_) |__
#   / __| __| | | | |/ _ \   | | | '_ \
#   \__ \ |_| |_| | |  __/   | | | |_) |
#   |___/\__|\__, |_|\___|   |_|_|_.__/
#            |___/
class AttributeSetsLibrary(dict):
    """ Attribute sets library """
    type = "attrSets"
    objects = []

    def save(self, name, screenshot=True, **info):
        """
        Saves an attribute set to disk
        Args:
            name (str): Name of the attribute set to save
            objects (lst): List of objects to create attribute sets of (default -> selected)
            folder (str): Folder within directory to save this to
            screenshot (bool): Determines if a screenshot should be saved
            **info: Any additional arguments to be saved in the accompanying json file
        """
        logger.debug("Type of attribute set is: {0}".format(self.type))

        savePath = lib.Path(PATH.path)
        savePath.child("presets").child(self.type).createDir()

        # path to json file to save
        path = os.path.join(savePath.path, "{0}.json".format(name))

        # add to json dictionary
        info['name'] = name

        # select custom object
        prevSelection = cmds.ls(sl=True)
        selection = prevSelection
        if self.objects:
            cmds.select(self.objects, r=True)
            selection = cmds.ls(sl=True)

        # capture screenshot
        if screenshot:
            shotPath = self.saveScreenshot(name, directory=savePath.path)
            info['screenshot'] = os.path.basename(shotPath)

        # get attributes
        selAttrs = cmds.channelBox("mainChannelBox", sma=True, q=True)  # gets selected attributes in channelbox
        if not selAttrs:
            selAttrs = cmds.listAttr(se=True)  # settable attributes

        attrs = []
        for obj in selection:
            for attr in selAttrs:
                if cmds.attributeQuery(attr, node=obj, exists=True):
                    attrs.append("{0}.{1}".format(obj, attr))

        logger.debug(attrs)

        # store attributes in dict
        savedAttrs = {}
        for attr in attrs:
            savedAttrs[attr] = cmds.getAttr(attr)
        info['attributes'] = savedAttrs

        # write and save json info
        with open(path, 'w') as f:
            json.dump(info, f, indent=4)

        self[name] = info

        # make everything normal again
        cmds.select(prevSelection, r=True)  # restore selection

    def find(self):
        """
        Finds the attribute sets on disk
        Args:
            directory (str): the directory to search in
        """
        self.clear()  # clear dictionary
        findPath = lib.Path(PATH.path)
        findPath.child("presets").child(self.type)

        files = os.listdir(findPath.path)  # list all files in directory
        attrSets = [f for f in files if f.endswith(".json")]  # only json files

        for aSet in attrSets:
            name, ext = os.path.splitext(aSet)
            setFile = os.path.join(findPath.path, aSet)

            with open(setFile, 'r') as f:
                info = json.load(f)

            # read screenshot
            screenshot = "{0}.jpg".format(name)
            if screenshot in files:
                info['screenshot'] = os.path.join(findPath.path, screenshot)

            # add default info (in case the json file does not have this)
            info['name'] = name
            info['path'] = setFile

            # add controller info to library
            self[name] = info  # add to dictionary

    def load(self, name):
        """
        Loads the specified attribute set
        Args:
            name (str): Name of the attribute set to import
        """
        attrs = self[name]['attributes']
        # check if substrate is available
        substrateAttr = "{0}.substrateTexture".format(mnpr_info.configNode)
        p = lib.Path(lib.getLibDir()).parent().child("textures")
        textures = os.listdir(p.path)
        if attrs[substrateAttr] not in textures:
            # check if substrates have been installed
            if len(textures) <= 2:
                result = cmds.confirmDialog(t="Substrates (papers/canvas) not found", m="The required substrate is not available.\nWould you like to download the MNPR substrates?", b=['Yes', 'Load anyway', 'Close'], icn="warning")
                if result == "Close":
                    return
                elif result == "Yes":
                    mnpr_runner.downloadSubstrates()
                    return
                else:
                    cmds.warning("Substrate texture not found, reverting to default substrate (style might not display correctly)")
                    attrs[substrateAttr] = "rough_default_2k.jpg"
            else:
                cmds.warning("Substrate texture not found, reverting to default substrate (style might not display correctly)")
                attrs[substrateAttr] = "rough_default_2k.jpg"

        # check change of style first
        styleAttr = "{0}.style".format(mnpr_info.configNode)
        if styleAttr in attrs:
            style = attrs[styleAttr]
            if style != cmds.mnpr(style=True):
                lib.setAttr(mnpr_info.configNode, "style", style)
                func = functools.partial(self.loadStyle, attrs)
                return cmds.scriptJob(runOnce=True, event=["SelectionChanged", func])
            else:
                # set attributes
                for attr in attrs:
                    splitter = attr.split('.')
                    lib.setAttr(splitter[0], splitter[1], attrs[attr])
        else:
            # for legacy presets (we do not worry about styles here)
            for attr in attrs:
                splitter = attr.split('.')
                if "NPRConfig" in splitter[0]:
                    splitter[0] = "mnprConfig"
                lib.setAttr(splitter[0], splitter[1], attrs[attr])
        lib.printInfo("Attributes set successfully")

    def loadStyle(self, attrs):
        if cmds.objExists(mnpr_info.configNode):
            # set attributes
            for attr in attrs:
                splitter = attr.split('.')
                lib.setAttr(splitter[0], splitter[1], attrs[attr], True)
            lib.printInfo("Style changed and attributes set successfully")

    def saveScreenshot(self, name, directory):
        """
        Saves screenshot out to disk
        Args:
            name: Name of the screenshot
            directory: Directory to save into
        """
        return mnpr_system.renderFrame(os.path.join(directory, name), 100, 100, 1, ".jpg")


#    _   _ ___
#   | | | |_ _|
#   | | | || |
#   | |_| || |
#    \___/|___|
#
class AttributeSetsUI(qt.CoopMayaUI):
    """
    The AttributeSetsUI is a dialog that lets us load and save attribute sets (e.g. presets, poses, etc)
    """
    def __init__(self, windowTitle="Attribute Sets", setType="attrSets", objects=None, rebuild=True, brand="studio.coop", tooltip="Manage attribute sets"):
        self.library = AttributeSetsLibrary()
        self.library.type = setType
        self.library.objects = objects

        super(AttributeSetsUI, self).__init__(windowTitle, dock=False, rebuild=rebuild, brand=brand, tooltip=tooltip)  # run inherited __init__

    def buildUI(self):
        """This method builds the UI"""
        self.layout.addWidget(self.header)

        # save widget
        saveWidget = QtWidgets.QWidget()
        saveLayout = QtWidgets.QHBoxLayout(saveWidget)
        self.layout.addWidget(saveWidget)

        self.saveInput = QtWidgets.QLineEdit()
        saveLayout.addWidget(self.saveInput)

        saveBtn = QtWidgets.QPushButton('Save')
        saveBtn.clicked.connect(self.save)
        saveLayout.addWidget(saveBtn)

        # parameters for thumbnails
        size = 64 * self.dpiS
        padding = 12 * self.dpiS

        # list widget (grid) that shows the thumbnails
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setViewMode(QtWidgets.QListWidget.IconMode)  # set list to icon mode
        self.listWidget.setIconSize(QtCore.QSize(size, size))  # set size
        self.listWidget.setResizeMode(QtWidgets.QListWidget.Adjust)  # responsive list
        self.listWidget.setGridSize(QtCore.QSize(size+padding, size+(padding*2)))
        self.layout.addWidget(self.listWidget)

        # btn widget
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        self.layout.addWidget(btnWidget)

        loadBtn = QtWidgets.QPushButton("Load")
        loadBtn.clicked.connect(self.load)
        btnLayout.addWidget(loadBtn)

        refreshBtn = QtWidgets.QPushButton("Refresh")
        refreshBtn.clicked.connect(self.populateUI)
        btnLayout.addWidget(refreshBtn)

        deleteBtn = QtWidgets.QPushButton("Delete")
        deleteBtn.clicked.connect(self.delete)
        btnLayout.addWidget(deleteBtn)

        self.layout.addWidget(self.brand)

    def populateUI(self):
        """This method clears and re-populates the list widget"""
        self.listWidget.clear()
        self.library.find()

        sorted_dict = sorted(self.library.items(), key=operator.itemgetter(0))

        for name, info in sorted_dict:  # key and value of dict
            item = QtWidgets.QListWidgetItem(name)
            self.listWidget.addItem(item)

            # add screenshot
            screenshot = info.get('screenshot')
            if screenshot:
                icon = QtGui.QIcon(screenshot)
                item.setIcon(icon)

            item.setToolTip(pprint.pformat(info))

    def load(self):
        """This method loads the attribute set"""
        currentItem = self.listWidget.currentItem()

        if not currentItem:
            return

        name = currentItem.text()
        cmds.undoInfo(openChunk=True, cn="Load Operation")
        try:
            self.library.load(name)
        except:
            traceback.print_exc()
        cmds.undoInfo(closeChunk=True, cn="Load Operation")
        mnpr_runner.reloadConfig()


    def save(self):
        """This method saves the attribute set"""
        name = self.saveInput.text()
        if not name.strip():
            cmds.warning("You must give a name")
            return

        self.library.save(name)
        self.populateUI()
        self.saveInput.setText("")

    def delete(self):
        """This method deletes the attribute set"""
        currentItem = self.listWidget.currentItem()

        if not currentItem:
            return

        deletePrompt = cmds.confirmDialog(title='Delete item',
                message='Do you really wish to delete this item?\nThere is no way of undoing this action.',
                button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No', ma='center')
        if deletePrompt == 'Yes':
            # get path and screenshot path
            name = currentItem.text()
            filePath = self.library[name]["path"]
            screenshotPath = self.library[name]["screenshot"]

            # remove files
            os.remove(filePath)
            os.remove(screenshotPath)

            self.populateUI()
