///////////////////////////////////////////////////////////////////////////////////
//                                                           _   _             
//    ___  ___ ___ _ __   ___      ___  _ __   ___ _ __ __ _| |_(_) ___  _ __  
//   / __|/ __/ _ \ '_ \ / _ \    / _ \| '_ \ / _ \ '__/ _` | __| |/ _ \| '_ \ 
//   \__ \ (_|  __/ | | |  __/   | (_) | |_) |  __/ | | (_| | |_| | (_) | | | |
//   |___/\___\___|_| |_|\___|    \___/| .__/ \___|_|  \__,_|\__|_|\___/|_| |_|
//                                     |_|                                                                 
//
//	\brief Scene render operation 
//	Contains the MSceneRender that renders the geometry in the scene to one or more render targets
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_sceneRender.h"
#include "mnpr_renderer.h"
#include "mnpr_nodes.h"
#include <maya/MItDag.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnTransform.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MPlugArray.h>
#include <maya/MPxHardwareShader.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MDrawContext.h>


SceneRender::SceneRender(const MString &name,
    MHWRender::MSceneRender::MSceneFilterOption sceneFilter, int clearMask, MRenderTargetList &targetList)
    : MSceneRender(name)
    , mSceneRenderFilter(sceneFilter)
    , mTargetList(&targetList) {

    mClearOperation.setMask(clearMask);             // custom clear mask (avoid calling clearOperation each frame)
    float clearColor[4] = { 0.0, 0.0 , 0.0, 0.0 };  // black clear color
    mClearOperation.setClearColor(clearColor);      // setting clear color
    mClearOperation.setClearDepth(1.0);
}


SceneRender::~SceneRender() {}


// return target list from mTargetList
MHWRender::MRenderTarget* const* SceneRender::targetOverrideList(unsigned int &listSize) {
    if (mTargetList) {
        operationTargets = mTargetList->getOperationOutputs(name());
        listSize = (unsigned int)(operationTargets.size());
        return &operationTargets[0];
    }
    listSize = 0;
    return nullptr;
}


// force the viewport to be shaded and textured to always display viewport shaders
MHWRender::MSceneRender::MDisplayMode SceneRender::displayModeOverride() {
    if (mSceneRenderFilter == MHWRender::MSceneRender::kRenderShadedItems) {
        return (MHWRender::MSceneRender::MDisplayMode)
            (MHWRender::MSceneRender::kShaded | MHWRender::MSceneRender::kTextured);
    }
    return MHWRender::MSceneRender::kNoDisplayModeOverride;
}


// force the UI scene render to not calculate any lighting
MHWRender::MSceneRender::MLightingMode SceneRender::lightModeOverride() {
    if (mSceneRenderFilter == MHWRender::MSceneRender::kRenderUIItems) {
        return MHWRender::MSceneRender::MLightingMode::kNoLight;
    } else {
        return MHWRender::MSceneRender::MLightingMode::kNoLightingModeOverride;
    }
}


// force the UI scene render to not calculate any shadows
const bool* SceneRender::shadowEnableOverride() {
    if (mSceneRenderFilter == MHWRender::MSceneRender::kRenderUIItems) {
        static const bool noShadowsForUI = false;
        return &noShadowsForUI; // UI doesn't need shadows
    }
    // For all other cases, just use whatever is currently set
    return nullptr;
}


MObject SceneRender::getSourceNodeConnectedTo(const MObject& node, const MString& attribute)
{
    MStatus status;
    MFnDependencyNode dgFn(node);
    MPlug plug = dgFn.findPlug(attribute, true, &status);
    if (status == MS::kSuccess && plug.isConnected())
    {
        // Get the connection - there can be at most one input to a plug
        MPlugArray connections;
        plug.connectedTo(connections, true, false);
        size_t length = connections.length();
        if (connections.length() > 0)
        {
            return connections[0].node();
        }
    }

    return MObject::kNullObj;
}


