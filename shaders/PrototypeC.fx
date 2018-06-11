//PrototypeC (Watercolor shader)
//by Santiago Montesdeoca
//11 JAN - present

#define PI 3.1415926
#define SMAX 99999

/*******************************************/
/***************** INCLUDES ****************/
/*******************************************/

//#include "include\\filteringSolidGaborNoise.fxh"

/*******************************************/
/************* MAYA paremeters *************/
/*******************************************/



/************* State *************/
//defines how to render
//default solid witout culling
RasterizerState DisableCulling {
	CullMode = NONE;
};

//for wireframe technique
RasterizerState WireframeCullFront {
		CullMode = Front;
		FillMode = WIREFRAME;
};

/************* Samplers *************/
//how textures will be sampled
//texture sampler
SamplerState ColorSampler {
	Filter = ANISOTROPIC;
	Filter = MIN_MAG_MIP_LINEAR; //ENABLE FOR PERFORMANCE
	AddressU = WRAP;
	AddressV = WRAP;
};
//shadow sampler???                                                                     ***
SamplerState SamplerShadowDepth {
	Filter = MIN_MAG_MIP_LINEAR;
	AddressU = Border;
	AddressV = Border;
	BorderColor = float4(1.0f, 1.0f, 1.0f, 1.0f);
};


/*******************************************************************************/
//
//  888888888888
//       88                                  ,d
//       88                                  88
//       88        ,adPPYba,  8b,     ,d8  MM88MMM  88       88  8b,dPPYba,   ,adPPYba,  ,adPPYba,
//       88       a8P_____88   `Y8, ,8P'     88     88       88  88P'   "Y8  a8P_____88  I8[    ""
//       88       8PP"""""""     )888(       88     88       88  88          8PP"""""""   `"Y8ba,
//       88       "8b,   ,aa   ,d8" "8b,     88,    "8a,   ,a88  88          "8b,   ,aa  aa    ]8I
//       88        `"Ybbd8"'  8P'     `Y8    "Y888   `"YbbdP'Y8  88           `"Ybbd8"'  `"YbbdP"'
//
/*******************************************************************************/
//defines texture attributes
Texture2D _MainTex : DIFFUSE <
	string UIGroup = "Shading";
	string UIWidget = "FilePicker";
	string ResourceName = "";
	string UIName =  "Color Texture File";
	string ResourceType = "2D";
	int UIOrder = 5;
	int UVEditorOrder = 1;
>;

Texture2D _NormalTex <
	string UIGroup = "Shading";
	string UIWidget = "FilePicker";
	string ResourceName = "";
	string UIName =  "Normal Map File";
	string ResourceType = "2D";
	int UIOrder = 20;
	int UVEditorOrder = 3;
>;

Texture2D _SpecTex <
	string UIGroup = "Shading";
	string UIWidget = "FilePicker";
	string ResourceName = "";
	string UIName =  "Specular Map File";
	string ResourceType = "2D";
	int UIOrder = 35;
	int UVEditorOrder = 2;
>;


/************* Shadow Maps *************/
// Shadow Maps
Texture2D light0ShadowMap : SHADOWMAP
<
	string Object = "Light 0";	// UI Group for lights, auto-closed
	string UIWidget = "None";
	int UIOrder = 5010;
>;

Texture2D light1ShadowMap : SHADOWMAP
<
	string Object = "Light 1";
	string UIWidget = "None";
	int UIOrder = 5020;
>;

Texture2D light2ShadowMap : SHADOWMAP
<
	string Object = "Light 2";
	string UIWidget = "None";
	int UIOrder = 5030;
>;
//

/************* Internal depth textures for Maya depth-peeling transparency *************/
//TODO: CHECK HOW EXACTLY THESE WORK
Texture2D transpDepthTexture : transpdepthtexture < string UIWidget = "None"; >;

Texture2D opaqueDepthTexture : opaquedepthtexture < string UIWidget = "None"; >;



/*******************************************************************************/
//
//  88888888888
//  88
//  88
//  88aaaaa      8b,dPPYba,  ,adPPYYba,  88,dPYba,,adPYba,    ,adPPYba,
//  88"""""      88P'   "Y8  ""     `Y8  88P'   "88"    "8a  a8P_____88
//  88           88          ,adPPPPP88  88      88      88  8PP"""""""
//  88           88          88,    ,88  88      88      88  "8b,   ,aa
//  88           88          `"8bbdP"Y8  88      88      88   `"Ybbd8"'
//
/*******************************************************************************/
cbuffer UpdatePerFrame : register(b0) {
	//MATRICES (provided by maya)
	float4x4 VIEWINV 		: ViewInverse 			< string UIWidget = "None"; >;
	float4x4 VIEW			: View					< string UIWidget = "None"; >;
	float4x4 PRJ			: Projection			< string UIWidget = "None"; >;
	float4x4 VIEWPRJ		: ViewProjection		< string UIWidget = "None"; >;
	float2 gScreenSize      : ViewportPixelSize     < string UIWidget = "None"; >;
	static float2 gTexel = 1.0f / gScreenSize;

	// If the user enables viewport gamma correction in Maya's global viewport rendering settings, the shader should not do gamma again
	bool MayaFullScreenGamma: MayaGammaCorrection < string UIWidget = "None"; > = false;
	bool IsSwatchRender : MayaSwatchRender          < string UIWidget = "None"; > = false;
	float gTimer            : TIME < string UIWidget = "None"; >;

	float3 _AtmosphereColor <
		string UIGroup = "LOD";
		string UIName =  "Atmosphere Color";
		string UIWidget = "Color";
		int UIOrder = 200;
	> = {1.0f, 1.0f, 1.0f};

	float _RangeStart <
		string UIGroup = "LOD";
		string UIName =  "Atmosphere Start";
		string UIWidget = "slider";
		float UIMin = 1.0;
		float UIMax = 50000.0;
		float UIStep = 1.0;
		int UIOrder = 205;
	> = {50.0f};

	float _RangeEnd <
		string UIGroup = "LOD";
		string UIName =  "Atmosphere End";
		string UIWidget = "slider";
		float UIMin = 1.0;
		float UIMax = 50000.0;
		float UIStep = 1.0;
		int UIOrder = 210;
	> = {200.0f};
}


