///////////////////////////////////////////////////////////////////////////////////
//                     __ _                           _
//     ___ ___  _ __  / _(_) __ _     _ __   ___   __| | ___
//    / __/ _ \| '_ \| |_| |/ _` |   | '_ \ / _ \ / _` |/ _ \
//   | (_| (_) | | | |  _| | (_| |   | | | | (_) | (_| |  __/
//    \___\___/|_| |_|_| |_|\__, |   |_| |_|\___/ \__,_|\___|
//                          |___/
//
//   \brief Configuration node
//	 Contains the configuration parameters to define engine settings and fx parameters
///////////////////////////////////////////////////////////////////////////////////
#include <maya/MFnDependencyNode.h>
#include "MPluginUtils.h"
#include "mnpr_renderer.h"
#include "mnpr_nodes.h"
#include "mnpr_quadRender.h"
#include "node_watercolor.hpp"
#include "node_oilpaint.hpp"
#include "node_sandbox.hpp"
#include "node_charcoal.hpp"


MTypeId ConfigNode::id(0x00127040);

// Evaluator
MObject ConfigNode::aEvaluate;

// ATTRIBUTES
// engine settings
static MObject aStyle;
static MObject aColorDepth;
static MObject aRenderSize;
static MObject aAntialiasing;
static MObject aDepthRange;
static MObject aDepthRangeMin;
static MObject aDepthRangeMax;
MObject aVelocityPV;
// substrate attributes
static MObject aSubstrateTex;
static MObject aSubstrateColor;
static MObject aSubstrateColorR;
static MObject aSubstrateColorG;
static MObject aSubstrateColorB;
static MObject aSubstrateShading;
static MObject aSubstrateLightDir;
static MObject aSubstrateLightTilt;
static MObject aSubstrateScale;
static MObject aSubstrateUpdate;
static MObject aSubstrateRoughness;
static MObject aSubstrateDistortion;
// atmosphere attributes
static MObject aAtmosphereColor;
static MObject aAtmosphereColorR;
static MObject aAtmosphereColorG;
static MObject aAtmosphereColorB;
static MObject aAtmosphereRange;
static MObject aAtmosphereRangeMin;
static MObject aAtmosphereRangeMax;
// post-processing attributes
static MObject aSaturation;
static MObject aContrast;
static MObject aBrightness;


// engine pointers
FXParameters* fxParameters;
EngineSettings* engineSettings;
MNPROverride* MNPR;


// CUSTOM 
MStatus ConfigNode::initializeCustomParameters() {
    // INITIALIZE CUSTOM PARAMETERS
    if (engineSettings->style == "Watercolor") {
        wc::initializeParameters(fxParameters, engineSettings);
    }
    else if (engineSettings->style == "Oil") {
        op::initializeParameters(fxParameters, engineSettings);
    }
    else if (engineSettings->style == "Charcoal") {
        ch::initializeParameters(fxParameters, engineSettings, aEvaluate);
    }
	else if (engineSettings->style == "Sandbox") {
		sb::initializeParameters(fxParameters, engineSettings);
	}
    cout << "Initialization of " << engineSettings->style << " parameters was successful" << endl;
    return MS::kSuccess;
}


MStatus ConfigNode::computeCustomParameters(MDataBlock& data) {
    // COMPUTE CUSTOM PARAMETERS
    if (engineSettings->initialized) {
        if (engineSettings->style == "Watercolor") {
            wc::computeParameters(MNPR, data, fxParameters, engineSettings);
        }
        else if (engineSettings->style == "Oil") {
            op::computeParameters(MNPR, data, fxParameters, engineSettings);
        }
        else if (engineSettings->style == "Charcoal") {
            ch::computeParameters(MNPR, data, fxParameters, engineSettings);
        }
		else if (engineSettings->style == "Sandbox") {
			sb::computeParameters(MNPR, data, fxParameters, engineSettings);
		}
    }
    return MS::kSuccess;
}


