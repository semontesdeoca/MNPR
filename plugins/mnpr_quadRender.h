#pragma once
///////////////////////////////////////////////////////////////////////////////////
//                          _                                _   _             
//     __ _ _   _  __ _  __| |     ___  _ __   ___ _ __ __ _| |_(_) ___  _ __  
//    / _` | | | |/ _` |/ _` |    / _ \| '_ \ / _ \ '__/ _` | __| |/ _ \| '_ \ 
//   | (_| | |_| | (_| | (_| |   | (_) | |_) |  __/ | | (_| | |_| | (_) | | | |
//    \__, |\__,_|\__,_|\__,_|    \___/| .__/ \___|_|  \__,_|\__|_|\___/|_| |_|
//       |_|                           |_|                                     
//
//	\brief Quad render operation 
//	Contains the MQuadRender that lets you render screen effects to one or more render targets
///////////////////////////////////////////////////////////////////////////////////
#include "MRenderTargetList.h"
#include "MOperationShader.h"


class QuadRender : public MHWRender::MQuadRender {
public:
    QuadRender(const MString &name, int clearMask, MRenderTargetList& targetList, MOperationShader& opShader);
    ~QuadRender();

    // OVERRIDEN METHODS
    virtual const MHWRender::MShaderInstance* shader();								      ///< set custom quad shader
    virtual MHWRender::MRenderTarget* const* targetOverrideList(unsigned int &listSize);  ///< set custom render target

    // additional methods that could be overriden in MQuadRender [Maya 2016+]
    // http://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__cpp_ref_class_mh_w_render_1_1_mquad_render_html
    // virtual MHWRender::MClearOperation & clearOperation();					   ///< clear render target
    // virtual const MHWRender::MDepthStencilState* depthStencilStateOverride();   ///< enable writting to depth/stencil buffer (disabled by default)
    // virtual const MHWRender::MRasterizerState* rasterizerStateOverride();	   ///< enable culling (None/Back/Front) and Fillmode (solid/wireframe)
    // virtual const MHWRender::MBlendState* blendStateOverride();				   ///< enable blending
    // inherited methods from MRenderOperation -> http://help.autodesk.com/view/MAYAUL/2018/ENU/?guid=__cpp_ref_class_mh_w_render_1_1_mrender_operation_html

    // GET
    MOperationShader* getOperationShader();  ///< get the MOperationShader of this quad operation

protected:
    MRenderTargetList* mTargetList = nullptr;				   ///< target list of renderer
    MOperationShader* mOpShader = nullptr;					   ///< operation shader
    MHWRender::MShaderInstance* mShaderInstance = nullptr;     ///< shader instance
    std::vector<MHWRender::MRenderTarget*> mOperationTargets;  ///< the output targets of this operation
    MHWRender::MRenderTargetAssignment targetAssignment;       ///< used to assign a render target to a 2D Texture
};
