#pragma once
///////////////////////////////////////////////////////////////////////////////////
//    __  __ _   _ ____  ____
//   |  \/  | \ | |  _ \|  _ \
//   | |\/| |  \| | |_) | |_) |
//   | |  | | |\  |  __/|  _ <
//   |_|  |_|_| \_|_|   |_| \_\
//
//   \brief MNPR Framework
//   Contains and manages the Maya Non-Photorealistic Renderer (MNPR) using VP2.0
//
//   Originally developed by: Santiago E. Montesdeoca
//   Contributors (a-z): Pierre Bénard, Yee Xin Chiew, Amir Semmo 
//
///////////////////////////////////////////////////////////////////////////////////
#include <map>
#include <vector>
#include <chrono>
#include <maya/MGlobal.h>
#include <maya/MAnimControl.h>
#include <maya/MShaderManager.h>
#include "MRenderTargetList.h"
#include "mnpr_sceneRender.h"
#include "mnpr_quadRender.h"
#include "MOperationShader.h"



//          _             _           _        __
//    _ __ | |_   _  __ _(_)_ __     (_)_ __  / _| ___
//   | '_ \| | | | |/ _` | | '_ \    | | '_ \| |_ / _ \
//   | |_) | | |_| | (_| | | | | |   | | | | |  _| (_) |
//   | .__/|_|\__,_|\__, |_|_| |_|   |_|_| |_|_|  \___/
//   |_|            |___/
extern const MString PLUGIN_NAME;
extern const MString RENDERER_NAME;
extern const MString AUTHOR_NAME;
extern const MString PURPOSE;
extern const std::vector<MString> STYLES;



//                     _                         _   _   _
//     ___ _ __   __ _(_)_ __   ___     ___  ___| |_| |_(_)_ __   __ _ ___
//    / _ \ '_ \ / _` | | '_ \ / _ \   / __|/ _ \ __| __| | '_ \ / _` / __|
//   |  __/ | | | (_| | | | | |  __/   \__ \  __/ |_| |_| | | | | (_| \__ \
//    \___|_| |_|\__, |_|_| |_|\___|   |___/\___|\__|\__|_|_| |_|\__, |___/
//               |___/                                           |___/
struct EngineSettings {
    // float, float2, float3, float4 |  should be vectors
    bool initialized = { false };                                   ///< initialization
    MString style = { "Watercolor" };                               ///< default style, Framework
    unsigned int colorDepth = { 1 };						        ///< color depth of render targets
    std::vector<float> mayaGamma = std::vector<float>{ 1.0f };                        ///< gamma state in Maya viewport
    std::vector<float> mnprGamma = std::vector<float>{ 0.0f };                        ///< MNPR gamma state
    std::vector<float> renderScale = std::vector<float>{ 1.0f };				        ///< render size(factor) of render targets
    std::vector<float> antialiasing = std::vector<float>{ 1.0f };		                ///< antialiasing quality of targets
    std::vector<float> depthRange = std::vector<float>{ 8.0f, 50.0f };		        ///< linear depth max range (maya units)
    std::vector<float> velocityPV = std::vector<float>{ 0.0f };                       ///< enable/disable velocity per vertex computation (cast as boolean)
    std::vector<float> colorChannels = std::vector<float>{ 1.0f, 1.0f, 1.0f, 0.0f };  ///< color channels to present
    std::vector<float> colorTransformationMode = std::vector<float>{ 0.0f };          ///< color transformation mode to use
    // ATMOSPHERE
    std::vector<float> atmosphereTint = std::vector<float>{ 1.0f, 1.0f, 1.0f };         ///< colors of atmosphere
    std::vector<float> atmosphereRange = std::vector<float>{ 25.0f, 300.0f };           ///< range of atmosphere perspective (maya units)
    // TIME, RANDOM
    std::vector<float> time = std::vector<float>{ 0.0f };                               ///< time in milliseconds, refreshed after each frame
    std::vector<float> random = std::vector<float>{ 0.0f, 0.0f, 0.0f };                 ///< 3 random integers cast as float, each between 0 and 254
    // SUBSTRATE
    MString substrateTexFilename = "rough_default_2k.jpg";			                    ///< substrate texture name
    std::vector<float> substrateColor = std::vector<float>{ 1.0f, 1.0f, 1.0f };	        ///< colors of substrate
    std::vector<float> substrateShading = std::vector<float>{ 0.5f };			        ///< deferred shading of substrate
    std::vector<float> substrateLightDir = std::vector<float>{ 180.0f };			    ///< direction of substrate deferred lighting
    std::vector<float> substrateLightTilt = std::vector<float>{ 45.0f };			    ///< tilt of substrate deferred lighting
    std::vector<float> substrateScale = std::vector<float>{1.0f};    			        ///< scale of the substrate texture
    std::vector<float> substrateUpdate = std::vector<float>{ 0.0f };				    ///< times/s for each substrate refresh
    std::vector<float> substrateRoughness = std::vector<float>{ 1.0f };		            ///< roughness of the substrate profile
    std::vector<float> substrateUVOffset = std::vector<float>{ 0.0f, 0.0f };		    ///< UV Offset of substrate texture
    std::vector<float> substrateDistortion = std::vector<float>{ 1.0f };		        ///< distortion that the substrate causes


