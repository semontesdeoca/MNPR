"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                          _
  _ __ ___  _ __  _ __  _ __     ___  ___| |_ _   _ _ __
 | '_ ` _ \| '_ \| '_ \| '__|   / __|/ _ \ __| | | | '_ \
 | | | | | | | | | |_) | |      \__ \  __/ |_| |_| | |_) |
 |_| |_| |_|_| |_| .__/|_|      |___/\___|\__|\__,_| .__/
                 |_|                               |_|
@summary:       This file installs MNPR by adding the required file directories into the Maya.env file
"""
from __future__ import print_function
import os, shutil, urllib, pprint
import maya.cmds as cmds
import maya.mel as mel
import coopLib as lib

distURL = "http://artineering.io/downloads/MNPR"


# GET MAYA VERSION
mayaV = int(lib.mayaVersion())
if mayaV < 2017:
    cmds.error("MNPR is only supported by Maya 2017, onwards.")


# SETTLE OS DEPENDENT CASES
localOS = lib.localOS()
sep = ':'         # separator
ext = ".bundle"   # plugin extension
iconPathEnd = ''  # icon path variable suffix
pSplit = "/"
if localOS == "win":
    ext = ".mll"
    sep = ';'
    pSplit = "\\"
if localOS == "linux":
    ext = ".so"
    iconPathEnd = '%B'


# SETTLE OS DEPENDENT DIRECTORIES
pluginDir = "plugins/{0}/{1}/".format(mayaV, localOS)
print(pluginDir)


def run(root):
    """
    Insert system paths in the Maya.env
    Args:
        root: root directory of MNPR
    """
    print("-> Installing MNPR")
    variables = {'MAYA_SHELF_PATH': [os.path.abspath(os.path.join(root, "shelves/"))],
                 'MAYA_SCRIPT_PATH': [os.path.abspath(os.path.join(root, "scripts/"))],
                 'PYTHONPATH': [os.path.abspath(os.path.join(root, "scripts/"))],
                 'MAYA_PLUG_IN_PATH': [os.path.abspath(os.path.join(root, pluginDir))],
                 'XBMLANGPATH': [os.path.abspath(os.path.join(root, "icons/{0}".format(iconPathEnd)))],
                 'MAYA_VP2_USE_GPU_MAX_TARGET_SIZE': [1],
                 'MNPR_PATH': [os.path.abspath(root)]
                 }

    # get Maya.env file
    mayaEnvFilePath = cmds.about(env=True, q=True)
    # check if Maya env exists (some users have reported that the Maya.env file did not exist in their environment dir)
    if not os.path.isfile(mayaEnvFilePath):
        tempFileDir = os.path.join(os.path.dirname(mayaEnvFilePath), "Maya.env")
        with open(tempFileDir, 'ab') as tmp:
            tmp.write("")

    # get Maya environment variables
    envVariables = getEnvironmentVariables(mayaEnvFilePath)
    print("ENVIRONMENT VARIABLES:")
    pprint.pprint(envVariables)

    # check if MNPR is already installed
    if not installationCheck(variables, envVariables):
        return

    # merge mnpr variables
    envVariables = mergeVariables(variables, envVariables)
    print("MODIFIED VARIABLES:")
    pprint.pprint(envVariables)

    # write environment variables
    tempFilePath = os.path.join(os.path.dirname(mayaEnvFilePath), "maya.tmp")
    writeVariables(tempFilePath, envVariables)

    # replace environment file
    shutil.move(tempFilePath, mayaEnvFilePath)

    # change renderer to support hardware shaders
    if cmds.about(win=True):
        mel.eval('setRenderingEngineInModelPanel "DirectX11"')
    else:
        mel.eval('setRenderingEngineInModelPanel "OpenGLCoreProfileCompat"')

    # get plugin for os
    getPlugin(variables)

    lib.printInfo("-> Installation complete")

    # restart maya
    cmds.confirmDialog(title='Restart Maya',
                       message='\nAll changes will be shown upon restarting Maya',
                       icn='warning', button='OK', ma='center')


def getEnvironmentVariables(mayaEnvFilePath):
    """
    Get the environment variables found at the Maya.env file
    Args:
        mayaEnvFilePath: Path of the Maya.env file
    Returns:
        envVariables (dict)
    """
    # read Maya environment variables
    envVariables = dict()
    with open(mayaEnvFilePath, 'rb') as f:
        for line in f:
            # get rid of new line chars
            line = line.replace("\n", "")
            line = line.replace("\r", "")

            # separate into variable and value
            breakdown = line.split('=')
            if len(breakdown) == 1:
                # no equal sign was used
                breakdown = line.split(' ')  # get rid of empty spaces at the beginning and end of the string
                breakdown = filter(None, breakdown)  # get rid of empty string list elements
            if len(breakdown) != 2:
                cmds.warning("Your Maya.env file has unrecognizable variables:\n{0}".format(breakdown))

            # get values of variable
            vals = breakdown[1].split(sep)
            vals = filter(None, vals)
            values = list()
            for val in vals:
                try:
                    val = int(val)
                    values.append(val)
                except ValueError:
                    # string value
                    values.append(val.strip(' '))
            # get variable name and save
            varName = breakdown[0].strip(' ')
            envVariables[varName] = values

    return envVariables


def installationCheck(variables, envVariables):
    """
    Checks for previous installations and handles each case
    Args:
        variables (dict): variables to add during installation
        envVariables (dict): existing environment variables

    Returns:
        Bool: True -> proceed with installation, False -> do not install
    """
    mnprVariable = 'MNPR_PATH'
    if mnprVariable in envVariables:
        mnprPath = variables[mnprVariable][0]
        # if installing from the existing MNPR path
        if envVariables[mnprVariable][0] == mnprPath:
            message = 'MNPR has already been installed from here:\n    "{0}"\n\nPlease restart Maya to show any performed changes.'.format(mnprPath)
            cmds.confirmDialog(m=message, title="MNPR already installed", b="Sure thing!", icn="information")
            return False
        # MNPR has been previously installed, what now?
        mString = "MNPR has been previously installed at:\n    {0}\n\nDo you wish to override the existing installation (files won't be deleted).".format(envVariables[mnprVariable][0])
        reply = cmds.confirmDialog(title='Overriding existing installation', message=mString, button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No', icn="warning")
        # don't do anything
        if reply == "No":
            lib.printInfo("-> Nothing was done to your current installation")
            return False
        # delete mnpr paths
        previousPath = "{0}".format(envVariables[mnprVariable][0])
        print("Deleting previous MNPR installation at : {0}".format(previousPath))
        for key in envVariables:
            for value in envVariables[key]:
                if previousPath in str(value):
                    envVariables[key].remove(value)
    return True


def mergeVariables(variables, envVariables):
    """
    Merge new variables with existing environment variables
    Args:
        variables (dict): variables to merge
        envVariables (dict): existing environment variables
    Returns:
        envVariables (dict)
    """
    print("")
    for var in variables:
        if var not in envVariables:
            # no variable existed, add
            envVariables[var] = variables[var]
        else:
            # variable already existed
            for varValue in variables[var]:
                # for each variable value to add
                if varValue in envVariables[var]:
                    print("{0}={1} is already set as an environment variable.".format(var, varValue))
                else:
                    # variable did not exist, insert in front
                    envVariables[var].insert(0, varValue)
                    # (optional) check for clashes of files with other variables
    print("Variables successfully updated.\n")
    return envVariables


def writeVariables(filePath, variables):
    """
    Write environment variables to file path
    Args:
        filePath (str): path to save variables to
        variables (dict): environment variables to save
    """
    with open(filePath, 'ab') as tmp:
        # the shelf environment variable must be the first
        shelfVariable = "MAYA_SHELF_PATH"
        if shelfVariable in variables:
            outLine = "{0}=".format(shelfVariable)
            for v in variables.pop(shelfVariable, None):
                outLine += "{0}{1}".format(v, sep)
            tmp.write(outLine + "\n")
        # write the rest of the variables
        for var in variables:
            outLine = "{0}=".format(var)
            for v in variables[var]:
                outLine += "{0}{1}".format(v, sep)
            tmp.write(outLine + "\n")


def getPlugin(variables):
    """
    Gets the plugin locally or online
    Args:
        variables (dict): environment variables
    """
    pluginName = "MNPR{0}".format(ext)

    # check if plugin is available, otherwise, download
    pluginDir = variables["MAYA_PLUG_IN_PATH"][0]
    lib.createDirectory(pluginDir)
    filesInDir = os.listdir(pluginDir)
    if not filesInDir:
        # download the right plugin for the OS and Maya version
        pluginURL = "{0}/plugins".format(distURL)
        pluginURL += "/{0}".format(mayaV)  # add Maya version
        pluginURL += "/{0}".format(lib.localOS())  # add OS
        pluginURL += "/{0}".format(pluginName)  # add plugin name

        # get plugin file online
        print("Getting plugin from: {0}".format(pluginURL))
        lib.printInfo("Downloading plugin...")
        downloader = urllib.URLopener()
        downloader.retrieve(pluginURL, os.path.join(pluginDir, pluginName))


def getSubstrates():
    """
    Downloads and extracts the substrate textures
    """
    url = "https://researchdata.ntu.edu.sg/api/access/datafile/2793?gbrecs=true"
    if lib.localOS() == "mac":
        result = cmds.confirmDialog(t="Download substrates", m="Please download the substrates and extract them into the textures folder of MNPR.", b="Download", icn="information")
        if result == "Download":
            lib.openUrl("https://doi.org/10.21979/N9/HI7GT7")
            lib.openUrl(url)
            return
        else:
            lib.printInfo("No substrates will be downloaded.")
            return
    # windows and linux
    import zipfile
    result = cmds.confirmDialog(t="Downloading substrates", m="Do you wish to download the substrates \nautomatically in the background?", b=['Yes', 'Manual download', 'Close'], icn="question")
    if result == "Manual download":
        lib.openUrl("https://doi.org/10.21979/N9/HI7GT7")
        lib.openUrl(url)
        return
    elif result == "Close":
        lib.printInfo("No substrates will be downloaded.")
        return
    else:
        p = lib.Path(lib.getLibDir())
        p.parent().child("textures")
        dest = os.path.join(p.path, "seamless_textures_light.zip")
        if lib.downloader(url, dest):
            print("Substrates downloaded, extracting...")
            zip = zipfile.ZipFile(dest, 'r')
            zip.extractall(p.path)
            zip.close()
            os.remove(dest)
            lib.printInfo("MNPR substrates installed successfully")
            cmds.confirmDialog(t="Download successful", m="The substrates downloaded successfully", b="Yay!", icn="information")
        else:
            cmds.warning("Problem downloading substrates, please download and install manually")
            result = cmds.confirmDialog(t="Download substrates", m="Please download the substrates and extract them into the textures folder of MNPR.", b="Download", icn="information")
            if result == "Download":
                lib.openUrl("https://doi.org/10.21979/N9/HI7GT7")
                lib.openUrl(url)


""" 
@TODO
def checkForFileClashes(path, envPaths):
    #Check for file clashes when different versions of the same script file exist in Maya
    #Args:
    #    path (str): path to check for file clashes
    #    envPaths (list): other environment paths
    # get files in path
    files = os.listdir(path)
    # check for each path
    for envPath in envPaths:
        # get files in path
        filesInPath = os.listdir(envPath)
        for file in files:
            if file in filesInPath:
                # file exists in another path, check which file is newer
                filePath = os.path.join(path, file)
                envFilePath = os.path.join(envPath, file)
                fileMod = os.path.getmtime(filePath)
                envFileMod = os.path.getmtime(envFilePath)
                if fileMod > envFileMod:
                    
                    # ask what to do, we have a newer file here
                else:
                    # we probably don't need the mnpr file
                # choose what to do with this clash and future clashes
"""
