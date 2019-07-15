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
#include "mnpr_quadRender.h"


QuadRender::QuadRender(const MString &name, int clearMask, MRenderTargetList& targetList, MOperationShader& opShader) :
    MQuadRender(name),
    mTargetList(&targetList),
    mOpShader(&opShader) {

    mClearOperation.setMask(clearMask);
}

QuadRender::~QuadRender() {
    cout << "~QuadRender(): " << name() << endl;
    delete mOpShader;  // delete operation shader
}


// set shader on quad (shaderinstance)
const MHWRender::MShaderInstance* QuadRender::shader() {
    MStatus status;
    mShaderInstance = mOpShader->shaderInstance();
    if (mShaderInstance) {
        // targets need to be refreshed every frame
        for (std::map<std::string, MHWRender::MRenderTarget*>::iterator iter = mOpShader->targetParameters.begin(); iter != mOpShader->targetParameters.end(); ++iter) {
            targetAssignment.target = iter->second;
            status = mShaderInstance->setParameter(iter->first.c_str(), targetAssignment);
        }
        
        // uniforms should ideally only be refreshed if they are changed in the config node (only affects performance if they would be a lot of them)
        for (std::map<std::string, std::vector<float>*>::iterator iter = mOpShader->uniformParameters.begin(); iter != mOpShader->uniformParameters.end(); ++iter) {
            status = mShaderInstance->setParameter(iter->first.c_str(), &iter->second->operator[](0));
        }

        // uniforms should ideally only be refreshed if they are changed in the config node (only affects performance if they would be a lot of them)
        for (std::map<std::string, MMatrix*>::iterator iter = mOpShader->matrixParameters.begin(); iter != mOpShader->matrixParameters.end(); ++iter) {
            status = mShaderInstance->setParameter(iter->first.c_str(), *iter->second);
        }

		// uniforms should ideally only be refreshed if they are changed in the config node (only affects performance if they would be a lot of them)
		for (auto iter = mOpShader->uniformArrayParameters.begin(); iter != mOpShader->uniformArrayParameters.end(); ++iter) {
			status = mShaderInstance->setArrayParameter(iter->first.c_str(), iter->second->data(), (unsigned int)iter->second->size());
		}
    }
    return mShaderInstance;
}


// return target list from mTargetList
MHWRender::MRenderTarget * const* QuadRender::targetOverrideList(unsigned int &listSize) {
    //cout << "Scene render: " << name() << endl;
    if (mTargetList) {
        mOperationTargets = mTargetList->getOperationOutputs(name());
        listSize = (unsigned int)(mOperationTargets.size());
        return &mOperationTargets[0];
    }
    listSize = 0;
    return nullptr;
}


// return operation shader
MOperationShader* QuadRender::getOperationShader() {
    return mOpShader;
}