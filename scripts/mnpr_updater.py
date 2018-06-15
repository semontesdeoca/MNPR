"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                                 _       _
  _ __ ___  _ __  _ __  _ __     _   _ _ __   __| | __ _| |_ ___ _ __
 | '_ ` _ \| '_ \| '_ \| '__|   | | | | '_ \ / _` |/ _` | __/ _ \ '__|
 | | | | | | | | | |_) | |      | |_| | |_) | (_| | (_| | ||  __/ |
 |_| |_| |_|_| |_| .__/|_|       \__,_| .__/ \__,_|\__,_|\__\___|_|
                 |_|                  |_|
@summary:       MNPR's automatic updated (beta)
"""
from __future__ import print_function
import maya.cmds as cmds
import os, urllib, pprint, json
import coopLib as lib
import mnpr_setup
import mnpr_info
import mnpr_system

distURL = mnpr_setup.distURL


def updateMNPR(directory, files2Update, files2Delete):
    """
    Updates MNPR at directory
    Args:
        directory (str): Directory where MNPR is installed
        files2Update (list): files that need to be updated
        files2Delete (list): files that need to be deleted
    Returns:
        True if update successful
    """
    print("\nUpdating files at {0}".format(directory))
    print("Files to update: {0}".format(files2Update))
    print("Files to delete: {0}".format(files2Delete))

    # unload MNPR
    mnpr_system.unloadPlugin(mnpr_info.prototype)

    # update files
    downloader = urllib.URLopener()
    for f in files2Update:
        onlineURL = "{0}{1}".format(distURL, f)
        print("Downloading {0}".format(onlineURL))
        filePath = os.path.abspath(os.path.join(directory, f.lstrip('/')))
        try:
            downloader.retrieve(onlineURL, filePath)
        except IOError:
            print("Error: Couldn't download {0} into {1}".format(onlineURL, filePath))
            continue
        # after download, reload modules
        try:
            module = f.split("/")[-1].split(".")[0]
            exec("reload({0})".format(module))
        except NameError:
            pass
        print("Download successful")

    # delete deprecated files
    for f in files2Delete:
        filePath = os.path.abspath(os.path.join(directory, f.lstrip('/')))
        print("Deleting {0}".format(filePath))
        try:
            os.remove(filePath)
        except:
            print("Couldn't remove {0}".format(filePath))

    lib.printInfo("Update completed.")
    return True


def createVersion(directory):
    """
    Creates a new MNPR version with all the latest updates
    Args:
        directory (str): Directory where files are made available for download
    """
    mnpr = dict()

    # get current version
    path = os.path.join(directory, "version.json")
    with open(path, 'r') as f:
        oldMNPR = json.load(f)
    mnpr["version"] = oldMNPR["version"] + 0.01

    # crawl files in download directory to create new version
    for root, dirs, files in os.walk(directory):
        relDir = root.replace(directory, '')
        relDir = relDir.replace('\\', '/')
        if files:
            mnpr[relDir] = dict()
            for f in files:
                mnpr[relDir][f] = os.path.getmtime(os.path.join(root, f))

    pprint.pprint(mnpr)

    # write and save json info
    with open(path, 'w') as f:
        json.dump(mnpr, f, indent=4)
    lib.printInfo("MNPR version created successfully")


def checkUpdates(directory):
    """
    Checks for MNPR updates online and lets the user decide what to do
    Args:
        directory (str): Directory of installed MNPR
    """
    print("Checking for updates...")
    # get local mnpr version
    localPath = os.path.join(directory, "version.json")
    with open(localPath, 'r') as f:
        localMNPR = json.load(f)

    # get online mnpr version
    onlinePath = distURL + "/version.json"
    tempPath = os.path.join(directory, "onlineVersion.json")
    downloader = urllib.URLopener()
    try:
        downloader.retrieve(onlinePath, tempPath)
    except IOError:
        lib.printInfo("Maya can't connect to the internet.")
        return
    with open(tempPath, 'r') as f:
        onlineMNPR = json.load(f)
    os.remove(tempPath)

    # check versions
    localVer = localMNPR.pop("version")
    onlineVer = onlineMNPR.pop("version")
    if onlineVer <= localVer:
        return "Nothing to update"

    # delete unnecessary plugin entries depending on OS
    mayaV = int(lib.mayaVersion())
    localOS = "win"
    if cmds.about(mac=True):
        localOS = "mac"
    elif cmds.about(linux=True):
        localOS = "linux"
    # search in local version
    keys2Delete = []
    for key in localMNPR:
        if "/plugins/" in key:
            if "/{0}/{1}".format(mayaV, localOS) not in key:
                keys2Delete.append(key)
                continue
    # delete unnecessary local keys
    for key in keys2Delete:
        localMNPR.pop(key)
    # search in online version
    keys2Delete = []
    for key in onlineMNPR:
        if "/plugins/" in key:
            if "/{0}/{1}".format(mayaV, localOS) not in key:
                keys2Delete.append(key)
                continue
    # delete unnecessary online keys
    for key in keys2Delete:
        onlineMNPR.pop(key)

    print("LOCAL")
    pprint.pprint(localMNPR)
    print("\nONLINE")
    pprint.pprint(onlineMNPR)

    # compare the two versions
    files2Update = []
    for key in onlineMNPR:
        if key in localMNPR:
            for file in onlineMNPR[key]:
                if file in localMNPR[key]:
                    if onlineMNPR[key][file]>localMNPR[key][file]:
                        # online file is newer than local file, download
                        files2Update.append("{0}/{1}".format(key, file))
                else:
                    # file doesn't exist locally, download
                    files2Update.append("{0}/{1}".format(key, file))
        else:
            for file in onlineMNPR[key]:
                files2Update.append("{0}/{1}".format(key, file))

    files2Delete = []
    for key in localMNPR:
        if key in onlineMNPR:
            for file in localMNPR[key]:
                if file not in onlineMNPR[key]:
                    files2Delete.append("{0}/{1}".format(key, file))
        else:
            for file in localMNPR[key]:
                files2Delete.append("{0}/{1}".format(key, file))

    # check if a shelf needs to update, as Maya would then require a restart
    restartMaya = False
    for f2u in files2Update:
        if "/shelves/" in f2u:
            restartMaya = True
    for f2d in files2Delete:
        if "/shelves/" in f2d:
            restartMaya = True

    # update prompt
    mString = "An update for MNPR is available, do you wish to download and install this update?\n\n"
    mString += "Files to be updated:\n"
    if files2Update:
        for fUpdate in files2Update:
            mString += "-. {0}\n".format(fUpdate)
    else:
        mString += "- None -\n"
    mString += "\nFiles to be deleted:\n"
    if files2Delete:
        for fDelete in files2Delete:
            mString += "-. {0}\n".format(fDelete)
    else:
        mString += "- None -\n"
    reply = cmds.confirmDialog(title='Update is available', message=mString, button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No', icn="information")
    # don't do anything
    if reply == "No":
        lib.printInfo("Nothing has been updated")
        return

    if restartMaya:
        mString = "The shelf will be updated, so Maya will close automatically after the update has concluded\n\n"
        mString += "No scenes/preferences will be saved upon closure, do you still wish to proceed?"
        reply = cmds.confirmDialog(title='Shelf update', message=mString, button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No', icn="warning")
        if reply == "No":
            lib.printInfo("Nothing has been updated")
            return

    if updateMNPR(directory, files2Update, files2Delete):
        if restartMaya:
            cmds.quit(abort=True)
