////////////////////////////////////////////////////////////////////////////////////////////////////
// quadOffset10.fx (HLSL)
// Brief: Managing offset target and charcoal mixing effect
// Contributors: Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//           __  __          _   
//     ___  / _|/ _|___  ___| |_ 
//    / _ \| |_| |_/ __|/ _ \ __|
//   | (_) |  _|  _\__ \  __/ |_ 
//    \___/|_| |_| |___/\___|\__|
//                               
////////////////////////////////////////////////////////////////////////////////////////////////////
// Operations for managing the offset target and creating the mixing effect for charcoal stylization
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gOffsetTex;
Texture2D gBlendTex;
Texture2D gStylizationTex;
Texture2D gAbstractionControlTex;


// OUTPUT
struct fragmentOutput {
	float4 outputTarget : SV_Target0;
};



//                        
//    _ __   __ _ ___ ___ 
//   | '_ \ / _` / __/ __|
//   | |_) | (_| \__ \__ \
//   | .__/ \__,_|___/___/
//   |_|                  

// Contributors: Yee Xin Chiew
// Passing of parameters to offset target for mixing and smudging effects
fragmentOutput offsetPass(vertexOutputSampler i) {
	fragmentOutput result;
	
	float ctrlB = gAbstractionControlTex.Sample(gSampler, i.uv).b;  // mixing
    float ctrlR = gAbstractionControlTex.Sample(gSampler, i.uv).r;  // smudging
	result.outputTarget = float4(ctrlB, ctrlR, 0, 0);
	return result;
}



//              _      _             
//    _ __ ___ (_)_  _(_)_ __   __ _ 
//   | '_ ` _ \| \ \/ / | '_ \ / _` |
//   | | | | | | |>  <| | | | | (_| |
//   |_| |_| |_|_/_/\_\_|_| |_|\__, |
//                             |___/

// Contributors: Yee Xin Chiew
// Mixing effect
fragmentOutput offsetFilter(vertexOutputSampler i) {
	fragmentOutput result;
	int3 loc = int3(i.pos.xy, 0);
	float4 stylizationTex = gStylizationTex.Load(loc);
	float4 blendTex = gBlendTex.Load(loc);
	//float depth = gDepthTex.Load(loc).r;
	float3 offsetCtrl = gOffsetTex.Load(loc).rgb;
	float ctrl = gAbstractionControlTex.Sample(gSampler, i.uv).b; 
	
	if (stylizationTex.a >= 0) { // mixed areas
		
		float inc = pow(3.0, offsetCtrl.r + 1.0); // non-linear increment
		float offs = saturate(offsetCtrl.r * inc);
		blendTex = lerp(stylizationTex, blendTex, offs);

		if (luminance(blendTex) < luminance(stylizationTex)) {
			result.outputTarget = blendTex;
		} else {
			result.outputTarget = stylizationTex;
		}
	} else {
		result.outputTarget = stylizationTex;
	}
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// OPERATION FOR OFFSET TARGET
technique11 offsetOutput {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, offsetPass()));
	}
}

// MIXING EFFECT
technique11 mixing {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, offsetFilter()));
	}
}