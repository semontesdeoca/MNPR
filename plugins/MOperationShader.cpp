///////////////////////////////////////////////////////////////////////////////////
//                               _   _                     _               _           
//     ___  _ __   ___ _ __ __ _| |_(_) ___  _ __      ___| |__   __ _  __| | ___ _ __ 
//    / _ \| '_ \ / _ \ '__/ _` | __| |/ _ \| '_ \    / __| '_ \ / _` |/ _` |/ _ \ '__|
//   | (_) | |_) |  __/ | | (_| | |_| | (_) | | | |   \__ \ | | | (_| | (_| |  __/ |   
//    \___/| .__/ \___|_|  \__,_|\__|_|\___/|_| |_|   |___/_| |_|\__,_|\__,_|\___|_|   
//         |_|                                                                         
//
//   \brief Operation shader class
//   Contains/manages the shader to be used in the operation, with all its parameters
///////////////////////////////////////////////////////////////////////////////////
#include "MPluginUtils.h"
#include "MOperationShader.h"
#include <memory>


MOperationShader::MOperationShader(const MString& shaderName, const MString& technique) :
    mSubDirectory(""), mShaderName(shaderName), mTechnique(technique) {
    setShaderInstance();  // initialize shader instance
}


MOperationShader::MOperationShader(const MString& subDirectory, const MString& shaderName, const MString& technique) :
    mSubDirectory(subDirectory), mShaderName(shaderName), mTechnique(technique) {
    setShaderInstance();  // initialize shader instance
}


MOperationShader::~MOperationShader() {
    cout << "~MOperationShader(): " << shaderName() << endl;

    // release shader instance
    resetShaderInstance();
    
    //release sampler states
    if (mSamplerState) {
        MHWRender::MStateManager::releaseSamplerState(mSamplerState);
        mSamplerState = nullptr;
    }
}


// creates the shader instance for this operation shader
void MOperationShader::setShaderInstance() {
    cout << "-> Setting up " << shaderName() << endl;
    if (shaderMgr) {
        // if no extension, "10.fx" for HLSL or ".cgfx" for GLSL will be directly assigned by Maya
        mShaderInstance = shaderMgr->getEffectsFileShader(shaderName(), mTechnique, 0, 0, true);
        if (mShaderInstance) {
			// set textures
			for (std::map<std::string, std::shared_ptr<MOperationShader::QuadTexture>>::iterator iter = textureParameters.begin(); iter != textureParameters.end(); ++iter) {
				iter->second->setShaderInstance(mShaderInstance);  // shader instance where QuadTexture is assigned
				iter->second->setParams();
			}
			// set sampler states
			for (std::map<std::string, MHWRender::MSamplerStateDesc>::iterator iter = samplerStateDescriptions.begin(); iter != samplerStateDescriptions.end(); ++iter) {
				mSamplerState = MHWRender::MStateManager::acquireSamplerState(iter->second);
				mShaderInstance->setParameter(iter->first.c_str(), *mSamplerState);
			}
        }
    }
}


// resets shader instance
void MOperationShader::resetShaderInstance() {
    mShaderInstance = nullptr;
    shaderMgr->removeEffectFromCache(shaderName(), mTechnique, 0, 0);
}



//              _     _                                          _                
//     __ _  __| | __| |    _ __   __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___ 
//    / _` |/ _` |/ _` |   | '_ \ / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
//   | (_| | (_| | (_| |   | |_) | (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
//    \__,_|\__,_|\__,_|   | .__/ \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
//                         |_|                                                    

// adds a float parameter
void MOperationShader::addParameter(const MString& paramName, std::vector<float>& value) {
    uniformParameters[paramName.asChar()] = &value;
}

// adds a float array parameter
void MOperationShader::addArrayParameter(const MString& paramName, std::vector<float>& values) {
	uniformArrayParameters[paramName.asChar()] = &values;
}

// adds a matrix parameter
void MOperationShader::addMatrixParameter(const MString& paramName, MMatrix& value) {
    matrixParameters[paramName.asChar()] = &value;
}


// adds a render target as parameter
void MOperationShader::addTargetParameter(const MString& paramName, MHWRender::MRenderTarget* target) {
    targetParameters[paramName.asChar()] = target;
}


// adds a texture as parameter
void MOperationShader::addTextureParameter(const MString& paramName, MString& textureFileName) {
    std::shared_ptr<QuadTexture> newTexture(new QuadTexture(paramName, textureFileName, mShaderInstance));
    textureParameters[paramName.asChar()] = newTexture;
	newTexture->setParams();
}


// adds a sampler state parameter
void MOperationShader::addSamplerState(const MString& paramName, MHWRender::MSamplerState::TextureAddress addressingMode, MHWRender::MSamplerState::TextureFilter filteringMode) {
    mSamplerDesc.addressU = mSamplerDesc.addressV = mSamplerDesc.addressW = addressingMode;
    mSamplerDesc.filter = filteringMode;
    mSamplerState = MHWRender::MStateManager::acquireSamplerState(mSamplerDesc);
	samplerStateDescriptions[paramName.asChar()] = mSamplerDesc;
	if (mShaderInstance){
        mShaderInstance->setParameter(paramName, *mSamplerState);
    } else {
		cout << "ERROR: Shader Instance not found while setting Sampler State " << paramName << " in " << mShaderName << endl;
	}
}