    /// print engine settings (DEBUG)
    void dPrint() {
        cout << "Initialized -> " << initialized << endl;
        cout << "Style -> " << style << endl;
        cout << "Color depth -> " << colorDepth << endl;
        cout << "Maya gamma enabled -> " << mayaGamma[0] << endl;
        cout << "MNPR gamma enabled -> " << mnprGamma[0] << endl;
        cout << "Render size -> " << renderScale[0] << endl;
        cout << "Depth range [" << depthRange[0] << ", " << depthRange[1] << "]" << endl;
        cout << "Velocity per vertex computation -> " << velocityPV[0] << endl;
        cout << "Color channels [" << colorChannels[0] << ", " << colorChannels[1] << ", " << colorChannels[2] << ", " << colorChannels[3] << "]" << endl;
        cout << "Color transformation mode -> " << colorTransformationMode[0] << endl;
        cout << "Substrate color -> [" << substrateColor[0] << "," << substrateColor[1] << "," << substrateColor[2] << "]" << endl;
        cout << "Substrate update -> " << substrateUpdate[0] << endl;
        cout << "Substrate roughness -> " << substrateRoughness[0] << endl;
        cout << "Substrate distortion -> " << substrateDistortion[0] << endl;
        cout << "Substrate light direction -> " << substrateLightDir[0] << endl;
        cout << "Substrate light tilt -> " << substrateLightTilt[0] << endl;
        cout << "Substrate shading -> " << substrateShading[0] << endl;
        cout << "Substrate scale -> " << substrateScale[0] << endl;
        cout << "Atmosphere color [" << atmosphereTint[0] << ", " << atmosphereTint[1] << ", " << atmosphereTint[2] << "]" << endl;
        cout << "Atmosphere range [" << atmosphereRange[0] << ", " << atmosphereRange[1] << "]" << endl;
    }
};



