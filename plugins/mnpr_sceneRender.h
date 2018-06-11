#pragma once
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
#include "MRenderTargetList.h"
#include <maya/MShaderManager.h>
#include <maya/MFnMesh.h>


class SceneRender : public MHWRender::MSceneRender {
public:
    SceneRender(const MString &name,
        MHWRender::MSceneRender::MSceneFilterOption sceneFilter,
        int clearMask,
        MRenderTargetList& targetList);
    ~SceneRender();

    // OVERRIDEN FUNCTIONS
    MHWRender::MRenderTarget* const* targetOverrideList(unsigned int &listSize);	///< set custom render target list
    MHWRender::MSceneRender::MSceneFilterOption renderFilterOverride();				///< scene draw filter override (only shaded, etc)
    MHWRender::MSceneRender::MDisplayMode displayModeOverride();					///< set display mode override (textured, etc)
    MHWRender::MSceneRender::MPostEffectsOverride postEffectsOverride();
    MHWRender::MSceneRender::MLightingMode lightModeOverride();			            ///< which lights are considered for rendering                                                               ///< set post override (disable SSAO, etc)
    const bool* shadowEnableOverride();      						                ///< override wich objects receive shadows?
    void postRender();													            ///< set custom post render setup
    void postSceneRender(const MHWRender::MDrawContext &context);					///< set custom post render operation


    // additional methods that could be overriden in MSceneRender [Maya 2016+]
    // http://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__cpp_ref_class_mh_w_render_1_1_mscene_render_html
    // virtual void preRender();													 ///< set custom pre render setup
    // virtual void postRender();													 ///< set custom post render cleanup
    // virtual void preSceneRender(const MDrawContext &context);					 ///< set custom pre render operation
    // virtual const MHWRender::MShaderInstance* shaderOverride();					 ///< render the entire scene with one shader
    // virtual MHWRender::MSceneRender::MCullingOption cullingOverride();			 ///< defines culling override
    // virtual const MHWRender::MCameraOverride* cameraOverride();					 ///< set custom camera override
    // virtual const MSelectionList* objectSetOverride();							 ///< override scene logic (e.g. render the selected objects only)
    // virtual MUint64 getObjectTypeExclusions();									 ///< exclude certain object types
    // virtual MHWRender::MSceneRender::MCullingOption cullingOverride();			 ///< defines culling override
    // virtual MHWRender::MClearOperation & clearOperation();						 ///< set custom clear function
    // virtual bool hasUIDrawables();												 ///< return true to enable addPreUIDraw... and addPostUIDraw...
    // virtual void addPreUIDrawables( MHWRender::MUIDrawManager& drawManager, const MHWRender::MFrameContext& frameContext );   ///< pre and post UI drawables (draw custom geometry, text, etc)
    // virtual void addPostUIDrawables( MHWRender::MUIDrawManager& drawManager, const MHWRender::MFrameContext& frameContext );  ///< check vieMNPROverride Pluggin for uses
    // virtual MRenderParameters* getParameters();									 ///< return input parameters that control the fragment render [Maya 2017+]
    // virtual MString fragmentName();												 ///< return the fragment name of the fragment script or fragment graph [Maya 2017+]
    // inherited methods from MRenderOperation -> http://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__cpp_ref_class_mh_w_render_1_1_mrender_operation_html


protected:
    MObject getSourceNodeConnectedTo(const MObject& node, const MString& attribute);
    void computePreviousScreenSpacePositions(MFnMesh &fnMesh, const MMatrix &viewProjectionPreviousMatrix, const MMatrix &worldPreviousMatrix);

    MRenderTargetList* mTargetList = nullptr;				  ///< target list of renderer
    std::vector<MHWRender::MRenderTarget*> operationTargets;  ///< the output targets of this operation

    MHWRender::MSceneRender::MSceneFilterOption mSceneRenderFilter;  ///< scene draw filter override (onlyShaded, etc)
    MHWRender::MTextureAssignment shadowMapResource;

    MMatrix viewProjectionPreviousMatrix;
};