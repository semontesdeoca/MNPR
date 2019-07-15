"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
@credits:       Updated by Artineering (https://artineering.io) to match MNPRX setup method
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
    variables = {'MNPR_PATH': [os.path.abspath(root)],
                 'MAYA_MODULE_PATH': [os.path.abspath(root)],
                 'MAYA_VP2_USE_GPU_MAX_TARGET_SIZE': [1]
                 }

    # get Maya.env file
    mayaEnvFilePath = cmds.about(env=True, q=True)
    # check if Maya env exists (some users have reported that the Maya.env file did not exist in their environment dir)
    if not os.path.isfile(mayaEnvFilePath):
        tempFileDir = os.path.join(os.path.dirname(mayaEnvFilePath), "Maya.env")
        with open(tempFileDir, 'ab') as tmp:
            tmp.write("")

    # get Maya environment variables
    envVariables, envVariablesOrder = getEnvironmentVariables(mayaEnvFilePath)
    print("ENVIRONMENT VARIABLES:")
    pprint.pprint(envVariables)

    # check if MNPR is already installed
    if installationCheck(variables, envVariables):
        return

    # merge mnpr variables
    envVariables = mergeVariables(variables, envVariables)
    print("MODIFIED VARIABLES:")
    pprint.pprint(envVariables)

    # write environment variables
    tempFilePath = os.path.join(os.path.dirname(mayaEnvFilePath), "maya.tmp")
    writeVariables(tempFilePath, envVariables, envVariablesOrder)

    # replace environment file
    shutil.move(tempFilePath, mayaEnvFilePath)

    # change renderer to support hardware shaders
    if cmds.about(win=True):
        mel.eval('setRenderingEngineInModelPanel "DirectX11"')
    else:
        mel.eval('setRenderingEngineInModelPanel "OpenGLCoreProfileCompat"')

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
    envVariablesOrder = []
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
            envVariablesOrder.append(varName)

    return envVariables, envVariablesOrder


def installationCheck(variables, envVariables):
    """
    Checks for previous installations and handles each case
    Args:
        variables (dict): variables to add during installation
        envVariables (dict): existing environment variables

    Returns:
        Bool: False -> proceed with installation, True -> do not install
    """
    # check for installation
    mnprVariable = 'MNPR_PATH'
    if mnprVariable in envVariables:
        # previous installation exists
        MNPRPath = "{0}".format(envVariables[mnprVariable][0])  # previous MNPR path
        iCheck = True  # integrity check starts True
        newMNPRPath = variables[mnprVariable][0]  # new MNPR path
        # if installing from the existing MNPR path
        if MNPRPath == newMNPRPath:
            # integrity check
            iCheck = integrityCheck(variables, envVariables)
            # if integrity check passed, MNPR
            if iCheck:
                message = 'MNPR has already been installed from here:\n    "{0}"\n\nPlease restart Maya to show any performed changes.'.format(newMNPRPath)
                cmds.confirmDialog(m=message, title="MNPR already installed", b="Sure thing!", icn="information")
                return True
        # MNPR has been previously installed, what now?
        mString = "MNPR has been previously installed at:\n    {0}\n\nDo you wish to override the existing installation (files won't be deleted).".format(envVariables[mnprVariable][0])
        if not iCheck:
            mString = "MNPR has been previously installed but needs to update for it to work\n\nDo you wish to update the existing installation (files won't be deleted)."
        reply = cmds.confirmDialog(title='Overriding existing installation', message=mString, button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No', icn="warning")
        # don't do anything
        if reply == "No":
            lib.printInfo("-> Nothing was done to your current installation")
            return True

        # delete MNPR paths from environment variables
        deleteMNPRVariables(envVariables, MNPRPath)
    return False


def integrityCheck(variables, envVariables):
    """
    Checks each variable and its values with the environment variables
    Args:
        variables: new environment variables
        envVariables: existing environment variables

    Returns:
        Bool: True -> integrity check successful, False -> integrity check unsuccessful
    """
    # integrity check
    for var in variables:
        if var not in envVariables:
            return False
        else:
            for value in variables[var]:
                if value not in envVariables[var]:
                    return False
    return True


def deleteMNPRVariables(envVariables, MNPRPath):
    """
    Delete all environment variables containing the MNPR path
    Args:
        envVariables (dict): all environment variables of the Maya.env file
        MNPRPath (str): the string of the MNPR path
    """
    print("Deleting previous MNPR installation at : {0}".format(MNPRPath))
    for key in envVariables:
        for value in envVariables[key]:
            if MNPRPath in str(value):
                envVariables[key].remove(value)


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


def writeVariables(filePath, variables, sortedVariables):
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
            # make sure that we are not saving an empty variable
            if variables[shelfVariable]:
                if shelfVariable in sortedVariables:
                    sortedVariables.remove(shelfVariable)
                outLine = "{0}=".format(shelfVariable)
                for v in variables.pop(shelfVariable, None):
                    outLine += "{0}{1}".format(v, sep)
                tmp.write(outLine + "\n")
        # add new variables in sortedVariables
        for var in variables:
            if var not in sortedVariables:
                sortedVariables.append(var)
        # write the variables in a sorted fashion
        for var in sortedVariables:
            # check if no sorted variables have been deleted
            if var in variables:
                # make sure that we are not saving an empty variable
                if variables[var]:
                    outLine = "{0}=".format(var)
                    for v in variables[var]:
                        outLine += "{0}{1}".format(v, sep)
                    tmp.write(outLine + "\n")



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