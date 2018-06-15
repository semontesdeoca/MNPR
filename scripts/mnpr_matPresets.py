"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                  _            _       _                              _
  _ __ ___   __ _| |_ ___ _ __(_) __ _| |    _ __  _ __ ___  ___  ___| |_ ___
 | '_ ` _ \ / _` | __/ _ \ '__| |/ _` | |   | '_ \| '__/ _ \/ __|/ _ \ __/ __|
 | | | | | | (_| | ||  __/ |  | | (_| | |   | |_) | | |  __/\__ \  __/ |_\__ \
 |_| |_| |_|\__,_|\__\___|_|  |_|\__,_|_|   | .__/|_|  \___||___/\___|\__|___/
                                            |_|
@summary:       MNPR's material presets interface and implementation
"""
from __future__ import print_function
import os, json, logging, pprint, operator, traceback
from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import coopLib as lib
import coopQt as qt
import mnpr_system
import mnpr_info
import mnpr_pFX

# LOGGING
logging.basicConfig()  # errors and everything else (2 separate log groups)
logger = logging.getLogger("matPresets")  # create a logger for this file
logger.setLevel(logging.DEBUG)  # defines the logging level (INFO for releases)
# logger.setLevel(logging.INFO)  # defines the logging level (DEBUG for debugging)

PATH = lib.Path(os.path.dirname(os.path.realpath(__file__))).parent()

# setting nodes
settingNodes = {"reflectanceModel",
                "vtxControls",
                "Shadow",
                "Flip-Back-Faces",
                "Transparent",
                "Specularity",
                "specularModel",
                "Specular-In-Transparent",
                "maxLights"
}

# procedural setting nodes
procSettingNodes = {"Variation_Procedural_MNPR",
                   "Variation_3D_MNPR",
                   "Application_Procedural_MNPR",
                   "Application_3D_MNPR",
                   "Density_Procedural_MNPR",
                   "Density_3D_MNPR",
                   "Detail_Procedural_MNPR",
                   "Detail_3D_MNPR",
                   "Distortion_Procedural_MNPR",
                   "Distortion_3D_MNPR",
                   "uIncline_Procedural_MNPR",
                   "uIncline_3D_MNPR",
                   "vIncline_Procedural_MNPR",
                   "vIncline_3D_MNPR",
                   "Shape_Procedural_MNPR",
                   "Shape_3D_MNPR",
                   "Edge_Procedural_MNPR",
                   "Edge_3D_MNPR",
                   "Transition_Procedural_MNPR",
                   "Transition_3D_MNPR",
                   "Blending_Procedural_MNPR",
                   "Blending_3D_MNPR"
}


# get material from selection
def getMaterial(selected):
    """
    Gets the material and its associated transforms
    Args:
        selected (list): list of selected objects

    Returns:
        Material (str), Transforms (list)
    """
    selection = cmds.ls(selected, l=True, o=True)
    if not selection:
        cmds.error("No selection was made")

    # get transforms and materials
    transforms = cmds.ls(selection, l=True, et="transform")
    materials = cmds.ls(selection, l=True, mat=True)

    # initialize sets
    xfmSet = set(transforms)
    matSet = set(materials)

    # if transforms were selected, add materials to set
    for xfm in xfmSet:
        cmds.select(xfm, r=True)
        cmds.hyperShade(smn=True)
        sMat = cmds.ls(sl=True, l=True, mat=True)
        if not sMat:
            sMat = "lambert1"
            cmds.hyperShade(sMat)
            logger.debug("No material on selected transform nodes, connected default material.")
        else:
            sMat = sMat[0]
        matSet.add(sMat)

    # if materials were selected, add transforms to set
    for mat in matSet:
        cmds.hyperShade(objects=mat)
        shape = cmds.ls(sl=True)
        # materials may exist without being assigned
        if shape:
            transform = (cmds.listRelatives( shape, fullPath=True, parent=True ))[0]
            xfmSet.add(transform)

    # if shapes were selected, add transforms and materials to sets
    shapes = cmds.ls(selection, l=True, et="mesh")
    for shape in shapes:
        transform = (cmds.listRelatives( shape, fullPath=True, parent=True ))[0]
        xfmSet.add(transform)
        cmds.select(transform, r=True)
        cmds.hyperShade(smn=True)
        matSet.add(cmds.ls(sl=True, l=True, mat=True)[0])

    # check for one material only
    if len(matSet) != 1:
        cmds.error("{0} was selected, please select objects with only one material.".format(selection))

    cmds.select(selected, r=True)

    return list(matSet)[0], list(xfmSet)


def createMaterial(objs, name="mnprMat_SFX", prototype="shaderFX", graph="mnpr_uber"):
    """
    Create and assign material to all objs
    Args:
        name (str): Name of new material
        objs (list): List of objects to assign new material into
        prototype (str): "shaderFX" or "prototypeC"
    Returns: Material name (str)
    """
    logger.debug("Creating new material for {0}".format(objs))

    # get shader file
    shaderFile = os.path.join(mnpr_info.environment, "shaders", "{0}.sfx".format(graph))
    if prototype != "shaderFX":
        if os.name == 'nt' and mnpr_info.backend == 'dx11':
            shaderFile = os.path.join(mnpr_info.environment, "shaders", "{0}.fx".format(prototype))
            if not os.path.isfile(shaderFile):
                shaderFile = os.path.join(mnpr_info.environment, "shaders", "{0}.fxo".format(prototype))
        else:
            shaderFile = os.path.join(mnpr_info.environment, "shaders", "{0}.ogsfx".format(prototype))

    # check if objects are meshes
    shapes = lib.getShapes(objs)
    if not len(shapes):
        cmds.error("{0} -> All selected objects need to be meshes".format(objs))

    # generate name of material
    newName = "{0}_{1}".format(name, mnpr_info.abbr)

    shader = ""
    if prototype == "shaderFX":
        shader = cmds.shadingNode('ShaderfxShader', asShader=True, name=name)
        cmds.shaderfx(sfxnode=shader, loadGraph=shaderFile)
    else:
        if os.name == 'nt' and mnpr_info.backend == 'dx11':
            shader = cmds.shadingNode('dx11Shader', asShader=True, n=newName)
        else:
            shader = cmds.shadingNode('GLSLShader', asShader=True, n=newName)

    # assign shader to selected
    cmds.select(objs, r=True)
    cmds.hyperShade(assign=shader)

    if prototype != "shaderFX":
        lib.setAttr(shader, "shader", shaderFile)
        lib.setAttr(shader, "xUseControl", False)

    return shader


def defaultLighting():
    """
    Creates the default lighting in the scene
    Useful when there is no lighting in the scene
    """
    # check if lights exist
    if cmds.ls(lt=True):
        return
    # save current selection
    selected = cmds.ls(sl=True, l=True)
    # create and place test light
    lightShape = cmds.directionalLight()
    lightXform = cmds.listRelatives(lightShape, p=True)[0]
    cmds.setAttr("{0}.tx".format(lightXform), 5)
    cmds.setAttr("{0}.ty".format(lightXform), 5)
    cmds.setAttr("{0}.ry".format(lightXform), 90)
    cmds.setAttr("{0}.rz".format(lightXform), 45)
    # activate lights on viewport
    viewport = lib.getActiveModelPanel()
    cmds.modelEditor(viewport, edit=True, displayLights="all")
    # bring back selection
    cmds.select(selected, r=True)


def getMaterialAttrs(mat, dictionary):
    """
    Adds material attributes to dictionary (e.g., settings, procedural settings, attributes and textures)
    Args:
        mat (str): name of material
        dictionary (dict): dictionary of material attributes
    """
    # get graph name
    nodeId = cmds.shaderfx(sfxnode=mat, getNodeIDByName="graphName")
    dictionary["graph"] = str(cmds.shaderfx(sfxnode=mat, getPropertyValue=(nodeId, "value")))
    # get settings
    settings = {}
    for settingNode in settingNodes:
        try:
            nodeId = cmds.shaderfx(sfxnode=mat, getSettingNodeID=settingNode)
        except RuntimeError:
            continue
        if "value" in cmds.shaderfx(sfxnode=mat, listProperties=nodeId):
            settings[settingNode] = cmds.shaderfx(sfxnode=mat, getPropertyValue=(nodeId, "value"))
        else:
             settings[settingNode] = cmds.shaderfx(sfxnode=mat, getPropertyValue=(nodeId, "options"))[-1]
    dictionary['settings'] = settings
    # get procedural settings
    procSettings = {}
    for settingNode in procSettingNodes:
        try:
            nodeId = cmds.shaderfx(sfxnode=mat, getNodeIDByName=settingNode)
        except RuntimeError:
            continue
        procSettings[settingNode] = cmds.shaderfx(sfxnode=mat, getPropertyValue=(nodeId, "value"))
    dictionary['procSettings'] = procSettings
    # get attributes and textures
    setAttrs = cmds.listAttr(mat, k=True)
    setTextures = cmds.listAttr(mat, uf=True)
    attributes = {}
    for attr in setAttrs:
        attributes[attr] = cmds.getAttr("{0}.{1}".format(mat, attr))
    dictionary['attributes'] = attributes
    textures = {}
    for texture in setTextures:
        textures[texture] = cmds.getAttr("{0}.{1}".format(mat, texture))
    dictionary['textures'] = textures


def setMaterialAttrs(mat, matAttrs, options={}):
    """
    Sets material attributes found in matAttrs (e.g., settings, procedural settings, attributes and textures)
    Args:
        mat (str): name of material
        matAttrs (dict): dictionary of material attributes
        options (dict): dictionary of options to set
    """
    if not options:
        # coming from update, set all to true
        options["textures"] = True
        options["noiseFX"] = True

    # set settings
    settings = matAttrs['settings']
    for setting in settings:
        nodeId = cmds.shaderfx(sfxnode=mat, getNodeIDByName=setting)
        if "value" in cmds.shaderfx(sfxnode=mat, listProperties=nodeId):
            type = cmds.shaderfx(sfxnode=mat, getPropertyType=(nodeId, "value"))
            eval("cmds.shaderfx(sfxnode=mat, edit_{0}=(nodeId, 'value', settings[setting]))".format(type))
        else:
            cmds.shaderfx(sfxnode=mat, edit_stringlist=(nodeId, "options", int(settings[setting])))
    # set procedural settings
    if options["noiseFX"]:
        procSettings = matAttrs['procSettings']
        for setting in procSettings:
            try:
                nodeId = cmds.shaderfx(sfxnode=mat, getNodeIDByName=setting)
                cmds.shaderfx(sfxnode=mat, edit_bool=(nodeId, "value", procSettings[setting]))
            except RuntimeError:
                #traceback.print_exc()
                print("Setting of {0} procedural node has failed".format(setting))
                continue
    # set all attributes
    if mnpr_system.updateAE():
        attributes = matAttrs['attributes']
        for attr in attributes:
            lib.setAttr(mat, attr, attributes[attr], True)
        # set all textures
        if options["textures"]:
            textures = matAttrs['textures']
            for texture in textures:
                lib.setAttr(mat, texture, textures[texture], True)


#                    _            _       _     _ _ _
#    _ __ ___   __ _| |_ ___ _ __(_) __ _| |   | (_) |__
#   | '_ ` _ \ / _` | __/ _ \ '__| |/ _` | |   | | | '_ \
#   | | | | | | (_| | ||  __/ |  | | (_| | |   | | | |_) |
#   |_| |_| |_|\__,_|\__\___|_|  |_|\__,_|_|   |_|_|_.__/
#
class MnprMaterialLibrary(dict):
    """
    Material library
    based on studio.coop's coopAttrManager
    """
    type = "materials"

    def save(self, name, screenshot=True, **info):
        """
        Saves an attribute set to disk
        Args:
            name (str): Name of the attribute set to save
            screenshot (bool): Determines if a screenshot should be saved
            **info: Any additional arguments to be saved in the accompanying json file
        """
        # select custom object
        prevSelection = cmds.ls(sl=True, l=True)
        selection = prevSelection

        # get material from selection
        mat, xforms = getMaterial(selection)
        print(mat, xforms)

        cmds.select(xforms, r=True)

        logger.info("Saving attributes of {0}".format(mat))

        # create directory
        logger.debug("Type of attribute set is: {0}".format(self.type))
        savePath = lib.Path(PATH.path)
        savePath.child("presets").child(self.type).createDir()

        # path to json file to save
        path = os.path.join(savePath.path, "{0}.json".format(name))

        # add to json dictionary
        info['name'] = name
        info['type'] = cmds.objectType(mat)

        # capture screenshot
        if screenshot:
            shotPath = self.saveScreenshot(name, directory=savePath.path)
            info['screenshot'] = os.path.basename(shotPath)

        if info['type'] == 'ShaderfxShader':
            getMaterialAttrs(mat, info)
        else:
            # DEPRECATED (PrototypeC)
            # get attributes
            setTextures = []
            setAttrs = cmds.listAttr(mat, ud=True, st="x*", k=True)  # settable attributes
            attributes = {}
            for attr in setAttrs:
                attributes[attr] = cmds.getAttr("{0}.{1}".format(mat, attr))
            info['attributes'] = attributes
            textures = {}
            for texture in setTextures:
                textures[texture] = cmds.getAttr("{0}.{1}".format(mat, texture))
            info['textures'] = textures

        # write and save json info
        with open(path, 'w') as f:
            json.dump(info, f, indent=4)

        self[name] = info
        # make everything normal again
        cmds.select(prevSelection, r=True)  # restore selection

    def find(self):
        """
        Finds the attribute sets on disk
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

    def load(self, name, options):
        """
        Loads the specified attribute set
        Args:
            name (str): Name of the attribute set to import
        """
        # get data
        selection = cmds.ls(sl=True, l=True)
        mat, xform = getMaterial(selection)
        if not mat:
            cmds.error("Nothing was selected")

        # if not the same material type, create new material
        matType = cmds.objectType(mat)
        try:
            graph = self[name]['graph']
        except KeyError:
            graph = "mnpr_uber"

        prevGraph = "NA"
        if self[name]['type'] != matType:
            mat = createMaterial(xform, graph=graph)
        else:
            # shaderFX shader, get current graph name
            try:
                nodeId = cmds.shaderfx(sfxnode=mat, getNodeIDByName="graphName")
                prevGraph = cmds.shaderfx(sfxnode=mat, getPropertyValue=(nodeId, "value"))
            except RuntimeError:
                pass
            # if a new material is desired, create anyways
            if options["newMaterial"]:
                mat = createMaterial([xform[0]], graph=graph)
            elif graph != prevGraph:
                shaderFile = os.path.join(mnpr_info.environment, "shaders", "{0}.sfx".format(graph))
                cmds.shaderfx(sfxnode=mat, loadGraph=shaderFile)

        # default lighting in case there are no lights
        defaultLighting()

        shapes = lib.getShapes(xform)
        # if colorSets are present, enable control to avoid wrong vertex stylization inputs
        if cmds.polyColorSet(shapes, query=True, allColorSets=True):
            mnpr_pFX.enableVtxCtrl(shapes)
        # disable/enable shadows when proxy geometry is involved
        if graph=="mnpr_geoproxy":
            for shape in shapes:
                lib.setAttr(shape, "castsShadows", False)
                lib.setAttr(shape, "receiveShadows", False)
        elif prevGraph=="mnpr_geoproxy":
            for shape in shapes:
                lib.setAttr(shape, "castsShadows", True)
                lib.setAttr(shape, "receiveShadows", True)

        # set material settings and attributes
        if matType == 'ShaderfxShader':
            setMaterialAttrs(mat, self[name], options)
        else:
            # set attributes in material
            print("->{0} will be replaced".format(mat))
            attrs = self[name]['attributes']
            for attr in attrs:
                lib.setAttr(mat, attr, attrs[attr])
            cmds.select(mat, r=True)

    def saveScreenshot(self, name, directory):
        """
        Saves screenshot out to disk
        Args:
            name: Name of the screenshot
            directory: Directory to save into
        """
        # get camera, current position and focus object
        cameraName = cmds.lookThru(q=True)
        prevPosition = cmds.getAttr("{0}.translate".format(cameraName))
        objName = cmds.ls(sl=True, l=True)
        if objName:
            objName = objName[0]
        else:
            cmds.error("No object has been selected")

        # frame camera to object
        cmds.viewFit()  # 'f' on keyboard
        distance = lib.distanceBetween(cameraName, objName)
        frameDistance = distance*0.5
        cmds.dolly(cameraName, d=-frameDistance)

        # take screenshot
        screenshotDir = mnpr_system.renderFrame(os.path.join(directory, name), 100, 100, 1, ".jpg")

        # bring camera back to normal
        lib.setAttr(cameraName, "translate", prevPosition)
        return screenshotDir


#    _   _ ___
#   | | | |_ _|
#   | | | || |
#   | |_| || |
#    \___/|___|
#
class MnprMaterialPresetsUI(qt.CoopMayaUI):
    """
    The mnprMaterialPresetsUI is a dialog that lets us load and save material presets for MNPR
    """
    def __init__(self, rebuild=True):
        self.library = MnprMaterialLibrary()
        super(MnprMaterialPresetsUI, self).__init__("Material Presets", dock=False, rebuild=rebuild, brand=mnpr_info.brand,
                                              tooltip="UI to create mnpr materials")

    def buildUI(self):
        """This method builds the UI"""
        windowWidget = QtWidgets.QWidget()
        windowLayout = QtWidgets.QHBoxLayout(windowWidget)
        windowLayout.setContentsMargins(0, 5*self.dpiS, 0, 0)

        # start with the tools
        toolWidget = QtWidgets.QWidget()
        toolLayout = QtWidgets.QVBoxLayout(toolWidget)
        toolLayout.setContentsMargins(0, 0, 0, 0)

        # save widget
        saveWidget = QtWidgets.QWidget()
        saveLayout = QtWidgets.QHBoxLayout(saveWidget)
        toolLayout.addWidget(saveWidget)

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
        toolLayout.addWidget(self.listWidget)

        # btn widget
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        toolLayout.addWidget(btnWidget)

        loadBtn = QtWidgets.QPushButton("Load")
        loadBtn.clicked.connect(self.load)
        btnLayout.addWidget(loadBtn)

        refreshBtn = QtWidgets.QPushButton("Refresh")
        refreshBtn.clicked.connect(self.populateUI)
        btnLayout.addWidget(refreshBtn)

        deleteBtn = QtWidgets.QPushButton("Delete")
        deleteBtn.clicked.connect(self.delete)
        btnLayout.addWidget(deleteBtn)

        windowLayout.addWidget(toolWidget)

        # options of tools
        optionsBox = QtWidgets.QGroupBox("Loading options")
        optionsLayout = QtWidgets.QVBoxLayout(optionsBox)
        optionsMargin = 2*self.dpiS
        optionsLayout.setContentsMargins(optionsMargin, optionsMargin, optionsMargin, optionsMargin)
        optionsLayout.setAlignment(QtCore.Qt.AlignTop)

        # add options
        self.newMaterialCBox = QtWidgets.QCheckBox("Create new material")
        optionsLayout.addWidget(self.newMaterialCBox)
        self.withTexturesCBox = QtWidgets.QCheckBox("Load textures")
        self.withTexturesCBox.setChecked(True)
        optionsLayout.addWidget(self.withTexturesCBox)
        self.withNoiseFXCBox = QtWidgets.QCheckBox("Load noiseFX")
        self.withNoiseFXCBox.setChecked(True)
        optionsLayout.addWidget(self.withNoiseFXCBox)

        windowLayout.addWidget(optionsBox)

        # compile window
        self.layout.addWidget(windowWidget)
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
        print(name)
        options = {"newMaterial": self.newMaterialCBox.isChecked(),
                   "textures": self.withTexturesCBox.isChecked(),
                   "noiseFX": self.withNoiseFXCBox.isChecked()}
        cmds.undoInfo(l=100)
        cmds.undoInfo(openChunk=True, cn="Load Operation")
        try:
            self.library.load(name, options)
        except:
            traceback.print_exc()
        cmds.undoInfo(closeChunk=True, cn="Load Operation")

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
