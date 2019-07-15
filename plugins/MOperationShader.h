#pragma once
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
#include <map>
#include <vector>
#include <memory>
#include <maya/MShaderManager.h>


class MOperationShader {
public:
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
    class QuadTexture {
    public:
        std::map<std::string, std::vector<float>*> uniformParameters;  ///< uniform parameters of texture

        QuadTexture(const MString& paramName, MString& textureFileName, MHWRender::MShaderInstance* shader);
        ~QuadTexture();
        
        void loadTexture(MString& newTexture);  ///< loads the MTexture and gets its dimensions
        MHWRender::MTexture* texture();  ///< return MTexture
        void setParams();  ///< sets uniform parameters to shader instance
        void setShaderInstance(MHWRender::MShaderInstance* shader);  ///< set the shader instance that is affected by this texture
        void setScale(float& texScale);  ///< set the scale of the quad texture
        void setUVOffset(float uvOffset[2]);  ///< set the UV offset of the quad texture
        void dPrintParams();   ///< prints the qyad texture parameters (DEBUG) 
    private:
        MHWRender::MTexture* mTex;  ///< texture
        MHWRender::MTextureDescription mTexDesc;  ///< texture description
        MHWRender::MShaderInstance* mShaderInstance;  ///< shader instance where texture is parameter of

        MString mParamName;		  ///< parameter namespace
        MString mTexDir;          ///< texture directory
        MString mTexPath;         ///< texture path
        float mTexScale;          ///< texture scale
        float mTexDimensions[2];  ///< pixel dimensions of texture
        float mTexUVOffset[2];    ///< uv offset of texture

        MHWRender::MTextureAssignment textureAssignment;  ///< used to assign a texture file to a 2D Texture
        MHWRender::MTextureManager* texManager = MHWRender::MRenderer::theRenderer()->getTextureManager();  ///< texture manager
    };

    /// parameter lists
    std::map<std::string, std::vector<float>*> uniformParameters;
	std::map<std::string, std::vector<float>*> uniformArrayParameters;
	std::map<std::string, MMatrix*> matrixParameters;
    std::map<std::string, MHWRender::MRenderTarget*> targetParameters;
    std::map<std::string, std::shared_ptr<QuadTexture>> textureParameters;
	std::map<std::string, MHWRender::MSamplerStateDesc> samplerStateDescriptions;


    /// constructor and destructor
    MOperationShader(const MString& shaderName, const MString& technique);
    MOperationShader(const MString& subDirectory, const MString& shaderName, const MString& technique);
    ~MOperationShader();

    /// creates the shader instance for this operation shader
    void setShaderInstance();

    /// adds a float parameter
    void addParameter(const MString& paramName, std::vector<float>& value);

	/// adds an array parameter
	void addArrayParameter(const MString& paramName, std::vector<float>& values);

    /// adds a matrix parameter
    void addMatrixParameter(const MString& paramName, MMatrix& value);

    /// adds a render target as parameter
    void addTargetParameter(const MString& paramName, MHWRender::MRenderTarget* target);

    /// adds a texture as parameter
    void addTextureParameter(const MString& paramName, MString& textureFileName);
    
    /// adds a sampler state parameter
    void addSamplerState(const MString& paramName, MHWRender::MSamplerState::TextureAddress addressingMode, MHWRender::MSamplerState::TextureFilter filteringMode);

    /// return file name with proper extension
    MString shaderName();

    /// returns the technique to render
    MString technique();

    /// returns the shader instance or sets one if non-existant
    MHWRender::MShaderInstance* shaderInstance();

    /// resets shader instance
    void resetShaderInstance();

protected:
    MString mSubDirectory;                                    ///< subdirectory to load the shader from, empty to use the default shader root directory
    MString mShaderName;								      ///< shader name
    MString mTechnique;									      ///< technique in the shader
    MHWRender::MShaderInstance* mShaderInstance = nullptr;    ///< shader to use for the quad render
    const MHWRender::MSamplerState* mSamplerState = nullptr;  ///< shader sampler state
    MHWRender::MSamplerStateDesc mSamplerDesc;				  ///< sampler state description

    const MHWRender::MShaderManager* shaderMgr = MHWRender::MRenderer::theRenderer()->getShaderManager();  ///< shader manager

    /// change shader extension depending on OS and release mode
    #if defined(NT_PLUGIN) && !defined(_DEBUG)
        MString mExt = "10.fxo";
    #else
        MString mExt = "";
    #endif
};