void SceneRender::computePreviousScreenSpacePositions(MFnMesh &fnMesh, const MMatrix &viewProjectionPreviousMatrix, const MMatrix &worldPreviousMatrix) {
    unsigned int lenVertexList = fnMesh.numVertices();

    MFnSingleIndexedComponent fnComponent;
    MObject fullComponent = fnComponent.create(MFn::kMeshVertComponent);

    fnComponent.setCompleteData(lenVertexList);

    MIntArray vertexIndexList;
    fnComponent.getElements(vertexIndexList);

    MString iSetName = "previousScreenPosition";

    MColorArray previousScreenPositions;
    if (fnMesh.hasColorChannels(iSetName)) {
        fnMesh.getVertexColors(previousScreenPositions, &iSetName);
    }
    else {
        previousScreenPositions = MColorArray(fnMesh.numVertices(), MColor(0.0, 0.0, 0.0, 0.0));
    }

    for (int k = 0; k < fnMesh.numVertices(); k++) {
        MPoint pos;
        fnMesh.getPoint(k, pos);

        pos = pos * worldPreviousMatrix;
        pos.w = 1.0;

        pos = pos * viewProjectionPreviousMatrix;
        pos = pos / pos.w;

        previousScreenPositions[k].r = static_cast<float>(pos.x);
        previousScreenPositions[k].g = static_cast<float>(pos.y);
        previousScreenPositions[k].b = static_cast<float>(pos.z);
    }

    if (!fnMesh.hasColorChannels(iSetName)) {
        fnMesh.createColorSetWithName(iSetName);
        fnMesh.setCurrentColorSetName(iSetName);
    }

    //fnMesh.setColors(previousScreenPositions, &iSetName);
    //fnMesh.assignColors(vertexIndexList, &iSetName);
    fnMesh.setVertexColors(previousScreenPositions, vertexIndexList);
}


