"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                 _   _ ___
  _ __ ___  _ __  _ __  _ __    | | | |_ _|___
 | '_ ` _ \| '_ \| '_ \| '__|   | | | || |/ __|
 | | | | | | | | | |_) | |      | |_| || |\__ \
 |_| |_| |_|_| |_| .__/|_|       \___/|___|___/
                 |_|
@summary:       Contains the pass breakdown and MNPR viewport renderer interfaces
"""
from __future__ import print_function
import os
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import coopLib as lib
import coopQt as qt
import mnpr_system
import mnpr_info


#    _                    _       _
#   | |__  _ __ ___  __ _| | ____| | _____      ___ __
#   | '_ \| '__/ _ \/ _` | |/ / _` |/ _ \ \ /\ / / '_ \
#   | |_) | | |  __/ (_| |   < (_| | (_) \ V  V /| | | |
#   |_.__/|_|  \___|\__,_|_|\_\__,_|\___/ \_/\_/ |_| |_|
#
class BreakdownUI(qt.CoopMayaUI):
    """ UI class for the operations(passes) breakdown """
    windowTitle = "Operations breakdown"

    def __init__(self, rebuild=False):
        super(BreakdownUI, self).__init__(self.windowTitle, dock=False, rebuild=rebuild, brand=mnpr_info.brand, tooltip="Control the override operations")
        self.cChannels = [True, True, True]  # display color channels

    def buildUI(self):
        # global UI variables
        self.setGeometry(500, 400, 250, 250)
        margin = 10 * self.dpiS

        # OPERATIONS
        rOpsGroup = qt.WidgetGroup(qLayout=QtWidgets.QGridLayout())
        rOps = cmds.mnpr(listOperations=True)
        index = 0
        self.operationsCBoxDict = dict()
        self.operationsReloadDict = dict()
        paintIconDir = os.path.join(mnpr_info.iconDir, "coop_refresh.png")
        for operation in rOps:
            self.operationsReloadDict[index] = qt.IconButton(paintIconDir, "Reload Shaders", [14 * self.dpiS, 14 * self.dpiS])
            self.operationsReloadDict[index].setProperty("operationIndex", index)
            rOpsGroup.addWidget(self.operationsReloadDict[index], index, 0)
            self.operationsCBoxDict[index] = QtWidgets.QCheckBox(operation)
            self.operationsCBoxDict[index].setChecked(True)
            rOpsGroup.addWidget(self.operationsCBoxDict[index], index, 1)
            index += 1

        # TARGETS
        targetGroup = qt.WidgetGroup(qLayout=QtWidgets.QHBoxLayout())
        targetLabel = QtWidgets.QLabel("Active target: ")
        self.targetCoBox = QtWidgets.QComboBox()
        nprTargets = cmds.mnpr(lsT=True)
        self.targetCoBox.addItems(nprTargets)
        self.targetCoBox.setCurrentIndex(len(nprTargets) - 1)
        targetGroup.addWidgets([targetLabel, self.targetCoBox])
        targetGroup.setContentsMargins(margin, margin, margin, margin)

        # CHANNELS
        channelGroup = qt.WidgetGroup(qLayout=QtWidgets.QHBoxLayout())
        channelsLabel = QtWidgets.QLabel("Channels: ")
        self.r = QtWidgets.QCheckBox("R")
        self.r.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.r.setChecked(True)
        self.g = QtWidgets.QCheckBox("G")
        self.g.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.g.setChecked(True)
        self.b = QtWidgets.QCheckBox("B")
        self.b.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.b.setChecked(True)
        self.a = QtWidgets.QCheckBox("A")
        self.a.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.negate = QtWidgets.QCheckBox("NEG")
        self.negate.setLayoutDirection(QtCore.Qt.RightToLeft)
        channelGroup.addWidgets([channelsLabel, self.r, self.g, self.b, self.a, self.negate])
        channelGroup.setContentsMargins(margin, margin, margin, margin)

        # COLOR TRANSFORMATION
        colorTransformGroup = qt.WidgetGroup(qLayout=QtWidgets.QHBoxLayout())
        colorTransformLabel = QtWidgets.QLabel("Color xform: ")
        self.colorTransformButtonGroup = QtWidgets.QButtonGroup()
        self.colorTransform0 = QtWidgets.QRadioButton("Original")
        self.colorTransform0.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.colorTransform0.setChecked(True)
        self.colorTransformButtonGroup.addButton(self.colorTransform0)
        self.colorTransform1 = QtWidgets.QRadioButton("-> Lab")
        self.colorTransform1.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.colorTransform1.setChecked(False)
        self.colorTransformButtonGroup.addButton(self.colorTransform1)
        self.colorTransform2 = QtWidgets.QRadioButton("-> RGB")
        self.colorTransform2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.colorTransform2.setChecked(False)
        self.colorTransformButtonGroup.addButton(self.colorTransform2)
        colorTransformGroup.addWidgets([colorTransformLabel, self.colorTransform0, self.colorTransform1, self.colorTransform2])
        colorTransformGroup.setContentsMargins(margin, margin, margin, margin)

        # Create Layout
        ''' Create the layouts and add widgets '''
        rOpsBox = QtWidgets.QGroupBox("Render Operations (passes)")
        rOpsLayout = QtWidgets.QVBoxLayout(rOpsBox)
        rOpsLayout.addWidget(rOpsGroup)

        # self.layout.addWidget(self.header)
        self.setContentsMargins(0, margin*1.5, 0, 0)
        self.layout.addWidget(rOpsBox)
        self.layout.addWidget(qt.HLine(height=10 * self.dpiS))
        self.layout.addWidget(targetGroup)
        self.layout.addWidget(qt.HLine(height=10 * self.dpiS))
        self.layout.addWidget(channelGroup)
        self.layout.addWidget(qt.HLine(height=10 * self.dpiS))
        self.layout.addWidget(colorTransformGroup)
        self.layout.addWidget(self.brand)

        # Create Connections
        ''' SIGNAL '''
        for index in range(len(rOps)):
            self.operationsCBoxDict[index].stateChanged.connect(self.operationChanged)
            self.operationsReloadDict[index].clicked.connect(self.reloadOperationShaders)
        self.targetCoBox.currentIndexChanged.connect(self.targetChanged)
        self.r.stateChanged.connect(self.channelsChanged)
        self.g.stateChanged.connect(self.channelsChanged)
        self.b.stateChanged.connect(self.channelsChanged)
        self.a.stateChanged.connect(self.channelsChanged)
        self.negate.stateChanged.connect(self.channelsChanged)
        self.colorTransformButtonGroup.buttonClicked['QAbstractButton *'].connect(self.colorTransformChanged)

    def operationChanged(self):
        """ Enable/disable operation in MNPR """
        operations = len(self.operationsCBoxDict.keys())
        changedOperation = 0
        for index in range(operations):
            prev = cmds.mnpr(renderOperation=index)
            if self.operationsCBoxDict[index].isChecked():
                cmds.mnpr(renderOperation=index, s=1)
            else:
                cmds.mnpr(renderOperation=index, s=0)
            if cmds.mnpr(renderOperation=index) != prev:
                changedOperation = index
        # give back information as to what the toggle is doing with mnpr
        print("mnpr -renderOperation {0} -s {1};".format(changedOperation, int(self.sender().isChecked())))

    def reloadOperationShaders(self):
        """ Reload shader of operation """
        operationIndex = self.sender().property("operationIndex")
        cmds.mnpr(rOS=operationIndex)
        print("mnpr -rOS {0};".format(operationIndex))

    def targetChanged(self):
        """ Change and visualize render target """
        cmds.mnpr(renderTarget=self.targetCoBox.currentIndex())
        print("mnpr -renderTarget {0};".format(self.targetCoBox.currentIndex()))

    def channelsChanged(self):
        """ Enable/disable RGBA channels """
        neg = 1 - self.negate.isChecked() * 2
        r = self.r.isChecked()
        g = self.g.isChecked()
        b = self.b.isChecked()
        a = self.a.isChecked()
        if self.sender() == self.a:
            if a:
                # alpha channel display was enabled -> disable color channels
                # save rgb
                self.cChannels[0] = r
                self.cChannels[1] = g
                self.cChannels[2] = b
                # uncheck rgb
                self.r.setChecked(False)
                self.g.setChecked(False)
                self.b.setChecked(False)
                # disable rgb
                self.r.setDisabled(True)
                self.g.setDisabled(True)
                self.b.setDisabled(True)
            else:
                # alpha channel display was disabled -> restore color channels
                # enable rgb
                self.r.setDisabled(False)
                self.g.setDisabled(False)
                self.b.setDisabled(False)
                # check rgb
                self.r.setChecked(self.cChannels[0])
                self.g.setChecked(self.cChannels[1])
                self.b.setChecked(self.cChannels[2])
                # set rgb
                r = self.cChannels[0]
                g = self.cChannels[1]
                b = self.cChannels[2]
        cmds.mnpr(ch=(r * neg, g * neg, b * neg, a * neg))
        if not a:
            print("mnpr -ch {0} {1} {2} {3}".format(r * neg, g * neg, b * neg, a * neg))
        else:
            print("mnpr -ch 0 0 0 {0}".format(a * neg))

    def colorTransformChanged(self, obj=0):
        """
        Perform and visualize color transformation
        Args:
            obj (QAbstractButton): Radiobutton of UI
        """
        colorTransformMode = 0  # keep original colors
        if obj == self.colorTransform1:
            colorTransformMode = 1
        elif obj == self.colorTransform2:
            colorTransformMode = 2
        cmds.mnpr(ct=(colorTransformMode))
        print("mnpr -ct {0};".format(colorTransformMode))


#                       _
#    _ __ ___ _ __   __| | ___ _ __ ___ _ __
#   | '__/ _ \ '_ \ / _` |/ _ \ '__/ _ \ '__|
#   | | |  __/ | | | (_| |  __/ | |  __/ |
#   |_|  \___|_| |_|\__,_|\___|_|  \___|_|
#
class ViewportRendererUI(qt.CoopMayaUI):
    """ UI class for the MNPR viewport renderer """

    def __init__(self, rebuild=False):
        super(ViewportRendererUI, self).__init__("Viewport Renderer", dock=False, rebuild=rebuild, brand=mnpr_info.brand,
                                                 tooltip="UI to render from the viewport")
        cmds.colorManagementPrefs(e=True, outputTransformEnabled=True)

    def buildUI(self):
        self.setGeometry(800, 400, 200, 300)

        # Create Controls
        self.layout.addWidget(self.header)  # header from CoopMayaUI

        # Frame capture
        frameCapBox = QtWidgets.QGroupBox("Frame Capture")
        frameCapLayout = QtWidgets.QVBoxLayout(frameCapBox)
        # Frame capture widgets
        frameCapLabel = QtWidgets.QLabel("Save current frame:")
        frameCapBtn = QtWidgets.QPushButton("Save")
        frameCapGrp = qt.WidgetGroup([frameCapLabel, frameCapBtn], QtWidgets.QHBoxLayout())
        self.frameCapCustomChBox = QtWidgets.QCheckBox("Custom Resolution")
        self.frameCapWLabel = QtWidgets.QLabel("w: ")
        self.frameCapWLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.frameCapWLabel.setEnabled(False)
        self.frameCapWSpin = QtWidgets.QSpinBox()
        self.frameCapWSpin.setRange(1, 16384)
        self.frameCapWSpin.setValue(1920)
        self.frameCapWSpin.setEnabled(False)
        self.frameCapHLabel = QtWidgets.QLabel("h: ")
        self.frameCapHLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.frameCapHLabel.setEnabled(False)
        self.frameCapHSpin = QtWidgets.QSpinBox()
        self.frameCapHSpin.setRange(1, 16384)
        self.frameCapHSpin.setValue(1080)
        self.frameCapHSpin.setEnabled(False)
        frameCapCustomResGrp = qt.WidgetGroup([self.frameCapWLabel, self.frameCapWSpin, self.frameCapHLabel, self.frameCapHSpin], QtWidgets.QHBoxLayout())
        frameCapFormatLabel = QtWidgets.QLabel("format:")
        frameCapFormatLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.frameCapFormatCoBox = QtWidgets.QComboBox()
        self.frameCapFormatCoBox.addItems(lib.IMGFORMATS.keys())
        self.supersampleImgChBox = QtWidgets.QCheckBox("Supersampling")
        self.supersampleImgChBox.setChecked(True)
        self.supersampleImgChBox.setToolTip("Increases internal render image size for anti-aliasing")
        frameCapCustomSettingsGrp = qt.WidgetGroup([self.supersampleImgChBox, frameCapFormatLabel, self.frameCapFormatCoBox], QtWidgets.QHBoxLayout())
        # viewport to render
        self.viewport2RenderChBox = QtWidgets.QCheckBox("Stylized Render")
        self.viewport2RenderChBox.setChecked(True)

        # Add frame capture widgets
        frameCapLayout.addWidget(frameCapGrp)
        frameCapLayout.addWidget(self.frameCapCustomChBox)
        frameCapLayout.addWidget(frameCapCustomResGrp)
        frameCapLayout.addWidget(frameCapCustomSettingsGrp)
        frameCapLayout.addWidget(self.viewport2RenderChBox)

        # Quick playblast
        playblastBox = QtWidgets.QGroupBox("Quick Playblast")
        playblastLayout = QtWidgets.QVBoxLayout(playblastBox)
        # Playblast widgets
        self.supersamplePlbChBox = QtWidgets.QCheckBox("Supersampling")
        self.supersamplePlbChBox.setChecked(True)
        self.supersamplePlbChBox.setToolTip("Increases internal render image size for anti-aliasing")
        self.supersamplePlbChBox.setEnabled(True)
        self.playblastSettingsViewportRaBtn = QtWidgets.QRadioButton("From Viewport")
        self.playblastSettingsViewportRaBtn.setToolTip("Playblast from viewport settings")
        self.playblastSettingsViewportRaBtn.setChecked(True)
        self.playblastSettingsRenderRaBtn = QtWidgets.QRadioButton("From Render Settings")
        self.playblastSettingsRenderRaBtn.setToolTip("Playblast from render settings")
        playblastBtn = QtWidgets.QPushButton("Playblast")
        # Add playblast widgets
        playblastLayout.addWidget(self.supersamplePlbChBox)
        playblastLayout.addWidget(self.playblastSettingsViewportRaBtn)
        playblastLayout.addWidget(self.playblastSettingsRenderRaBtn)
        playblastLayout.addWidget(playblastBtn)

        # Populate UI
        ''' Create the main layouts and add widgets '''
        self.layout.addWidget(frameCapBox)
        self.layout.addWidget(qt.HLine(height=20 * self.dpiS))
        self.layout.addWidget(playblastBox)
        self.layout.addWidget(self.brand)

        # Create connections
        ''' SIGNALS '''
        frameCapBtn.clicked.connect(self.renderFrame)
        playblastBtn.clicked.connect(self.playblast)
        self.frameCapCustomChBox.toggled.connect(self.customRes)

    def customRes(self):
        """ Enables the input of custom resolution sizes """
        if self.frameCapCustomChBox.isChecked():
            self.frameCapWLabel.setEnabled(True)
            self.frameCapWSpin.setEnabled(True)
            self.frameCapHLabel.setEnabled(True)
            self.frameCapHSpin.setEnabled(True)
        else:
            self.frameCapWLabel.setEnabled(False)
            self.frameCapWSpin.setEnabled(False)
            self.frameCapHLabel.setEnabled(False)
            self.frameCapHSpin.setEnabled(False)

    def renderFrame(self):
        """ Gather all information from UI to render current frame """
        # get width and height
        modelPanel = lib.getActiveModelPanel()
        width = cmds.modelEditor(modelPanel, w=True, q=True)
        height = cmds.modelEditor(modelPanel, h=True, q=True)
        if self.frameCapCustomChBox.isChecked():
            width = self.frameCapWSpin.value()
            height = self.frameCapHSpin.value()
        # get render size (supersampling or not)
        renderSize = 1
        if self.supersampleImgChBox.isChecked():
            renderSize = 2
        # get save directory
        fileFilter = "*" + self.frameCapFormatCoBox.currentText()
        saveDir = cmds.fileDialog2(fileFilter=fileFilter, fileMode=0, cap="Save image in:", dialogStyle=2)
        if not saveDir:
            cmds.error("Filename not specified")
        saveDir = saveDir[0]
        # get image format
        imgFormat = self.frameCapFormatCoBox.currentText()
        # get renderer
        override = mnpr_info.prototype
        if not self.viewport2RenderChBox.isChecked():
            override = ""
        # render frame using npr system
        mnpr_system.renderFrame(saveDir, width, height, renderSize, imgFormat, override)

    def playblast(self):
        """ Gather all information from UI to playblast current timeline """
        # FROM VIEWPORT
        # get width and height
        modelPanel = lib.getActiveModelPanel()
        width = cmds.modelEditor(modelPanel, w=True, q=True)
        height = cmds.modelEditor(modelPanel, h=True, q=True)
        # get camera to work from
        currentCamera = cmds.modelEditor(modelPanel, cam=True, q=True)
        currentCameraShape = cmds.listRelatives(currentCamera, s=True)
        if currentCameraShape:
            currentCameraShape = currentCameraShape[0]
        else:
            # we already had the camera shape
            currentCameraShape = currentCamera
        renderCamera = currentCameraShape  # in case none is selected as renderable
        # FROM RENDER SETTINGS
        if self.playblastSettingsRenderRaBtn.isChecked():
            # get with and height
            width = cmds.getAttr("defaultResolution.width")
            height = cmds.getAttr("defaultResolution.height")
            # get camera
            cameras = cmds.ls(type='camera')
            for cam in cameras:
                if cmds.getAttr("{0}.renderable".format(cam)) == 1:
                    renderCamera = cam
        # define where to playblast to
        fileFilter = "*.mov"
        saveDir = cmds.fileDialog2(fileFilter=fileFilter, fileMode=0, cap="Save video in:", dialogStyle=2)
        if not saveDir:
            cmds.error("Filename not specified")
        saveDir = saveDir[0]
        # get render size (supersampling or not)
        renderSize = 1
        if self.supersamplePlbChBox.isChecked():
            renderSize = 2
        # playblast timeline using npr system
        print(renderSize)
        mnpr_system.playblast(saveDir, width, height, renderCamera, modelPanel, renderSize)
