"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                _              _______  __
    _ __   ___ (_)___  ___    |  ___\ \/ /
   | '_ \ / _ \| / __|/ _ \   | |_   \  /
   | | | | (_) | \__ \  __/   |  _|  /  \
   |_| |_|\___/|_|___/\___|   |_|   /_/\_\

@summary:       NoiseFX classes and functions
                NoiseFX is responsible for the material effect control
"""
from __future__ import print_function
import maya.cmds as cmds
import coopLib as lib


lastSelection = []  # last performed selection
lastMaterials = []  # last edited materials


# FX nodes class
class FxNodes:
    """
    FxNodes class contains the unique ShaderFX node names for the procedural noise controls
    """
    def __init__(self, scale, intensity, shift, type, state):
        self.scaleNodeName = scale
        self.intensityNodeName = intensity
        self.shiftNodeName = shift
        self.stateNodeName = state
        self.typeNodeName = type

        # node ids
        self.scale = 0
        self.intensity = 0
        self.shift = 0
        self.state = 0
        self.type = 0

    def refreshIds(self, mat):
        """
            Store the node IDs of the FX nodes
        Args:
            mat (str): Material name to get node ids from
        """
        self.scale = cmds.shaderfx(sfxnode=mat, getNodeIDByName=self.scaleNodeName)
        self.intensity = cmds.shaderfx(sfxnode=mat, getNodeIDByName=self.intensityNodeName)
        self.shift = cmds.shaderfx(sfxnode=mat, getNodeIDByName=self.shiftNodeName)
        self.state = cmds.shaderfx(sfxnode=mat, getNodeIDByName=self.stateNodeName)
        self.type = cmds.shaderfx(sfxnode=mat, getNodeIDByName=self.typeNodeName)


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


#########################################################################################################
# PROCEDURAL CONTROL NAMES
# Dictionary of control node names based on the vertex color control set and the SCHEMA of MNPR
controlNodes = dict()

# pigment control set
variationIds = FxNodes(scale="Variation_Scale_MNPR",
                       intensity="Variation_Intensity_MNPR",
                       shift="Variation_Shift_MNPR",
                       type="Variation_3D_MNPR",
                       state="Variation_Procedural_MNPR")
applicationIds = FxNodes(scale="Application_Scale_MNPR",
                         intensity="Application_Intensity_MNPR",
                         shift="Application_Shift_MNPR",
                         type="Application_3D_MNPR",
                         state="Application_Procedural_MNPR")
densityIds = FxNodes(scale="Density_Scale_MNPR",
                     intensity="Density_Intensity_MNPR",
                     shift="Density_Shift_MNPR",
                     type="Density_3D_MNPR",
                     state="Density_Procedural_MNPR")
detailIds = FxNodes(scale="Detail_Scale_MNPR",
                    intensity="Detail_Intensity_MNPR",
                    shift="Detail_Shift_MNPR",
                    state="Detail_3D_MNPR",
                    type="Detail_Procedural_MNPR")
controlNodes["controlSetA"] = [variationIds, applicationIds, densityIds, detailIds]  # RGBA

# substrate control set
distortionIds = FxNodes(scale="Distortion_Scale_MNPR",
                        intensity="Distortion_Intensity_MNPR",
                        shift="Distortion_Shift_MNPR",
                        type="Distortion_3D_MNPR",
                        state="Distortion_Procedural_MNPR")
uInclineIds = FxNodes(scale="uIncline_Scale_MNPR",
                      intensity="uIncline_Intensity_MNPR",
                      shift="uIncline_Shift_MNPR",
                      type="uIncline_3D_MNPR",
                      state="uIncline_Procedural_MNPR")
vInclineIds = FxNodes(scale="vIncline_Scale_MNPR",
                      intensity="vIncline_Intensity_MNPR",
                      shift="vIncline_Shift_MNPR",
                      type="vIncline_3D_MNPR",
                      state="vIncline_Procedural_MNPR")
shapeIds = FxNodes(scale="Shape_Scale_MNPR",
                   intensity="Shape_Intensity_MNPR",
                   shift="Shape_Shift_MNPR",
                   type="Shape_3D_MNPR",
                   state="Shape_Procedural_MNPR")
controlNodes["controlSetB"] = [distortionIds, uInclineIds, vInclineIds, shapeIds]  # RGBA

# edge control set
intensityIds = FxNodes(scale="Edge_Scale_MNPR",
                       intensity="Edge_Intensity_MNPR",
                       shift="Edge_Shift_MNPR",
                       type="Edge_3D_MNPR",
                       state="Edge_Procedural_MNPR")
widthIds = FxNodes(scale="Edge_Scale_MNPR",
                   intensity="Width_Intensity_MNPR",
                   shift="Edge_Shift_MNPR",
                   type="Edge_3D_MNPR",
                   state="Edge_Procedural_MNPR")
fidelityIds = FxNodes(scale="Transition_Scale_MNPR",
                      intensity="Transition_Intensity_MNPR",
                      shift="Transition_Shift_MNPR",
                      type="Transition_3D_MNPR",
                      state="Transition_Procedural_MNPR")
blendingIds = FxNodes(scale="Blending_Scale_MNPR",
                      intensity="Blending_Intensity_MNPR",
                      shift="Blending_Shift_MNPR",
                      type="Blending_3D_MNPR",
                      state="Blending_Procedural_MNPR")
controlNodes["controlSetC"] = [intensityIds, widthIds, fidelityIds, blendingIds]  # RGBA
# ===========================================================================================


def getNodeNames(fx, idx):
    """
    Get node names of fx operation for procedural effects
    Args:
        fx (obj):  MNPR_FX object
                   e.g. MNPR_FX("distortion", "Substrate distortion", "controlSetB", [[1, 0, 0, 0]], ["distort", "revert"], ["noise"])
        idx (int): index of fx operation in case two operations are found in the same fx object

    Returns:
        (obj):     FxNodes object containing the node names that control each procedural operation
    """
    # get RGBA channel
    channelIdx = 0
    for channel in fx.channels[idx]:
        if channel:
            channelIdx = fx.channels[idx].index(channel)
            break

    # return node names
    return controlNodes[fx.controlSet][channelIdx]


def getMaterials():
    """
    Get material list for procedural effects
    Returns:
        (list): list of materials
    """
    global lastMaterials
    materials = lib.getMaterials(cmds.ls(sl=True))
    if not materials:
        if lastMaterials:
            cmds.warning("No objects with materials have been selected, taking previous selection")
            materials = lastMaterials
        else:
            cmds.error("No objects with materials have been selected")
    else:
        lastMaterials = materials
    return materials


def selectMaterials():
    """
    Selects the materials if they have not been selected already
    """
    if cmds.ls(sl=True) != lastMaterials:
        cmds.select(getMaterials(), r=True)


def noiseWorldScale(widget):
    """
    Modify the world scale value of procedural control
    Args:
        widget (LabeledSlider): LabeledSlider object calling the function
    """
    materials = getMaterials()

    # get value to enter
    valueDiff = widget.slider.relValue()
    valueDiff /= 100.0  # scale between [-1:1]

    # get node names
    worldScale = "World_Scale_MNPR"

    for mat in materials:
        prevValue = cmds.getAttr("{0}.{1}".format(mat, worldScale))
        newValue = prevValue + valueDiff
        lib.setAttr(mat, worldScale, newValue)


def noiseTypeClicked(fx):
    """
    Toggle between noise types (3D or 2D)
    Args:
        fx (MNPR_FX): MnprFx object coming from the caller
    """
    materials = getMaterials()

    # get node names of operation
    sfxNodes = getNodeNames(fx, 0)

    lib.printInfo("Recompiling material")
    typeId = getId(materials[0], sfxNodes.typeNodeName)  # base toggle on first material state
    state = cmds.shaderfx(sfxnode=materials[0], getPropertyValue=(typeId, "value"))
    for mat in materials:
        cmds.shaderfx(sfxnode=mat, edit_bool=(typeId, "value", not state))
    if state:
        lib.printInfo("NoiseFX for {0} is now in 2D".format(fx.description))
    else:
        lib.printInfo("NoiseFX for {0} is now in 3D".format(fx.description))


def noiseToggleClicked(fx):
    """
    Toggle procedural effect (On or Off)
    Args:
        fx (MNPR_FX): MnprFx object coming from the caller
    """
    materials = getMaterials()

    # get node names of operation
    sfxNodes = getNodeNames(fx, 0)

    lib.printInfo("Recompiling material")
    stateId = getId(materials[0], sfxNodes.stateNodeName)  # base toggle on first material state
    state = cmds.shaderfx(sfxnode=materials[0], getPropertyValue=(stateId, "value"))
    for mat in materials:
        stateId = getId(mat, sfxNodes.stateNodeName)
        cmds.shaderfx(sfxnode=mat, edit_bool=(stateId, "value", not state))
    if state:
        lib.printInfo("NoiseFX for {0} is off".format(fx.description))
    else:
        lib.printInfo("NoiseFX for {0} is on".format(fx.description))


def noiseSlide(fx, widget):
    """
    Noise slide, will modify the procedural noise of an effect
    Args:
        fx (MNPR_FX): MNPR_FX object coming from the caller
        widget (LabeledSlider): LabeledSlider object that is calling this function
    """
    # get index of sliding operation
    idx = 0  # default scale index
    if widget.label != "scale":
        idx = fx.procOptions.index(widget.label)

    # get node names of operation
    sfxNodes = getNodeNames(fx, idx)

    # get value to enter
    valueDiff = widget.slider.relValue()
    if widget.label == "scale":
        valueDiff /= 100.0
    else:
        valueDiff /= 5.0

    materials = getMaterials()

    for mat in materials:
        # turn on procedural noise if turned off
        stateId = getId(mat, sfxNodes.stateNodeName)
        if not cmds.shaderfx(sfxnode=mat, getPropertyValue=(stateId, "value")):
            lib.printInfo("Recompiling material")
            cmds.shaderfx(sfxnode=mat, edit_bool=(stateId, "value", True))

        # get attribute name
        attr = ""
        if widget.label != "scale":
            attr = sfxNodes.intensityNodeName
        else:
            attr = sfxNodes.scaleNodeName

        # set attribute
        attribute = "{0}.{1}".format(mat, attr)
        prevValue = cmds.getAttr(attribute)
        newValue = prevValue+valueDiff
        lib.setAttr(mat, attr, newValue)


def noiseShift(fx, widget):
    """
    Noise shift, will shift the procedural noise of an effect
    Args:
        fx (MNPR_FX): MNPR_FX object coming from the caller
        widget (RelativeSlider): RelativeSlider object that is calling this function
    """
    # get value to enter
    valueDiff = widget.relValue()
    valueDiff /= 100.0  # shift between [-1:1]

    # get node names
    sfxNodes = getNodeNames(fx, 0)

    # shift each material
    materials = getMaterials()
    for mat in materials:
        # turn on procedural noise if turned off
        stateId = getId(mat, sfxNodes.stateNodeName)
        if not cmds.shaderfx(sfxnode=mat, getPropertyValue=(stateId, "value")):
            cmds.shaderfx(sfxnode=mat, edit_bool=(stateId, "value", True))

        # set attribute
        prevValue = cmds.getAttr("{0}.{1}".format(mat, sfxNodes.shiftNodeName))
        newValue = prevValue+valueDiff
        lib.setAttr(mat, sfxNodes.shiftNodeName, newValue)


def noiseReset(fx):
    """
    Turn off and reset noise parameters to their defaults
    Args:
        fx (MNPR_FX): MNPR_FX object coming from the caller
    """
    # get node names of operation
    sfxNodes = getNodeNames(fx, 0)

    lib.printInfo("Recompiling material")

    # reset each material
    materials = getMaterials()
    for mat in materials:

        # turn off procedural noise
        stateId = getId(mat, sfxNodes.stateNodeName)
        cmds.shaderfx(sfxnode=mat, edit_bool=(stateId, "value", False))

        sfxNodes.refreshIds(mat)
        # reset attributes
        cmds.shaderfx(sfxnode=mat, edit_float=(sfxNodes.scale, "value", 1.0))
        cmds.shaderfx(sfxnode=mat, edit_float=(sfxNodes.intensity, "value", 10.0))
        cmds.shaderfx(sfxnode=mat, edit_float=(sfxNodes.shift, "value", 0.0))
        cmds.shaderfx(sfxnode=mat, edit_bool=(sfxNodes.scale, "value", True))

    lib.printInfo("{0} procedural control has been reset".format(fx.description))
