///////////////////////////////////////////////////////////////////////////////////
//    __  __ _   _ ____  ____
//   |  \/  | \ | |  _ \|  _ \
//   | |\/| |  \| | |_) | |_) |
//   | |  | | |\  |  __/|  _ <
//   |_|  |_|_| \_|_|   |_| \_\
//
//   \brief MNPR Framework
//   Contains and manages the Maya Non-Photorealistic Renderer (MNPR) using VP2.0
//
//   Originally developed by: Santiago E. Montesdeoca
//   Contributors (a-z): Pierre Bénard, Yee Xin Chiew, Amir Semmo 
//
///////////////////////////////////////////////////////////////////////////////////
#include "MPluginUtils.h"
#include "MOperationShader.h"
#include "MRenderTargetList.h"
#include "mnpr_renderer.h"
#include "mnpr_sceneRender.h"
#include "mnpr_quadRender.h"
#include "mnpr_hudRender.h"
#include "mnpr_present.h"
#include "mnpr_nodes.h"
#include "style_watercolor.hpp"
#include "style_oilpaint.hpp"
#include "style_charcoal.hpp"
#include <chrono>


const MString PLUGIN_NAME = "MNPR";                  // the same name as your plugin with no spaces or special characters
const MString RENDERER_NAME = "MNPR";               // name in the renderer to appear in the Maya viewport
const MString AUTHOR_NAME = "Santiago Montesdeoca";  // name of the author of the override
const MString PURPOSE = "Research";                  // purpose of plugin ("Research" or "Client")
const std::vector<MString> STYLES = { "Framework", "Watercolor", "Charcoal" };  // supported styles

MHWRender::MRasterFormat MNPROverride::colorDepths[3] = { MHWRender::kR8G8B8A8_SNORM, MHWRender::kR16G16B16A16_SNORM, MHWRender::kR32G32B32A32_FLOAT };


MStatus MNPROverride::addCustomTargets() {
    // CUSTOM TARGETS FOR STYLIZATION
    if (mEngSettings.style == "Watercolor") {
        wc::addTargets(mRenderTargets);
    }
    else if (mEngSettings.style == "Oil") {
        op::addTargets(mRenderTargets);
    }
    else if (mEngSettings.style == "Charcoal") {
        ch::addTargets(mRenderTargets);
    }
    return MS::kSuccess;
}


MStatus MNPROverride::addCustomOperations() {
    // STYLIZATION OPERATIONS
    if (mEngSettings.style == "Watercolor") {
        wc::addOperations(mOperations, mRenderTargets, mEngSettings, mFxParams);
    }
    else if (mEngSettings.style == "Oil") {
        op::addOperations(mOperations, mRenderTargets, mEngSettings, mFxParams);
    }
    else if (mEngSettings.style == "Charcoal") {
        ch::addOperations(mOperations, mRenderTargets, mEngSettings, mFxParams);
    }
    return MS::kSuccess;
}



//                             _     _      
//     _____   _____ _ __ _ __(_) __| | ___ 
//    / _ \ \ / / _ \ '__| '__| |/ _` |/ _ \
//   | (_) \ V /  __/ |  | |  | | (_| |  __/
//    \___/ \_/ \___|_|  |_|  |_|\__,_|\___|
//                                          
// renderer constructor
MNPROverride::MNPROverride(const MString& name, const MString& uiName) :
    MRenderOverride(name), mRendererName(uiName) {

    cout << "CREATING RENDER OVERRIDE" << endl;
    MGlobal::displayInfo("Loading render override, please be patient");

    mCheckMayaPointers();			  // check and load maya pointers
    utils::setPluginEnv(name);        // set renderer environment
    mInsertShaderPath();              // insert shader path

    initializeMNPR();  // initialize MNPR
}


