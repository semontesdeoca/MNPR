#pragma once
///////////////////////////////////////////////////////////////////////////////////
//                  _                     _                                _      
//   __      ____ _| |_ ___ _ __ ___ ___ | | ___  _ __     _ __   ___   __| | ___ 
//   \ \ /\ / / _` | __/ _ \ '__/ __/ _ \| |/ _ \| '__|   | '_ \ / _ \ / _` |/ _ \
//    \ V  V / (_| | ||  __/ | | (_| (_) | | (_) | |      | | | | (_) | (_| |  __/
//     \_/\_/ \__,_|\__\___|_|  \___\___/|_|\___/|_|      |_| |_|\___/ \__,_|\___|
//                                                                                
//	 \brief Watercolor config node
//	 Contains the attributes and node computation for the watercolor stylization
//
//   Developed by: Santiago Montesdeoca
//
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"
#include "mnpr_nodes.h"


// stylization attributes
static MObject aBleedingThreshold;
static MObject aBleedingRadius;
static MObject aEdgeDarkeningIntensity;
static MObject aEdgeDarkeningWidth;
static MObject aGapsOverlapsWidth;
static MObject aPigmentDensity;
static MObject aDryBrushThreshold;


namespace wc {
    void initializeParameters(FXParameters *mFxParams, EngineSettings *mEngSettings) {
        // adds parameters in the config node
        MStatus status;
        float renderScale = mEngSettings->renderScale[0];
        // MFn helpers
        MFnEnumAttribute eAttr;
        MFnTypedAttribute tAttr;
        MFnNumericAttribute nAttr;

        // disable/enable engine settings
        mEngSettings->velocityPV[0] = 0.0;

        // color bleeding threshold
        aBleedingThreshold = nAttr.create("bleedingThreshold", "bleedingThreshold", MFnNumericData::kFloat, mFxParams->bleedingThreshold[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.0);
        nAttr.setSoftMax(0.003);
        nAttr.setMax(1.0);
        ConfigNode::enableAttribute(aBleedingThreshold);

        // color bleeding radius
        aBleedingRadius = nAttr.create("bleedingRadius", "bleedingRadius", MFnNumericData::kInt, mFxParams->bleedingRadius[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(1.0);
        nAttr.setMax(40.0);
        ConfigNode::enableAttribute(aBleedingRadius);

        // edge darkening intensity
        aEdgeDarkeningIntensity = nAttr.create("edgeDarkeningIntensity", "edgeDarkeningIntensity", MFnNumericData::kFloat, mFxParams->edgeDarkeningIntensity[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.0);
        nAttr.setSoftMax(3.0);
        nAttr.setMax(25.0);
        ConfigNode::enableAttribute(aEdgeDarkeningIntensity);

        // edge darkening width
        aEdgeDarkeningWidth = nAttr.create("edgeDarkeningWidth", "edgeDarkeningWidth", MFnNumericData::kInt, mFxParams->edgeDarkeningWidth[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(1);
        nAttr.setMax(50);
        ConfigNode::enableAttribute(aEdgeDarkeningWidth);

        // gaps and overlaps width
        aGapsOverlapsWidth = nAttr.create("maxGapsOverlapsWidth", "maxGapsOverlapsWidth", MFnNumericData::kInt, mFxParams->gapsOverlapsWidth[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(1);
        nAttr.setSoftMax(5);
        nAttr.setMax(10);
        ConfigNode::enableAttribute(aGapsOverlapsWidth);

        // pigment density
        aPigmentDensity = nAttr.create("pigmentDensity", "pigmentDensity", MFnNumericData::kFloat, mFxParams->pigmentDensity[0]);
        MAKE_INPUT(nAttr);
        nAttr.setSoftMin(0.0);
        nAttr.setSoftMax(10.0);
        ConfigNode::enableAttribute(aPigmentDensity);

        // drybrush threshold
        aDryBrushThreshold = nAttr.create("drybrushThreshold", "drybrushThreshold", MFnNumericData::kFloat, mFxParams->dryBrushThreshold[0]);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.0);
        nAttr.setSoftMax(20.0);
        ConfigNode::enableAttribute(aDryBrushThreshold);
    }


    void computeParameters(MNPROverride* mmnpr_renderer, MDataBlock data, FXParameters *mFxParams, EngineSettings *mEngSettings) {
        MStatus status;

        // BLEEDING
        mFxParams->bleedingThreshold[0] = data.inputValue(aBleedingThreshold, &status).asFloat();
        int bleedingRadius = (int)(data.inputValue(aBleedingRadius, &status).asShort() * mEngSettings->renderScale[0]);
        if ((mFxParams->bleedingRadius[0] != bleedingRadius) || (!mEngSettings->initialized)) {
            mFxParams->bleedingRadius[0] = (float)bleedingRadius;
            float sigma = (float)bleedingRadius * 2.0f;
            // calculate new bleeding kernel
            float normDivisor = 0;
            for (int x = -bleedingRadius; x <= bleedingRadius; x++) {
                float weight = (float)(0.15915*exp(-0.5*x*x / (sigma*sigma)) / sigma);
                //float weight = (float)(pow((6.283185*sigma*sigma), -0.5) * exp((-0.5*x*x) / (sigma*sigma)));
                normDivisor += weight;
                mFxParams->bleedingWeigths[x + bleedingRadius] = weight;
            }
            // normalize weights
            for (int x = -bleedingRadius; x <= bleedingRadius; x++) {
                mFxParams->bleedingWeigths[x + bleedingRadius] /= normDivisor;
            }
            // send weights to shaders
            MOperationShader* opShader;
            QuadRender* quadOp = (QuadRender*)mmnpr_renderer->renderOperation("[quad] separable H");
            opShader = quadOp->getOperationShader();
            MHWRender::MShaderInstance* shaderInstance = opShader->shaderInstance();
            if (shaderInstance) {
                shaderInstance->setParameter("gBleedingRadius", &mFxParams->bleedingRadius[0]);
                shaderInstance->setArrayParameter("gGaussianWeights", &mFxParams->bleedingWeigths[0], (bleedingRadius * 2) + 1);
            }
            quadOp = (QuadRender*)mmnpr_renderer->renderOperation("[quad] separable V");
            opShader = quadOp->getOperationShader();
            shaderInstance = opShader->shaderInstance();
            if (shaderInstance) {
                shaderInstance->setParameter("gBleedingRadius", &mFxParams->bleedingRadius[0]);
                shaderInstance->setArrayParameter("gGaussianWeights", &mFxParams->bleedingWeigths[0], (bleedingRadius * 2) + 1);
            }
        }

        // EDGE DARKENING
        mFxParams->edgeDarkeningIntensity[0] = data.inputValue(aEdgeDarkeningIntensity, &status).asFloat() * mEngSettings->renderScale[0];
        mFxParams->edgeDarkeningWidth[0] = roundf(data.inputValue(aEdgeDarkeningWidth, &status).asShort() * mEngSettings->renderScale[0]);

        // GAPS & OVERLAPS
        mFxParams->gapsOverlapsWidth[0] = roundf(data.inputValue(aGapsOverlapsWidth, &status).asShort() * mEngSettings->renderScale[0]);

        // PIGMENT EFFECTS
        mFxParams->pigmentDensity[0] = data.inputValue(aPigmentDensity, &status).asFloat();
        float drybrushThresholdInput = data.inputValue(aDryBrushThreshold, &status).asFloat();
        mFxParams->dryBrushThreshold[0] = (float)20.0 - drybrushThresholdInput;
    }

};