/*******************************************************************************/
//
//    ,ad8888ba,    88              88
//   d8"'    `"8b   88              ""                            ,d
//  d8'        `8b  88                                            88
//  88          88  88,dPPYba,      88   ,adPPYba,   ,adPPYba,  MM88MMM
//  88          88  88P'    "8a     88  a8P_____88  a8"     ""    88
//  Y8,        ,8P  88       d8     88  8PP"""""""  8b            88
//   Y8a.    .a8P   88b,   ,a8"     88  "8b,   ,aa  "8a,   ,aa    88,
//    `"Y8888Y"'    8Y"Ybbd8"'      88   `"Ybbd8"'   `"Ybbd8"'    "Y888
//                                 ,88
/*******************************************************************************/
cbuffer UpdatePerObject : register(b1) {
	// MATRICES
	float4x4 WORLD 		: World 					< string UIWidget = "None"; >;
	float4x4 WORLDIT 	: WorldInverseTranspose 	< string UIWidget = "None"; >;
	float4x4 WVP		: WorldViewProjection		< string UIWidget = "None"; >;

    // CONTROL
    bool _UseControl < string UIWidget = "None"; > = true;


	//             88                                88  88
	//             88                                88  ""
	//             88                                88
	//  ,adPPYba,  88,dPPYba,   ,adPPYYba,   ,adPPYb,88  88  8b,dPPYba,    ,adPPYb,d8
	//  I8[    ""  88P'    "8a  ""     `Y8  a8"    `Y88  88  88P'   `"8a  a8"    `Y88
	//   `"Y8ba,   88       88  ,adPPPPP88  8b       88  88  88       88  8b       88
	//  aa    ]8I  88       88  88,    ,88  "8a,   ,d88  88  88       88  "8a,   ,d88
	//  `"YbbdP"'  88       88  `"8bbdP"Y8   `"8bbdP"Y8  88  88       88   `"YbbdP"Y8
	//                                                                     aa,    ,88
	//                                                                      "Y8bbdP"
	// ---------------------------------------------
	// Basic Shading Group
	// ---------------------------------------------
	bool _UseColorTexture <
		string UIGroup = "Shading";
		string UIName = "Color Texture";
		int UIOrder = 1;
	> = false;

	float3 _ColorTint : COLOR <
		string UIGroup = "Shading";
		string UIName =  "Color Tint";
		string UIWidget = "Color";
		int UIOrder = 10;
	> = {1.0f, 1.0f, 1.0f};

	// ---------------------------------------------
	// Normal Group
	// ---------------------------------------------
	bool _UseNormalTexture <
		string UIGroup = "Shading";
		string UIName = "Normal Map";
		int UIOrder = 15;
	> = false;

	bool _FlipU <
		string UIGroup = "Shading";
		string UIName = "Flip U";
		int UIOrder = 23;
	> = false;

	bool _FlipV <
		string UIGroup = "Shading";
		string UIName = "Flip V";
		int UIOrder = 24;
	> = false;

	float _BumpDepth <
		string UIGroup = "Shading";
		string UIName = "Bump Depth";
		string UIWidget = "slider";
		float UIMin = -2.0;
		float UIMax = 2.0;
		float UIStep = 0.1;
		int UIOrder = 25;
	> = {1.0f};

	// ---------------------------------------------
	// Specular GROUP
	// ---------------------------------------------
	bool _UseSpecularTexture <
		string UIGroup = "Shading";
		string UIName = "Specular Map";
		int UIOrder = 30;
	> = false;

	float _Specular <
		string UIGroup = "Shading";
		string UIName =  "Specular Roll Off";
		string UIWidget = "slider";
		float UIMin = 0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 40;
	> = {0.0f};

	float _SpecDiffusion <
		string UIGroup = "Shading";
		string UIName = "Specular Diffussion";
		string UIWidget = "slider";
		float UIMin = 0;
		float UIMax = 0.99;
		float UIStep = 0.05;
		int UIOrder = 45;
	> = {0.0f};

	float _SpecTransparency <
		string UIGroup = "Shading";
		string UIName = "Specular Transparency";
		string UIWidget = "slider";
		float UIMin = 0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 50;
	> = {0.0f};



	// ---------------------------------------------
	// Shade GROUP
	// ---------------------------------------------
	bool _UseShadows <
		string UIGroup = "Shading";
		string UIName = "Shadows";
		int UIOrder = 60;
	> = true;

	// This offset allows you to fix any in-correct self shadowing caused by limited precision.
	// This tends to get affected by scene scale and polygon count of the objects involved.
	float _ShadowDepthBias : ShadowMapBias <
		string UIGroup = "Shading";
		string UIWidget = "Slider";
		float UIMin = 0.000;
		float UISoftMax = 10.000;
		float UIStep = 0.0001;
		string UIName = "Shadow Bias";
		int UIOrder = 65;
	> = {0.001f};


	//                           88                                                88
	//                           ""                 ,d                             88
	//                                              88                             88
	//  8b,dPPYba,   ,adPPYYba,  88  8b,dPPYba,   MM88MMM   ,adPPYba,  8b,dPPYba,  88  8b       d8
	//  88P'    "8a  ""     `Y8  88  88P'   `"8a    88     a8P_____88  88P'   "Y8  88  `8b     d8'
	//  88       d8  ,adPPPPP88  88  88       88    88     8PP"""""""  88          88   `8b   d8'
	//  88b,   ,a8"  88,    ,88  88  88       88    88,    "8b,   ,aa  88          88    `8b,d8'
	//  88`YbbdP"'   `"8bbdP"Y8  88  88       88    "Y888   `"Ybbd8"'  88          88      Y88'
	//  88                                                                                 d8'
	//  88
	// ---------------------------------------------
	// Painterly shading GROUP
	// ---------------------------------------------
	float _DiffuseFactor : DFACTOR <
		string UIGroup = "Painterly Shading";
		string UIName =  "Diffuse Factor";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 100;
	> = {0.2f};

	float3 _ShadeColor <
		string UIGroup = "Painterly Shading";
		string UIName =  "Shade Color";
		string UIWidget = "Color";
		int UIOrder = 105;
	> = {0.0f, 0.0f, 0.0f};

	float _ShadeWrap <
		string UIGroup = "Painterly Shading";
		string UIName =  "Shade Wrap";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 110;
	> = {0.0f};

	bool _UseOverrideShade <
		string UIGroup = "Painterly Shading";
		string UIName = "Shade Override";
		int UIOrder = 115;
	> = true;

	float _Dilute <
		string UIGroup = "Painterly Shading";
		string UIName =  "Dilute Paint";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 120;
	> = {0.8f};

	float _Cangiante <
		string UIGroup = "Painterly Shading";
		string UIName =  "Cangiante";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 125;
	> = {0.2f};

	float _DiluteArea <
		string UIGroup = "Painterly Shading";
		string UIName =  "Dilute Area";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 130;
	> = {1.0f};

	float _HighArea <
		string UIGroup = "Painterly Shading";
		string UIName =  "Highlight Area";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 0.5;
		float UIStep = 0.05;
		int UIOrder = 135;
	> = {0.0f};

	float _HighTransparency <
		string UIGroup = "Painterly Shading";
		string UIName =  "Highlight Transparency";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 140;
	> = {0.0f};

	//                             ,d
	//                             88
	//   ,adPPYba,  8b,     ,d8  MM88MMM  8b,dPPYba,  ,adPPYYba,
	//  a8P_____88   `Y8, ,8P'     88     88P'   "Y8  ""     `Y8
	//  8PP"""""""     )888(       88     88          ,adPPPPP88
	//  "8b,   ,aa   ,d8" "8b,     88,    88          88,    ,88
	//   `"Ybbd8"'  8P'     `Y8    "Y888  88          `"8bbdP"Y8
	//
	// ---------------------------------------------
	// Additional Object-space effects
	// ---------------------------------------------
	float _DarkEdges <
		string Object = "Additional object-space effects";	// UI Group for auto-closed
		string UIName =  "Darkened Edge";
		string UIWidget = "slider";
		float UIMin = 0.0;
		float UIMax = 1.0;
		float UIStep = 0.05;
		int UIOrder = 300;
	> = {0.0f};

	// ---------------------------------------------
	// Hand Tremor GROUP
	// ---------------------------------------------
	float _Tremor <
		bool SasUiVisible = false;
	> = {4.0f};

	float _TremorFront <
		bool SasUiVisible = false;
	> = {0.4f};

	float _TremorSpeed <
		bool SasUiVisible = false;
	> = {10.0f};

	float _TremorFreq <
		bool SasUiVisible = false;
	> = {10.0f};

	// ---------------------------------------------
	// Paper Color
	// ---------------------------------------------
	float3 _PaperColor <
		bool SasUiVisible = false;
	> = {1.0f, 1.0f, 1.0f};

	float _BleedOffset <
		bool SasUiVisible = false;
	> = {0.5f};

    // ---------------------------------------------
    // Gabor Noise
    // ---------------------------------------------
    /*
    float _GaborNoiseScale <
        string Object = "Gabor noise";
        string UIName = "Gabor noise scale";
        string UIWidget = "slider";
        float UIMin = 0.0001;
        float UIMax = 100.0;
        float UIStep = 0.0001;
    > = { 1.0f };

    float _GaborNoiseLambda <
        string Object = "Gabor noise";
        string UIName = "Gabor noise lambda";
        string UIWidget = "slider";
        float UIMin = 0.0;
        float UIMax = 1.0;
        float UIStep = 0.001;
    > = { 0.035f };

    float _GaborNoiseR <
        string Object = "Gabor noise";
        string UIName = "Gabor noise r";
        string UIWidget = "slider";
        float UIMin = 0.0;
        float UIMax = 100.0;
        float UIStep = 0.001;
    > = { 5.9f };

    int _GaborNoiseSeed <
        string Object = "Gabor noise";
        string UIName = "Gabor noise seed";
        string UIWidget = "slider";
        float UIMin = 0;
        float UIMax = 99999;
    > = { 1234 }; 

    float3 _GaborNoiseOmega <
        string Object = "Gabor noise";
        string UIName = "Gabor noise omega";
        string UIWidget = "slider";
        float UIMin = 0.0;
        float UIMax = 10.0;
        float UIStep = 0.01;
    > = { 0.22325f, 0.0f, 0.0f };

    float _GaborNoiseA <
        string Object = "Gabor noise";
        string UIName = "Gabor noise A";
        string UIWidget = "slider";
        float UIMin = 0.0;
        float UIMax = 100.0;
        float UIStep = 0.001;
    > = { 0.188f };

    int _GaborNoiseType <
        string Object = "Gabor noise";
        string UIName = "Gabor noise type";
        string UIWidget = "slider";
        float UIMin = 0;
        float UIMax = 2;
    > = { 1 }; // isotropic

    bool _GaborNoiseFilter <
        string Object = "Gabor noise";
        string UIName = "Gabor noise filter";
    > = false;
    */

}


