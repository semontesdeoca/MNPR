#pragma once
///////////////////////////////////////////////////////////////////////////////////
//         _                               _ 
//     ___| |__   __ _ _ __ ___ ___   __ _| |
//    / __| '_ \ / _` | '__/ __/ _ \ / _` | |
//   | (__| | | | (_| | | | (_| (_) | (_| | |
//    \___|_| |_|\__,_|_|  \___\___/ \__,_|_|
//                                           
//	 \brief Charcoal stylization pipeline
//	 Contains the charcoal stylization pipeline with all necessary targets and operations
//
//   Developed by: Yee Xin Chiew
//
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"


namespace ch {

    void addTargets(MRenderTargetList &targetList) {
        // add style specific targets

        unsigned int tWidth = targetList[0]->width();
        unsigned int tHeight = targetList[0]->height();
        int MSAA = targetList[0]->multiSampleCount();
        unsigned arraySliceCount = 0;
        bool isCubeMap = false;
        MHWRender::MRasterFormat rgba8 = MHWRender::kR8G8B8A8_SNORM;
        MHWRender::MRasterFormat rgb8 = MHWRender::kR8G8B8X8;

        targetList.append(MHWRender::MRenderTargetDescription("offsetTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("granulateTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("blendTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("edgeBlurControl", tWidth, tHeight, 1, rgba8, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("edgeBlurTarget", tWidth, tHeight, MSAA, rgba8, arraySliceCount, isCubeMap));

    }


    void addOperations(MHWRender::MRenderOperationList &mRenderOperations, MRenderTargetList &mRenderTargets,
        EngineSettings &mEngSettings, FXParameters &mFxParams) {
        MString opName = "";

        opName = "[quad] offset Output";
        auto opShader = new MOperationShader("ch", "quadOffset", "offsetOutput"); // quadCharcoalOffset
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gAbstractionControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget"))); // controlTargetAbstraction
        auto quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "offsetTarget" });
        

        opName = "[quad] offset H";
        opShader = new MOperationShader("ch", "quadOffsetBlend", "offsetH"); // quadCharcoalBlend
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gDepthTex", mRenderTargets.target(mRenderTargets.indexOf("linearDepth")));
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget"))); // controlTargetSubstrate
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "offsetTarget" });

        opName = "[quad] offset V";
        opShader = new MOperationShader("ch", "quadOffsetBlend", "offsetV");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gDepthTex", mRenderTargets.target(mRenderTargets.indexOf("linearDepth")));
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget"))); // controlTargetSubstrate ???
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "offsetTarget" });

        opName = "[quad] blur H";
        opShader = new MOperationShader("ch", "quadBlur", "blurH"); // quadCharcoalBlur
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "blendTarget" });


        opName = "[quad] blur V";
        opShader = new MOperationShader("ch", "quadBlur", "blurV");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("blendTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "blendTarget" });

        opName = "[quad] mixing";
        opShader = new MOperationShader("ch", "quadOffset", "mixing");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gBlendTex", mRenderTargets.target(mRenderTargets.indexOf("blendTarget")));
        opShader->addTargetParameter("gAbstractionControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget"))); // controlTargetSubstrate
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });

        opName = "[quad] edge blur H";
        opShader = new MOperationShader("ch", "quadEdgeBlur", "edgeBlurH");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gEdgeBlurTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget")));
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("edgeCtrlTarget"))); // controlTargetEdges
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "edgeBlurTarget", "edgeBlurControl" });

        opName = "[quad] edge blur V";
        opShader = new MOperationShader("ch", "quadEdgeBlur", "edgeBlurV"); ////opShader = new MOperationShader("quadBlur", "dynamicBlurV");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("edgeBlurTarget"))); // use the one with horizontal blur
        opShader->addTargetParameter("gEdgeBlurTex", mRenderTargets.target(mRenderTargets.indexOf("edgeBlurControl")));
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("edgeCtrlTarget"))); // controlTargetEdges
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "edgeBlurTarget", "edgeBlurControl" });

        opName = "[quad] edge filter";
        opShader = new MOperationShader("ch", "quadEdgeManipulation", "edgeFilter"); // quadCharcoalEdge
        opShader->addTargetParameter("gEdgeSoftenTex", mRenderTargets.target(mRenderTargets.indexOf("edgeBlurTarget")));
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gEdgeBlurControlTex", mRenderTargets.target(mRenderTargets.indexOf("edgeBlurControl")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });

        // charcoal
        opName = "[quad] dry brush op";
        opShader = new MOperationShader("ch", "quadCharcoal", "dryMedia");
        opShader->addTargetParameter("gLightingTex", mRenderTargets.target(mRenderTargets.indexOf("diffuseTarget")));
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gSubstrateTex", mRenderTargets.target(mRenderTargets.indexOf("substrateTarget")));
        opShader->addTargetParameter("gCtrlPigmentTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        opShader->addParameter("gSubstrateRoughness", mEngSettings.substrateRoughness);
        opShader->addParameter("gDryMediaThreshold", mFxParams.dryMediaThreshold);
        opShader->addParameter("gSubstrateColor", mEngSettings.substrateColor);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });


        opName = "[quad] smudging";
        opShader = new MOperationShader("ch", "quadSmudging", "smudging");
        opShader->addTargetParameter("gStylizationTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gBlendTex", mRenderTargets.target(mRenderTargets.indexOf("blendTarget")));
        opShader->addTargetParameter("gEdgeBlurTex", mRenderTargets.target(mRenderTargets.indexOf("edgeBlurTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget")));  // smudging control
        opShader->addTargetParameter("gOffsetTex", mRenderTargets.target(mRenderTargets.indexOf("offsetTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });


        opName = "[quad] pigment density";
        opShader = new MOperationShader("quadPigmentManipulation", "pigmentDensityCC");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });
    }

};
