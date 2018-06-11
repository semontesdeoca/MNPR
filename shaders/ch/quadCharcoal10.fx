////////////////////////////////////////////////////////////////////////////////////////////////////
// quadCharcoal10.fx (HLSL)
// Brief: Charcoal effect
// Contributors: Yee Xin Chiew, Santiago Montesdeoca
////////////////////////////////////////////////////////////////////////////////////////////////////
//         _                               _ 
//     ___| |__   __ _ _ __ ___ ___   __ _| |
//    / __| '_ \ / _` | '__/ __/ _ \ / _` | |
//   | (__| | | | (_| | | | (_| (_) | (_| | |
//    \___|_| |_|\__,_|_|  \___\___/ \__,_|_|
//                                           
////////////////////////////////////////////////////////////////////////////////////////////////////
// Renders the charcoal effect based on height map of paper substrate
////////////////////////////////////////////////////////////////////////////////////////////////////

#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gSubstrateTex;  // substrate texture (paper, canvas, etc)
Texture2D gStylizationTex;
Texture2D gBlendTex;
Texture2D gLightingTex;
Texture2D gCtrlPigmentTex;


// VARIABLES
// Engine settings
float gDryMediaThreshold = 5.0f;
float gSubstrateRoughness;
float3 gSubstrateColor = float3(1.0, 1.0, 1.0);


// OUTPUT
struct fragmentOutput {
	float4 stylizationOutput : SV_Target0;
};



//        _                                 _ _       
//     __| |_ __ _   _   _ __ ___   ___  __| (_) __ _ 
//    / _` | '__| | | | | '_ ` _ \ / _ \/ _` | |/ _` |
//   | (_| | |  | |_| | | | | | | |  __/ (_| | | (_| |
//    \__,_|_|   \__, | |_| |_| |_|\___|\__,_|_|\__,_|
//               |___/                                

// Contributors: Yee Xin Chiew, Santiago Montesdeoca
// Charcoal effect
fragmentOutput dryMediaFrag(vertexOutputSampler i) {
	fragmentOutput result;
    float3 finalResult;

	int3 loc = int3(i.pos.xy, 0);  // coordinates for post-processing
	float4 renderTex = gStylizationTex.Load(loc);

    if (length(renderTex.rgb-gSubstrateColor) > 0.01) {
        float heightMap = gSubstrateTex.Load(loc).b;
        heightMap = 0.5 + ((heightMap - 0.5) * gSubstrateRoughness);

        // 1) How much drybrush is applied depends on lighting
        float applicationLight = luminance(gLightingTex.Load(loc).rgb);

        // 2) If drybrush/granulation is applied
        float applicationCtrl = -gCtrlPigmentTex.Sample(gSampler, i.uv).g;  // invert (drybrush ctrl is negative)

        // Calculate application
        float application = saturate(applicationCtrl + applicationLight);

        float dryDiff = heightMap - (application);

        if (dryDiff > 0) {
            // Heightmap is higher than application ->  peaks will be colored
            finalResult = pow(renderTex.rgb, (1 - gDryMediaThreshold) + (dryDiff * 2));
        } else {
            // Valleys won't be colored
            finalResult = lerp(renderTex.rgb, gSubstrateColor, -dryDiff * (gDryMediaThreshold*5.0));
        }

        result.stylizationOutput = float4(finalResult, renderTex.a);
    } else {
        result.stylizationOutput = renderTex;
    }
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// DRY MEDIA EFFECT
technique11 dryMedia {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetPixelShader(CompileShader(ps_5_0, dryMediaFrag()));
	}
}