#pragma once
///////////////////////////////////////////////////////////////////////////////////
//         _                               _                     _      
//     ___| |__   __ _ _ __ ___ ___   __ _| |    _ __   ___   __| | ___ 
//    / __| '_ \ / _` | '__/ __/ _ \ / _` | |   | '_ \ / _ \ / _` |/ _ \
//   | (__| | | | (_| | | | (_| (_) | (_| | |   | | | | (_) | (_| |  __/
//    \___|_| |_|\__,_|_|  \___\___/ \__,_|_|   |_| |_|\___/ \__,_|\___|
//                                                                      
//	 \brief Charcoal config node
//	 Contains attributes and node computation for the charcoal stylization
//
//   Developed by: Yee Xin Chiew
//
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"
#include "mnpr_nodes.h"


// stylization attributes
static MObject aDryMediaThreshold;


namespace ch {
    void initializeParameters(FXParameters *mFxParams, EngineSettings *mEngSettings, MObject &aEvaluate) {
        // adds parameters in the config node
        MStatus status;
        float renderScale = mEngSettings->renderScale[0];
        // MFn helpers
        MFnEnumAttribute eAttr;
        MFnTypedAttribute tAttr;
        MFnNumericAttribute nAttr;

        // dry media threshold
        aDryMediaThreshold = nAttr.create("dryMediaThreshold", "dryMediaThreshold", MFnNumericData::kFloat, mFxParams->dryMediaThreshold[0], &status);
        MAKE_INPUT(nAttr);
        nAttr.setMin(0.0);
        nAttr.setSoftMax(1.0);
        ConfigNode::addAttribute(aDryMediaThreshold);
        ConfigNode::attributeAffects(aDryMediaThreshold, aEvaluate);
    }


    void computeParameters(MNPROverride* mmnpr_renderer, MDataBlock data, FXParameters *mFxParams, EngineSettings *mEngSettings) {
        MStatus status;

        mFxParams->dryMediaThreshold[0] = (float)data.inputValue(aDryMediaThreshold, &status).asFloat();
    }

};