//               _   
//     __ _  ___| |_ 
//    / _` |/ _ \ __|
//   | (_| |  __/ |_ 
//    \__, |\___|\__|
//    |___/          

// return file name with proper extension
MString MOperationShader::shaderName() {
    MString shaderFileName = (mSubDirectory == "") ? (mShaderName + mExt) : (mSubDirectory + "/" + mShaderName + mExt);
    return shaderFileName;
}


// returns the technique to render
MString MOperationShader::technique() {
    return mTechnique;
}


// returns the shader instance or sets one if non-existant
MHWRender::MShaderInstance* MOperationShader::shaderInstance() {
    if (mShaderInstance == nullptr) {
        setShaderInstance();
    }
    if (mShaderInstance) {
        return mShaderInstance;
    }
    else {
        return nullptr;
    }
}



///////////////////////////////////////////////////////////////////////////////////
//                          _     _            _                  
//     __ _ _   _  __ _  __| |   | |_ _____  _| |_ _   _ _ __ ___ 
//    / _` | | | |/ _` |/ _` |   | __/ _ \ \/ / __| | | | '__/ _ \
//   | (_| | |_| | (_| | (_| |   | ||  __/>  <| |_| |_| | | |  __/
//    \__, |\__,_|\__,_|\__,_|    \__\___/_/\_\\__|\__,_|_|  \___|
//       |_|                                                      
//
//   \brief Quad texture class
//   Contains/manages textures within the shader
///////////////////////////////////////////////////////////////////////////////////
MOperationShader::QuadTexture::QuadTexture(const MString& paramName, MString& textureFileName, MHWRender::MShaderInstance* shader) {
    // initialize protected variables
    mTexDir = utils::pluginEnv("textures");
    mShaderInstance = shader;
    mParamName = paramName;
    mTexScale = 1.0;
    mTexUVOffset[0] = 0.0;
    mTexUVOffset[1] = 0.0;
	mTex = nullptr;
    loadTexture(textureFileName);
}


MOperationShader::QuadTexture::~QuadTexture() {
    if (mTex != nullptr) {
        texManager->releaseTexture(mTex);
        cout << "QuadTexture: " << mTexPath << " destroyed" << endl;
    }
}


// loads the MTexture and gets its dimensions
void MOperationShader::QuadTexture::loadTexture(MString& newTexture) {
	// release texture
	if (mTex != nullptr) {
		texManager->releaseTexture(mTex);
	}
	// get new texture
	mTexPath = mTexDir + newTexture;
    mTex = texManager->acquireTexture(mTexPath, mTexPath);
    if (mTex) {
        mTex->textureDescription(mTexDesc);
        mTexDimensions[0] = (float)mTexDesc.fWidth;
        mTexDimensions[1] = (float)mTexDesc.fHeight;
    } else {
        cout << "ERROR: Texture not found: " << newTexture << endl;
    }
}


// return MTexture
MHWRender::MTexture* MOperationShader::QuadTexture::texture() {
    return mTex;
}


// sets uniform parameters to shader instance
void MOperationShader::QuadTexture::setParams() {
    if (mShaderInstance){
        textureAssignment.texture = mTex;
        mShaderInstance->setParameter(mParamName, textureAssignment);
        mShaderInstance->setParameter(mParamName + "UVOffset", mTexUVOffset);
        mShaderInstance->setParameter(mParamName + "Scale", mTexScale);
        mShaderInstance->setParameter(mParamName + "Dimensions", mTexDimensions);
    }
}


// set the shader instance that is affected by this texture
void MOperationShader::QuadTexture::setShaderInstance(MHWRender::MShaderInstance* shader) {
    mShaderInstance = shader;
}


// set the scale of the quad texture
void MOperationShader::QuadTexture::setScale(float& texScale) {
    mTexScale = texScale;
}


// set the UV offset of the quad texture
void MOperationShader::QuadTexture::setUVOffset(float uvOffset[2]) {
    mTexUVOffset[0] = uvOffset[0];
    mTexUVOffset[0] = uvOffset[1];
}


// prints the qyad texture parameters (DEBUG) 
void MOperationShader::QuadTexture::dPrintParams() {
    cout << "Parameter name: " << mParamName << endl;
    cout << "Texture path: " << mTexPath << endl;
    cout << "Texture scale: " << mTexScale << endl;
    cout << "Texture UV Offset: [" << mTexUVOffset[0] << ", " << mTexUVOffset[1] << "]" << endl;
    cout << "Texture dimensions: [" << mTexDimensions[0] << ", " << mTexDimensions[1] << "]" << endl;
}