/*******************************************************************************/
//
//  88           88               88
//  88           ""               88             ,d
//  88                            88             88
//  88           88   ,adPPYb,d8  88,dPPYba,   MM88MMM  ,adPPYba,
//  88           88  a8"    `Y88  88P'    "8a    88     I8[    ""
//  88           88  8b       88  88       88    88      `"Y8ba,
//  88           88  "8a,   ,d88  88       88    88,    aa    ]8I
//  88888888888  88   `"YbbdP"Y8  88       88    "Y888  `"YbbdP"'
//                    aa,    ,88
//                     "Y8bbdP"
//
/*******************************************************************************/
// for auto-binding done in Maya
cbuffer UpdateLights : register(b2) {
	// ---------------------------------------------
	// Light 0 GROUP
	// ---------------------------------------------
	// This value is controlled by Maya to tell us if a light should be calculated
	// For example the artist may disable a light in the scene, or choose to see only the selected light
	// This flag allows Maya to tell our shader not to contribute this light into the lighting
	bool light0Enable : LIGHTENABLE <
		string Object = "Light 0";	// UI Group for lights, auto-closed
		string UIName = "Enable Light 0";
		int UIOrder = 500;
	> = false;	// maya manages lights itself and defaults to no lights

	// follows LightParameterInfo::ELightType
	// spot = 2, point = 3, directional = 4, ambient = 5,
	int light0Type : LIGHTTYPE <
		string Object = "Light 0";
		string UIName = "Light 0 Type";
		string UIFieldNames ="None:Default:Spot:Point:Directional:Ambient";
		int UIOrder = 501;
		float UIMin = 0;
		float UIMax = 5;
		float UIStep = 1;
	> = 2;	// default to spot so the cone angle etc work when "Use Shader Settings" option is used

	float3 light0Pos : POSITION <
		string Object = "Light 0";
		string UIName = "Light 0 Position";
		string Space = "World";
		int UIOrder = 502;
	> = {100.0f, 100.0f, 100.0f};

	float3 light0Color : LIGHTCOLOR <
		string Object = "Light 0";
		string UIName = "Light 0 Color";
		string UIWidget = "Color";
		int UIOrder = 503;
	> = { 1.0f, 1.0f, 1.0f};

	float light0Intensity : LIGHTINTENSITY <
		string Object = "Light 0";
		string UIName = "Light 0 Intensity";
		float UIMin = 0.0;
		float UIMax = SMAX;
		float UIStep = 0.01;
		int UIOrder = 504;
	> = { 1.0f };

	float3 light0Dir : DIRECTION <
		string Object = "Light 0";
		string UIName = "Light 0 Direction";
		string Space = "World";
		int UIOrder = 505;
	> = {100.0f, 100.0f, 100.0f};

	float light0ConeAngle : HOTSPOT < // In radians
		string Object = "Light 0";
		string UIName = "Light 0 Cone Angle";
		float UIMin = 0;
		float UIMax = PI/2;
		int UIOrder = 506;
	> = { 0.46f };

	float light0FallOff : FALLOFF <// In radians. Sould be HIGHER then cone angle or lighted area will invert
		string Object = "Light 0";
		string UIName = "Light 0 Penumbra Angle";
		float UIMin = 0;
		float UIMax = PI/2;
		int UIOrder = 507;
	> = { 0.7f };

	float light0AttenScale : DECAYRATE <
		string Object = "Light 0";
		string UIName = "Light 0 Decay";
		float UIMin = 0.0;
		float UIMax = SMAX;
		float UIStep = 0.01;
		int UIOrder = 508;
	> = {0.0};

	bool light0ShadowOn : SHADOWFLAG <
		string Object = "Light 0";
		string UIName = "Light 0 Casts Shadow";
		string UIWidget = "None";
		int UIOrder = 509;
	> = true;

	bool light0Specular : LIGHTSPECULAR <
		string Object = "Light 0";
		string UIName = "Light 0 Specular";
		int UIOrder = 510;
	> = 1;

	float4x4 light0Matrix : SHADOWMAPMATRIX	<
		string Object = "Light 0";
		string UIWidget = "None";
		int UIOrder = 511;
	>;


// ---------------------------------------------
	// Light 1 GROUP
	// ---------------------------------------------
	bool light1Enable : LIGHTENABLE <
		string Object = "Light 1";
		string UIName = "Enable Light 1";
		int UIOrder = 520;
	> = false;

	int light1Type : LIGHTTYPE <
		string Object = "Light 1";
		string UIName = "Light 1 Type";
		string UIFieldNames ="None:Default:Spot:Point:Directional:Ambient";
		float UIMin = 0;
		float UIMax = 5;
		int UIOrder = 521;
	> = 2;

	float3 light1Pos : POSITION <
		string Object = "Light 1";
		string UIName = "Light 1 Position";
		string Space = "World";
		int UIOrder = 522;
	> = {-100.0f, 100.0f, 100.0f};

	float3 light1Color : LIGHTCOLOR <
		string Object = "Light 1";
		string UIName = "Light 1 Color";
		string UIWidget = "Color";
		int UIOrder = 523;
	> = { 1.0f, 1.0f, 1.0f};

	float light1Intensity : LIGHTINTENSITY <
			string Object = "Light 1";
			string UIName = "Light 1 Intensity";
			float UIMin = 0.0;
			float UIMax = SMAX;
			float UIStep = 0.01;
			int UIOrder = 524;
	> = { 1.0f };

	float3 light1Dir : DIRECTION <
		string Object = "Light 1";
		string UIName = "Light 1 Direction";
		string Space = "World";
		int UIOrder = 525;
	> = {100.0f, 100.0f, 100.0f};

	float light1ConeAngle : HOTSPOT <// In radians
		string Object = "Light 1";
		string UIName = "Light 1 Cone Angle";
		float UIMin = 0;
		float UIMax = PI/2;
		int UIOrder = 526;
	> = { 45.0f };


	float light1FallOff : FALLOFF <// In radians. Sould be HIGHER then cone angle or lighted area will invert
		string Object = "Light 1";
		string UIName = "Light 1 Penumbra Angle";
		float UIMin = 0;
		float UIMax = PI/2;
		int UIOrder = 527;
	> = { 0.0f };

	float light1AttenScale : DECAYRATE <
		string Object = "Light 1";
		string UIName = "Light 1 Decay";
		float UIMin = 0.0;
		float UIMax = SMAX;
		float UIStep = 0.01;
		int UIOrder = 528;
	> = {0.0};

	bool light1ShadowOn : SHADOWFLAG <
		string Object = "Light 1";
		string UIName = "Light 1 Casts Shadow";
		string UIWidget = "None";
		int UIOrder = 529;
	> = true;

	float4x4 light1Matrix : SHADOWMAPMATRIX	<
		string Object = "Light 1";
		string UIWidget = "None";
		int UIOrder = 530;
	>;


	// ---------------------------------------------
	// Light 2 GROUP
	// ---------------------------------------------
	bool light2Enable : LIGHTENABLE <
		string Object = "Light 2";
		string UIName = "Enable Light 2";
		int UIOrder = 550;
	> = false;

	int light2Type : LIGHTTYPE <
		string Object = "Light 2";
		string UIName = "Light 2 Type";
		string UIFieldNames ="None:Default:Spot:Point:Directional:Ambient";
		float UIMin = 0;
		float UIMax = 5;
		int UIOrder = 551;
	> = 2;

	float3 light2Pos : POSITION <
		string Object = "Light 2";
		string UIName = "Light 2 Position";
		string Space = "World";
		int UIOrder = 552;
	> = {100.0f, 100.0f, -100.0f};

	float3 light2Color : LIGHTCOLOR <
		string Object = "Light 2";
		string UIName = "Light 2 Color";
		string UIWidget = "Color";
		int UIOrder = 553;
	> = { 1.0f, 1.0f, 1.0f};

	float light2Intensity : LIGHTINTENSITY <
		string Object = "Light 2";
		string UIName = "Light 2 Intensity";
		float UIMin = 0.0;
		float UIMax = SMAX;
		float UIStep = 0.01;
		int UIOrder = 554;
	> = { 1.0f };

	float3 light2Dir : DIRECTION <
		string Object = "Light 2";
		string UIName = "Light 2 Direction";
		string Space = "World";
		int UIOrder = 555;
	> = {100.0f, 100.0f, 100.0f};

	float light2ConeAngle : HOTSPOT <// In radians
		string Object = "Light 2";
		string UIName = "Light 2 Cone Angle";
		float UIMin = 0;
		float UIMax = PI/2;
		int UIOrder = 556;
	> = { 45.0f };

	float light2FallOff : FALLOFF <// In radians. Sould be HIGHER then cone angle or lighted area will invert
		string Object = "Light 2";
		string UIName = "Light 2 Penumbra Angle";
		float UIMin = 0;
		float UIMax = PI/2;
		int UIOrder = 557;
	> = { 0.0f };

	float light2AttenScale : DECAYRATE <
		string Object = "Light 2";
		string UIName = "Light 2 Decay";
		float UIMin = 0.0;
		float UIMax = SMAX;
		float UIStep = 0.01;
		int UIOrder = 558;
	> = {0.0};

	bool light2ShadowOn : SHADOWFLAG <
		string Object = "Light 2";
		string UIName = "Light 2 Casts Shadow";
		string UIWidget = "None";
		int UIOrder = 559;
	> = true;

	float4x4 light2Matrix : SHADOWMAPMATRIX	<
		string Object = "Light 2";
		string UIWidget = "None";
		int UIOrder = 660;
	>;

}


