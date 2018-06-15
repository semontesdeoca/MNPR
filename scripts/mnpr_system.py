"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                               _
  _ __ ___  _ __  _ __  _ __     ___ _   _ ___| |_ ___ _ __ ___
 | '_ ` _ \| '_ \| '_ \| '__|   / __| | | / __| __/ _ \ '_ ` _ \
 | | | | | | | | | |_) | |      \__ \ |_| \__ \ ||  __/ | | | | |
 |_| |_| |_|_| |_| .__/|_|      |___/\__, |___/\__\___|_| |_| |_|
                 |_|                 |___/
@summary:       MNPR related functions
"""
from __future__ import print_function
import os
import traceback
import maya.cmds as cmds
import maya.mel as mel
import coopLib as lib
import mnpr_info
import mnpr_runner
import mnpr_matPresets

mnpr_info.loadPlugin()

dx2sfxAttr = {"xUseColorTexture": "Albedo_Texture",
              "xColorTint": "Color_Tint",
              "xUseNormalTexture": "Normal_Map",
              "xFlipU": "Invert_U",
              "xFlipV": "Invert_V",
              "xBumpDepth": "Bump_Depth",
              "xUseSpecularTexture": "Specular_Map",
              "xSpecular": "Specular_Roll_Off",
              "xSpecDiffusion": "Specular_Diffusion",
              "xSpecTransparency": "Specular_Transparency",
              "xUseShadows": "",
              "xShadowDepthBias": "",
              "xDiffuseFactor": "Diffuse_Factor",
              "xShadeColor": "Shade_Color",
              "xShadeWrap": "Shade_Wrap",
              "xUseOverrideShade": "Shade_Override",
              "xDilute": "Dilute_Paint",
              "xCangiante": "Cangiante",
              "xDiluteArea": "Dilute_Area",
              "xHighArea": "Highlight_Roll_Off",
              "xHighTransparency": "Highlight_Transparency",
              "xAtmosphereColor": "",
              "xRangeStart": "",
              "xRangeEnd": "",
              "xDarkEdges": "",
              "xMainTex": "Albedo_Texture_File",
              "xNormalTex": "Normal_Map_File",
              "xSpecTex": "Specular_Map_File"
              }


def check():
    """Makes sure everything is running right"""
    print("SYSTEM CHECK FOR {0}".format(mnpr_info.prototype))
    # check viewport
    viewport = lib.getActiveModelPanel()
    cmds.modelEditor(viewport, dtx=True, e=True)  # display textures

    # plugin needs to be loaded
    mnpr_info.loadRenderer()

    # 3rd party plugins must be loaded
    cmds.loadPlugin('shaderFXPlugin', quiet=True)
    if cmds.about(nt=True, q=True):
        cmds.loadPlugin('dx11Shader', quiet=True)  # deprecated (only shadeFXPlugin in the future)
    cmds.loadPlugin('glslShader', quiet=True)  # deprecated (only shaderFXPlugin in the future)

    # viewport renderer must be set
    mel.eval("setRendererAndOverrideInModelPanel vp2Renderer {0} {1};".format(mnpr_info.prototype, viewport))

    # modify color of heads up display
    cmds.displayColor("headsUpDisplayLabels", 2, dormant=True)
    cmds.displayColor("headsUpDisplayValues", 2, dormant=True)

    # make sure a config node exists
    if not cmds.objExists(mnpr_info.configNode):
        selected = cmds.ls(sl=True, l=True)
        selectConfig()
        cmds.select(selected, r=True)

    lib.printInfo("-> SYSTEM CHECK SUCCESSFUL")


def changeStyle():
    """Resets MNPR to load a new style"""
    # reset stylization
    cmds.mnpr(resetStylization=True)

    # delete old config node
    if cmds.objExists(mnpr_info.configNode):
        cmds.delete(mnpr_info.configNode)
    # flush undo
    cmds.flushUndo()
    print("style deleted")
    # deregister node
    cmds.mnpr(rn=False)
    # register node
    cmds.mnpr(rn=True)
    # create new config node
    selectConfig()
    # refresh AETemplate
    mnpr_runner.reloadConfig()

    # set new media type
    mnpr_info.media = cmds.mnpr(style=True, q=True)

    # rebuild opened UI's
    import mnpr_UIs
    if cmds.window(mnpr_UIs.BreakdownUI.windowTitle, exists=True):
        mnpr_runner.openOverrideSettings(rebuild=True)
    import mnpr_FX
    if cmds.window(mnpr_FX.MNPR_FX_UI.windowTitle, exists=True):
        mnpr_runner.openPaintFX(rebuild=True)

    lib.printInfo("Style changed")


def togglePlugin(force=""):
    """
    Toggles active or forces desired plugin prototype
    Args:
        force (str): plugin name to force
    """
    if force:
        unloadPlugin(mnpr_info.prototype)
        mnpr_info.prototype = force
        check()
    else:
        # toggle loaded prototype
        if cmds.pluginInfo(mnpr_info.prototype, loaded=True, q=True):
            unloadPlugin(mnpr_info.prototype)
        else:
            check()


def unloadPlugin(plugin):
    """
    Unloads plugin and cleans scene from plugin traces
    Args:
        plugin (str): name of plugin to be unloaded
    """
    # check which prototype is active
    if cmds.pluginInfo(plugin, loaded=True, q=True):
        # remove traces and unload
        if cmds.objExists(mnpr_info.configNode):
            cmds.delete(mnpr_info.configNode)  # delete config node
        cmds.flushUndo()  # clear undo queue
        cmds.unloadPlugin(plugin)  # unload plugin
        lib.printInfo("->PLUGIN SUCCESSFULLY UNLOADED")


def showShaderAttr():
    """ Select material and show in attribute editor """
    if cmds.ls(sl=True):
        cmds.hyperShade(smn=True)
        mel.eval("openAEWindow")
    else:
        cmds.warning("Select object with shader")


def refreshShaders():
    """ Refreshes object-space plugin shaders """
    shaderDir = systemDir("shaders")

    if os.name == 'nt' and mnpr_info.backend == 'dx11':
        shaderFile = os.path.join(shaderDir, "PrototypeC.fx")
        if not os.path.isfile(shaderFile):
            shaderFile = os.path.join(shaderDir, "prototypeC.fxo")
        shaders = cmds.ls(type="dx11Shader")
    else:
        shaderFile = os.path.join(shaderDir, "PrototypeC.ogsfx")
        shaders = cmds.ls(type="GLSLShader")

    for shader in shaders:
        cmds.setAttr("{0}.shader".format(shader), shaderFile, type="string")
    lib.printInfo('Shaders refreshed')
    return True


def updateShaderFX():
    """ Updates shaderFX shaders"""
    shaderDir = systemDir("shaders")
    materials = cmds.ls(type="ShaderfxShader")

    counter = 0
    for mat in materials:
        counter += 1
        # get materials attributes
        matAttrs = {}
        mnpr_matPresets.getMaterialAttrs(mat, matAttrs)

        # load new graph
        shaderFile = os.path.join(shaderDir, "{0}.sfx".format(matAttrs["graph"]))
        cmds.shaderfx(sfxnode=mat, loadGraph=shaderFile)

        # set attributes
        mnpr_matPresets.setMaterialAttrs(mat, matAttrs)

        print("{0} has been updated to the latest version".format(mat))
        print("{0}/{1} materials updated".format(counter, len(materials)))

    lib.printInfo('Shaders updated')


def dx112glsl():
    """ Converts dx11 materials to glsl materials """
    check()
    dx11Shaders = cmds.ls(type="dx11Shader")
    print(dx11Shaders)
    for dx11Shader in dx11Shaders:
        print("Transfering {0} shader".format(dx11Shader))
        # get all attributes
        attributes = cmds.listAttr(dx11Shader, ud=True, st="x*", k=True)
        print(attributes)
        # get all connected nodes
        connectedNodes = cmds.listConnections(dx11Shader, t="file", c=True, p=True)
        print(connectedNodes)
        # get all shapes
        cmds.select(dx11Shader, r=True)
        cmds.hyperShade(objects="")
        shapes = cmds.ls(sl=True)
        print(shapes)
    
        # create glsl shader
        shader = cmds.shadingNode('GLSLShader', asShader=True, n="{0}_GL".format(dx11Shader))
        cmds.select(shapes, r=True)
        cmds.hyperShade(assign=shader)
        print(">>> Shader {0} created".format(shader))
        # assign attributes
        shaderFile = os.path.join(mnpr_info.environment,"shaders","PrototypeC.ogsfx")
        cmds.setAttr("{0}.shader".format(shader), shaderFile, type="string")
        print("Setting attributes for {0}".format(shader))
        for attr in attributes:
            value = cmds.getAttr("{0}.{1}".format(dx11Shader, attr))
            try:
                if type(value) == type([]):
                    cmds.setAttr("{0}.{1}".format(shader, attr), value[0][0], value[0][1], value[0][2], typ="double3")
                else:
                    cmds.setAttr("{0}.{1}".format(shader, attr), value)
            except:
                print("Found problemt when setting {0}.{1}, skipping for now".format(shader, attr))
        # connect nodes
        if connectedNodes:
            for i in range(0, len(connectedNodes), 2):
                inputAttr = connectedNodes[i].split(".")[1]
                cmds.connectAttr(connectedNodes[i+1], "{0}.{1}".format(shader, inputAttr))
        # set control sets
        if cmds.attributeQuery("Color0_Source", node=shader, ex=True):
            cmds.setAttr("{0}.Color0_Source".format(shader), "color:controlSetA", type="string" )
        if cmds.attributeQuery("Color1_Source", node=shader, ex=True):
            cmds.setAttr("{0}.Color1_Source".format(shader), "color:controlSetB", type="string" )
        if cmds.attributeQuery("Color2_Source", node=shader, ex=True):
            cmds.setAttr("{0}.Color2_Source".format(shader), "color:controlSetC", type="string" )
        # delete dx11 shader
        #cmds.delete(dx11Shader)


def dx112sfx(graph="mnpr_uber"):
    """
    Converts dx11 materials to shaderFX materials
    Args:
        graph (str): ShaderFX graph name (filename)
    """
    check()
    dx11Shaders = cmds.ls(type="dx11Shader")
    prototypeCNodes = []
    for dx11Shader in dx11Shaders:
        shaderPath = cmds.getAttr("{0}.shader".format(dx11Shader))
        if "rototypeC" not in shaderPath:
            continue
        prototypeCNodes.append(dx11Shader)

        print("Converting {0} shader".format(dx11Shader))
        # get all attributes
        attributes = cmds.listAttr(dx11Shader, ud=True, st="x*", k=True)
        print(attributes)
        # get all connected nodes
        connectedNodes = cmds.listConnections(dx11Shader, t="file", c=True)
        print(connectedNodes)
        # get all shapes
        cmds.select(dx11Shader, r=True)
        cmds.hyperShade(objects="")
        shapes = cmds.ls(sl=True)
        print(shapes)

        # create shaderFX shader
        shader = cmds.shadingNode('ShaderfxShader', asShader=True, name="{0}".format(dx11Shader.replace("_WC", "_SFX")))
        cmds.select(shapes, r=True)
        cmds.hyperShade(assign=shader)
        shaderFile = os.path.join(mnpr_info.environment, "shaders", "{0}.sfx".format(graph))
        cmds.shaderfx(sfxnode=shader, loadGraph=shaderFile)
        print(">>> Shader {0} created".format(shader))
        # assign settings
        vtxControl = bool(cmds.getAttr("{0}.{1}".format(dx11Shader, "xUseControl")))
        if vtxControl:
            nodeId = cmds.shaderfx(sfxnode=shader, getNodeIDByName="vtxControls")
            cmds.shaderfx(sfxnode=shader, edit_bool=(nodeId, "value", vtxControl))
        shadows = bool(cmds.getAttr("{0}.{1}".format(dx11Shader, "xUseShadows")))
        if not shadows:
            nodeId = cmds.shaderfx(sfxnode=shader, getNodeIDByName="Shadow")
            cmds.shaderfx(sfxnode=shader, edit_bool=(nodeId, "value", shadows))
        specularity = bool(cmds.getAttr("{0}.{1}".format(dx11Shader, "xSpecular")))
        if specularity:
            nodeId = cmds.shaderfx(sfxnode=shader, getNodeIDByName="Specularity")
            cmds.shaderfx(sfxnode=shader, edit_bool=(nodeId, "value", specularity))
        # assign attributes
        print("Setting attributes for {0}".format(shader))
        for attr in attributes:
            value = cmds.getAttr("{0}.{1}".format(dx11Shader, attr))
            if attr in dx2sfxAttr:
                lib.setAttr(shader, dx2sfxAttr[attr], value)
        # assign textures
        if connectedNodes:
            for i in range(0, len(connectedNodes), 2):
                textureDir = cmds.getAttr("{0}.{1}".format(connectedNodes[i+1], "fileTextureName"))
                attr = connectedNodes[i].split(".")[1]
                lib.setAttr(shader, dx2sfxAttr[attr], textureDir)

    # delete prototypeC shaders
    cmds.delete(prototypeCNodes)


def systemDir(folder=''):
    """
    Returns the system directory
    Args:
        folder (str): folder to append to system directory

    Returns:
        (str): path to system directory
    """
    rootDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(rootDir, folder)


def selectConfig():
    """Select configuration node and re-check connections"""
    # delete old configuration nodes
    if cmds.objExists("NPRConfig"):
        cmds.delete("NPRConfig")

    if not cmds.objExists(mnpr_info.configNode):
        print(mnpr_info.configNode)
        cmds.createNode("mnprConfig", n=mnpr_info.configNode)

        cmds.connectAttr("{0}.evaluate".format(mnpr_info.configNode), "persp.visibility", f=True)
        mel.eval("AttributeEditor")
        lib.printInfo("-> CONFIG NODE CREATED AND CONNECTED")
    else:
        cmds.select(mnpr_info.configNode)
        mel.eval("AttributeEditor")
        lib.printInfo("Selected {0} configuration node".format(mnpr_info.prototype))


def optimizePerformance():
    """Function to optimize performance by disabling some Maya functions"""
    cmds.evaluationManager(mode="off")  # set up animation evaluation to DG


def renderFrame(saveDir, width, height, renderSize=1, imgFormat=".jpg", override=mnpr_info.prototype):
    """
    Renders current frame in the viewport
    Args:
        saveDir (str): save directory
        width (int): width in pixels
        height (int): height in pixels
        renderSize (float): render size (factor)
        imgFormat (str): .jpg, .exr, etc)
        override (str): name of desired override (if any)
    """
    check()  # check that everything is in order
    renderSize = resolutionCheck(width, height, renderSize)  # make sure resolution is reasonable

    # get working values to be changed
    workingRenderSize = cmds.getAttr("{0}.renderScale".format(mnpr_info.configNode))
    workingColorDepth = cmds.getAttr("{0}.colorDepth".format(mnpr_info.configNode))

    # set desired attributes
    if workingColorDepth != 2:
        lib.setAttr(mnpr_info.configNode, "colorDepth", 2)
    if renderSize != workingRenderSize:
        lib.setAttr(mnpr_info.configNode, "renderScale", renderSize)
    # prepare renderer
    cmds.mnpr(g=True)  # enable mnprGamma
    mnprOperations = len(cmds.mnpr(lsO=True))
    cmds.mnpr(renderOperation=mnprOperations-1, s=0)  # HUD
    cmds.mnpr(renderOperation=mnprOperations-2, s=0)  # UI
    cmds.refresh()

    # render frame
    try:
        screenshotPath = lib.screenshot(saveDir, width, height, format=imgFormat, override=override)  # render the frame
    except WindowsError:
        print("Screenshot saving has been canceled")
    except:
        traceback.print_exc()


    if screenshotPath:
        # bring everything back to normal
        cmds.mnpr(renderOperation=mnprOperations-1, s=1)  # HUD
        cmds.mnpr(renderOperation=mnprOperations-2, s=1)  # UI
        lib.setAttr(mnpr_info.configNode, "renderScale", workingRenderSize)
        lib.setAttr(mnpr_info.configNode, "colorDepth", workingColorDepth)
        cmds.mnpr(g=False)
        cmds.refresh()
        return screenshotPath


def playblast(saveDir, width, height, renderCamera, modelPanel, renderSize=1):
    """
    Playblasts the timeslider
    Args:
        saveDir (str): save directory with *.mov extension
        width (int):  width in pixels
        height:  height in pixels
        renderCamera: camera to playblast from
        modelPanel: modelPanel to playblast from
        renderSize: render size (factor)
    """
    check()  # check that everything is in order
    renderSize = resolutionCheck(width, height, renderSize)  # make sure resolution is reasonable
    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
    audioNode = cmds.timeControl(aPlayBackSliderPython, q=True, s=True)  # get audio node

    # get working values to be changed
    workingRenderSize = cmds.getAttr("{0}.renderScale".format(mnpr_info.configNode))
    workingColorDepth = cmds.getAttr("{0}.colorDepth".format(mnpr_info.configNode))
    workingCamera = cmds.modelEditor(modelPanel, cam=True, q=True)
    workingCameraShape = cmds.listRelatives(workingCamera, s=True)
    if workingCameraShape:
        workingCameraShape = workingCameraShape[0]
    else:
        # we already have the shape
        workingCameraShape = workingCamera
    

    # set desired attributes
    cmds.mnpr(g=True)
    mnprOperations = len(cmds.mnpr(lsO=True))
    cmds.mnpr(renderOperation=mnprOperations-1, s=0)  # HUD
    cmds.mnpr(renderOperation=mnprOperations-2, s=0)  # UI
    cmds.modelEditor(modelPanel, cam=renderCamera, e=True)  # change modelPanel
    lib.setAttr(mnpr_info.configNode, "renderScale", renderSize)
    lib.setAttr(mnpr_info.configNode, "colorDepth", 2)  # needs to be 32bit to avoid artefacts
    cmds.refresh()

    # try playblasting
    try:
        cmds.playblast(f=saveDir, format="qt", w=width, h=height, percent=100, qlt=100, v=True, fo=True, os=True,
                       s=audioNode, compression="PNG")
    except RuntimeError:
        try:
            cmds.playblast(f=saveDir, format="avi", w=width, h=height, percent=100, qlt=100, v=True, fo=True, os=True,
                           s=audioNode)
        except RuntimeError:
            cmds.error("Video cannot be playblasted as qt or avi, please check the installed codecs.")

    # bring everything back to normal
    cmds.mnpr(renderOperation=mnprOperations-1, s=1)  # HUD
    cmds.mnpr(renderOperation=mnprOperations-2, s=1)  # UI
    cmds.modelEditor(modelPanel, cam=workingCameraShape, e=True)
    lib.setAttr(mnpr_info.configNode, "renderScale", workingRenderSize)
    lib.setAttr(mnpr_info.configNode, "colorDepth", workingColorDepth)
    cmds.mnpr(g=False)
    cmds.refresh()

    lib.printInfo("Video has been successfully playblasted to: {0}".format(saveDir))


def resolutionCheck(width, height, renderSize=1.0):
    """
    Checks if resolution is between reasonable hardware limitations
    Args:
        width (int): viewport width
        height (int): viewport height
        renderSize (float): render size (factor)

    Returns:
        renderSize (int): viable render size (factor)
    """
    if (width*renderSize > 16384) or (height*renderSize > 16384):
        cmds.warning("Resolution too high to supersample, reducing render size")
        return resolutionCheck(width, height, renderSize/2.0)
    else:
        if (width * height * pow(renderSize, 2)) > 150000000:
            confirm = cmds.confirmDialog(title='Crash Warning',
                                         message='Rendering a frame at such high resolutions might take long and even crash Maya\nWould you like to continue anyway?',
                                         icn="warning", button=['Yes', 'No'], defaultButton='Yes',
                                         cancelButton='No', dismissString='No', ma='center')
            if confirm == 'No':
                cmds.error("Frame capture cancelled by user")
    return renderSize


def updateAE():
    mel.eval("refreshEditorTemplates;")
    return True
