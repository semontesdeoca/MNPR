"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                _       _       _______  __
    _ __   __ _(_)_ __ | |_    |  ___\ \/ /
   | '_ \ / _` | | '_ \| __|   | |_   \  /
   | |_) | (_| | | | | | |_    |  _|  /  \
   | .__/ \__,_|_|_| |_|\__|   |_|   /_/\_\
   |_|
@summary:       PaintFX classes and functions
                PaintFX is responsible for the mapped effect control

"""
from __future__ import print_function
import os, math, logging
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om  # python api 2.0
import coopLib as lib
import mnpr_system
import mnpr_info

try:
    xrange          # Python 2
except NameError:
    xrange = range  # Python 3

logging.basicConfig()  # errors and everything else (2 separate log groups)
logger = logging.getLogger("pFX")  # create a logger for this file
logger.setLevel(logging.DEBUG)  # defines the logging level (INFO for releases)
# logger.setLevel(logging.INFO)  # defines the logging level (DEBUG for debugging)


def getId(mat, uniqueNodeName):
    """
    Utility function to get the id of uniqueNodeName within mat
    Args:
        mat (str): Material to get node id from
        uniqueNodeName (str): Unique node name in ShaderFX
    Returns:
        (int): Node id in ShaderFX graph
    """
    nodeId = cmds.shaderfx(sfxnode=mat, getNodeIDByName=uniqueNodeName)

    return nodeId


def enableVtxCtrl(shapes):
    """
    Enable vertex color control on shapes
    Args:
        shapes (list): List of shapes (str) to enable vertex control to
    """
    # enable ctrl in material
    selected = cmds.ls(sl=True, l=True)
    cmds.hyperShade(smn=True)
    mats = cmds.ls(sl=True, l=True, mat=True)
    for mat in mats:
        if cmds.nodeType(mat) == "ShaderfxShader":
            nodeId = getId(mat, "vtxControls")
            cmds.shaderfx(sfxnode=mat, edit_bool=(nodeId, "value", True))
        else:
            if cmds.attributeQuery("xUseControl", node=mat, ex=True):
                lib.setAttr(mat, "xUseControl", True)
            if cmds.attributeQuery("Color0_Source", node=mat, ex=True):
                lib.setAttr(mat, "Color0_Source", "color:controlSetA")
            if cmds.attributeQuery("Color1_Source", node=mat, ex=True):
                lib.setAttr(mat, "Color1_Source", "color:controlSetB")
            if cmds.attributeQuery("Color2_Source", node=mat, ex=True):
                lib.setAttr(mat, "Color2_Source", "color:controlSetC")
    cmds.select(selected, r=True)

    # create vtx control sets
    for shape in shapes:
        colorSets = cmds.polyColorSet(shape, query=True, allColorSets=True)
        if not colorSets:
            colorSets = []
        if "controlSetC" not in colorSets:
            logger.debug("Creating control sets for {0}".format(shape))
            # create color sets
            cmds.polyColorSet(shape, cs='controlSetA', create=True)
            cmds.polyColorSet(shape, cs='controlSetB', create=True)
            cmds.polyColorSet(shape, cs='controlSetC', create=True)
            defaultVertexColors(shape)


def defaultVertexColors(shape):
    """
    Assign default vertex colors to shape
    Args:
        shape (str): Shape to assign default vertex colors to
    """
    oShape = lib.getMObject(shape)
    fnMesh = om.MFnMesh(oShape)  # access mesh data (oShape can also be replaced by MDagPath of shape)
    #controlSetA
    oVertexColorArray = fnMesh.getVertexColors('controlSetA')  # MColorArray
    vertexListLength = len(oVertexColorArray)
    vertexIndexArray = list(xrange(vertexListLength))
    for vertex in vertexIndexArray:
        oVertexColorArray[vertex].r = 0.0
        oVertexColorArray[vertex].g = 0.0
        oVertexColorArray[vertex].b = 0.0
        oVertexColorArray[vertex].a = 0.0
    fnMesh.setCurrentColorSetName('controlSetA')
    fnMesh.setVertexColors(oVertexColorArray, vertexIndexArray)
    #controlSetB
    oVertexColorArray = fnMesh.getVertexColors('controlSetB') #MColorArray
    for vertex in vertexIndexArray:
        oVertexColorArray[vertex].r = 0.0
        oVertexColorArray[vertex].g = 0.0
        oVertexColorArray[vertex].b = 0.0
        oVertexColorArray[vertex].a = 0.0
    fnMesh.setCurrentColorSetName('controlSetB')
    fnMesh.setVertexColors(oVertexColorArray, vertexIndexArray)
    #controlSetC
    oVertexColorArray = fnMesh.getVertexColors('controlSetC') #MColorArray
    for vertex in vertexIndexArray:
        oVertexColorArray[vertex].r = 0.0
        oVertexColorArray[vertex].g = 0.0
        oVertexColorArray[vertex].b = 0.0
        oVertexColorArray[vertex].a = 0.0
    fnMesh.setCurrentColorSetName('controlSetC')
    fnMesh.setVertexColors(oVertexColorArray, vertexIndexArray)
    print("vertex colors should have been set")


@lib.timer
def update2MNPR():
    """
    Updates older versions
    """
    if mnpr_system.refreshShaders():
        # delete old config node
        if cmds.objExists("watercolorConfig"):
            if not cmds.ls(sl=True):
                cmds.error("Please select all objects you wish to upgrade to work with MNPR")
            cmds.delete("watercolorConfig")

            mnpr_system.check()  # check system and create new config node

            selected = cmds.ls(sl=True)
            selectedShapes = cmds.ls(selected, s=True)
            for shape in selectedShapes:
                selected.remove(shape)
                # add transform node instead
                selected.insert(0, cmds.listRelatives(shape, f=True, p=True)[0])
            cmds.select(selected, r=True)

            # update all shapes
            logger.info("Updating vertex color sets of: {0}".format(selected))
            shapes = cmds.listRelatives(selected, shapes=True, noIntermediate=True, path=True)
            logger.debug(shapes)
            if not shapes:
                cmds.error("Some selected objects were not meshes!")
            for shape in shapes:
                translateVtxCtrl(shape)

            # update vertex color sets mapping in shaders
            if os.name == 'nt' and mnpr_info.backend == 'dx11':
                shaders = cmds.ls(type="dx11Shader")
            else:
                shaders = cmds.ls(type="GLSLShader")
            if shaders:
                for shader in shaders:
                    if cmds.attributeQuery("Color0_Source", node=shader, ex=True):
                        cmds.setAttr("{0}.Color0_Source".format(shader), "color:controlSetA", type="string")
                    if cmds.attributeQuery("Color1_Source", node=shader, ex=True):
                        cmds.setAttr("{0}.Color1_Source".format(shader), "color:controlSetB", type="string")
                    if cmds.attributeQuery("Color2_Source", node=shader, ex=True):
                        cmds.setAttr("{0}.Color2_Source".format(shader), "color:controlSetC", type="string")

                # refresh shader to show changes
                if os.name == 'nt' and mnpr_info.backend == 'dx11':
                    cmds.dx11Shader(shaders[0], r=True)
                else:
                    cmds.GLSLShader(shaders[0], r=True)

        mnpr_system.dx112sfx()


def translateVtxCtrl(shape):
    """
    Translates vertex color parameters to conform with new parametrization schemes
    Args:
        shape (string): Shape to translate vertex color parameters
    """
    logger.info("Changing ctrl assignments in shape: {0}".format(shape))
    v1 = False  # checking if its not the fist prototype

    colorSets = cmds.polyColorSet(shape, query=True, allColorSets=True)
    # update existing color sets
    if colorSets:
        logger.debug(colorSets)
        # check if default controlSetB exists (this will tell us if the color sets have been updated in the shape)
        if "controlSetB" not in colorSets:
            v1 = True
            if "colorSet1" in colorSets:
                cmds.polyColorSet(shape, rename=True, colorSet="colorSet1", newColorSet='controlSetA')
            if "controlSetA" not in cmds.polyColorSet(shape, query=True, allColorSets=True ):
                # shape has color set but has not been prepped
                logger.info("{0} has not been prepped, skipping.".format(shape))
                return
            # copy colorSetA to controlSetB and controlSetC
            cmds.polyColorSet(shape, copy=True, colorSet='controlSetA', newColorSet='controlSetB')
            cmds.polyColorSet(shape, copy=True, colorSet='controlSetA', newColorSet='controlSetC')
        # modulate channels in maya python API
        # initialize objects
        oShape = lib.getMObject(shape)  # grabs the MObject of the shape
        fnMesh = om.MFnMesh(oShape)  # access mesh data (oShape can also be replaced by MDagPath)
        # controlSetA
        oVertexColorArrayA = fnMesh.getVertexColors('controlSetA')  # MColorArray
        vertexListLength = len(oVertexColorArrayA)
        vertexIndexArray = list(xrange(vertexListLength))
        if v1:
            for vertex in vertexIndexArray:
                oVertexColorArrayA[vertex].r = 0.5
                oVertexColorArrayA[vertex].g = max(min(2.5 * oVertexColorArrayA[vertex].g, 1.0), 0.4)
                oVertexColorArrayA[vertex].b = min((1.0 - oVertexColorArrayA[vertex].a) * 1.2, 1.0)
                oVertexColorArrayA[vertex].a = 0
        for vertex in vertexIndexArray:
            oVertexColorArrayA[vertex].r = 0.0
            oVertexColorArrayA[vertex].g = (oVertexColorArrayA[vertex].g - 0.5) * 2.0
            oVertexColorArrayA[vertex].b = (oVertexColorArrayA[vertex].b - 0.6) * 1.67
        fnMesh.setCurrentColorSetName('controlSetA')
        fnMesh.setVertexColors(oVertexColorArrayA, vertexIndexArray)
        # controlSetB
        oVertexColorArrayB = fnMesh.getVertexColors('controlSetB')  # MColorArray
        if v1:
            for vertex in vertexIndexArray:
                oVertexColorArrayB[vertex].r = min(2.0 * oVertexColorArrayB[vertex].r, 1.0)
                oVertexColorArrayB[vertex].g = 0.5
                oVertexColorArrayB[vertex].b = 0.5
                oVertexColorArrayB[vertex].a = 0
        for vertex in vertexIndexArray:
            oVertexColorArrayB[vertex].r = (oVertexColorArrayB[vertex].r - 0.2) * 1.25
            oVertexColorArrayB[vertex].g = 0
            oVertexColorArrayB[vertex].b = 0
        fnMesh.setCurrentColorSetName('controlSetB')
        fnMesh.setVertexColors(oVertexColorArrayB, vertexIndexArray)
        # controlSetC
        oVertexColorArrayC = fnMesh.getVertexColors('controlSetC')  # MColorArray
        if v1:
            for vertex in vertexIndexArray:
                oVertexColorArrayC[vertex].r = 0.2
                oVertexColorArrayC[vertex].g = 0.5
                oVertexColorArrayC[vertex].b = max(0.0, (oVertexColorArrayC[vertex].b - 0.5) * 2)
                oVertexColorArrayC[vertex].a = 0.5
        for vertex in vertexIndexArray:
            oVertexColorArrayC[vertex].r = (oVertexColorArrayC[vertex].r - 0.2) * 1.25
            oVertexColorArrayC[vertex].g = (oVertexColorArrayC[vertex].g - 0.5) * 2.0
            blue = oVertexColorArrayC[vertex].b
            oVertexColorArrayC[vertex].b = (oVertexColorArrayC[vertex].a - 0.5) * 2.0
            oVertexColorArrayC[vertex].a = max((blue - 0.5) * 2.0, 0.0)
        fnMesh.setCurrentColorSetName('controlSetC')
        fnMesh.setVertexColors(oVertexColorArrayC, vertexIndexArray)
        print("Control parameters changed in shape: {0}".format(shape))
    else:
        logger.info("{0} has not been prepped, skipping.".format(shape))


def checkPaintingContext():
    """
    Checks the painting context to check that everything is in order
    """
    resetContext = False
    if cmds.artAttrCtx("artAttrColorPerVertexContext", exists=True):
        resetContext = False

    mel.eval("PaintVertexColorTool;")  # make sure the paint vertex context exists

    if resetContext:
        cmds.resetTool('artAttrColorPerVertexContext')
        cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', stampProfile="gaussian", e=True)


def paintClicked(widget):
    """
    Paint operations when icon is clicked
    """
    logger.debug("paintClicked() from {0}".format(widget.fx))
    if not widget.amountSld.value():
        paintToggleClicked(widget)
    else:
        paintValueChanged(widget)


def paintIndex(widget):
    """
    Returns the index of the current paint operation
    Args:
        widget (PaintWidget): PaintWidget object calling the function
    Returns:
        (int): Index of the painting operation
    """
    paintType = ""
    for key in widget.fx.paintOptions:
        if widget.optionWidgets[key].isChecked():
            paintType = key
    return widget.fx.paintOptions.index(paintType)


def paintValueChanged(widget):
    """
    Runs when the slider value has been changed
    Args:
        widget (PaintWidget): PaintWidget object calling the function
    """
    checkPaintingContext()
    # get paintType and paint value
    paintType = ""
    for key in widget.fx.paintOptions:
        if widget.optionWidgets[key].isChecked():
            paintType = key
    paintValue = widget.amountSld.value()
    # modify UI
    operationIndex = widget.fx.paintOptions.index(paintType)
    if paintValue > 0:
        if operationIndex % 2:
            widget.optionWidgets[widget.fx.paintOptions[operationIndex - 1]].setChecked(True)
            paintType = widget.fx.paintOptions[operationIndex - 1]
    else:
        if not (operationIndex % 2):
            widget.optionWidgets[widget.fx.paintOptions[operationIndex + 1]].setChecked(True)
            paintType = widget.fx.paintOptions[operationIndex + 1]
    logger.debug("Painting {0} with type {1} and value {2}".format(widget.fx.name, paintType, paintValue))

    # find channels
    operation = int(math.floor(widget.fx.paintOptions.index(paintType) / 2.0))
    channels = widget.fx.channels[operation]

    # find channel to paint
    channelIndex = 0
    for channel in channels:
        if channel:
            channelIndex = channels.index(channel)
            break

    # find paint value
    channels[channelIndex] = abs(paintValue) / 100.0

    if paintValue > 0:
        paint(RGBA=channels, paintType="additive", colorSet=widget.fx.controlSet)
    else:
        paint(RGBA=channels, paintType="subtract", colorSet=widget.fx.controlSet)

    #mel.eval("PaintVertexColorTool;")


def paintToggleClicked(widget):
    """
    Runs when a toggle is clicked
    Args:
        widget (PaintWidget): PaintWidget object calling the function
    """
    logger.debug("paintToggleClicked() from {0}".format(widget.fx.name))
    paintType = ""
    for key in widget.fx.paintOptions:
        if widget.optionWidgets[key].isChecked():
            paintType = key
    signum = ((widget.fx.paintOptions.index(paintType) % 2) * -2) + 1
    sliderValue = widget.amountSld.value()
    # check when slider is 0
    if sliderValue == 0:
        widget.amountSld.setValue(50 * signum)
        return
    # normal behaviour
    if sliderValue < 0:
        if signum > 0:
            widget.amountSld.setValue(-widget.amountSld.value())
    else:
        if signum < 0:
            widget.amountSld.setValue(-widget.amountSld.value())


def paintFloodClicked(widget, reset=False):
    """
    Floods the selected geometry with a value
    Args:
        widget (PaintWidget): PaintWidget object calling the function
        reset: if flood needs to reset or add/subtract
    """
    logger.debug("paintFloodClicked() from {0} with reset = {1}".format(widget.fx.name, reset))

    # find flood type
    floodType = ""
    for key in widget.fx.paintOptions:
        if widget.optionWidgets[key].isChecked():
            floodType = key
    operation = int(math.floor(widget.fx.paintOptions.index(floodType) / 2.0))
    # find channels
    channels = widget.fx.channels[operation]
    # perform flood operation
    if reset:
        # reset vertex colors
        vertexColorFloodMaya(widget.fx.controlSet, 0, channels, True)
    else:
        value = widget.amountSld.value()
        # make sure there is a value
        if value == 0:
            value = 50
            widget.amountSld.setValue(50)
        # flood vertex colors
        paintValue = value / 100.0 / 2.0  # normalize between 0 - 0.5
        vertexColorFloodMaya(widget.fx.controlSet, paintValue, channels, False)


def paintKeyClicked(widget, key=True):
    """
    Inserts or removes a keyframe on the vertex colors of a shape
    Args:
        widget (PaintWidget): PaintWidget object calling the function
        key (bool): Key or remove key
    """
    # get vertices to key
    mel.eval("ConvertSelectionToVertices;")
    selectedVertices = cmds.ls(sl=True, et="float3")
    if selectedVertices:
        c = ["ColorR", "ColorG", "ColorB", "Alpha"]
        # get shape, channels and colorset
        shapes = lib.getShapes(selectedVertices)
        channels = widget.fx.channels
        colorSet = widget.fx.controlSet
        cmds.polyColorSet(shapes, currentColorSet=True, cs=colorSet)  # sets the current color set of shapes

        # get suffix of attribute to key
        channelIdx = math.trunc(paintIndex(widget)/2.0)
        suffix = ""
        for idx in xrange(len(channels[channelIdx])):
            if channels[channelIdx][idx]:
                 suffix = c[idx]
                 break
        # vertex colors in maya are stored per adjacent face, to minimize the amount
        # of animation curves, we can find exactly which vtx face and attribute to key
        # in the specified vertex color set, and its respective polyColorPerVertex node
        vtxFaces = [vtx.replace("vtx", "vtxFace") for vtx in selectedVertices]
        vtxFaceAttrs = cmds.listAttr(vtxFaces, s=True)  # list attributes of adjacent faces
        attributes = [attr for attr in vtxFaceAttrs if "vertexFace{0}".format(suffix) in attr]
        pColorVertexNodes = polyColorPerVertexNodes(shapes, colorSet)
        if pColorVertexNodes:
            for attr in attributes:
                if key:
                    # key vertex color attribute
                    cmds.setKeyframe("{0}.{1}".format(pColorVertexNodes[0], attr))
                else:
                    # remove the vertex color key
                    currentTime = cmds.currentTime(query=True)
                    cmds.cutKey("{0}.{1}".format(pColorVertexNodes[0], attr), time=(currentTime, currentTime))
        else:
            cmds.error("History has been deleted from the mesh object, keying of vertex colors is impossible")

    showKeyedTimeline(widget)


def showKeyedTimeline(widget):
    """
    Selects the polyColorPerVertex node associated to the geometry to show its timeline and keys
    Args:
        widget (PaintWidget): PaintWidget object calling the function
    """
    selected = cmds.ls(sl=True)
    if not selected:
        cmds.error("Nothing selected")

    # check if another polyColorPerVertex node exists
    pColorPerVertexNode = [node for node in selected if cmds.nodeType(node) == "polyColorPerVertex"]
    if pColorPerVertexNode:
        cmds.select(pColorPerVertexNode[0], d=True)
        selected.remove(pColorPerVertexNode[0])

    # add current polyColorPerVertex node to selection
    pColorVertexNodes = polyColorPerVertexNodes(selected, widget.fx.controlSet)
    cmds.select(pColorVertexNodes, add=True)


def polyColorPerVertexNodes(objs, colorSet=""):
    """
    Returns the polyColorPerVertex nodes associated to the passed objects
    Args:
        objs (lst): List of objects to search within
        colorSet (str): Return the polyColorPerVertex node associated to the specified color set
    Returns:
        (list): polyColorPerVertex nodes
    """
    history = cmds.listHistory(objs, leaf=True, interestLevel=1)
    nodes = [node for node in history if cmds.nodeType(node) == "polyColorPerVertex"]
    if colorSet:
        return [node for node in nodes if cmds.getAttr("{0}.colorSetName".format(node)) == colorSet]
    else:
        return nodes


def paint(RGBA, paintType, cClamp=["none", 0, 1], aClamp=["none", 0, 1], colorSet="controlSetA"):
    """
    Set artisan context with painting and brush parameters for artAttrPaintVertexCtx
    Args:
        RGBA (list): Channels to paint e.g. [ 0, 1, 0, 0 ]
        paintType (str): "additive" or "subtract"
        cClamp (list): Clamping settings for color [clamp, clamplower, clampupper]
        aClamp (list): Clamping settings for alpha [clamp, clamplower, clampupper]
        colorSet (str): Color set to paint into
    """
    # SET UP ARTISAN CONTEXT
    # set channels to RGBA and enable paint tool attributes
    cmds.radioButtonGrp('artAttrColorChannelChoices', sl=2, e=True)  # set to RGBA in artisan UI
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', paintRGBA=True, e=True)  # set to RGBA
    cmds.floatSliderGrp('colorPerVertexAlpha', en=True, e=True)  # enable alpha painting
    cmds.floatFieldGrp('colorPerVertexMinMaxAlphaValue', en=True, e=True)  # enable alpha min max
    cmds.checkBoxGrp('artAttrAlphaClampChkBox', en=True, e=True)  # enable alpha clamp checkbox

    # before stroke command
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext',
                               bsc="artAttrPaintVertexCtx -edit -showactive 0 artAttrColorPerVertexContext", e=True)
    # after stroke command
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext',
                               asc="artAttrPaintVertexCtx -edit -showactive 1 artAttrColorPerVertexContext", e=True)

    # PREPARE MESHES
    selected = cmds.ls(sl=True)
    shapes = lib.getShapes(selected)
    enableVtxCtrl(shapes)

    # SET UP PAINTING PARAMETERS
    cmds.polyColorSet(shapes, currentColorSet=True, cs=colorSet)  # sets the current color set of all shapes
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', selectedattroper=paintType, e=True)  # add or substract color
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', cl4=RGBA, e=True)  # define channels to paint
    cmds.floatSliderGrp('colorPerVertexAlpha', value=RGBA[3], e=True)  # set alpha painting value
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', opacity=0.2, e=True)  # set opacity to 0.2
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', accopacity=True, e=True)  # oppacity accumulates
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', clamp=cClamp[0], e=True)  # color clamp
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', clamplower=cClamp[1], e=True)  # lower clamp
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', clampupper=cClamp[2], e=True)  # upper clamp
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', alphaclamp=aClamp[0], e=True)  # alpha clamp
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', alphaclamplower=aClamp[1], e=True)  # alpha lower clamp
    cmds.artAttrPaintVertexCtx('artAttrColorPerVertexContext', alphaclampupper=aClamp[2], e=True)  #alpha upper clamp


@lib.timer
def vertexColorFloodMaya(colorSet, value, channels=[False, False, False, False], replace=True):
    """
    Assigns vertex colors to a specific colorSet of all selected objects
    Args:
        colorSet (str): Which color set to flood
        value (float): What value to flood the color with
        channels (bool lst): RGBA list of color channels to flood
        replace (bool): If the value needs to be replaced
    """
    logger.debug("-> Flooding {0} at channels {1} with value {2}".format(colorSet, channels, value))
    channelChars = ['r', 'g', 'b', 'a']
    # find selected shapes
    selected = cmds.ls(sl=True)
    shapes = lib.getShapes(selected)
    enableVtxCtrl(shapes)
    # set the current color set
    try:
        cmds.polyColorSet(shapes, currentColorSet=True, cs=colorSet)  # sets the current color set of all shapes
    except RuntimeError:
        cmds.error("One or more of the objects has not been prepped")
    # find channel to flood
    for channel in channels:
        if channel:
            channelChar = channelChars[channels.index(channel)]
            if replace:
                logger.debug("Resetting control parameters in: {0} with {1}".format(shapes, value))
                eval("cmds.polyColorPerVertex({0}={1})".format(channelChar, value))
            else:
                logger.debug("Flooding control parameters in: {0} with {1}".format(shapes, value))
                eval("cmds.polyColorPerVertex({0}={1}, rel=True)".format(channelChar, value))


#    _                            _      __                         _
#   (_)_ __ ___  _ __   ___  _ __| |_   / /____  ___ __   ___  _ __| |_
#   | | '_ ` _ \| '_ \ / _ \| '__| __| / / _ \ \/ / '_ \ / _ \| '__| __|
#   | | | | | | | |_) | (_) | |  | |_ / /  __/>  <| |_) | (_) | |  | |_
#   |_|_| |_| |_| .__/ \___/|_|   \__/_/ \___/_/\_\ .__/ \___/|_|   \__|
#               |_|                               |_|
def exportPaintFX():
    """
    Export the painted vertex colors of the selected objects to a json file
    """
    # get selected objects
    selected = cmds.ls(sl=True)

    # get save directory
    fileFilter = "*.json"
    exportPath = cmds.fileDialog2(fileFilter=fileFilter, fileMode=0,
                                  startingDirectory=cmds.workspace(rd=True, q=True),
                                  cap="Export vertex parameters as:", dialogStyle=2)
    if not exportPath:
        cmds.error("Filename not specified")
    exportPath = exportPath[0]

    lib.exportVertexColors(selected, exportPath)


def importPaintFX():
    """
    Import vertex colors of a previously exported json file
    """
    # get import directory
    fileFilter = "*.json"
    importPath = cmds.fileDialog2(fileFilter=fileFilter, fileMode=1,
                                  startingDirectory=cmds.workspace(rd=True, q=True),
                                  cap="Import vertex parameters from:", dialogStyle=2)
    if not importPath:
        cmds.error("Filename not specified")
    importPath = importPath[0]

    lib.importVertexColors(importPath)
