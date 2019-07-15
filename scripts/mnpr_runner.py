"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR

  _ __ ___  _ __  _ __  _ __     _ __ _   _ _ __  _ __   ___ _ __
 | '_ ` _ \| '_ \| '_ \| '__|   | '__| | | | '_ \| '_ \ / _ \ '__|
 | | | | | | | | | |_) | |      | |  | |_| | | | | | | |  __/ |
 |_| |_| |_|_| |_| .__/|_|      |_|   \__,_|_| |_|_| |_|\___|_|
                 |_|
@summary:   A centralized file to run functions from the shelf
"""
from __future__ import print_function
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omUI
import maya.cmds as cmds
import maya.mel as mel
import coopLib as lib
import mnpr_presets
import mnpr_matPresets
import mnpr_system
import mnpr_info
import mnpr_UIs
import mnpr_FX

try:
    reload         # Python 2
except NameError:  # Python 3
    from importlib import reload

try:
    long           # Python 2
except NameError:
    long = int     # Python 3


def openPresets(rebuild=True):
    """Opens the stylization presets UI
     Args:
        rebuild (bool): If the UI is rebuilt when opened
    """
    mnpr_system.check()
    mnpr_presets.AttributeSetsUI(windowTitle="Stylization Presets",
                                    setType="styles",
                                    objects=mnpr_info.configNode,
                                    rebuild=rebuild,
                                    brand=mnpr_info.brand,
                                    tooltip="Load/Save stylization presets")


def openMaterialPresets(rebuild=True):
    """
    Opens the material presets UI
     Args:
        rebuild (bool): If the UI is rebuilt when opened
    """
    mnpr_system.check()
    mnpr_matPresets.MnprMaterialPresetsUI(rebuild=rebuild)


def openOverrideSettings(rebuild=False):
    """Opens the viewport renderer UI
     Args:
        rebuild (bool): If the UI is rebuilt when opened
    """
    mnpr_system.check()
    mnpr_system.selectConfig()
    if cmds.mnpr(listOperations=True)[0]:
        mnpr_UIs.BreakdownUI(rebuild=rebuild)


def openNoiseFX(dock=False, rebuild=False):
    """Opens the noiseFX UI
     Args:
        dock (bool): If the UI should be docked
        rebuild (bool): If the UI is rebuilt when opened
    """
    fxType = "material-space"
    mnpr_system.check()
    print("Opening noiseFX with dock = {0}".format(dock))
    windowObj = mnpr_FX.MNPR_FX_UI(dock=dock, rebuild=rebuild, tab=fxType)

    # change tab
    ptr = omUI.MQtUtil.findWindow(windowObj.windowTitle)  # pointer to main window
    window = wrapInstance(long(ptr), QtWidgets.QWidget)  # wrapper
    tabWidget = window.findChildren(QtWidgets.QTabWidget)
    tabWidget[0].setCurrentIndex(0)


def openPaintFX(dock=False, rebuild=False):
    """Opens the paintFX UI
     Args:
        dock (bool): If the UI should be docked
        rebuild (bool): If the UI is rebuilt when opened
    """
    fxType = "vertex-space"
    mnpr_system.check()
    # temporary workaround to painting ceasing to work correctly
    if rebuild:
        reload(mnpr_FX)
    print("Opening paintFX with dock = {0}".format(dock))
    windowObj = mnpr_FX.MNPR_FX_UI(dock=dock, rebuild=rebuild, tab=fxType)

    # change tab
    ptr = omUI.MQtUtil.findWindow(windowObj.windowTitle)  # pointer to main window
    window = wrapInstance(long(ptr), QtWidgets.QWidget)  # wrapper
    tabWidget = window.findChildren(QtWidgets.QTabWidget)
    tabWidget[0].setCurrentIndex(1)


def openViewportRenderer(rebuild=False):
    """Opens the viewport renderer UI
    Args:
        rebuild (bool): If the UI is rebuilt when opened
    """
    mnpr_system.check()
    mnpr_UIs.ViewportRendererUI(rebuild=rebuild)


def changeStyle():
    """Changes the style within MNPR"""
    mnpr_system.changeStyle()


def reloadConfig():
    """Reloads AE template of config node"""
    mel.eval('source "AEmnprConfigTemplate.mel";')
    mel.eval('refreshEditorTemplates;')
    return True


def updateMNPR(env=''):
    """
    Checks for updates and updates MNPR
    Args:
        env (str): MNPR directory
    """
    mnpr_system.check()
    if not env:
        env = cmds.mnpr(env=True)
    import mnpr_updater
    mnpr_updater.checkUpdates(env)


def testScene(prototype="shaderFX"):
    """
    Creates a boring default scene with a sphere
    Args:
        prototype (str): either with "shaderFX" or "prototypeC"
    """
    mnpr_system.check()
    # create and place test sphere
    cmds.polySphere()
    testSphere = cmds.ls(sl=True)
    mnpr_matPresets.createMaterial(testSphere, prototype=prototype)
    mnpr_matPresets.defaultLighting()
    lib.printInfo("Default scene created")


def downloadSubstrates():
    """ Downloads MNPR substrates in separate thread """
    import thread
    import mnpr_setup
    thread.start_new_thread(mnpr_setup.getSubstrates, ())


def charcoalContrast():
    """ Modifies ShaderFX materials to generate contrast from lightness """
    materials = cmds.ls(type="ShaderfxShader")
    for mat in materials:
        lib.setAttr(mat, "Shade_Override", 0)
        lib.setAttr(mat, "Diffuse_Factor", 0.8)
    lib.printInfo("ShaderFX materials changed for charcoal stylization")
