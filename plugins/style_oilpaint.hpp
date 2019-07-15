#pragma once
///////////////////////////////////////////////////////////////////////////////////
//          _ _                 _       _   
//     ___ (_) |    _ __   __ _(_)_ __ | |_ 
//    / _ \| | |   | '_ \ / _` | | '_ \| __|
//   | (_) | | |   | |_) | (_| | | | | | |_ 
//    \___/|_|_|   | .__/ \__,_|_|_| |_|\__|
//                 |_|                      
//	 \brief Oil paint stylization pipeline
//	 Contains the oil paint stylization pipeline with all necessary targets and operations
//
//   Developed by: Amir Semmo (Computer Graphics Systems Group, Hasso-Plattner-Institut)
//
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"


namespace op {

    void addTargets(MRenderTargetList &targetList) {
        // add style specific targets
        unsigned int tWidth = targetList[0]->width();
        unsigned int tHeight = targetList[0]->height();
        int MSAA = targetList[0]->multiSampleCount();
        unsigned arraySliceCount = 0;
        bool isCubeMap = false;
        MHWRender::MRasterFormat rgba8 = MHWRender::kR8G8B8A8_SNORM;
        MHWRender::MRasterFormat rgb8 = MHWRender::kR8G8B8X8;
        MHWRender::MRasterFormat r16f = MHWRender::kR16_FLOAT;
        MHWRender::MRasterFormat rg16f = MHWRender::kR16G16_FLOAT;
        MHWRender::MRasterFormat rgba16f = MHWRender::kR16G16B16A16_FLOAT;
        MHWRender::MRasterFormat rgba32f = MHWRender::kR32G32B32A32_FLOAT;

        targetList.append(MHWRender::MRenderTargetDescription("labTarget", tWidth, tHeight, 1, rgba32f, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("structureTensorTarget", tWidth, tHeight, 1, rgba32f, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("tangentFlowMapTarget", tWidth, tHeight, 1, rgba32f, arraySliceCount, isCubeMap));
        targetList.append(MHWRender::MRenderTargetDescription("noiseTarget", tWidth, tHeight, 1, rg16f, arraySliceCount, isCubeMap)); // previous frame encoded in y-channel
        targetList.append(MHWRender::MRenderTargetDescription("noiseSmoothedTarget", tWidth, tHeight, 1, rg16f, arraySliceCount, isCubeMap)); // previous frame encoded in y-channel
        targetList.append(MHWRender::MRenderTargetDescription("filterTarget", tWidth, tHeight, 1, r16f, arraySliceCount, isCubeMap));
    }


    void addOperations(MHWRender::MRenderOperationList &mRenderOperations, MRenderTargetList &mRenderTargets,
        EngineSettings &mEngSettings, FXParameters &mFxParams) {
        MString opName = "";

        static std::vector<float> gDxD0 = { 1.0f, 0.0f };
        static std::vector<float> gDxD1 = { 0.0f, 1.0f };

        opName = "[quad] gaps and overlaps";
        auto opShader = new MOperationShader("quadGapsOverlaps", "gapsOverlaps");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gEdgeTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("edgeCtrlTarget")));
        opShader->addParameter("gGORadius", mFxParams.gapsOverlapsWidth);
        opShader->addParameter("gSubstrateColor", mEngSettings.substrateColor);
        auto quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget", "filterTarget" });

        opName = "[quad] pigment density";
        opShader = new MOperationShader("quadPigmentManipulation", "pigmentDensityOP");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gFilterTex", mRenderTargets.target(mRenderTargets.indexOf("filterTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        opShader->addParameter("gSubstrateColor", mEngSettings.substrateColor);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget", "filterTarget" });

        opName = "[quad] color smoothing pass #0";
        opShader = new MOperationShader("quadBilateralSmoothing", "bilateralSeparated");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        static std::vector<float> bilateralSmoothingPass0 = { 1.0f };
        opShader->addParameter("gPass", bilateralSmoothingPass0);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });

        opName = "[quad] color smoothing pass #1";
        opShader = new MOperationShader("quadBilateralSmoothing", "bilateralSeparated");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        static std::vector<float> bilateralSmoothingPass1 = { 1.0f };
        opShader->addParameter("gPass", bilateralSmoothingPass1);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });

        opName = "[quad] rgb2lab color transform";
        opShader = new MOperationShader("quadColorTransform", "rgb2labTransform");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "labTarget" });

        opName = "[quad] structure tensor";
        opShader = new MOperationShader("quadTangentFlowMap", "structureTensor");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("labTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "structureTensorTarget" });

        opName = "[quad] smoothing structure tensor";
        opShader = new MOperationShader("op", "quadGaussianSmoothing", "gauss2D");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("structureTensorTarget")));
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addParameter("gSubstrateColor", mEngSettings.substrateColor);
        opShader->addParameter("gSigma", mFxParams.opSTSmoothing);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "tangentFlowMapTarget" });

        opName = "[quad] tangent flow map synthesis";
        opShader = new MOperationShader("quadTangentFlowMap", "tangentFlowMap");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("tangentFlowMapTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "tangentFlowMapTarget" });

        opName = "[quad] edge flow-aligned smoothing";
        opShader = new MOperationShader("op", "quadFlowAlignedSmoothing", "flowAlignedSmoothing");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget"))); // logTarget
        opShader->addTargetParameter("gTfmTex", mRenderTargets.target(mRenderTargets.indexOf("tangentFlowMapTarget")));
        static std::vector<float> edgeSmoothingSigma = { 1.0f };
        opShader->addParameter("gSigma", edgeSmoothingSigma);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "edgeTarget" });

        opName = "[quad] structure tensor adapted smoothing #0";
        opShader = new MOperationShader("op", "quadGaussianSmoothing", "gauss2DAdaptedXYSeparated");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("structureTensorTarget")));
        opShader->addTargetParameter("gEdgeTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget")));
        opShader->addParameter("gSigma", mFxParams.opSTSmoothing);
        static std::vector<float> stAdaptedSmoothingDxDy0 = { 1.0f, 0.0f };
        opShader->addParameter("gDxDy", stAdaptedSmoothingDxDy0);
        opShader->addParameter("gTauG", mFxParams.opPaintStrokeFidelity);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "structureTensorTarget" });

        opName = "[quad] structure tensor adapted smoothing #1";
        opShader = new MOperationShader("op", "quadGaussianSmoothing", "gauss2DAdaptedXYSeparated");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("structureTensorTarget")));
        opShader->addTargetParameter("gEdgeTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget")));
        opShader->addParameter("gSigma", mFxParams.opSTSmoothing);
        static std::vector<float> stAdaptedSmoothingDxDy1 = { 0.0f, 1.0f };
        opShader->addParameter("gDxDy", stAdaptedSmoothingDxDy1);
        opShader->addParameter("gTauG", mFxParams.opPaintStrokeFidelity);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "structureTensorTarget" });

        opName = "[quad] tangent flow map adaptive synthesis";
        opShader = new MOperationShader("quadTangentFlowMap", "tangentFlowMap");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("structureTensorTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "tangentFlowMapTarget" });

        opName = "[quad] noise synthesis";
        opShader = new MOperationShader("op", "quadNoise", "noiseSynthesis");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipLinear);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("labTarget")));
        opShader->addTargetParameter("gDepthTex", mRenderTargets.target(mRenderTargets.indexOf("linearDepth")));
        opShader->addTargetParameter("gNoiseTex", mRenderTargets.target(mRenderTargets.indexOf("noiseTarget")));
        opShader->addTargetParameter("gVelocityTex", mRenderTargets.target(mRenderTargets.indexOf("velocity")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        opShader->addParameter("gScale", mFxParams.opBrushScale);
        opShader->addParameter("gMicro", mFxParams.opBrushMicro);
        opShader->addParameter("gTime", mEngSettings.time);
        opShader->addParameter("gRandom", mEngSettings.random);
        mRenderTargets.setOperationOutputs(opName, { "noiseTarget" });

        opName = "[quad] noise pre-smoothing";
        opShader = new MOperationShader("op", "quadGaussianSmoothing", "gauss2DX");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("noiseTarget")));
        static std::vector<float> noisePreBlurringSigma = { 0.5f };
        opShader->addParameter("gSigma", noisePreBlurringSigma);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "noiseTarget" });

        opName = "[quad] noise advection (coherent noise)";
        opShader = new MOperationShader("op", "quadNoise", "coherentNoiseSynthesis");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipLinear);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("labTarget")));
        opShader->addTargetParameter("gDepthTex", mRenderTargets.target(mRenderTargets.indexOf("linearDepth")));
        opShader->addTargetParameter("gNoiseTex", mRenderTargets.target(mRenderTargets.indexOf("noiseTarget")));
        opShader->addTargetParameter("gVelocityTex", mRenderTargets.target(mRenderTargets.indexOf("velocity")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        opShader->addParameter("gScale", mFxParams.opBrushScale);
        opShader->addParameter("gMicro", mFxParams.opBrushMicro);
        opShader->addParameter("gTime", mEngSettings.time);
        mRenderTargets.setOperationOutputs(opName, { "noiseTarget" });

        /*
        opName = "[quad] noise post-smoothing";
        opShader = new MOperationShader("op", "quadGaussianSmoothing", "gauss2DX");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("noiseTarget")));
        static std::vector<float> noisePostBlurringSigma = { 0.5 };
        opShader->addParameter("gSigma", noisePostBlurringSigma);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "noiseTarget" });
        */

        opName = "[quad] pigment application";
        opShader = new MOperationShader("quadPigmentApplication", "pigmentApplicationOP");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gFilterTex", mRenderTargets.target(mRenderTargets.indexOf("filterTarget")));
        opShader->addTargetParameter("gSubstrateTex", mRenderTargets.target(mRenderTargets.indexOf("substrateTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        opShader->addParameter("gSubstrateColor", mEngSettings.substrateColor);
        opShader->addParameter("gPigmentDensity", mFxParams.pigmentDensity);
        opShader->addParameter("gDryBrushThreshold", mFxParams.dryBrushThreshold);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget", "filterTarget" });

        opName = "[quad] noise and color (packed) flow-aligned smoothing";
        opShader = new MOperationShader("op", "quadFlowAlignedSmoothing", "flowAlignedSmoothingThresholded");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gNoiseTex", mRenderTargets.target(mRenderTargets.indexOf("noiseTarget")));
        opShader->addTargetParameter("gTfmTex", mRenderTargets.target(mRenderTargets.indexOf("tangentFlowMapTarget")));
        opShader->addTargetParameter("gEdgeTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget")));
        opShader->addParameter("gSigma", mFxParams.opColorSmoothing);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget", "noiseSmoothedTarget" });

        opName = "[quad] noise texture shading";
        opShader = new MOperationShader("op", "quadImpasto", "impasto");
        opShader->addSamplerState("gSampler", MHWRender::MSamplerState::kTexClamp, MHWRender::MSamplerState::kMinMagMipPoint);
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("noiseSmoothedTarget")));
        opShader->addTargetParameter("gFilterTex", mRenderTargets.target(mRenderTargets.indexOf("filterTarget")));
        opShader->addTargetParameter("gSubstrateTex", mRenderTargets.target(mRenderTargets.indexOf("substrateTarget")));
        opShader->addTargetParameter("gPigmentControlTex", mRenderTargets.target(mRenderTargets.indexOf("pigmentCtrlTarget")));
        opShader->addTargetParameter("gAbstractionControlTex", mRenderTargets.target(mRenderTargets.indexOf("abstractCtrlTarget")));
        opShader->addParameter("gBumpScale", mFxParams.opBumpScale);
        opShader->addParameter("gSigma", mFxParams.opColorSmoothing);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "substrateTarget" });

        opName = "[quad] oil compose";
        opShader = new MOperationShader("op", "quadCompose", "oilCompose");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gFilterTex", mRenderTargets.target(mRenderTargets.indexOf("filterTarget")));
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });

        opName = "[quad] substrate distortion";
        opShader = new MOperationShader("quadSubstrate", "substrateDistortionEdges");
        opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
        opShader->addTargetParameter("gEdgeTex", mRenderTargets.target(mRenderTargets.indexOf("edgeTarget")));
        opShader->addTargetParameter("gControlTex", mRenderTargets.target(mRenderTargets.indexOf("substrateCtrlTarget")));
        opShader->addTargetParameter("gSubstrateTex", mRenderTargets.target(mRenderTargets.indexOf("substrateTarget")));
        opShader->addParameter("gSubstrateDistortion", mEngSettings.substrateDistortion);
        quadOp = new QuadRender(opName,
            MHWRender::MClearOperation::kClearNone,
            mRenderTargets,
            *opShader);
        mRenderOperations.append(quadOp);
        mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });
    }
};