void SceneRender::postRender() {
    MHWRender::MRenderer* theRenderer = MHWRender::MRenderer::theRenderer(false);
    MNPROverride* mmnpr_renderer = (MNPROverride*)theRenderer->findRenderOverride(PLUGIN_NAME);
    if (!mmnpr_renderer) {
        cout << "WARNING: No render override instance was found" << endl;
        return;
    }

    // get renderer parameters and engine settings
    EngineSettings* engineSettings = mmnpr_renderer->engineSettings();

    if (engineSettings->velocityPV[0] == 0.0 || this->mSceneRenderFilter != kRenderShadedItems)
        return;

    static MMatrix viewProjectionPreviousPreviousMatrix = {};

    bool viewProjectionMatrixChanged = false;
    if (viewProjectionPreviousPreviousMatrix != viewProjectionPreviousMatrix) {
        viewProjectionMatrixChanged = true;
    }

    viewProjectionPreviousPreviousMatrix = viewProjectionPreviousMatrix;

    // create an iterator to go through all meshes
    MItDag it(MItDag::kDepthFirst, MFn::kMesh);

    // loop through all nodes
    while (!it.isDone()) {
        // attach a function set for a dag node to the
        // object. Rather than access data directly, 
        // we access it via the function set. 
        MObject obj = it.currentItem();
        MFnMesh fnMesh(obj);

        // Get the current path
        const MDagPath dagPath = fnMesh.dagPath();

        // Find how many shaders are used by this instance of the mesh
        MObjectArray shaders;

        MIntArray shaderIndices;
        unsigned instanceNumber = dagPath.instanceNumber();
        fnMesh.getConnectedShaders(instanceNumber, shaders, shaderIndices);

        for (uint i = 0; i < shaders.length(); i++) {
            MStatus status;
            MFnDependencyNode shaderNode(shaders[i], &status);

            std::string shaderNodeName = shaderNode.name().asChar();

            if (shaders[i].hasFn(MFn::kShadingEngine)) {
                MObject shadingEngine = shaders[i];
                MObject shader = getSourceNodeConnectedTo(shadingEngine, "surfaceShader");

                if (shader.hasFn(MFn::kPluginHardwareShader)) {
                    MPxHardwareShader* pHWShader = MPxHardwareShader::getHardwareShaderPtr(shader);

                    MStatus status;
                    MFnDependencyNode shaderNode(shader, &status);

                    MObject colorSource3Obj = shaderNode.attribute("Color3_Source");
                    MPlug colorSource3Plg(shader, colorSource3Obj);
                    colorSource3Plg.setString("color:previousScreenPosition");
                }
            }
        }

        // get matrix data
        MFnDagNode thisShapeNodeFn(obj);
        MObject parentXFormNodeObj = thisShapeNodeFn.parent(0);
        MFnDependencyNode parentXFormNodeFn(parentXFormNodeObj);

        MObject worldMatrixObj = parentXFormNodeFn.attribute("worldMatrix");
        MPlug worldMatrixPlg(parentXFormNodeObj, worldMatrixObj);
        worldMatrixPlg = worldMatrixPlg.elementByLogicalIndex(0);
        worldMatrixPlg.getValue(worldMatrixObj);
        MFnMatrixData worldMatrixData(worldMatrixObj);
        MMatrix worldMatrix = worldMatrixData.matrix();

        MFnDagNode objFn(it.currentItem());

        bool worldMatrixChanged = false;

        // add world matrix as attribute
        if (objFn.hasAttribute("WorldPreviousMatrix")) {
            MPlug pAttr = objFn.findPlug("WorldPreviousMatrix", true);
            MObject pObj;
            pAttr.getValue(pObj);
            MFnMatrixData fnMat(pObj);

            pAttr.getValue(pObj);
            MMatrix worldMatrixPrevious = fnMat.matrix();

            if (worldMatrixPrevious != worldMatrix) {
                fnMat.set(worldMatrix);
                pAttr.setValue(pObj);
                worldMatrixChanged = true;
            }
        }
        else {
            MFnMatrixAttribute attr;
            attr.create("WorldPreviousMatrix", "WorldPreviousMatrix", MFnMatrixAttribute::kDouble);
            MAKE_INPUT(attr);
            attr.setDefault(worldMatrix);
            objFn.addAttribute(attr.object());
            worldMatrixChanged = true;
        }

        // apparently we cannot optimize here, because even though worldMatrix does not change, velocity still needs to be updated (with static viewProjectionMatrix)...
        //if (worldMatrixChanged || viewProjectionMatrixChanged) {
            computePreviousScreenSpacePositions(fnMesh, viewProjectionPreviousMatrix, worldMatrix);
        //}

        // move to next node
        it.next();
    }
}


void SceneRender::postSceneRender(const MHWRender::MDrawContext &context) {
    // get rid of any shadow maps that Maya fails to release
    //cout << "postSceneRender()" << name() << endl;
    /*
    MHWRender::MDrawContext::LightFilter considerAllSceneLights = MHWRender::MDrawContext::kFilteredIgnoreLightLimit;
    MHWRender::MRenderer::needEvaluateAllLights();
    unsigned int lightCount = drawContext.numberOfActiveLights(considerAllSceneLights);

    MHWRender::MLightParameterInformation *lightParam = context.getLightParameterInformation(i, considerAllSceneLights);
    if (lightParam)
    {
    */

    viewProjectionPreviousMatrix = context.getMatrix(MHWRender::MFrameContext::kViewProjMtx);
}


// force none of Maya's post effects overrides
// Reasoning: motion blur and depth of field should also affect all control targets
MHWRender::MSceneRender::MPostEffectsOverride SceneRender::postEffectsOverride() {
    return MHWRender::MSceneRender::kPostEffectDisableAll;
}


// custom scene filter override to draw opaque, transparent or non-shaded (UI) items.
// set in constructor
MHWRender::MSceneRender::MSceneFilterOption SceneRender::renderFilterOverride() {
    return mSceneRenderFilter;  // value set in constructor
}
