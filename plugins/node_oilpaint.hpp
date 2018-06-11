#pragma once
///////////////////////////////////////////////////////////////////////////////////
//          _ _                 _       _                       _      
//     ___ (_) |    _ __   __ _(_)_ __ | |_     _ __   ___   __| | ___ 
//    / _ \| | |   | '_ \ / _` | | '_ \| __|   | '_ \ / _ \ / _` |/ _ \
//   | (_) | | |   | |_) | (_| | | | | | |_    | | | | (_) | (_| |  __/
//    \___/|_|_|   | .__/ \__,_|_|_| |_|\__|   |_| |_|\___/ \__,_|\___|
//                 |_|                                                 
//	 \brief Oil paint config node
//	 Contains the attributes and node computation for the oil paint stylization
//
//   Developed by: Amir Semmo (Computer Graphics Systems Group, Hasso-Plattner-Institut)
//
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"
#include "mnpr_nodes.h"


extern MObject aVelocityPV;

// stylization attributes
static MObject aOpColorSmoothing;
static MObject aOpSTSmoothing;
static MObject aOpPaintStrokeFidelity;
static MObject aOpBumpScale;
static MObject aOpBrushScale;
static MObject aOpBrushMicro;


namespace op {
    void initializeParameters(FXParameters *mFxParams, EngineSettings *mEngSettings) {
        // adds parameters in the config node
        MStatus status;
        // MFn helpers
        MFnEnumAttribute eAttr;
        MFnTypedAttribute tAttr;
        MFnNumericAttribute nAttr;

        // disable/enable engine settings
        ConfigNode::enableAttribute(aVelocityPV);
        
        // paint stroke length
        aOpColorSmoothing = nAttr.create("paintStrokeLength", "paintStrokeLength", MFnNumericData::kFloat, mFxParams->opColorSmoothing[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.1);
        nAttr.setMax(20.0);
        ConfigNode::enableAttribute(aOpColorSmoothing);
        // paint stroke width
        aOpSTSmoothing = nAttr.create("paintStrokeWidth", "paintStrokeWidth", MFnNumericData::kFloat, mFxParams->opSTSmoothing[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(1.2);
        nAttr.setMax(20.0);
        ConfigNode::enableAttribute(aOpSTSmoothing);
        // paint stroke fidelity
        aOpPaintStrokeFidelity = nAttr.create("paintStrokeFidelity", "paintStrokeFidelity", MFnNumericData::kFloat, mFxParams->opPaintStrokeFidelity[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.0);
        nAttr.setMax(1.2);
        ConfigNode::enableAttribute(aOpPaintStrokeFidelity);
        // texture bump scale
        aOpBumpScale = nAttr.create("impasto", "impasto", MFnNumericData::kFloat, mFxParams->opBumpScale[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.0);
        nAttr.setMax(200.0);
        ConfigNode::enableAttribute(aOpBumpScale);

        // Disabled for now until we find a solution on how to scale/parameterize the (coherent) white noise
        // texture brush scale
        //aOpBrushScale = nAttr.create("paintTextureScale", "paintTextureScale", MFnNumericData::kFloat, mFxParams->opBrushScale[0], &status);
        //MAKE_INPUT(nAttr);
        //nAttr.setMin(1.0);
        //nAttr.setMax(10.0);
        //mnpr_node::enableAttribute(aOpBrushScale);
        // texture micro brush
        //aOpBrushMicro = nAttr.create("paintTextureTurbulence", "paintTextureTurbulence", MFnNumericData::kFloat, mFxParams->opBrushMicro[0], &status);
        //MAKE_INPUT(nAttr);
        //nAttr.setMin(0.0);
        //nAttr.setMax(2.0);
        //mnpr_node::enableAttribute(aOpBrushMicro);
    }


    void computeParameters(MNPROverride* mmnpr_renderer, MDataBlock data, FXParameters *mFxParams, EngineSettings *mEngSettings) {
        MStatus status;
        // SPECIALIZED ENGINE SETTINGS
        mEngSettings->velocityPV[0] = (data.inputValue(aVelocityPV, &status).asBool() ? 1.0f : 0.0f);
        // STYLIZATION SETTINGS
        mFxParams->opColorSmoothing[0] = data.inputValue(aOpColorSmoothing, &status).asFloat();
        mFxParams->opSTSmoothing[0] = data.inputValue(aOpSTSmoothing, &status).asFloat();
        mFxParams->opPaintStrokeFidelity[0] = data.inputValue(aOpPaintStrokeFidelity, &status).asFloat();
        mFxParams->opBumpScale[0] = data.inputValue(aOpBumpScale, &status).asFloat();
        //mFxParams->opBrushScale[0] = data.inputValue(aOpBrushScale, &status).asFloat();
        //mFxParams->opBrushMicro[0] = data.inputValue(aOpBrushMicro, &status).asFloat();
    }

};