/*******************************************************************************/
//               ,d                                            ,d
//               88                                            88
//  ,adPPYba,  MM88MMM  8b,dPPYba,  88       88   ,adPPYba,  MM88MMM  ,adPPYba,
//  I8[    ""    88     88P'   "Y8  88       88  a8"     ""    88     I8[    ""
//   `"Y8ba,     88     88          88       88  8b            88      `"Y8ba,
//  aa    ]8I    88,    88          "8a,   ,a88  "8a,   ,aa    88,    aa    ]8I
//  `"YbbdP"'    "Y888  88           `"YbbdP'Y8   `"Ybbd8"'    "Y888  `"YbbdP"'
//
/*******************************************************************************/
struct appData {
	float3 vertex 		: POSITION;
	float2 texcoord 	: TEXCOORD;
	float4 vColor0      : COLOR0;
	float4 vColor1		: COLOR1;
	float4 vColor2		: COLOR2;
	float4 vColor3		: COLOR3;
	float3 normal		: NORMAL;
	float3 binormal		: BINORMAL;
	float4 tangent		: TANGENT;
};

struct vertexOutput {
	float4 vColor0 : COLOR0;
	float4 vColor1 : COLOR1;
	float4 vColor2 : COLOR2;
    float4 vPreviousScreenPosition : COLOR3;
	float4 pos : SV_POSITION;
	float3 posWorld : TEXCOORD0;
	float3 normalWorld : NORMAL;
	float3 tangentWorld : TANGENT;
	float3 binormalWorld : TEXCOORD1;
	float3 lightDir : TEXCOORD2;
	float3 viewDir : TEXCOORD3;
	float3 velocityDepth : TEXCOORD4;
	float2 tex : TEXCOORD5;
	float nDotV : TEXCOORD6;
};