void MNPROverride::initializeMNPR() {
    // MNPR TARGETS
    unsigned int tWidth = 1;
    unsigned int tHeight = 1;
    int MSAA = 1;
    unsigned arraySliceCount = 0;
    bool isCubeMap = false;
    MHWRender::MRasterFormat userDepth = colorDepths[mEngSettings.colorDepth];
    MHWRender::MRasterFormat rgba8 = MHWRender::kR8G8B8A8_SNORM;
    MHWRender::MRasterFormat rgb8 = MHWRender::kR8G8B8X8;
    MHWRender::MRasterFormat rgba16f = MHWRender::kR16G16B16A16_FLOAT;
    MHWRender::MRasterFormat rgba32f = MHWRender::kR32G32B32A32_FLOAT;
    mRenderTargets.append(MHWRender::MRenderTargetDescription("colorTarget", tWidth, tHeight, MSAA, userDepth, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("depthTarget", tWidth, tHeight, MSAA, MHWRender::kD24S8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("diffuseTarget", tWidth, tHeight, MSAA, userDepth, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("specularTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("pigmentCtrlTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("substrateCtrlTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("edgeCtrlTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("abstractCtrlTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("substrateTarget", tWidth, tHeight, 1, rgba16f, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("linearDepth", tWidth, tHeight, 1, MHWRender::kR32G32_FLOAT, arraySliceCount, isCubeMap)); // previous frame encoded in y-channel
    // mRenderTargets.append(MHWRender::MRenderTargetDescription("normalsTarget", tWidth, tHeight, MSAA, MHWRender::kR16G16B16A16_SNORM, arraySliceCount, isCubeMap));
    // mRenderTargets.append(MHWRender::MRenderTargetDescription("worldPosTarget", tWidth, tHeight, MSAA, MHWRender::kR16G16B16A16_SNORM, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("edgeTarget", tWidth, tHeight, 1, rgba8, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("velocity", tWidth, tHeight, 1, MHWRender::kR32G32_FLOAT, arraySliceCount, isCubeMap));

    // CUSTOM TARGETS
    addCustomTargets();

    // OUTPUT TARGETS
    mRenderTargets.append(MHWRender::MRenderTargetDescription("stylizationTarget", tWidth, tHeight, 1, userDepth, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("outputTarget", tWidth, tHeight, 1, userDepth, arraySliceCount, isCubeMap));
    mRenderTargets.append(MHWRender::MRenderTargetDescription("presentTarget", tWidth, tHeight, 1, userDepth, arraySliceCount, isCubeMap));

    // dPrintTargets(mRenderTargets);  // print all targets to debug

    // set present operation and active target
    mRenderTargets.setPresentTarget(mRenderTargets.length() - 1);

    // SET CUSTOM OPERATIONS
    MString opName = "";

    opName = "[scene] Maya render";
    sceneOp = new SceneRender(opName,  // name
                              MHWRender::MSceneRender::kRenderShadedItems,  // filter
                              MHWRender::MClearOperation::kClearAll,        // clear mask
                              mRenderTargets);                              // render targets
    mOperations.append(sceneOp);
    std::vector<MString> mnprTargetNames = { "colorTarget", "depthTarget", "diffuseTarget", "specularTarget",
                                             "pigmentCtrlTarget", "substrateCtrlTarget", "edgeCtrlTarget", "abstractCtrlTarget", "velocity" };
    mRenderTargets.setOperationOutputs(opName, mnprTargetNames);


    // post-processing and loading
    opName = "[quad] adjust-load";
    opShader = new MOperationShader("quadAdjustLoad", "adjustLoadMNPR");
    opShader->addParameter("gGamma", mEngSettings.mayaGamma);
    opShader->addParameter("gDepthRange", mEngSettings.depthRange);
    opShader->addParameter("gSaturation", mFxParams.saturation);
    opShader->addParameter("gContrast", mFxParams.contrast);
    opShader->addParameter("gBrightness", mFxParams.brightness);
    opShader->addParameter("gSubstrateColor", mEngSettings.substrateColor);
    opShader->addParameter("gAtmosphereTint", mEngSettings.atmosphereTint);
    opShader->addParameter("gAtmosphereRange", mEngSettings.atmosphereRange);
    opShader->addParameter("gEnableVelocityPV", mEngSettings.velocityPV);
    opShader->addTargetParameter("gColorTex", mRenderTargets.target(0));
    opShader->addTargetParameter("gZBuffer", mRenderTargets.target(mRenderTargets.indexOf("depthTarget")));
    opShader->addTargetParameter("gDiffuseTex", mRenderTargets.target(mRenderTargets.indexOf("diffuseTarget")));
    opShader->addTargetParameter("gSpecularTex", mRenderTargets.target(mRenderTargets.indexOf("specularTarget")));
    opShader->addTargetParameter("gLinearDepthTex", mRenderTargets.target(mRenderTargets.indexOf("linearDepth")));
    opShader->addTargetParameter("gVelocityTex", mRenderTargets.target(mRenderTargets.indexOf("velocity")));
    opShader->addTextureParameter("gSubstrateTex", mEngSettings.substrateTexFilename);
    opShader->addParameter("gSubstrateRoughness", mEngSettings.substrateRoughness);
    quadOp = new QuadRender(opName,
                            MHWRender::MClearOperation::kClearNone,
                            mRenderTargets,
                            *opShader);
    mOperations.append(quadOp);
    std::vector<MString> pTargets = { "stylizationTarget", "substrateTarget", "linearDepth", "velocity" };
    mRenderTargets.setOperationOutputs(opName, pTargets);

    // edge detection
    opName = "[quad] edge detection";
    opShader = new MOperationShader("quadEdgeDetection", "sobelRGBDEdgeDetection");
    opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
    opShader->addTargetParameter("gDepthTex", mRenderTargets.target(mRenderTargets.indexOf("linearDepth")));
    quadOp = new QuadRender(opName,
        MHWRender::MClearOperation::kClearNone,
        mRenderTargets,
        *opShader);
    mOperations.append(quadOp);
    mRenderTargets.setOperationOutputs(opName, { "edgeTarget" });


    // STYLIZATION OPERATIONS
    addCustomOperations();


    // antialiasing
    opName = "[quad] antialiasing";
    opShader = new MOperationShader("quadAA", "FXAA");
    opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
    opShader->addParameter("gRenderScale", mEngSettings.renderScale);
    opShader->addParameter("gAntialiasingQuality", mEngSettings.antialiasing);
    quadOp = new QuadRender(opName,
        MHWRender::MClearOperation::kClearNone,
        mRenderTargets,
        *opShader);
    mOperations.append(quadOp);
    mRenderTargets.setOperationOutputs(opName, { "outputTarget" });
    
    // deferred substrate lighting
    opName = "[quad] substrate lighting";
    if (mEngSettings.style == "Oil") {
        opShader = new MOperationShader("quadSubstrate", "deferredImpastoLighting");
    } else {
        opShader = new MOperationShader("quadSubstrate", "deferredLighting");
    }
    opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("outputTarget")));
    opShader->addTargetParameter("gSubstrateTex", mRenderTargets.target(mRenderTargets.indexOf("substrateTarget")));
    opShader->addParameter("gGamma", mEngSettings.mayaGamma);
    opShader->addParameter("gSubstrateLightDir", mEngSettings.substrateLightDir);
    opShader->addParameter("gSubstrateLightTilt", mEngSettings.substrateLightTilt);
    opShader->addParameter("gSubstrateShading", mEngSettings.substrateShading);
    quadOp = new QuadRender(opName,
        MHWRender::MClearOperation::kClearNone,
        mRenderTargets,
        *opShader);
    mOperations.append(quadOp);
    mRenderTargets.setOperationOutputs(opName, { "outputTarget" });

    // present quad operation (with debugging information)
    opName = "[quad] debugger";
    opShader = new MOperationShader("quadDebug", "debugPresentMNPR");
    opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("outputTarget")));
    opShader->addParameter("gMnprGamma", mEngSettings.mnprGamma);
    opShader->addParameter("gColorChannels", mEngSettings.colorChannels);
    opShader->addParameter("gColorTransform", mEngSettings.colorTransformationMode);
    quadOp = new QuadRender(opName,
        MHWRender::MClearOperation::kClearNone,
        mRenderTargets,
        *opShader);
    mOperations.append(quadOp);
    mRenderTargets.setOperationOutputs(opName, { "presentTarget" });

    // normal Maya UI render
    opName = "[scene] Maya Scene UI";
    sceneOp = new SceneRender(opName,  // name
        MHWRender::MSceneRender::kRenderUIItems,  // filter
        (unsigned int)(MHWRender::MClearOperation::kClearNone),
        mRenderTargets);  // don't clear anything
    mOperations.append(sceneOp);
    mRenderTargets.setOperationOutputs(opName, { "presentTarget", "depthTarget" });

    // HUD render
    MString mnprAPI = MGlobal::executeCommandStringResult("optionVar -q vp2RenderingEngine");
    mnprInfo = RENDERER_NAME + " " + mEngSettings.style + "     (" + mnprAPI + ")";
    auto hudOp = new HUDOperation(&mRenderTargets, mnprInfo);
    mOperations.append(hudOp);

    // present
    opName = "[present]";
    auto presentOp = new PresentTarget(opName, &mRenderTargets);
    mOperations.append(presentOp);

    // dPrintOperations(mOperations);  // print all operations to debug
}

// renderer destructor
MNPROverride::~MNPROverride() {
    cout << "~MNPROverride()" << endl;

    mOperations.clear();     // clear all operations
    mRenderTargets.clear();  // clear all targets

    cleanup();  // end of frame cleanup
}

// begining of frame setup
MStatus MNPROverride::setup(const MString & destPanel) {
    MStatus status = mUpdateRenderer();  // update renderer
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

// end of frame cleanup
MStatus MNPROverride::cleanup() {
    MHWRender::MRenderer::setLightsAndShadowsDirty();
    //texManager->

    return MStatus::kSuccess;
}

// get renderer name (in renderer menu in the viewport panel)
MString MNPROverride::uiName() const {
    return mRendererName;
}

// sets the supported graphics API
MHWRender::DrawAPI MNPROverride::supportedDrawAPIs() const {
    return (MHWRender::kDirectX11 | MHWRender::kOpenGLCoreProfile);
}


//               _
//     __ _  ___| |_
//    / _` |/ _ \ __|
//   | (_| |  __/ |_
//    \__, |\___|\__|
//    |___/
// get fx parameters
FXParameters* MNPROverride::effectParams() {
    return &mFxParams;
}
// get engine settings
EngineSettings* MNPROverride::engineSettings() {
    return &mEngSettings;
}
// get render targets
MStringArray MNPROverride::renderTargets() {
    MStringArray targetNames;
    for (int i = 0; i < mRenderTargets.length()-1; i++) {
        targetNames.append(mRenderTargets[i]->name());
    }
    return targetNames;
}
// get operation names
MStringArray MNPROverride::renderOperations() {
    MStringArray operationNames;
    for (int i = 0; i < mOperations.length()-1; i++) {
        operationNames.append(mOperations[i]->name());
    }
    return operationNames;
}
// get individual operation
MHWRender::MRenderOperation* MNPROverride::renderOperation(MString t_operationName) {
    int idx = mOperations.indexOf(t_operationName);
    if (idx < 0) {
        cout << "ERROR: Operation was not found" << endl;
    }
    return mOperations[idx];
}


//                   _
//     ___ _   _ ___| |_ ___  _ __ ___
//    / __| | | / __| __/ _ \| '_ ` _ \
//   | (__| |_| \__ \ || (_) | | | | | |
//    \___|\__,_|___/\__\___/|_| |_| |_|
//
// reset stylization
void MNPROverride::resetStylization() {
    cout << "RESETTING STYLIZATION" << endl;
    cleanup();
    mOperations.clear();     // clear all operations
    mRenderTargets.clear();  // clear all targets
    initializeMNPR();  // initialize MNPR
}

// reset shader instances to force reload of shaders
// operationIndex: set to -1 (default) to reload all shaders or an to operation index to reload only specific shaders
void MNPROverride::resetShaderInstances(int operationIndex) {
    MOperationShader* opShader;
    QuadRender* quadOp;
    //SceneRender* sceneOp;

    for (int i = 0; i < mOperations.length(); i++) {
        if ((operationIndex == -1 || operationIndex == i) && mOperations[i]->operationType() == MHWRender::MRenderOperation::kQuadRender) {
            cout << "-> Resetting shader instance of " << mOperations[i]->name() << " (QuadRender)" << endl;
            quadOp = (QuadRender *)mOperations[i];
            opShader = quadOp->getOperationShader();
            opShader->resetShaderInstance();
            continue;
        }
        if ((operationIndex == -1 || operationIndex == i) && mOperations[i]->operationType() == MHWRender::MRenderOperation::kSceneRender) {
            cout << "-> Resetting shader instance of "  << mOperations[i]->name() << " (SceneRender)" << endl;
            // scene renders can also present shader overrides, implement a reset shader instance when necessary
            continue;
        }
    }
}

// change color depth of render targets
void MNPROverride::changeColorDepth() {
    cout << "-> Changing color depth" << endl;
    MHWRender::MRasterFormat userDepth = colorDepths[mEngSettings.colorDepth];
    mRenderTargets[mRenderTargets.indexOf("diffuseTarget")]->setRasterFormat(userDepth);
    mRenderTargets[mRenderTargets.indexOf("colorTarget")]->setRasterFormat(userDepth);
    mRenderTargets[mRenderTargets.indexOf("stylizationTarget")]->setRasterFormat(userDepth);
    mRenderTargets[mRenderTargets.indexOf("outputTarget")]->setRasterFormat(userDepth);
    mRenderTargets[mRenderTargets.indexOf("presentTarget")]->setRasterFormat(userDepth);
    mTargetUpdate = true;
}

void MNPROverride::changeAntialiasingEffect() {
    cout << "-> Changing antialiasing effect" << endl;
    opShader = new MOperationShader("quadAAMNPR", "FXAA");
    opShader->addParameter("gAntialiasingQuality", mEngSettings.antialiasing);
}

// change MSAA of targets
void MNPROverride::changeMSAA(unsigned int t_MSAA) {
    for (int i = 0; i < mRenderTargets.length(); i++) {
        mRenderTargets[i]->setMultiSampleCount(t_MSAA);
    }
    mRenderTargets.updateTargetDescriptions();
}

// change the present target
void MNPROverride::changeActiveTarget(unsigned int activeTargetIndex) {
    MOperationShader* opShader;
    QuadRender* quadOp = (QuadRender*)renderOperation("[quad] debugger");
    opShader = quadOp->getOperationShader();
    if (opShader) {
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(activeTargetIndex));
    }
}

// debug the present operation
void MNPROverride::debugOperation(float r = 1, float g = 1, float b = 1, float a = 0) {
    mEngSettings.colorChannels[0] = r;
    mEngSettings.colorChannels[1] = g;
    mEngSettings.colorChannels[2] = b;
    mEngSettings.colorChannels[3] = a;
}

// debug the present using a color transformation
void MNPROverride::debugColorTransform(float mode = 0) {
    mEngSettings.colorTransformationMode[0] = mode;
}

// refresh targets
void MNPROverride::refreshTargets() {
    cout << "-> Refreshing render targets" << endl;
    mRenderTargets[0]->setWidth(1);  // force viewport update
}

void MNPROverride::setPlugin(MObject& plugin) {
    mPlugin = plugin;
}


//                    _            _           _
//    _ __  _ __ ___ | |_ ___  ___| |_ ___  __| |
//   | '_ \| '__/ _ \| __/ _ \/ __| __/ _ \/ _` |
//   | |_) | | | (_) | ||  __/ (__| ||  __/ (_| |
//   | .__/|_|  \___/ \__\___|\___|\__\___|\__,_|
//   |_|
//
// update internal maya pointers in the engine
MStatus MNPROverride::mCheckMayaPointers() {
    renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) return MS::kFailure;
    shaderMgr = renderer->getShaderManager();
    if (!shaderMgr) return MS::kFailure;
    targetManager = renderer->getRenderTargetManager();
    if (!targetManager) return MS::kFailure;
    texManager = renderer->getTextureManager();
    if (!texManager) return MS::kFailure;

    return MS::kSuccess;
}

// insert shader path into the engine
void MNPROverride::mInsertShaderPath() {
    if (shaderMgr) {
        MString nprShaderPath = utils::pluginEnv("shaders");
        //check if nprShaderPath has been included before
        MStringArray shaderPathsArray;
        shaderMgr->shaderPaths(shaderPathsArray);
        bool pathFound = false;
        for (unsigned int i = 0; i < shaderPathsArray.length(); i++) {
            if (shaderPathsArray[i] == nprShaderPath) {
                pathFound = true;
                cout << "-> Shader directory has previously been added" << endl;
                break;
            }
        }
        //add shader path if not found
        if (pathFound == false) {
            shaderMgr->addShaderPath(nprShaderPath);
            cout << "-> Shader directory added: " << nprShaderPath << endl;
        }
    }
}


// update the renderer (runs every frame)
MStatus MNPROverride::mUpdateRenderer() {
    // get current viewport description
    frameContext = this->getFrameContext();
    MHWRender::MRenderTargetDescription viewportDescription;
    MHWRender::MRenderTarget* colorTarget = const_cast<MHWRender::MRenderTarget*>(frameContext->getCurrentColorRenderTarget());
    colorTarget->targetDescription(viewportDescription);

    // time in milliseconds
    auto t1 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> fp_ms = t1.time_since_epoch();
    mEngSettings.time[0] = static_cast<float>(fp_ms.count());

    // three random numbers between 0 and 254 (integer)
    for (int i = 0; i < 3; ++i) {
        srand((unsigned int)mEngSettings.time[0]+i);
        mEngSettings.random[i] = static_cast<float>(rand() % 255);
    }

    // get gamma settings
    if (mEngSettings.mnprGamma[0] == 0.0){
        mEngSettings.mayaGamma[0] = frameContext->getPostEffectEnabled(MHWRender::MFrameContext::kGammaCorrection);
    }

    // update viewport size
    if (mRenderTargets[0]->width() != viewportDescription.width() * mEngSettings.renderScale[0]
        || mRenderTargets[0]->height() != viewportDescription.height() * mEngSettings.renderScale[0]) {
        mTargetUpdate = true;
        int newWidth = int(viewportDescription.width() * mEngSettings.renderScale[0]);
        int newHeight = int(viewportDescription.height() * mEngSettings.renderScale[0]);
        for (int i = 0; i < mRenderTargets.length() - 1; i++) {
            mRenderTargets[i]->setWidth(newWidth);
            mRenderTargets[i]->setHeight(newHeight);
        }
        // output target always the size of the viewport
        mRenderTargets[mRenderTargets.indexOf("outputTarget")]->setWidth(viewportDescription.width());
        mRenderTargets[mRenderTargets.indexOf("outputTarget")]->setHeight(viewportDescription.height());
        mRenderTargets[mRenderTargets.indexOf("presentTarget")]->setWidth(viewportDescription.width());
        mRenderTargets[mRenderTargets.indexOf("presentTarget")]->setHeight(viewportDescription.height());
    }

    // update MSAA
    if (mRenderTargets[0]->multiSampleCount() != viewportDescription.multiSampleCount()) {
        mTargetUpdate = true;
        for (int i = 0; i < mRenderTargets.length(); i++) {
            mRenderTargets[i]->setMultiSampleCount(viewportDescription.multiSampleCount());
        }
    }

    // update frame based attributes
    if (mEngSettings.substrateUpdate[0]) {
        timeMs = (float)animControl.currentTime().as(MTime::kMilliseconds);
        // update position of substrate
        if (abs(timeMs - prevTimeMs) > (mEngSettings.substrateUpdate[0])) {
            // get uv offset in engine
            double intPart = 3.0;
            mEngSettings.substrateUVOffset[0] = (float)modf(sin(timeMs) * 0.5453, &intPart);
            mEngSettings.substrateUVOffset[1] = (float)modf(sin(timeMs) * 0.8317, &intPart);
            prevTimeMs = timeMs;

            // update in shader
            quadOp = (QuadRender*)renderOperation("[quad] adjust-load");
            opShader = quadOp->getOperationShader();
            opShader->textureParameters["gSubstrateTex"]->setUVOffset(&mEngSettings.substrateUVOffset[0]);
            opShader->textureParameters["gSubstrateTex"]->setParams();
        }
    }

    // update targets with new descriptions
    if (mTargetUpdate) {
        for (int i = 0; i < mRenderTargets.length(); i++) {
            mRenderTargets.target(i)->updateDescription(*(mRenderTargets[i]));
        }
        mTargetUpdate = false;
    }

    return MStatus::kSuccess;
}


//        _      _                                    _   _               _
//     __| | ___| |__  _   _  __ _     _ __ ___   ___| |_| |__   ___   __| |___
//    / _` |/ _ \ '_ \| | | |/ _` |   | '_ ` _ \ / _ \ __| '_ \ / _ \ / _` / __|
//   | (_| |  __/ |_) | |_| | (_| |   | | | | | |  __/ |_| | | | (_) | (_| \__ \
//    \__,_|\___|_.__/ \__,_|\__, |   |_| |_| |_|\___|\__|_| |_|\___/ \__,_|___/
//                           |___/
// print operations (DEBUG)
void MNPROverride::dPrintOperations(MHWRender::MRenderOperationList& opsList) {
    cout << "DEBUG: PRINTING OPERATIONS" << endl;
    unsigned int mayaOperations = opsList.length();
    cout << "Total of mOperations: " << mayaOperations << endl;
    for (unsigned int i = 0; i < mayaOperations; i++) {
        cout << "-> " << opsList[i]->name() << endl;
        cout << "OperationType: " << opsList[i]->operationType() << endl;
    }
}

// print targets (DEBUG)
void MNPROverride::dPrintTargets(MRenderTargetList & targetList) {
    cout << "DEBUG: PRINTING TARGETS" << endl;
    unsigned int mayaTargets = targetList.length();
    cout << "Total of mTargets: " << mayaTargets << endl;
    for (unsigned int i = 0; i < mayaTargets; i++) {
        // from targets themselves
        cout << "DEBUG: FROM TARGETS" << endl;
        MHWRender::MRenderTargetDescription t_targetDesc;
        MHWRender::MRenderTarget* t_target = targetList.target(i);
        t_target->targetDescription(t_targetDesc);
        cout << "-> " << t_targetDesc.name() << endl;
        cout << "Dimensions: [" << t_targetDesc.width() << ", " << t_targetDesc.height() << "]" << endl;
        cout << "Raster format: " << t_targetDesc.rasterFormat() << endl;
        cout << "Multi-sampling: " << t_targetDesc.multiSampleCount() << endl;

        // from description list
        cout << "DEBUG: FROM DESCRIPTIONS" << endl;
        cout << "-> " << targetList[i]->name() << endl;
        cout << "Dimensions: [" << targetList[i]->width() << ", " << targetList[i]->height() << "]" << endl;
        cout << "Raster format: " << targetList[i]->rasterFormat() << endl;
        cout << "Multi-sampling: " << targetList[i]->multiSampleCount() << endl;
    }
}
