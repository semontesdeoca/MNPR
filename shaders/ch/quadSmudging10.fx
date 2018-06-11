////////////////////////////////////////////////////////////////////////////////////////////////////
// quadSmudging10.fx (HLSL)
// Brief: Smudging effect
// Contributors: Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//                            _       _             
//    ___ _ __ ___  _   _  __| | __ _(_)_ __   __ _ 
//   / __| '_ ` _ \| | | |/ _` |/ _` | | '_ \ / _` |
//   \__ \ | | | | | |_| | (_| | (_| | | | | | (_| |
//   |___/_| |_| |_|\__,_|\__,_|\__, |_|_| |_|\__, |
//                              |___/         |___/
////////////////////////////////////////////////////////////////////////////////////////////////////
// Operations to create the smudging effect in charcoal stylization.
////////////////////////////////////////////////////////////////////////////////////////////////////

#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gStylizationTex;
Texture2D gBlendTex;
Texture2D gEdgeBlurTex;
Texture2D gControlTex;
Texture2D gOffsetTex;


// OUTPUT
struct fragmentOutput {
	float4 stylizationOutput : SV_Target0;
};


//                            _       _             
//    ___ _ __ ___  _   _  __| | __ _(_)_ __   __ _ 
//   / __| '_ ` _ \| | | |/ _` |/ _` | | '_ \ / _` |
//   \__ \ | | | | | |_| | (_| | (_| | | | | | (_| |
//   |___/_| |_| |_|\__,_|\__,_|\__, |_|_| |_|\__, |
//                              |___/         |___/

// Contributors: Yee Xin Chiew
// Smudging effect
fragmentOutput smudgingEffect(vertexOutputSampler i) {
	fragmentOutput result;
	
	int3 loc = int3(i.pos.xy, 0);  // coordinates for post-processing
	float4 renderTex = gStylizationTex.Load(loc);
	float4 blendTex = gBlendTex.Load(loc);
	float4 edgeBlurTex = gEdgeBlurTex.Load(loc);
	// 
	float pressure = gControlTex.Sample(gSampler, i.uv).r;  // smudging in red of abstraction (DETAIL)
    float mix = gControlTex.Sample(gSampler, i.uv).b;  // mix in blue of abstraction target
    pressure += mix;
	float offsetMixing = gOffsetTex.Load(loc).r;
	float offsetPressure = gOffsetTex.Load(loc).g;
	
	float4 finalResult = renderTex;

	// Handle pressure (smudging)
	if (pressure > 0.01) {
		pressure = pressure * 0.8;
		float4 toBlend = (luminance(blendTex) > luminance(edgeBlurTex)) ? edgeBlurTex : blendTex;
		finalResult = lerp(finalResult, toBlend, pressure);
	} else if (offsetMixing > 0.01) {
		// Problem:
		// edge softening effect is not evident in the results if mixing + smudging are both applied
		float4 toBlend = (luminance(blendTex) > luminance(finalResult)) ? finalResult : blendTex;
		finalResult = lerp(finalResult, toBlend, saturate((0.5 + offsetMixing) * offsetPressure * 5.0));
	}
	result.stylizationOutput = finalResult;
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// SMUDGING EFFECT
technique11 smudging {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetPixelShader(CompileShader(ps_5_0, smudgingEffect()));
	}
}