// Output to 3 diferent targets
struct pixelShaderOutput {
	float4 colorOutput : SV_Target0;
    float4 diffuseOutput : SV_Target1;
    float4 specularOutput : SV_Target2;
	float4 pigmentCtrlOutput: SV_Target3;
    float4 substrateCtrlOutput: SV_Target4;
    float4 edgeCtrlOutput: SV_Target5;
    float4 abstractionCtrlOutput: SV_Target6;
    float2 velocityOutput: SV_Target7;
};


/*******************************************************************************/
//
//  88  88               88                    88
//  88  ""               88             ,d     ""
//  88                   88             88
//  88  88   ,adPPYb,d8  88,dPPYba,   MM88MMM  88  8b,dPPYba,    ,adPPYb,d8
//  88  88  a8"    `Y88  88P'    "8a    88     88  88P'   `"8a  a8"    `Y88
//  88  88  8b       88  88       88    88     88  88       88  8b       88
//  88  88  "8a,   ,d88  88       88    88,    88  88       88  "8a,   ,d88
//  88  88   `"YbbdP"Y8  88       88    "Y888  88  88       88   `"YbbdP"Y8
//           aa,    ,88                                          aa,    ,88
//            "Y8bbdP"                                            "Y8bbdP"
/*******************************************************************************/
// Spot light cone
float getLightConeAngle(float coneAngle, float coneFalloff, float3 lightVec, float3 lightDir)
{
	// the cone falloff should be equal or bigger then the coneAngle or the light inverts
	// this is added to make manually tweaking the spot settings easier.
	if (coneFalloff < coneAngle)
		coneFalloff = coneAngle;

	float LdotDir = dot(lightVec, lightDir);

	// cheaper cone, no fall-off control would be:
	// float cone = pow(saturate(LdotDir), 1 / coneAngle);

	// higher quality cone (more expensive):
	float cone = smoothstep( cos(coneFalloff), cos(coneAngle), LdotDir);

	return cone;
}

// ---------------------------------------------
// Shadows
// ---------------------------------------------
#define SHADOW_FILTER_TAPS_CNT 10
float2 SuperFilterTaps[SHADOW_FILTER_TAPS_CNT] < string UIWidget = "None"; > = {
	{-0.84052f, -0.073954f},
	{-0.326235f, -0.40583f},
	{-0.698464f, 0.457259f},
	{-0.203356f, 0.6205847f},
	{0.96345f, -0.194353f},
	{0.473434f, -0.480026f},
	{0.519454f, 0.767034f},
	{0.185461f, -0.8945231f},
	{0.507351f, 0.064963f},
	{-0.321932f, 0.5954349f}
};

float shadowMapTexelSize < string UIWidget = "None"; > = {0.00195313}; // (1.0f / 512)