// node initializer function
MStatus ConfigNode::initialize() {
    MStatus status;

    // MFn helpers
    MFnEnumAttribute eAttr;
    MFnTypedAttribute tAttr;
    MFnNumericAttribute nAttr;

    MHWRender::MRenderer* theRenderer = MHWRender::MRenderer::theRenderer();
    MNPR = (MNPROverride*)theRenderer->findRenderOverride(PLUGIN_NAME);
    if (!MNPR) {
        cout << "WARNING: No render override instance was found" << endl;
        return MStatus::kFailure;
    }

    // get renderer parameters and engine settings
    fxParameters = MNPR->effectParams();
    engineSettings = MNPR->engineSettings();

    // evaluation attribute (this attribute will be attached to the DAG for dirty propagation)
    aEvaluate = nAttr.create("evaluate", "evaluate", MFnNumericData::kBoolean, 1);
    nAttr.setWritable(false);
    nAttr.setStorable(false);
    addAttribute(aEvaluate);

    // STYLE
    if (PURPOSE == "Research") {
        short idx = utils::indexOfMString(STYLES, engineSettings->style);
        aStyle = eAttr.create("style", "style", idx);
        for (int i = 0; i < STYLES.size(); i++) {
            eAttr.addField(STYLES[i], i);
        }
        eAttr.setChannelBox(true);
        eAttr.setDefault(idx);
        enableAttribute(aStyle);
    }

    // ENGINE SETTINGS
    // color depth
    aColorDepth = eAttr.create("colorDepth", "colorDepth", (unsigned int)engineSettings->colorDepth);
    eAttr.addField("8 bit", 0);
    eAttr.addField("16 bit", 1);
    eAttr.addField("32 bit", 2);
    eAttr.setChannelBox(true);
    eAttr.setDefault(engineSettings->colorDepth);
    enableAttribute(aColorDepth);
    // render scale
    float renderScale = engineSettings->renderScale[0];
    aRenderSize = eAttr.create("renderScale", "renderScale", (short)floor(renderScale));
    eAttr.addField("Half (x0.5)", 0);
    eAttr.addField("Normal", 1);
    eAttr.addField("Double (x2)", 2);
    eAttr.setChannelBox(true);
    eAttr.setDefault((short)floor(renderScale));
    enableAttribute(aRenderSize);
    // antialiasing
    float antialiasing = engineSettings->antialiasing[0];
    aAntialiasing = eAttr.create("antialiasing", "antialiasing", (short)floor(antialiasing));
    eAttr.addField("None", 0);
    eAttr.addField("FXAA", 1);
    eAttr.addField("FXAA (high)", 2);
    eAttr.setChannelBox(true);
    eAttr.setDefault((short)floor(antialiasing));
    enableAttribute(aAntialiasing);
    // depth range
    aDepthRangeMin = nAttr.create("depthRangeMin", "depthRangeMin", MFnNumericData::kFloat, engineSettings->depthRange[0]);
    nAttr.setMin(0);
    aDepthRangeMax = nAttr.create("depthRangeMax", "depthRangeMax", MFnNumericData::kFloat, engineSettings->depthRange[1]);
    nAttr.setMin(0);
    aDepthRange = nAttr.create("depthRange", "depthRange", aDepthRangeMin, aDepthRangeMax);
    MAKE_INPUT(nAttr);
    enableAttribute(aDepthRange);
    // atmosphere tint
    aAtmosphereColorR = nAttr.create("atmosphereTintR", "atmosphereTintR", MFnNumericData::kFloat, engineSettings->atmosphereTint[0]);
    aAtmosphereColorG = nAttr.create("atmosphereTintG", "atmosphereTintG", MFnNumericData::kFloat, engineSettings->atmosphereTint[1]);
    aAtmosphereColorB = nAttr.create("atmosphereTintB", "atmosphereTintB", MFnNumericData::kFloat, engineSettings->atmosphereTint[2]);
    aAtmosphereColor = nAttr.create("atmosphereTint", "atmosphereTint", aAtmosphereColorR, aAtmosphereColorG, aAtmosphereColorB);
    MAKE_INPUT(nAttr);
    nAttr.setUsedAsColor(true);
    enableAttribute(aAtmosphereColor); 
    // atmosphere range
    aAtmosphereRangeMin = nAttr.create("atmosphereRangeMin", "atmosphereRangeMin", MFnNumericData::kFloat, engineSettings->atmosphereRange[0]);
    nAttr.setMin(0);
    aAtmosphereRangeMax = nAttr.create("atmosphereRangeMax", "atmosphereRangeMax", MFnNumericData::kFloat, engineSettings->atmosphereRange[1]);
    nAttr.setMin(0);
    aAtmosphereRange = nAttr.create("atmosphereRange", "atmosphereRange", aAtmosphereRangeMin, aAtmosphereRangeMax);
    MAKE_INPUT(nAttr);
    enableAttribute(aAtmosphereRange);
    // velocity per vertex
    bool velocityPV = engineSettings->velocityPV[0];
    aVelocityPV = nAttr.create("velocityPV", "velocityPV", MFnNumericData::kBoolean, velocityPV);
    nAttr.setDefault(engineSettings->velocityPV[0] == 1.0 ? true : false);
    MAKE_INPUT(nAttr);
    // enableAttribute only in the styles that use this to de-clutter config node

    // SUBSTRATE
    // substrate texture
    MFnStringData fnData;
    MObject oData = fnData.create(engineSettings->substrateTexFilename);
    aSubstrateTex = tAttr.create("substrateTexture", "substrateTexture", MFnData::kString, oData);
    tAttr.setStorable(true);
    enableAttribute(aSubstrateTex);
    // substrate color
    aSubstrateColorR = nAttr.create("substrateColorR", "substrateColorR", MFnNumericData::kFloat, engineSettings->substrateColor[0]);
    aSubstrateColorG = nAttr.create("substrateColorG", "substrateColorG", MFnNumericData::kFloat, engineSettings->substrateColor[1]);
    aSubstrateColorB = nAttr.create("substrateColorB", "substrateColorB", MFnNumericData::kFloat, engineSettings->substrateColor[2]);
    aSubstrateColor = nAttr.create("substrateColor", "substrateColor", aSubstrateColorR, aSubstrateColorG, aSubstrateColorB);
    MAKE_INPUT(nAttr);
    nAttr.setUsedAsColor(true);
    enableAttribute(aSubstrateColor);
    //substrate light
    aSubstrateShading = nAttr.create("substrateShading", "substrateShading", MFnNumericData::kFloat, engineSettings->substrateShading[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0);
    nAttr.setMax(1);
    enableAttribute(aSubstrateShading);
    //substrate light dir
    aSubstrateLightDir = nAttr.create("substrateLightDir", "substrateLightDir", MFnNumericData::kFloat, engineSettings->substrateLightDir[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0);
    nAttr.setMax(359);
    enableAttribute(aSubstrateLightDir);
    //substrate light tilt
    aSubstrateLightTilt = nAttr.create("substrateLightTilt", "substrateLightTilt", MFnNumericData::kFloat, engineSettings->substrateLightTilt[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0);
    nAttr.setMax(89);
    enableAttribute(aSubstrateLightTilt);
    //substrate scale
    aSubstrateScale = nAttr.create("substrateScale", "substrateScale", MFnNumericData::kFloat, engineSettings->substrateScale[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0.1);
    nAttr.setMax(2.5);
    enableAttribute(aSubstrateScale);
    //substrate update
    aSubstrateUpdate = nAttr.create("substrateUpdate", "substrateUpdate", MFnNumericData::kFloat, engineSettings->substrateUpdate[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0.0);
    nAttr.setSoftMax(24.0);
    enableAttribute(aSubstrateUpdate);
    //substrate roughness
    aSubstrateRoughness = nAttr.create("substrateRoughness", "substrateRoughness", MFnNumericData::kFloat, engineSettings->substrateRoughness[0]);
    MAKE_INPUT(nAttr);
    nAttr.setSoftMin(0.0);
    nAttr.setSoftMax(2.0);
    enableAttribute(aSubstrateRoughness);
    //substrate distortion
    aSubstrateDistortion = nAttr.create("substrateDistortion", "substrateDistortion", MFnNumericData::kFloat, engineSettings->substrateDistortion[0]);
    MAKE_INPUT(nAttr);
    nAttr.setSoftMin(0.0);
    nAttr.setSoftMax(10);
    enableAttribute(aSubstrateDistortion);

    // POST-PROCESSING
    // saturation
    aSaturation = nAttr.create("saturation", "saturation", MFnNumericData::kFloat, fxParameters->saturation[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0);
    nAttr.setSoftMax(5);
    enableAttribute(aSaturation);
    // contrast
    aContrast = nAttr.create("contrast", "contrast", MFnNumericData::kFloat, fxParameters->contrast[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0);
    nAttr.setSoftMax(2);
    enableAttribute(aContrast);
    // brightness
    aBrightness = nAttr.create("brightness", "brightness", MFnNumericData::kFloat, fxParameters->brightness[0], &status);
    MAKE_INPUT(nAttr);
    nAttr.setMin(0);
    nAttr.setSoftMax(2);
    enableAttribute(aBrightness);

    initializeCustomParameters();

    return MS::kSuccess;
}


// node compute function
MStatus ConfigNode::compute(const MPlug& plug, MDataBlock& data) {
    //cout << "compute()" << endl;
    MStatus status;

    // STYLE (first check)
    unsigned int idx = 0;
    MDataHandle styleHandle = data.inputValue(aStyle, &status); 
    if (!status) {
        idx = utils::indexOfMString(STYLES, engineSettings->style);
    } else {
        idx = styleHandle.asShort();
    }
    if (engineSettings->style != STYLES[idx]) {       
        cout << "Changing style to: " << STYLES[idx] << endl;
        engineSettings->initialized = false;
        engineSettings->renderScale[0] = 1;  // change resolution to normalize parameters
    }

    // ENGINE SETTINGS
    unsigned int colorDepth = data.inputValue(aColorDepth, &status).asShort();
    if (colorDepth != engineSettings->colorDepth) {
        engineSettings->colorDepth = colorDepth;
        MNPR->changeColorDepth();
    }
    float renderScale = powf(2.0f, (float)data.inputValue(aRenderSize, &status).asShort()) / 2.0f;
    if (renderScale != engineSettings->renderScale[0]) {
        if (engineSettings->initialized) {
            engineSettings->renderScale[0] = renderScale;
            MNPR->refreshTargets();
        }
    }
    float antialiasing = (float)data.inputValue(aAntialiasing, &status).asShort();
    if (antialiasing != engineSettings->antialiasing[0]) {
        if (engineSettings->initialized) {
            engineSettings->antialiasing[0] = antialiasing;
            MNPR->changeAntialiasingEffect();
        }
    }

    engineSettings->depthRange[0] = data.inputValue(aDepthRangeMin, &status).asFloat();
    engineSettings->depthRange[1] = data.inputValue(aDepthRangeMax, &status).asFloat();

    MFloatVector fvColor = data.inputValue(aAtmosphereColor, &status).asFloatVector();
    engineSettings->atmosphereTint[0] = fvColor[0];
    engineSettings->atmosphereTint[1] = fvColor[1];
    engineSettings->atmosphereTint[2] = fvColor[2];
    engineSettings->atmosphereRange[0] = data.inputValue(aAtmosphereRangeMin, &status).asFloat();
    engineSettings->atmosphereRange[1] = data.inputValue(aAtmosphereRangeMax, &status).asFloat();


    // SUBSTRATE
    fvColor = data.inputValue(aSubstrateColor, &status).asFloatVector();
    engineSettings->substrateColor[0] = fvColor[0];
    engineSettings->substrateColor[1] = fvColor[1];
    engineSettings->substrateColor[2] = fvColor[2];
    engineSettings->substrateShading[0] = data.inputValue(aSubstrateShading, &status).asFloat();
    engineSettings->substrateLightDir[0] = data.inputValue(aSubstrateLightDir, &status).asFloat();
    engineSettings->substrateLightTilt[0] = data.inputValue(aSubstrateLightTilt, &status).asFloat();
    engineSettings->substrateRoughness[0] = data.inputValue(aSubstrateRoughness, &status).asFloat();
    engineSettings->substrateDistortion[0] = data.inputValue(aSubstrateDistortion, &status).asFloat() * engineSettings->renderScale[0];
    // substrate update (refresh X times per second)
    engineSettings->substrateUpdate[0] = data.inputValue(aSubstrateUpdate, &status).asFloat();
    if (engineSettings->substrateUpdate[0]) {
        engineSettings->substrateUpdate[0] = 1000 / engineSettings->substrateUpdate[0];  // in ms
    }
    // update quad texture (substrate)
    MOperationShader* opShader;
    QuadRender* quadOp = (QuadRender*)MNPR->renderOperation("[quad] adjust-load");
    opShader = quadOp->getOperationShader();
    if (opShader) {
        // substrate scale
        engineSettings->substrateScale[0] = 1.0f / (data.inputValue(aSubstrateScale, &status).asFloat() * engineSettings->renderScale[0]);
        opShader->textureParameters["gSubstrateTex"]->setScale(engineSettings->substrateScale[0]);
        // substrate filename
        MString surfaceTex = data.inputValue(aSubstrateTex, &status).asString();
        if (surfaceTex != engineSettings->substrateTexFilename) {
            engineSettings->substrateTexFilename = surfaceTex;
            opShader->textureParameters["gSubstrateTex"]->loadTexture(engineSettings->substrateTexFilename);
        }
        opShader->textureParameters["gSubstrateTex"]->setParams();
    }
    //engineSettings->dPrint();


    // COMPUTE CUSTOM PARAMETERS
    computeCustomParameters(data);


    // POST-PROCESSING
    fxParameters->saturation[0] = data.inputValue(aSaturation, &status).asFloat();
    fxParameters->contrast[0] = data.inputValue(aContrast, &status).asFloat();
    fxParameters->brightness[0] = data.inputValue(aBrightness, &status).asFloat();
    //fxParameters->dPrint();

    // CLEAN PLUG
    data.setClean(plug);

    // STYLE (SECOND CHECK)
    if (engineSettings->style != STYLES[idx]) {
        engineSettings->style = STYLES[idx];  // set style
        engineSettings->renderScale[0] = renderScale;  // set user defined scale
        MGlobal::executePythonCommandOnIdle("import mnpr_runner\nmnpr_runner.changeStyle()");
    } else {
        engineSettings->initialized = true;  // mark as initialized
    }

    // REFRESH VIEWPORT
    MAnimControl animControl;
    if (!animControl.isPlaying()) {
        MGlobal::executeCommandOnIdle("refresh");
    }

    return MS::kSuccess;
}



// Attribute enabler
MStatus ConfigNode::enableAttribute(MObject& attribute) {
    addAttribute(attribute);
    attributeAffects(attribute, aEvaluate);
    return MS::kSuccess;
}
