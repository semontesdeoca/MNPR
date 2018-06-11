////////////////////////////////////////////////////////////////////////////////////////////////////
// quadOffsetBlend10.fx (HLSL)
// Brief: Blurring operations for offset target
// Contributors: Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//    _     _                _ _             
//   | |__ | | ___ _ __   __| (_)_ __   __ _ 
//   | '_ \| |/ _ \ '_ \ / _` | | '_ \ / _` |
//   | |_) | |  __/ | | | (_| | | | | | (_| |
//   |_.__/|_|\___|_| |_|\__,_|_|_| |_|\__, |
//                                     |___/ 
////////////////////////////////////////////////////////////////////////////////////////////////////
// Blurring operations for the offset target to create the mixing effect in charcoal stylization.
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gDepthTex;
Texture2D gControlTex;
Texture2D gOffsetTex;


// VARIABLES
// Discrete gaussian weights calculated with sigma 40.0
static float gaussianWeights[41] = {0.014481,	0.014477,	0.014463,	0.014441,	0.014409,	0.014369,	0.014319,	0.014261,	0.014195,	0.014119,	0.014036,	0.013944,	0.013844,	0.013736,	0.013621,	0.013498,	0.013368,	0.013231,	0.013087,	0.012936,	0.01278,0.012617,	0.012449,	0.012275,	0.012096,	0.011912,	0.011724,	0.011531,	0.011335,	0.011135,	0.010931,	0.010725,	0.010516,	0.010304,	0.010091,	0.009876,	0.009659,	0.009441,	0.009222,	0.009003,	0.008784};


// OUTPUT
struct fragmentOutput {
	float4 outputTarget : SV_Target0;
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



//    _     _                _ _             
//   | |__ | | ___ _ __   __| (_)_ __   __ _ 
//   | '_ \| |/ _ \ '_ \ / _` | | '_ \ / _` |
//   | |_) | |  __/ | | | (_| | | | | | (_| |
//   |_.__/|_|\___|_| |_|\__,_|_|_| |_|\__, |
//                                     |___/ 

// Contributors: Yee Xin Chiew
// Operation for blurring the offset target (referenced from watercolor)
fragmentOutput offsetBlend(vertexOutputSampler i, float2 dir) {
	fragmentOutput result;

	float4 offsetTex = gOffsetTex.Sample(gSampler, i.uv);

	float depth = gDepthTex.Sample(gSampler, i.uv).r;
	float ctrlAbs = 0;
	if (dir.y > 0) {
		ctrlAbs = offsetTex.r;
	} else {
		ctrlAbs = gControlTex.Sample(gSampler, i.uv).b; // controlTargetSubstrate		
	}
	//int kernelRadius = (dir.y > 0) ? ((1 + ctrlAbs) * 30) : (2-depth) * 30;
	int kernelRadius = (1 + ctrlAbs) * 30; // for performance
	float sigma = kernelRadius / 2.0;
	float normalizer = 1.0 / kernelRadius;
	
	float4 offsetTexResult = float4(0,0,0,0);
	float normDivisor = 0;
	bool blend = false;
	
	//[unroll(100)] for (int k = -kernelRadius; k < kernelRadius + 1; k++) {
	kernelRadius = 40;
	for (int k = -kernelRadius; k < kernelRadius + 1; k++) {
		float2 destUV = saturate(i.uv + float2(k*gTexel*dir));
		float4 destOffsetTex = gOffsetTex.Sample(gSampler, destUV);

		float destDepth = gDepthTex.Sample(gSampler, destUV).r;

		float destCtrlAbs = 0;
		if (dir.y > 0) {
			destCtrlAbs = destOffsetTex.r;
		} else {
			destCtrlAbs = gControlTex.Sample(gSampler, destUV).b; // controlTargetSubstrate
		}
		bool destIsFront = false;

		if (depth > destDepth) { // destination pixel is nearer to the camera
			destIsFront = true;
		}
		if (destCtrlAbs && destIsFront || ctrlAbs && !destIsFront) {
			blend = true;
		}
		
		float weight = gaussianWeight(abs(k), sigma);
		// Handle blurring differently for offsetTex
		if (blend) {
			offsetTexResult += destOffsetTex * weight;
		}
		else {
			offsetTexResult += offsetTex * weight;
		}
		normDivisor += weight;
	}
	offsetTexResult = offsetTexResult / normDivisor;
	result.outputTarget = float4(offsetTexResult.xy, offsetTex.b, offsetTexResult.a);
	return result;
}



//    _                _                _        _ 
//   | |__   ___  _ __(_)_______  _ __ | |_ __ _| |
//   | '_ \ / _ \| '__| |_  / _ \| '_ \| __/ _` | |
//   | | | | (_) | |  | |/ / (_) | | | | || (_| | |
//   |_| |_|\___/|_|  |_/___\___/|_| |_|\__\__,_|_|
//                                                 
fragmentOutput offsetHorizontal(vertexOutputSampler i) {
	fragmentOutput result = offsetBlend(i, float2(1, 0));
	return result;
}



//                   _   _           _ 
//   __   _____ _ __| |_(_) ___ __ _| |
//   \ \ / / _ \ '__| __| |/ __/ _` | |
//    \ V /  __/ |  | |_| | (_| (_| | |
//     \_/ \___|_|   \__|_|\___\__,_|_|
//                                     
fragmentOutput offsetVertical(vertexOutputSampler i) {
	fragmentOutput result = offsetBlend(i, float2(0, 1));
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// HORIZONTAL BLUR
technique11 offsetH {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, offsetHorizontal()));
	}
}

// VERTICAL BLUR
technique11 offsetV {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, offsetVertical()));
	}
}