// Percentage-Closer Filtering
// taken from AutodeskUberShader
float lightShadow(float4x4 LightViewPrj, uniform Texture2D ShadowMapTexture, float3 VertexWorldPosition, float nDotL) {
	float shadow = 1.0f;

	float4 Pndc = mul( float4(VertexWorldPosition.xyz,1.0) ,  LightViewPrj);
	Pndc.xyz /= Pndc.w; //divide by 1?
	if ( Pndc.x > -1.0f && Pndc.x < 1.0f && Pndc.y  > -1.0f && Pndc.y <  1.0f && Pndc.z >  0.0f && Pndc.z <  1.0f ) {
		float2 uv = 0.5f * Pndc.xy + 0.5f; //normalize UV [0-1]
		uv = float2(uv.x,(1.0-uv.y));	// maya flip Y
		float z = Pndc.z - _ShadowDepthBias / Pndc.w;

		// we'll sample a bunch of times to smooth our shadow a little bit around the edges:
		//shadow = 0.0f;
		//for(int i=0; i<SHADOW_FILTER_TAPS_CNT; ++i) {
			//float2 suv = uv + (SuperFilterTaps[i] * shadowMapTexelSize);
			//float val = z - ShadowMapTexture.SampleLevel(SamplerShadowDepth, suv, 0 ).x;
			//shadow += (val >= 0.0f) ? 0.0f : (1.0f / SHADOW_FILTER_TAPS_CNT);
		//}

		// a single sample would be:
		shadow = 1.0f;
		float shadowMapZ = ShadowMapTexture.Sample(SamplerShadowDepth, uv).x;
		float val = z - shadowMapZ;
		//float val = z - ShadowMapTexture.SampleLevel(SamplerShadowDepth, uv, 0 ).x; //in case we use mip maps
		shadow = (val >= 0.0f)? 0.0f : 1.0f; // 1 -> shadow
		shadow = shadow + ceil(-nDotL);
		//shadow = lerp(1.0f, shadow, _ShadowMultiplier);
	}
	return shadow;
	//return Pndc.y;
}


// ---------------------------------------------
// Lighting
// ---------------------------------------------
struct lightOut {
	float3 specular;
	float3 color;
	float3 dilute;
	float shade;
};

lightOut calculateLight	(	bool lightEnable, int lightType, float lightAtten, float3 lightPos, float3 vertWorldPos,
							float3 lightColor, float lightIntensity, float3 lightDir, float lightConeAngle, float lightFallOff, float4x4 lightViewPrjMatrix,
							uniform Texture2D lightShadowMap, bool lightShadowOn, float3 normalWorld, float diffuseArea, float diffuseFactor, float diluteArea,
							float specular, float specDiffusion, float specTransparency, float3 viewDir, float depth) {
	lightOut L = (lightOut)0;
	L.specular = 0.0;
	L.color = float3(0,0,0);
	L.dilute = 0.0;


	if(lightEnable){
		//for Maya, flip the lightDir (weird)
		lightDir = -lightDir;
		//spot = 2, point = 3, directional = 4, ambient = 5,

		//ambient light
		//-> no diffuse, specular or shadow casting
		if (lightType == 5){
			L.color = lightColor * lightIntensity;
			return L;
		}

		//directional light -> no position
		bool isDirectionalLight = (lightType == 4);
		float3 lightVec = lerp(lightPos - vertWorldPos, lightDir, isDirectionalLight);
		float3 nLightVec = normalize(lightVec); //normalized light vector

		//diffuse
		//dot product
		float nDotL = dot(normalWorld, nLightVec);

		//Wrapped Lambert
		//Derived from half lambert, presents problems with shadow mapping
		//float WL = diffuseArea + (1-diffuseArea) * nDotL;
		float dotMask = saturate(nDotL);
		float DF = lerp(1,dotMask, _DiffuseFactor); //diffuse factor
		float SW = lerp(0,saturate(-nDotL), _ShadeWrap); //shade wrap
		float CL = saturate(DF*(1-SW)); //custom lambert
		float3 diffuseColor = lightColor * lightIntensity * CL; //diffuse reflectance (lambert)

		//dilute area
		float3 diluted = saturate((dotMask+(diluteArea-1))/diluteArea);

		//specular (Phong)
		float3 specularColor = 0;
		if(_Specular){
			float rDotV = dot(reflect(nLightVec, normalWorld),-viewDir);
			float specularEdge = _DarkEdges * (saturate(((1-specular)-rDotV)*200/depth)-1); //darkened edge mask
			specularColor = (lerp(specularEdge,0,specDiffusion) + 2*saturate((max(1-specular, rDotV)-(1-specular))*pow((2-specDiffusion),10)))*(1-specTransparency);
			specularColor *= saturate(dot(normalWorld, lightDir)*2);	// prevent spec leak on back side of model
		}


		//attenuation
		if (!isDirectionalLight){
			bool enableAttenuation = lightAtten > 0.0001f;
			float attenuation = lerp(1.0, 1 / pow(length(lightVec), lightAtten), enableAttenuation);
			//compensate diffuse and specular
			diffuseColor *= attenuation;
			specularColor *= attenuation;
		}

		// spot light Cone Angle
		if (lightType == 2) {
			float angle = getLightConeAngle(lightConeAngle, lightFallOff, nLightVec, lightDir);
			diffuseColor *= angle;
			specularColor *= angle;
		}



		// shadows

		//L.shade = 0.0;
		if (_UseShadows && lightShadowOn) {
			float shadow = lightShadow(lightViewPrjMatrix, lightShadowMap, vertWorldPos, nDotL);
			if(shadow<1){
				diffuseColor =  lightColor * lightIntensity * (1-diffuseFactor);
				L.shade = 1;
			}
			specularColor *= floor(shadow); //get rid of specular in the shade
		}


		//L.dilute = nDotL.xxx;
		//L.color = shadeColor;
		L.color = diffuseColor;
		L.specular = specularColor;
		L.dilute = diluted;
		//L.dilute = diffuseColor;
	}

	return L;
}

// velocity vector computation
float2 calculateVelocity(in float2 currentPos, in float2 previousPos, in float zOverW) {
    //if (zOverW == 1.0) {
    //    return float2(0.0, 0.0);
    //}

    // Use this frame's position and last frame's to compute the pixelvelocity.
    float2 velocity = (currentPos - previousPos) / 2.0;

    return 1.0 * velocity;
    //  step(0, abs(velocity)) * velocity * 1000.0;
}



