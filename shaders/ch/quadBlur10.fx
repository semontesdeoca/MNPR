////////////////////////////////////////////////////////////////////////////////////////////////////
// quadBlur10.fx (HLSL)
// Brief: Blurring algorithms for charcoal mixing effect
// Contributors: Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//    _     _                 _             
//   | |__ | |_   _ _ __ _ __(_)_ __   __ _ 
//   | '_ \| | | | | '__| '__| | '_ \ / _` |
//   | |_) | | |_| | |  | |  | | | | | (_| |
//   |_.__/|_|\__,_|_|  |_|  |_|_| |_|\__, |
//                                    |___/ 
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader provides the blurring operations needed to create the mixing effect in 
// charcoal stylization
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gOffsetTex;
Texture2D gControlTex;
Texture2D gStylizationTex;


// OUTPUT
struct fragmentOutput {
	float4 stylizationOutput : SV_Target0;
};



//     __                  _   _                 
//    / _|_   _ _ __   ___| |_(_) ___  _ __  ___ 
//   | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
//   |  _| |_| | | | | (__| |_| | (_) | | | \__ \
//   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
//
// GAUSSIAN WEIGHT
float gaussianWeight(float x, float sigma) {
	float weight = 0.15915*exp(-0.5*x*x / (sigma*sigma)) / sigma;
	return weight;
}



//    _     _              _                    __  __          _   
//   | |__ | |_   _ _ __  | |__  _   _    ___  / _|/ _|___  ___| |_ 
//   | '_ \| | | | | '__| | '_ \| | | |  / _ \| |_| |_/ __|/ _ \ __|
//   | |_) | | |_| | |    | |_) | |_| | | (_) |  _|  _\__ \  __/ |_ 
//   |_.__/|_|\__,_|_|    |_.__/ \__, |  \___/|_| |_| |___/\___|\__|
//                               |___/                              

// Contributors: Yee Xin Chiew
// Blur the entire stylization tex based on value in offset target
fragmentOutput offsetBlur(vertexOutputSampler i, float2 dir) {
	fragmentOutput result;

	float offsetCtrl = gOffsetTex.Sample(gSampler, i.uv).r;
	float4 stylizationTex = gStylizationTex.Sample(gSampler, i.uv);
	
	// Use a dynamic kernel
	int kernelRadius = (2 - offsetCtrl) * 30;
	float normalizer = 1.0 / kernelRadius;
	float sigma = kernelRadius / 2.0;

	float weight = gaussianWeight(0.0, sigma);
	float4 sTex = stylizationTex * weight;
	float normDivisor = weight;
	[unroll(100)] for (int o = 1; o < kernelRadius; o++) {
		float2 rUV = saturate(i.uv + float2(o*gTexel*dir));
		float2 lUV = saturate(i.uv + float2(-o*gTexel*dir));
		float4 texR = gStylizationTex.Sample(gSampler, rUV);
		float4 texL = gStylizationTex.Sample(gSampler, lUV);

		float granuR = gControlTex.Sample(gSampler, rUV).g; // granulation
		float granuL = gControlTex.Sample(gSampler, lUV).g; // granulation

		weight = gaussianWeight(o, sigma);
		sTex += weight * (texR + texL);
		normDivisor += weight * 2;
	}
	sTex = (sTex / normDivisor);
	result.stylizationOutput = sTex;
	
	return result;
}



//    _                _                _        _ 
//   | |__   ___  _ __(_)_______  _ __ | |_ __ _| |
//   | '_ \ / _ \| '__| |_  / _ \| '_ \| __/ _` | |
//   | | | | (_) | |  | |/ / (_) | | | | || (_| | |
//   |_| |_|\___/|_|  |_/___\___/|_| |_|\__\__,_|_|
//                                                 
fragmentOutput blurOffsetH(vertexOutputSampler i) {
	fragmentOutput result = offsetBlur(i, float2(1, 0));
	return result;
}



//                   _   _           _ 
//   __   _____ _ __| |_(_) ___ __ _| |
//   \ \ / / _ \ '__| __| |/ __/ _` | |
//    \ V /  __/ |  | |_| | (_| (_| | |
//     \_/ \___|_|   \__|_|\___\__,_|_|
//                                     
fragmentOutput blurOffsetV(vertexOutputSampler i) {
	fragmentOutput result = offsetBlur(i, float2(0, 1));
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// HORIZONTAL BLUR
technique11 blurH {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, blurOffsetH()));
	}
}

// VERTICAL BLUR
technique11 blurV {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, blurOffsetV()));
	}
}