////////////////////////////////////////////////////////////////////////////////////////////////////
// quadCommon.fxh (HLSL)
// Brief: Common utility shader elements for MNPR
// Contributors: Santiago Montesdeoca
////////////////////////////////////////////////////////////////////////////////////////////////////
//                          _
//     __ _ _   _  __ _  __| |       ___ ___  _ __ ___  _ __ ___   ___  _ __
//    / _` | | | |/ _` |/ _` |_____ / __/ _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \
//   | (_| | |_| | (_| | (_| |_____| (_| (_) | | | | | | | | | | | (_) | | | |
//    \__, |\__,_|\__,_|\__,_|      \___\___/|_| |_| |_|_| |_| |_|\___/|_| |_|
//       |_|
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides utility variables, structs, vertex shader and functions to aid
// the development of quad operations in MNPR
////////////////////////////////////////////////////////////////////////////////////////////////////
#ifndef _QUADCOMMON_FXH
#define _QUADCOMMON_FXH


// COMMON MAYA VARIABLES
float4x4 gWVP : WorldViewProjection;     // world-view-projection transformation
float2 gScreenSize : ViewportPixelSize;  // screen size, in pixels


// COMMON VARIABLES
static float3 luminanceCoeff = float3(0.241, 0.691, 0.068);
static float2 gTexel = 1.0f / gScreenSize;
static const float PI = 3.14159265f;


// COMMON TEXTURES
Texture2D gColorTex;      // color target


// COMMON SAMPLERS
uniform SamplerState gSampler;



//        _                   _
//    ___| |_ _ __ _   _  ___| |_ ___
//   / __| __| '__| | | |/ __| __/ __|
//   \__ \ |_| |  | |_| | (__| |_\__ \
//   |___/\__|_|   \__,_|\___|\__|___/
//
// base input structs
struct appData {
	float3 vertex : POSITION;
};
struct appDataSampler {
	float3 vertex : POSITION;
	float2 texcoord : TEXCOORD0;
};
struct vertexOutput {
	float4 pos : SV_POSITION;
};
struct vertexOutputSampler {
	float4 pos : SV_POSITION;
	float2 uv : TEXCOORD0;
};



//                   _                    _               _
//   __   _____ _ __| |_ _____  __    ___| |__   __ _  __| | ___ _ __ ___
//   \ \ / / _ \ '__| __/ _ \ \/ /   / __| '_ \ / _` |/ _` |/ _ \ '__/ __|
//    \ V /  __/ |  | ||  __/>  <    \__ \ | | | (_| | (_| |  __/ |  \__ \
//     \_/ \___|_|   \__\___/_/\_\   |___/_| |_|\__,_|\__,_|\___|_|  |___/
//
// VERTEX SHADER
vertexOutput quadVert(appData v) {
	vertexOutput o;
	o.pos = mul(float4(v.vertex, 1.0f), gWVP);
	return o;
}

// VERTEX SHADER (with uvs)
vertexOutputSampler quadVertSampler(appDataSampler v) {
	vertexOutputSampler o;
	o.pos = mul(float4(v.vertex, 1.0f), gWVP);
	o.uv = v.texcoord;
	return o;
}



//     __                  _   _
//    / _|_   _ _ __   ___| |_(_) ___  _ __  ___
//   | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
//   |  _| |_| | | | | (__| |_| | (_) | | | \__ \
//   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
//
float luminance(float3 color) {
	return dot(color.rgb, luminanceCoeff);
}

float4 unpremultiply(float4 color) {
	if (color.a) {
		color.rgb /= color.a;
	}
	return color;
}

#endif /* _QUADCOMMON_FXH */