/*******************************************************************************/
//
//                                         ,d
//                                         88
//  8b       d8   ,adPPYba,  8b,dPPYba,  MM88MMM   ,adPPYba,  8b,     ,d8
//  `8b     d8'  a8P_____88  88P'   "Y8    88     a8P_____88   `Y8, ,8P'
//   `8b   d8'   8PP"""""""  88            88     8PP"""""""     )888(
//    `8b,d8'    "8b,   ,aa  88            88,    "8b,   ,aa   ,d8" "8b,
//      "8"       `"Ybbd8"'  88            "Y888   `"Ybbd8"'  8P'     `Y8
//
/*******************************************************************************/
vertexOutput vs(appData v) {
	vertexOutput o = (vertexOutput)0;

	// vertex colors
	if (_UseControl){
		o.vColor0 = v.vColor0;
        o.vColor1 = v.vColor1;
        o.vColor2 = v.vColor2;
	} else {
	    o.vColor0 = float4(0,0,0,0);
        o.vColor1 = float4(0,0,0,0);
        o.vColor2 = float4(0,0,0,0);
	}

    o.vPreviousScreenPosition = v.vColor3;

	//TEXTURE
	o.tex = float2(v.texcoord.x, 1.0 - v.texcoord.y);

	//world position
	o.posWorld = mul(float4(v.vertex.xyz,1), WORLD).xyz; //use non-jittered pos

	//vectors from vertex 
	o.normalWorld = normalize(mul(float4(v.normal,0.0), WORLD).xyz);
	o.tangentWorld = normalize(mul(v.tangent, WORLD).xyz);
	o.binormalWorld = normalize(cross(o.normalWorld, o.tangentWorld));

	//view direction
	o.viewDir  = normalize(VIEWINV[3].xyz - o.posWorld);
	o.nDotV = dot(o.normalWorld, o.viewDir);

	//light direction
	o.lightDir = normalize(-light0Dir);

	//z-depth
	float depth = distance(o.posWorld, VIEWINV[3].xyz);

	//Return here if swatch render
	if (IsSwatchRender){
		o.pos = mul(float4(v.vertex.xyz,1.0), WVP);
		return o;
	}

	//////////////////////////////////////////////////////////////////////////
	//VERTEX DEFORMATIONS
	float3 newPos = v.vertex.xyz;

	//move vertex from bleed
	newPos += o.normalWorld*saturate(v.vColor2.a-0.7)*_BleedOffset;


	//determine tremor angle
	float angleTremor = min(saturate(o.nDotV*1.2),(1-_TremorFront));
	//hand tremor
	float4 pPos = mul(float4(newPos,1.0), WVP);
	float4 tremorPos = pPos+float4(sin(gTimer * (_TremorSpeed*100)  + v.vertex * (_TremorFreq*10)) * _Tremor * gTexel,0, 0);

	//lerp tremor according to angle
	o.pos = lerp(tremorPos,pPos,angleTremor);

    // velocity
    float2 velocity = calculateVelocity(o.pos.xy / o.pos.w, v.vColor3.xy, depth);

    o.velocityDepth = float3(velocity, depth);

	return o;
}





/*******************************************************************************/
//               88                           88
//               ""                           88
//                                            88
//  8b,dPPYba,   88  8b,     ,d8   ,adPPYba,  88
//  88P'    "8a  88   `Y8, ,8P'   a8P_____88  88
//  88       d8  88     )888(     8PP"""""""  88
//  88b,   ,a8"  88   ,d8" "8b,   "8b,   ,aa  88
//  88`YbbdP"'   88  8P'     `Y8   `"Ybbd8"'  88
//  88
//  88
/*******************************************************************************/
pixelShaderOutput psTextured(vertexOutput i, bool FrontFace : SV_IsFrontFace) : SV_Target {
	pixelShaderOutput result;

	float3 pixel = (float3)0;
	float transparency = 1.0f;

	float4 control1 = float4(i.vColor0.rgb, transparency);
	float4 control2 = float4(i.vColor1.rgb, transparency);
	float4 control3 = float4(i.vColor2.rgb, transparency);
	float4 control4 = float4(i.vColor0.a, i.vColor1.a, i.vColor2.a, transparency);

	//normal
	float3 normalWorld = normalize(i.normalWorld);

	//normal mapping
	if (_UseNormalTexture) {
		float3 tangentWorld = normalize(i.tangentWorld);
		float3 binormalWorld = normalize(i.binormalWorld);
		//Normal transpose matrix
		float3x3 local2WorldTranspose = float3x3(tangentWorld, binormalWorld, normalWorld);
		//Sample normal map
		float3 normalMap = _NormalTex.Sample(ColorSampler, i.tex).xyz * 2 - 1; //to transform float values to -1...1
		//adjust values
		if (_FlipU) {
			normalMap.r = -normalMap.r; //normal X is on the red channel
		}
		if (_FlipV) {
			normalMap.g = -normalMap.g; //normal y is on the green channel
		}
		//Calculate new normal direction
		normalMap.rg *= _BumpDepth;
		normalWorld = normalize(mul(normalMap, local2WorldTranspose));
	}

	//specular mapping
	float4 specularMap = float4(1.0f,1.0f,1.0f,1.0f);
	if (_UseSpecularTexture) {
		specularMap = _SpecTex.Sample(ColorSampler, i.tex);
	}

	//texture mapping
	float3 tex = _ColorTint;
	float grayscale = 1.0f;
	if (_UseColorTexture) {
		float4 sampledPixel = _MainTex.Sample(ColorSampler, i.tex);
		tex *= sampledPixel.rgb;
		transparency = sampledPixel.a;
		grayscale = 0.2989 * tex.r + 0.5870 * tex.g + 0.1140 * tex.b;
	}

	//light calculations (Maya currently only supports 3 lights auto-bind, could expand this if necessary)
	lightOut light0 = calculateLight(light0Enable, light0Type, light0AttenScale, light0Pos, i.posWorld.xyz,
										light0Color, light0Intensity, light0Dir, light0ConeAngle, light0FallOff, light0Matrix,
										light0ShadowMap, light0ShadowOn, normalWorld, _ShadeWrap, _DiffuseFactor, _DiluteArea,
										_Specular, _SpecDiffusion, _SpecTransparency, i.viewDir, i.velocityDepth.z);
	lightOut light1 = calculateLight(light1Enable, light1Type, light1AttenScale, light1Pos, i.posWorld.xyz,
										light1Color, light1Intensity, light1Dir, light1ConeAngle, light1FallOff, light1Matrix,
										light1ShadowMap, light1ShadowOn, normalWorld, _ShadeWrap, _DiffuseFactor, _DiluteArea,
										_Specular, _SpecDiffusion, _SpecTransparency, i.viewDir, i.velocityDepth.z);
	lightOut light2 = calculateLight(light2Enable, light2Type, light2AttenScale, light2Pos, i.posWorld.xyz,
										light2Color, light2Intensity, light2Dir, light2ConeAngle, light2FallOff, light2Matrix,
										light2ShadowMap, light2ShadowOn, normalWorld, _ShadeWrap, _DiffuseFactor, _DiluteArea,
										_Specular, _SpecDiffusion, _SpecTransparency, i.viewDir, i.velocityDepth.z);

	float3 lightTotal =  light0.color + light1.color + light2.color;
	float3 specTotal = light0.specular + light1.specular + light2.specular;
	float3 dilute = light0.dilute + light1.dilute + light2.dilute;
	float shade = light0.shade + light1.shade + light2.shade;


	if (!MayaFullScreenGamma) {
		lightTotal = pow(lightTotal, 1.0/2.2); // gamma correct for screen
	}
	dilute = lerp(dilute, pow(dilute, 2.2), saturate(-1+_Dilute+_Cangiante));//soften gradation if dilute and cangiante are at the same time

	// //if its not in shade
	float3 highlight = float3(0.0f,0.0f,0.0f);
	if (shade<1.0){
		tex.rgb = tex.rgb + saturate(dilute*_Cangiante); //cangiante
		tex.rgb = lerp(tex.rgb, _PaperColor, dilute*_Dilute); //dilute
		if (_HighArea) {
			highlight = (max(1-_HighArea.xxx, dilute)-(1-_HighArea.xxx))*800/i.velocityDepth.z;
			highlight = saturate(lerp(-highlight*_DarkEdges, highlight, trunc(highlight))); //highlight darkenedEdges
		}
	}

	//diffuse calculations
	float3 watercolor = float3(0,0,0);
	if(_UseOverrideShade){
		float3 c = lerp(_ShadeColor, tex.rgb, saturate(lightTotal));
		watercolor = c + (specTotal * specularMap.rgb) + highlight*(1-_HighTransparency);
	} else {
		float3 c = lerp(_ShadeColor*grayscale, tex.rgb, saturate(lightTotal));
		c = lerp((1-_DiffuseFactor), c, saturate(lightTotal));
		watercolor = c + (specTotal * specularMap.rgb) + highlight*(1-_HighTransparency);
	}

	if(IsSwatchRender){
		result.colorOutput = float4(watercolor, transparency);
		return result;
	}


	//object-space darkened edges
	float3 wDarkenEdge = watercolor;
	if (_DarkEdges) {
		float dEdges = saturate(i.nDotV*max(3,20/i.velocityDepth.z));
		float darkenedEdges = lerp(1, dEdges, _DarkEdges); //(1-_DarkEdges)+(_DarkEdges*(dEdges))
		wDarkenEdge = lerp(watercolor*darkenedEdges, watercolor, saturate(dilute)+0.5);
	}

	float3 controlledColor = wDarkenEdge;

    // solid Gabor noise
    //float noise = filteringSolidGaborNoiseKernel(i.posObject.xyz, i.posWorld.xyz, normalWorld, i.velocityDepth.z,
    //                                            _GaborNoiseScale, _GaborNoiseLambda, _GaborNoiseR, _GaborNoiseSeed,
    //                                            _GaborNoiseOmega, _GaborNoiseA, _GaborNoiseType, _GaborNoiseFilter);

    // velocity
    float2 velocity = i.velocityDepth.xy;

	//FADE
	//pixel = lerp(wDarkenEdge, _AtmosphereColor.rgb, saturate((i.velocityDepth.z-_RangeStart)/_RangeEnd));
	pixel = lerp(controlledColor, _AtmosphereColor.rgb, saturate((i.velocityDepth.z-_RangeStart)/_RangeEnd));
	//return float4(pixel,1);
	result.colorOutput = float4(saturate(pixel), transparency);
    result.pigmentCtrlOutput = float4(control1.xyz, 1);
    result.substrateCtrlOutput = float4(control2.xyz, 1);
    result.edgeCtrlOutput = float4(control3.xyz, 1);
    result.abstractionCtrlOutput = float4(control4.xyz, 1);
    result.velocityOutput = velocity;
	return result;
}