//     __                                               _
//    / _|_  __    _ __   __ _ _ __ __ _ _ __ ___   ___| |_ ___ _ __ ___
//   | |_\ \/ /   | '_ \ / _` | '__/ _` | '_ ` _ \ / _ \ __/ _ \ '__/ __|
//   |  _|>  <    | |_) | (_| | | | (_| | | | | | |  __/ ||  __/ |  \__ \
//   |_| /_/\_\   | .__/ \__,_|_|  \__,_|_| |_| |_|\___|\__\___|_|  |___/
//                |_|
struct FXParameters {
    // float, float2, float3, float4 |  should be vectors
    std::vector<float> saturation = std::vector<float>{ 1.0f };
    std::vector<float> contrast = std::vector<float>{ 1.0f };
    std::vector<float> brightness = std::vector<float>{ 1.0f };
    // watercolor parameters
    std::vector<float> bleedingThreshold = std::vector<float>{ 0.0002f };
    std::vector<float> bleedingRadius = std::vector<float>{ 10.0f };
    std::vector<float> bleedingWeigths = std::vector<float>(161);
    std::vector<float> edgeDarkeningIntensity = std::vector<float>{ 1.0f };
    std::vector<float> edgeDarkeningWidth = std::vector<float>{ 3.0f };
    std::vector<float> gapsOverlapsWidth = std::vector<float>{ 3.0f };
    std::vector<float> pigmentDensity = std::vector<float>{ 5.0f };
    std::vector<float> dryBrushThreshold = std::vector<float>{ 15.0f };
    // oilpaint parameters
    std::vector<float> opColorSmoothing = std::vector<float>{ 8.0f };
    std::vector<float> opSTSmoothing = std::vector<float>{ 2.5f };
    std::vector<float> opPaintStrokeFidelity = std::vector<float>{ 1.2f };
    std::vector<float> opBumpScale = std::vector<float>{ 60.0f };
    std::vector<float> opBrushScale = std::vector<float>{ 0.75f };
    std::vector<float> opBrushMicro = std::vector<float>{ 2.0f };
    // charcoal parameters
    std::vector<float> dryMediaThreshold = std::vector<float>{ 0.5f };
	// sandbox parameters
	std::vector<float> awesomeParameter = std::vector<float>{ 1.0f };


    /// print fx parameters (DEBUG)
    void dPrint() {
        cout << "Saturation -> " << saturation[0] << endl;
        cout << "Contrast -> " << contrast[0] << endl;
        cout << "Brightness -> " << brightness[0] << endl;
        // TODO: SWITCH
        if (false) {
        // watercolor parameters
            cout << "Bleeding threshold ->" << bleedingThreshold[0] << endl;
            cout << "Bleeding radius ->" << bleedingRadius[0] << endl;
            cout << "Bleeding weigths -> [ ";
            for (int x = 0; x <= bleedingRadius[0] * 2; x++) {
                cout << bleedingWeigths[x] << ", ";
            }
            cout << "]" << endl;
            cout << "Edge darkening intensity -> " << edgeDarkeningIntensity[0] << endl;
            cout << "Edge darkening width -> " << edgeDarkeningWidth[0] << endl;
            cout << "Gaps and Overlaps width -> " << gapsOverlapsWidth[0] << endl;
            cout << "Pigment density -> " << pigmentDensity[0] << endl;
            cout << "Dry brush threshold -> " << dryBrushThreshold[0] << endl;
        }
        else {
            // oil paint parameters
            cout << "Paint stroke length ->" << opColorSmoothing[0] << endl;
            cout << "Paint stroke width ->" << opSTSmoothing[0] << endl;
            cout << "Paint stroke fidelity ->" << opPaintStrokeFidelity[0] << endl;
            cout << "Texture bump scale ->" << opBumpScale[0] << endl;
            cout << "Texture brush scale ->" << opBrushScale[0] << endl;
            cout << "Texture micro brush ->" << opBrushMicro[0] << endl;
        }
    }
};



///////////////////////////////////////////////////////////////////////////////////
//
//                             _     _
//     _____   _____ _ __ _ __(_) __| | ___
//    / _ \ \ / / _ \ '__| '__| |/ _` |/ _ \
//   | (_) \ V /  __/ |  | |  | | (_| |  __/
//    \___/ \_/ \___|_|  |_|  |_|\__,_|\___|
//
//	\brief MNPR render override using VP2.0
//  Instances of this class enable to create a custom render loop and operations
///////////////////////////////////////////////////////////////////////////////////
class MNPROverride : public MHWRender::MRenderOverride {
public:
    MNPROverride(const MString& name, const MString& uiName);
    virtual ~MNPROverride();

