"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                 _        __
  _ __ ___  _ __  _ __  _ __    (_)_ __  / _| ___
 | '_ ` _ \| '_ \| '_ \| '__|   | | '_ \| |_ / _ \
 | | | | | | | | | |_) | |      | | | | |  _| (_) |
 |_| |_| |_|_| |_| .__/|_|      |_|_| |_|_|  \___/
                 |_|
@summary:   Global plugin variables and functions
"""
import maya.cmds as cmds

prototype = "MNPR"             # which plugin prototype are you working with
media = "NPR"                  # what media are you simulating (watercolor, oil, stippling, npr)
abbr = 'NPR'                   # abbreviation of the media (used for shaders, etc)
configNode = "mnprConfig"      # name of your configuration node
brand = "powered by MNPR"      # brand of the plugin
environment = ""               # directory of plugin environment
iconDir = ""                   # directory within plugin environment
backend = 'GLSL'               # rendering backend of VP2.0
if cmds.optionVar(q="vp2RenderingEngine") == "DirectX11":
    backend = 'dx11'


def loadRenderer(newPrototype=prototype, newMedia=media, newAbbr=abbr):
    """
    Loads renderer and its globals
    Args:
        newPrototype (str): plugin prototype name
        newMedia (str): name of npr media (e.g. watercolor, charcoal, etc)
        newAbbr (str): abbreviation of the npr media (e.g. WC, CH, etc)
    """
    global prototype, media, abbr, environment, iconDir
    prototype = newPrototype
    media = newMedia
    abbr = newAbbr
    loadPlugin()
    environment = cmds.mnpr(env=True, q=True)
    iconDir = "{0}icons".format(environment)


def loadPlugin():
    """Loads the plugin"""
    try:
        cmds.loadPlugin(prototype, quiet=True)
    except RuntimeError:
        cmds.error("Maya can't find the {0} plugin or the version of the plugin is not compatible with this version of Maya (see FAQ for more information)".format(prototype))