// Pixel shader.
float4 vColorFrag(vertexOutput i) : SV_Target {
	float4 correctedColor = saturate(i.vColor0);
	/*
	if (!MayaFullScreenGamma){
		correctedColor = pow(correctedColor, 1.0/2.2);
	}
	*/
	return float4(correctedColor.a,correctedColor.a,correctedColor.a,0);
}




//------------------------------------
// pixel shader for shadow map generation
// Overrides Mayas internal shadow map pixel-shader
//------------------------------------
float4 ShadowMapPS(vertexOutput i) : SV_Target {
	float4 Pndc = mul( float4(i.posWorld, 1.0f), VIEWPRJ );

	// divide Z and W component from clip space vertex position to get final depth per pixel
	float retZ = Pndc.z / Pndc.w;

	retZ += fwidth(retZ); //don't seem to require any softening
	return retZ.xxxx;
}

/*******************************************************************************/
//                                   88                        88
//    ,d                             88                        ""
//    88                             88
//  MM88MMM   ,adPPYba,   ,adPPYba,  88,dPPYba,   8b,dPPYba,   88   ,adPPYb,d8  88       88   ,adPPYba,  ,adPPYba,
//    88     a8P_____88  a8"     ""  88P'    "8a  88P'   `"8a  88  a8"    `Y88  88       88  a8P_____88  I8[    ""
//    88     8PP"""""""  8b          88       88  88       88  88  8b       88  88       88  8PP"""""""   `"Y8ba,
//    88,    "8b,   ,aa  "8a,   ,aa  88       88  88       88  88  "8a    ,d88  "8a,   ,a88  "8b,   ,aa  aa    ]8I
//    "Y888   `"Ybbd8"'   `"Ybbd8"'  88       88  88       88  88   `"YbbdP'88   `"YbbdP'Y8   `"Ybbd8"'  `"YbbdP"'
//                                                                          88
/*******************************************************************************/
technique11 wTextured {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, vs()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, psTextured()));
		SetRasterizerState(DisableCulling);
	}
	//override maya shadow map
	//pass pShadow < string drawContext = "shadowPass"; >	{// shadow pass
	//	SetVertexShader(CompileShader(vs_5_0, vs()));
	//	SetHullShader(NULL);
	//	SetDomainShader(NULL);
	//	SetGeometryShader(NULL);
	//	SetPixelShader(CompileShader(ps_5_0, ShadowMapPS()));
	//}
}

technique11 vColor {
  pass p0 {// tell maya during what draw context this shader should be active, in this case 'Color'
	SetVertexShader(CompileShader(vs_5_0, vs()));
	SetGeometryShader(NULL);
	SetPixelShader(CompileShader(ps_5_0, vColorFrag()));
  }
}