    // OVERRIDEN METHODS
    virtual MStatus setup(const MString & destPanel);  ///< sets the render loop
    virtual MStatus cleanup();                         ///< cleans up for the next frame
    MString uiName() const;							   ///< get renderer name (in renderer menu in the viewport panel)
    MHWRender::DrawAPI supportedDrawAPIs() const;      ///< sets the supported graphics API

    // additional methods that could be overriden
    virtual bool startOperationIterator();                   ///< starts operations
    virtual MHWRender::MRenderOperation* renderOperation();  ///< gets current render operation
    virtual bool nextRenderOperation();                      ///< increases the render operation

    // GET
    FXParameters* effectParams();												///< get fx parameters
    EngineSettings* engineSettings();											///< get engine settings
    MStringArray renderTargets();											///< get render targets
    MStringArray renderOperations();										///< get operation names
    MHWRender::MRenderOperation* renderOperation(MString t_operationName);  ///< get individual operation

    // CUSTOM
    virtual void initializeMNPR();                                    ///< MNPR initializer
    virtual MStatus addCustomTargets();                               ///< adds custom render targets to MNPR
    virtual MStatus addCustomRenderOperations();                            ///< adds custom render operations to MNPR
    virtual void resetShaderInstances(int operationIndex = -1);       ///< reset shader instances (reload)
    virtual void changeColorDepth();								  ///< change color depth of render targets
    virtual void changeAntialiasingEffect();						  ///< change antialiasing quality of targets
    virtual void changeMSAA(unsigned int t_MSAA);					  ///< change MSAA of targets
    virtual void changeActiveTarget(unsigned int activeTargetIndex);  ///< change active present target
    virtual void debugOperation(float r, float g, float b, float a);  ///< change debugging channels
    virtual void debugColorTransform(float mode);                     ///< change the mode of color transformation
    virtual void refreshTargets();									  ///< refresh targets
    virtual void setPlugin(MObject& plugin);                          ///< stores the MObject of the plugin
    virtual void resetStylization();

protected:
    friend class Cmd;
    friend class mnpr_node;

    // MAYA VP2.0 POINTERS
    MHWRender::MRenderer* renderer;
    MHWRender::MTextureManager* texManager;
    const MHWRender::MShaderManager* shaderMgr;
    const MHWRender::MRenderTargetManager* targetManager;
    const MHWRender::MFrameContext* frameContext;

    // OPERATION POINTERS
    QuadRender* quadOp = nullptr;
    SceneRender* sceneOp = nullptr;
    MOperationShader* opShader = nullptr;

    // ANIMATION TRACKERS
    float timeMs;              ///< time in milliseconds (timeline)
    float prevTimeMs;          ///< previously tracked time in milliseconds (timeline)
    MAnimControl animControl;  ///< anim control (timeline)

    // ENGINE VARIABLES
    MObject mPlugin;
    MString mRendererName;			   ///< renderer name (in renderer menu in the viewport panel)
    MString mnprInfo;				   ///< MNPR information
	int mCurRenderOperation;		   ///< current render operations
	MHWRender::MRenderOperationList mRenderOperations;	///< render operations
	MRenderTargetList mRenderTargets;  ///< render target list
    FXParameters mFxParams;                ///< fx attributes
    EngineSettings mEngSettings;		   ///< engine settings
    bool mTargetUpdate = true;		   ///< force target update
    static MHWRender::MRasterFormat colorDepths[3];

    // ENGINE FUNCTIONS
    MStatus mCheckMayaPointers();									 ///< update internal maya pointers
    void mInsertShaderPath();										 ///< insert shader path
    MStatus mUpdateRenderer();										 ///< update the renderer (runs every frame)

    // DEBUG METHODS
    void dPrintOperations(MHWRender::MRenderOperationList& opsList);  ///< print operations (DEBUG)
    void dPrintTargets(MRenderTargetList& targetList);				  ///< print targets (DEBUG)
};
