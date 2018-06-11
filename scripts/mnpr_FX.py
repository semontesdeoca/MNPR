"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                   _______  __
    _ __ ___  _ __  _ __  _ __    |  ___\ \/ /
   | '_ ` _ \| '_ \| '_ \| '__|   | |_   \  /
   | | | | | | | | | |_) | |      |  _|  /  \
   |_| |_| |_|_| |_| .__/|_|      |_|   /_/\_\
                   |_|
@summary:       MNPR's noiseFX and paintFX interface
"""
import os, logging
from PySide2 import QtWidgets, QtCore, QtGui
import maya.mel as mel
import maya.cmds as cmds
import coopLib as lib
import coopQt as qt
import mnpr_system
import mnpr_info
import mnpr_pFX as pFX
import mnpr_nFX as nFX

logging.basicConfig()  # errors and everything else (2 separate log groups)
logger = logging.getLogger("mnpr_FX")  # create a logger for this file
logger.setLevel(logging.DEBUG)  # defines the logging level (INFO for releases)
# logger.setLevel(logging.INFO)  # defines the logging level (DEBUG for debugging)


#########################################################################################################
#
#             _
#    ___  ___| |__   ___ _ __ ___   __ _
#   / __|/ __| '_ \ / _ \ '_ ` _ \ / _` |
#   \__ \ (__| | | |  __/ | | | | | (_| |
#   |___/\___|_| |_|\___|_| |_| |_|\__,_|
#
# IMPORTANT: Please adhere to this schema for cross-stylistic compatibility using MNPR
#
# VERTEX CONTROL SEPARATED INTO 3 VERTEX COLOR SETS THAT RENDER TO 4 CONTROL TARGETS
# - pigmentCtrlTarget
# - substrateCtrlTarget
# - edgeCtrlTarget
# - abstractCtrlTarget
#
# Note: Abstraction is embedded in the alpha channel of each vertex color set
#
# controlSetA (Pigmentation effects):
#    RED   - general   : PIGMENT VARIATIONS
#          - watercolor: -
#          - oil paint : -
#          - charcoal  : -
#    GREEN - general   : PIGMENT APPLICATION
#          - watercolor: pigment application (granulation - dry-brush)
#          - oil paint : pigment application (impasto - dry-brush)
#          - charcoal  : pigment application 
#    BLUE  - general   : PIGMENT DENSITY
#          - watercolor: pigment density
#          - oil paint : pigment density
#          - charcoal  : pigment darkness 
#    ALPHA - general   : DETAIL | [RED in abstraction target]
#          - watercolor: -
#          - oil paint : color detail
#          - charcoal  : smudging
#
# controlSetB (Substrate Effects):
#    RED   - general   : SUBSTRATE DISTORTION
#          - watercolor: substrate distortion
#          - oil paint : substrate distortion
#          - charcoal  :
#    GREEN - general   :  U-INCLINATION (also used to specify direction, in general)
#          - watercolor: -
#          - oil paint : -
#          - charcoal  : -
#    BLUE  - general   : V-INCLINATION (also used to specify direction, in general)
#          - watercolor: -
#          - oil paint : -
#          - charcoal  : -
#    ALPHA - general   : SHAPE | [GREEN in abstraction target]
#          - watercolor: -
#          - oil paint : -
#          - charcoal  : -
#
# controlSetC (Edge effects):
#    RED   - general   : EDGE INTENSITY
#          - watercolor: edge darkening
#          - oil paint : -
#          - charcoal  : -
#    GREEN - general   : EDGE WIDTH
#          - watercolor: edge width
#          - oil paint : -
#          - charcoal  : 
#    BLUE  - general   : EDGE TRANSITION
#          - watercolor: gaps and overlaps
#          - oil paint : gaps and overlaps
#          - charcoal  :
#    ALPHA - general   : BLENDING | [BLUE in abstraction target]
#          - watercolor: color bleeding
#          - oil paint : paint stroke length
#          - charcoal  : mixing
#
# ===========================================================================================


# MNPR FX class
class MNPR_FX:
    """
    MNPR_FX class contains the required information to create an art-directed effect and
    automatically generate the required UI widgets to control
    """
    def __init__(self, name, description, controlSet, channels, paintOptions=["Increase", "Decrease"], procOptions=["noise"]):
        self.name = name  # effect name
        self.description = description  # description of effect
        self.controlSet = controlSet  # vtx control set containing this effect
        self.channels = channels  # channels that control this effect
        self.paintOptions = paintOptions  # vertex paint options
        self.procOptions = procOptions  # procedural material options


def getStyleFX():
    """
    Defines and returns the style effects
    Returns: style effects (list of MNPR_FX)
    """
    # general effects
    distortionFX = MNPR_FX("distortion", "Substrate distortion", "controlSetB", [[1, 0, 0, 0]], ["distort", "revert"], ["noise"])
    gapsOverlapsFX = MNPR_FX("gaps-overlaps", "Gaps and overlaps", "controlSetC", [[0, 0, 1, 0]], ["overlaps", "gaps"], ["noise"])

    # watercolor effects
    densityFX_WC = MNPR_FX("density", "Pigment turbulence", "controlSetA", [[0, 0, 1, 0]], ["accumulate", "dilute"], ["noise"])
    applicationFX_WC = MNPR_FX("application", "Granulate | Dry-brush", "controlSetA", [[0, 1, 0, 0]], ["granulate", "dry-brush"], ["noise"])
    blendingFX_WC = MNPR_FX("blending", "Color bleeding (wet-in-wet)", "controlSetC", [[0, 0, 0, 1]], ["bleed", "revert"], ["noise"])
    edgeFX_WC = MNPR_FX("edge manip", "Edge darkening", "controlSetC", [[1, 0, 0, 0], [0, 1, 0, 0]], ["darken", "lighten", "wider", "narrower"], ["n. dark", "n. wide"])
    watercolorFX = [densityFX_WC, applicationFX_WC, distortionFX, edgeFX_WC, gapsOverlapsFX, blendingFX_WC]

    # oil effects
    densityFX_OP = MNPR_FX("density", "Pigment turbulence", "controlSetA", [[0, 0, 1, 0]], ["accumulate", "dilute"], ["noise"])
    blendingFX_OP = MNPR_FX("blending", "Paint stroke length", "controlSetC", [[0, 0, 0, 1]], ["increase", "decrease"], ["noise"])
    detailFX_OP = MNPR_FX("detail", "Paint stroke width", "controlSetA", [[0, 0, 0, 1]], ["increase", "decrease"], ["noise"])
    applicationFX_OP = MNPR_FX("application", "Impasto | Dry-brush", "controlSetA", [[0, 1, 0, 0]], ["impasto", "dry-brush"], ["noise"])
    oilFX = [densityFX_OP, blendingFX_OP, detailFX_OP, applicationFX_OP, distortionFX, gapsOverlapsFX]

    # charcoal effects
    densityFX_CH = MNPR_FX("density", "Pigment density", "controlSetA", [[0, 0, 1, 0]], ["accumulate", "dilute"], ["noise"])
    applicationFX_CH = MNPR_FX("application", "Pigment application", "controlSetA", [[0, 1, 0, 0]], ["even", "granulation"], ["noise"])
    mixingFX_CH = MNPR_FX("mixing", "Mixing", "controlSetC", [[0, 0, 0, 1]], ["mix", "separate"], ["noise"])
    smudgingFX_CH = MNPR_FX("smudging", "Smudging", "controlSetA", [[0, 0, 0, 1]], ["smudge", "revert"], ["noise"])
    edgeFX_CH = MNPR_FX("edge manip", "Edge manipulation", "controlSetC", [[1, 0, 0, 0]], ["soften", "revert"], ["n. soften", "n. darken"])
    charcoalFX = [distortionFX, densityFX_CH, applicationFX_CH, mixingFX_CH, smudgingFX_CH, edgeFX_CH]

    # query mnpr style and return
    style = cmds.mnpr(style=True, q=True).encode('latin1')  # some users have had problems without encode('latin1')
    if style == "Watercolor":
        return watercolorFX
    elif style == "Oil":
        return oilFX
    elif style == "Charcoal":
        return charcoalFX
    return []


#    _   _ ___
#   | | | |_ _|
#   | | | || |
#   | |_| || |
#    \___/|___|
#
class MNPR_FX_UI(qt.CoopMayaUI):
    """
    The UI class for paint FX window
    """
    windowTitle = "mnprFX"

    def __init__(self, dock=False, rebuild=False, tab="vertex-space"):
        # checks
        if not mnpr_info.environment:
            mnpr_info.loadRenderer()
        if not cmds.contextInfo("artAttrColorPerVertexContext", ex=True):
            mel.eval("PaintVertexColorToolOptions;")
            cmds.evalDeferred('maya.mel.eval("SelectTool;")')

        # initialize
        self.tab = tab
        super(MNPR_FX_UI, self).__init__(self.windowTitle, dock=dock, rebuild=rebuild, brand=mnpr_info.brand, tooltip="Paint local stylization effects")


    def buildUI(self):

        self.setGeometry(100, 100, 270 * self.dpiS, 720 * self.dpiS)
        self.setMaximumWidth(280 * self.dpiS)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # scroll area
        scrollWidget = QtWidgets.QWidget()
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                   QtWidgets.QSizePolicy.Maximum)  # avoid spacing between elements when resizing
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollLayout.setSpacing(0)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        scrollArea.setWidget(scrollWidget)
        self.layout.addWidget(scrollArea)

        # tabs
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet(
            "QTabWidget::pane{ border: 0; } QTabBar::tab:selected{background-color: rgb(69, 69, 69);} QTabBar::tab{background-color: rgb(40, 40, 40);}")
        self.scrollLayout.addWidget(self.tabWidget)
        materialSpaceWidget = QtWidgets.QWidget()
        materialSpaceWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                        QtWidgets.QSizePolicy.Maximum)  # avoid spacing between elements when resizing
        materialSpaceLayout = QtWidgets.QVBoxLayout(materialSpaceWidget)
        materialSpaceLayout.setContentsMargins(0, 0, 0, 0)
        materialSpaceLayout.setSpacing(5 * self.dpiS)
        vertexSpaceWidget = QtWidgets.QWidget()
        vertexSpaceWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                        QtWidgets.QSizePolicy.Maximum)  # avoid spacing between elements when resizing
        vertexSpaceLayout = QtWidgets.QVBoxLayout(vertexSpaceWidget)
        vertexSpaceLayout.setContentsMargins(0, 0, 0, 0)
        vertexSpaceLayout.setSpacing(5 * self.dpiS)

        self.tabWidget.addTab(materialSpaceWidget, "material-space")
        self.tabWidget.addTab(vertexSpaceWidget, "vertex-space")

        if self.tab == "vertex-space":
            self.tabWidget.setCurrentIndex(1)

        # get style FX
        FX = getStyleFX()

        #                    _            _       _                                    
        #    _ __ ___   __ _| |_ ___ _ __(_) __ _| |          ___ _ __   __ _  ___ ___ 
        #   | '_ ` _ \ / _` | __/ _ \ '__| |/ _` | |  _____  / __| '_ \ / _` |/ __/ _ \
        #   | | | | | | (_| | ||  __/ |  | | (_| | | |_____| \__ \ |_) | (_| | (_|  __/
        #   |_| |_| |_|\__,_|\__\___|_|  |_|\__,_|_|         |___/ .__/ \__,_|\___\___|
        #                                                        |_|                   
        # material-space tab
        pad = 5 * self.dpiS
        materialHeaderWidget = QtWidgets.QWidget()
        materialSpaceLayout.addWidget(materialHeaderWidget)
        materialHeaderLayout = QtWidgets.QHBoxLayout(materialHeaderWidget)
        materialHeaderLayout.setContentsMargins(pad, pad, pad, pad)
        materialTabLabel = QtWidgets.QLabel("NoiseFX on material")
        materialTabLabel.setStyleSheet("QLabel {font-weight: bold;}")
        materialHeaderLayout.addWidget(materialTabLabel)
        materialHeaderLayout.addStretch()
        materialPresetsBtn = QtWidgets.QPushButton("presets")
        materialHeaderLayout.addWidget(materialPresetsBtn, QtCore.Qt.AlignRight)
        materialPresetsBtn.setMaximumWidth(45 * self.dpiS)
        materialPresetsBtn.setToolTip("Open shaderFX presets")
        materialPresetsBtn.setEnabled(False)

        # UI separator
        materialSpaceLayout.addWidget(qt.HLine())

        # create noise widgets
        for fx in FX:
            nWidget = NoiseWidget(fx, self.dpiS)
            materialSpaceLayout.addWidget(nWidget)

        # world scale slider
        self.wScaleSld = LabeledSlider("World Scale", self.dpiS, leftMargin=10, rightMargin=10, topMargin=10, bottomMargin=10)
        self.wScaleSld.slider.valueChanged.connect(lambda: nFX.noiseWorldScale(self.wScaleSld))
        materialSpaceLayout.addWidget(self.wScaleSld)
        materialSpaceLayout.addStretch()

        #                   _
        #   __   _____ _ __| |_ _____  __          ___ _ __   __ _  ___ ___
        #   \ \ / / _ \ '__| __/ _ \ \/ /  _____  / __| '_ \ / _` |/ __/ _ \
        #    \ V /  __/ |  | ||  __/>  <  |_____| \__ \ |_) | (_| | (_|  __/
        #     \_/ \___|_|   \__\___/_/\_\         |___/ .__/ \__,_|\___\___|
        #                                             |_|
        # vertex-space tab
        # import / export
        pad = 5 * self.dpiS
        vertexHeaderWidget = QtWidgets.QWidget()
        vertexSpaceLayout.addWidget(vertexHeaderWidget)
        vertexHeaderLayout = QtWidgets.QHBoxLayout(vertexHeaderWidget)
        vertexHeaderLayout.setContentsMargins(pad, pad, pad, pad)
        vertexTabLabel = QtWidgets.QLabel("PaintFX on vertices")
        vertexTabLabel.setStyleSheet("QLabel {font-weight: bold;}")
        vertexHeaderLayout.addWidget(vertexTabLabel)
        vertexHeaderLayout.addStretch()
        vertexImportBtn = QtWidgets.QPushButton("import")
        vertexHeaderLayout.addWidget(vertexImportBtn, QtCore.Qt.AlignRight)
        vertexImportBtn.setMaximumWidth(45 * self.dpiS)
        vertexImportBtn.setToolTip("Import painted effects")
        vertexImportBtn.clicked.connect(lambda: pFX.importPaintFX())
        vertexExportBtn = QtWidgets.QPushButton("export")
        vertexHeaderLayout.addWidget(vertexExportBtn, QtCore.Qt.AlignRight)
        vertexExportBtn.setMaximumWidth(45 * self.dpiS)
        vertexExportBtn.setToolTip("Export painted effects")
        vertexExportBtn.clicked.connect(lambda: pFX.exportPaintFX())

        vertexSpaceLayout.addWidget(qt.HLine())  # separator

        # create paint widgets
        for fx in FX:
            pWidget = PaintWidget(fx, self.dpiS)
            vertexSpaceLayout.addWidget(pWidget)

        vertexSpaceLayout.addStretch()  # stretch

        # footer
        self.layout.addWidget(self.brand)


#                _       _              _     _            _
#    _ __   __ _(_)_ __ | |_  __      _(_) __| | __ _  ___| |_
#   | '_ \ / _` | | '_ \| __| \ \ /\ / / |/ _` |/ _` |/ _ \ __|
#   | |_) | (_| | | | | | |_   \ V  V /| | (_| | (_| |  __/ |_
#   | .__/ \__,_|_|_| |_|\__|   \_/\_/ |_|\__,_|\__, |\___|\__|
#   |_|                                         |___/
class PaintWidget(QtWidgets.QWidget):
    def __init__(self, fx, dpiS=1.0):
        # run __init__ of inherited widget
        super(PaintWidget, self).__init__()
        self.fx = fx
        self.dpiS = dpiS
        self.optionWidgets = dict()
        self.iconDir = os.path.join(mnpr_info.iconDir, "pFx")
        # build UI
        self.buildUI()

    def buildUI(self):
        self.setFixedHeight(95 * self.dpiS)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)  # avoid spacing between elements when resizing

        # header
        sider = VerticalLabel(self.fx.name, self.dpiS)
        layout.addWidget(sider)

        # paintKey column
        paintKeyColumnWidget = QtWidgets.QWidget()
        layout.addWidget(paintKeyColumnWidget)
        paintKeyColumnLayout = QtWidgets.QVBoxLayout(paintKeyColumnWidget)
        paintKeyColumnLayout.setContentsMargins(10 * self.dpiS, 15 * self.dpiS, 10 * self.dpiS, 0)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(50, 50, 50, 255))
        paintKeyColumnWidget.setAutoFillBackground(True)
        paintKeyColumnWidget.setPalette(palette)
        # paintKey column widgets
        # paint button
        style = cmds.mnpr(q=True, style=True)
        iconName = lib.toCamelCase("{0}_{1}.png".format(self.fx.name, style))
        paintIconDir = os.path.join(self.iconDir, iconName)
        paintBtn = qt.IconButton(paintIconDir, "Paint {0}".format(self.fx.description), [45 * self.dpiS, 45 * self.dpiS])
        paintKeyColumnLayout.addWidget(paintBtn)
        # key buttons
        keysWidget = QtWidgets.QWidget()
        paintKeyColumnLayout.addWidget(keysWidget)
        keysLayout = QtWidgets.QHBoxLayout(keysWidget)
        keysLayout.setContentsMargins(0, 0, 0, 10 * self.dpiS)
        keysLayout.setSpacing(0)
        insertKeyDir = os.path.join(self.iconDir, "insertKey.png")
        insertKeyBtn = qt.IconButton(insertKeyDir, "Keyframe", [14 * self.dpiS, 14 * self.dpiS], hColor=(100, 100, 100))
        keysLayout.addWidget(insertKeyBtn)
        showKeyedTimelineDir = os.path.join(self.iconDir, "timeline.png")
        showKeyedTimelineBtn = qt.IconButton(showKeyedTimelineDir, "Show keys in timeline", [16 * self.dpiS, 8 * self.dpiS], hColor=(100, 100, 100))
        keysLayout.addWidget(showKeyedTimelineBtn)
        removeKeyDir = os.path.join(self.iconDir, "removeKey.png")
        removeKeyBtn = qt.IconButton(removeKeyDir, "Delete Keyframe", [14 * self.dpiS, 14 * self.dpiS], hColor=(100, 100, 100))
        keysLayout.addWidget(removeKeyBtn)

        # settings column
        pad = 5 * self.dpiS
        settingsColumnWidget = QtWidgets.QWidget()
        layout.addWidget(settingsColumnWidget)
        settingsColumnLayout = QtWidgets.QGridLayout(settingsColumnWidget)
        settingsColumnLayout.setContentsMargins(pad, pad, pad, pad)
        settingsColumnLayout.setSpacing(pad)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(60, 60, 60, 255))
        settingsColumnWidget.setAutoFillBackground(True)
        settingsColumnWidget.setPalette(palette)
        # paint options widget
        self.groupBoxWidget = QtWidgets.QGroupBox("{0}".format(self.fx.description))
        settingsColumnLayout.addWidget(self.groupBoxWidget, 1, 1, 2, 2)  # (Widget, row, column, rowspan, colspan)
        groupBoxLayout = QtWidgets.QGridLayout(self.groupBoxWidget)
        groupBoxLayout.setContentsMargins(pad * 3, pad * 3, 0, 0)
        groupBoxLayout.setSpacing(0)
        self.groupBoxWidget.setAutoFillBackground(True)
        self.groupBoxWidget.setStyleSheet(
            "QGroupBox { background-color: rgb(60, 60, 60); border: 0px; font-style: italic; font-weight: bold; }");
        # add radio buttons dynamically
        row = 1
        column = 1
        for key in self.fx.paintOptions:
            self.optionWidgets[key] = QtWidgets.QRadioButton(key)
            groupBoxLayout.addWidget(self.optionWidgets[key], row, column, 1, 1)
            row += 1
            if row > 2:
                column += 1
                row = 1
        self.optionWidgets[self.fx.paintOptions[0]].setChecked(True)
        # reset and flood buttons
        resetBtn = QtWidgets.QPushButton("Reset")
        settingsColumnLayout.addWidget(resetBtn, 3, 1, 1, 1)
        floodBtn = QtWidgets.QPushButton("Flood")
        settingsColumnLayout.addWidget(floodBtn, 3, 2, 1, 1)
        # vertical slider
        self.amountSld = QtWidgets.QSlider(QtCore.Qt.Vertical)
        settingsColumnLayout.addWidget(self.amountSld, 1, 3, 3, 1)
        self.amountSld.setRange(-100, 100)

        """ SIGNALS """
        paintBtn.clicked.connect(lambda: pFX.paintClicked(self))
        insertKeyBtn.clicked.connect(lambda: pFX.paintKeyClicked(self, True))
        showKeyedTimelineBtn.clicked.connect(lambda: pFX.showKeyedTimeline(self))
        removeKeyBtn.clicked.connect(lambda: pFX.paintKeyClicked(self, False))
        for key in self.fx.paintOptions:
            self.optionWidgets[key].clicked.connect(lambda: pFX.paintToggleClicked(self))
        resetBtn.clicked.connect(lambda: pFX.paintFloodClicked(self, True))
        floodBtn.clicked.connect(lambda: pFX.paintFloodClicked(self, False))
        self.amountSld.valueChanged.connect(lambda: pFX.paintValueChanged(self))


#                _                     _     _            _
#    _ __   ___ (_)___  ___  __      _(_) __| | __ _  ___| |_
#   | '_ \ / _ \| / __|/ _ \ \ \ /\ / / |/ _` |/ _` |/ _ \ __|
#   | | | | (_) | \__ \  __/  \ V  V /| | (_| | (_| |  __/ |_
#   |_| |_|\___/|_|___/\___|   \_/\_/ |_|\__,_|\__, |\___|\__|
#                                              |___/
class NoiseWidget(QtWidgets.QWidget):
    def __init__(self, fx, dpiS=1.0):
        # run __init__ of inherited widget
        super(NoiseWidget, self).__init__()
        self.fx = fx
        self.dpiS = dpiS
        self.optionsDict = dict()
        self.iconDir = os.path.join(mnpr_info.iconDir, "nFx")
        # build UI
        self.buildUI()

    def buildUI(self):

        self.setFixedHeight(95 * self.dpiS)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                           QtWidgets.QSizePolicy.Maximum)  # avoid spacing between elements when resizing

        # header
        sider = VerticalLabel(self.fx.name, self.dpiS)
        layout.addWidget(sider)

        # type column
        typeColumnWidget = QtWidgets.QWidget()
        layout.addWidget(typeColumnWidget)
        typeColumnLayout = QtWidgets.QVBoxLayout(typeColumnWidget)
        typeColumnLayout.setContentsMargins(10 * self.dpiS, 15 * self.dpiS, 10 * self.dpiS, 10 * self.dpiS)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(50, 50, 50, 255))
        typeColumnWidget.setAutoFillBackground(True)
        typeColumnWidget.setPalette(palette)
        # type column widgets
        # material button
        style = cmds.mnpr(q=True, style=True)
        iconName = lib.toCamelCase("{0}_{1}.png".format(self.fx.name, style))
        noiseIconDir = os.path.join(self.iconDir, iconName)
        noiseBtn = qt.IconButton(noiseIconDir, "Noise {0}".format(self.fx.name), [45 * self.dpiS, 45 * self.dpiS], hColor=(100, 100, 100))
        typeColumnLayout.addWidget(noiseBtn)
        # type options
        typeOptionsGrp = QtWidgets.QWidget()
        typeColumnLayout.addWidget(typeOptionsGrp)
        typeOptionsLayout = QtWidgets.QHBoxLayout(typeOptionsGrp)
        typeOptionsLayout.setContentsMargins(0, 0, 0, 0)
        typeOptionsLayout.setSpacing(0)
        toggleIconDir = os.path.join(self.iconDir, "io.png")
        toggleBtn = qt.IconButton(toggleIconDir, "On | Off", [14 * self.dpiS, 14 * self.dpiS], hColor=(100, 100, 100))
        typeOptionsLayout.addWidget(toggleBtn)
        typeIconDir = os.path.join(self.iconDir, "3D2D.png")
        typeBtn = qt.IconButton(typeIconDir, "3D | 2D", [28 * self.dpiS, 14 * self.dpiS], hColor=(100, 100, 100))
        typeOptionsLayout.addWidget(typeBtn)

        # settings column
        pad = 5 * self.dpiS
        settingsColumnWidget = QtWidgets.QWidget()
        settingsColumnWidget.setFixedWidth(186 * self.dpiS)
        layout.addWidget(settingsColumnWidget)
        settingsColumnLayout = QtWidgets.QGridLayout(settingsColumnWidget)
        settingsColumnLayout.setContentsMargins(pad, pad, pad, pad*1.5)
        settingsColumnLayout.setSpacing(pad)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(60, 60, 60, 255))
        settingsColumnWidget.setAutoFillBackground(True)
        settingsColumnWidget.setPalette(palette)
        # noise options widget
        self.groupBoxWidget = QtWidgets.QGroupBox("{0}".format(self.fx.description))
        settingsColumnLayout.addWidget(self.groupBoxWidget, 1, 1, 2, 2)  # (Widget, row, column, rowspan, colspan)
        groupBoxLayout = QtWidgets.QVBoxLayout(self.groupBoxWidget)
        spacing = pad
        top = pad * 5
        if len(self.fx.procOptions) < 2:
            spacing *= 3
            top = pad * 6
        groupBoxLayout.setContentsMargins(pad, top, 0, 0)
        groupBoxLayout.setSpacing(spacing)
        self.groupBoxWidget.setAutoFillBackground(True)
        self.groupBoxWidget.setStyleSheet("QGroupBox { background-color: rgb(60, 60, 60); border: 0px; font-style: italic; font-weight: bold; }");
        # add radio buttons dynamically
        self.optionsDict["scale"] = LabeledSlider("scale", dpiS=self.dpiS, labelWidth=40)
        self.optionsDict["scale"].slider.valueChanged.connect(lambda: nFX.noiseSlide(self.fx, self.optionsDict["scale"]))
        groupBoxLayout.addWidget(self.optionsDict["scale"])
        for option in self.fx.procOptions:
            self.optionsDict[option] = LabeledSlider(option, dpiS=self.dpiS, labelWidth=40)
            self.optionsDict[option].slider.valueChanged.connect(self.makeFunc(self.fx, self.optionsDict[option]))
            groupBoxLayout.addWidget(self.optionsDict[option])

        # reset and shift
        resetIconDir = os.path.join(self.iconDir, "reset.png")
        resetBtn = qt.IconButton(resetIconDir, "Reset {0}".format(self.fx.name), [14 * self.dpiS, 14 * self.dpiS], bColor=(60, 60, 60), hColor=(100,100,100))
        settingsColumnLayout.addWidget(resetBtn, 1, 3, 1, 1)
        self.shiftSlider = qt.RelativeSlider(QtCore.Qt.Vertical)
        settingsColumnLayout.addWidget(self.shiftSlider, 2, 3, 2, 1)
        self.shiftSlider.setRange(-100, 100)
        self.shiftSlider.valueChanged.connect(lambda: nFX.noiseShift(self.fx, self.shiftSlider))
        self.shiftSlider.sliderPressed.connect(lambda: nFX.selectMaterials())

        """ SIGNALS """
        noiseBtn.clicked.connect(lambda: mnpr_system.showShaderAttr())
        resetBtn.clicked.connect(lambda: nFX.noiseReset(self.fx))
        typeBtn.clicked.connect(lambda: nFX.noiseTypeClicked(self.fx))
        toggleBtn.clicked.connect(lambda: nFX.noiseToggleClicked(self.fx))

    def makeFunc(self, fx, labeledSlider):
        # function to get around lambdas in loops that override each other
        return lambda: nFX.noiseSlide(fx, labeledSlider)


#             _     _            _
#   __      _(_) __| | __ _  ___| |_ ___
#   \ \ /\ / / |/ _` |/ _` |/ _ \ __/ __|
#    \ V  V /| | (_| | (_| |  __/ |_\__ \
#     \_/\_/ |_|\__,_|\__, |\___|\__|___/
#                     |___/
class VerticalLabel(QtWidgets.QWidget):
    def __init__(self, text=None, dpiS=1.0):
        super(self.__class__, self).__init__()
        self.text = text
        self.dpiS = dpiS

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.rotate(-90)
        sider = QtCore.QRect(-95 * self.dpiS, 0, 95 * self.dpiS, 18 * self.dpiS)
        bgColor = QtGui.QColor(40, 40, 40, 255)
        painter.setPen(bgColor)
        painter.setBrush(bgColor)
        painter.drawRect(sider)

        if self.text:
            painter.setFont(QtGui.QFont(painter.font().family(), painter.font().pointSize(), QtGui.QFont.Bold))
            painter.setPen(QtCore.Qt.lightGray)
            painter.drawText(sider, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.text)
        painter.end()

    def sizeHint(self):
        return QtCore.QSize(18 * self.dpiS, 0)


class LabeledSlider(QtWidgets.QWidget):
    def __init__(self, label, dpiS=1.0, labelWidth=0, leftMargin=0, topMargin=0, rightMargin=0, bottomMargin=0):
        super(LabeledSlider, self).__init__()
        self.dpiS = dpiS
        self.label = label
        self.labelWidth = labelWidth
        self.margins = [leftMargin*dpiS, topMargin*dpiS, rightMargin*dpiS, bottomMargin*dpiS]
        # build UI
        self.buildUI()

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(self.margins[0], self.margins[1], self.margins[2], self.margins[3])
        layout.setSpacing(10 * self.dpiS)

        label = QtWidgets.QLabel(self.label)
        label.setMinimumWidth(self.labelWidth * self.dpiS)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        layout.addWidget(label, 0, 0)
        self.slider = qt.RelativeSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(-100, 100)
        layout.addWidget(self.slider, 0, 1)

        self.slider.sliderPressed.connect(lambda: nFX.selectMaterials())
