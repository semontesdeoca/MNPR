////////////////////////////////////////////////////////////////////////////////////////////////////
// quadAdjustLoad10.fx (HLSL)
// Brief: Adjusting and loading render targets
// Contributors: Santiago Montesdeoca, Yee Xin Chiew, Amir Semmo
////////////////////////////////////////////////////////////////////////////////////////////////////
//              _  _           _        _                 _
//     __ _  __| |(_)_   _ ___| |_     | | ___   __ _  __| |
//    / _` |/ _` || | | | / __| __|____| |/ _ \ / _` |/ _` |
//   | (_| | (_| || | |_| \__ \ ||_____| | (_) | (_| | (_| |
//    \__,_|\__,_|/ |\__,_|___/\__|    |_|\___/ \__,_|\__,_|
//              |__/
////////////////////////////////////////////////////////////////////////////////////////////////////
// This base shader adjusts and loads any required elements for future stylization in MNPR
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// MAYA VARIABLES
float gNCP : NearClipPlane;  // near clip plane distance

// TEXTURES
Texture2D gDiffuseTex;    // diffuse
Texture2D gSpecularTex;   // specular
Texture2D gZBuffer;       // ZBuffer
Texture2D gSubstrateTex;  // substrate texture (paper, canvas, etc)
Texture2D gLinearDepthTex; // linearized depth
Texture2D gVelocityTex;  // velocity


// VARIABLES
// post-processing effects
float gSaturation = 1.0;
float gContrast = 1.0;
float gBrightness = 1.0;

// engine settings
float gGamma = 1.0;
float2 gDepthRange = float2(8.0, 50.0);
float3 gSubstrateColor = float3(1.0, 1.0, 1.0);
float gEnableVelocityPV;
float gSubstrateRoughness;
float gSubstrateTexScale;
float2 gSubstrateTexDimensions;
float2 gSubstrateTexUVOffset;
float3 gAtmosphereTint;
float2 gAtmosphereRange;


// MRT
struct fragmentOutput {
	float4 stylizationOutput : SV_Target0;
	float4 substrateOutput : SV_Target1;
	float2 depthOutput : SV_Target2;
    float2 velocity : SV_Target3;
};



//     __                  _   _
//    / _|_   _ _ __   ___| |_(_) ___  _ __  ___
//   | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
//   |  _| |_| | | | | (__| |_| | (_) | | | \__ \
//   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
//
// remap range
float remap(float value, float oldMin, float oldMax, float newMin, float newMax) {
	return newMin + (((value - oldMin) / (oldMax - oldMin)) * (newMax - newMin));
}



//              _  _           _             _                 _
//     __ _  __| |(_)_   _ ___| |_          | | ___   __ _  __| |
//    / _` |/ _` || | | | / __| __|  _____  | |/ _ \ / _` |/ _` |
//   | (_| | (_| || | |_| \__ \ |_  |_____| | | (_) | (_| | (_| |
//    \__,_|\__,_|/ |\__,_|___/\__|         |_|\___/ \__,_|\__,_|
//              |__/

// Contributors: Santiago Montesdeoca, Yee Xin Chiew, Amir Semmo
// This shader performs four operations:
// 1.- Simple color post processing operations over the Maya render (tgt 1)
// 2.- Adds the substrate color as the background color (tgt 1)
// 3.- Loads the substrate texture into the substrate target (tgt 2)
// 4.- Modulates Maya's Z-buffer to a linear depth target with a custom range (tgt 3)
fragmentOutput adjustLoadFrag(vertexOutputSampler i) {
	fragmentOutput result;
    int3 loc = int3(i.pos.xy, 0);  // coordinates for loading texels

    // LINEAR DEPTH
    // Maya depth buffer is calculated as: zBuffer = 1 - gNCP/z;
    float zBuffer = gZBuffer.Load(loc).r;
    float depth = 1.0;
    float depthInMayaUnits = 1000000000.0;  // maximum depth
    if (zBuffer < 1.0) {
        depthInMayaUnits = -gNCP / (zBuffer - 1.0);  // [0 ... gNCP]
        depth = remap(depthInMayaUnits, gDepthRange.x, gDepthRange.y, 0, 1);
    }
    // save depth of previous frame
    float depthPrevious = gLinearDepthTex.Load(loc).r;
    result.depthOutput = float2(depth, depthPrevious);



	// POST-PROCESSING
	// get pixel value
	float4 renderTex = gColorTex.Load(loc);
    float4 diffuseTex = gDiffuseTex.Load(loc);
    //float depthOfStylizedShaders = gSpecularTex.Load(loc).a;
    float mask = gSpecularTex.Load(loc).a;
    if (mask > 0) {
        if (gGamma < 1) {
            // if viewport is not gamma corrected, at least keep light linearity
            diffuseTex.rgb = pow(diffuseTex.rgb, 0.454545455);
        }
        //renderTex.rgb *= lightingTex.rgb;
        // shade color embedded in negative values of lightingTex
        //float3 shadeColor = lerp(saturate(lightingTex * float3(-1, -1, -1)))
        renderTex.rgb *= diffuseTex.rgb;
        renderTex.rgb += gSpecularTex.Load(loc).rgb;  // add specular contribution
    }
	// color operations
	float luma = luminance(renderTex.rgb);
	float3 saturationResult = float3(lerp(luma.xxx, renderTex.rgb, gSaturation));
	float3 contrastResult = lerp(float3(0.5, 0.5, 0.5), saturationResult, gContrast * 0.5 + 0.5);
	float b = gBrightness - 1.0;
	float3 brightnessResult = saturate(contrastResult.rgb + b);

    // atmospheric operations
    float remapedDepth = saturate(remap(depthInMayaUnits, gAtmosphereRange.x, gAtmosphereRange.y, 0, 1));
    float3 atmospericResult = lerp(brightnessResult, gAtmosphereTint, remapedDepth);

	// add substrate color
	renderTex.rgb = lerp(gSubstrateColor, atmospericResult, renderTex.a);
	result.stylizationOutput = renderTex;


	// SUBSTRATE
	// get proper UVS
	float2 uv = i.uv * (gScreenSize / gSubstrateTexDimensions) * (gSubstrateTexScale) + gSubstrateTexUVOffset;
	// get substrate pixel
	float3 substrate = gSubstrateTex.Sample(gSampler, uv).rgb;
	substrate = substrate - 0.5;;  // bring to [-0.5 - 0 - 0.5]
	substrate *= gSubstrateRoughness;  // define roughness
    result.substrateOutput = float4(substrate + 0.5, 0.0);  // bring back to [0 - 1]

    // velocity reset if disabled
    result.velocity = (gEnableVelocityPV == 1.0 ? gVelocityTex.Load(loc).xy : float2(0.0, 0.0));

	return result;
}



//    _            _           _
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|
// ADJUST AND LOAD EVERYTHING FOR STYLIZATION
technique11 adjustLoadMNPR {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetPixelShader(CompileShader(ps_5_0, adjustLoadFrag()));
	}
}
