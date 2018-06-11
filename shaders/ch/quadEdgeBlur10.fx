////////////////////////////////////////////////////////////////////////////////////////////////////
// quadEdgeBlur10.fx (HLSL)
// Brief: Edge softening effect
// Contributors: Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//             _              _     _            
//     ___  __| | __ _  ___  | |__ | |_   _ _ __ 
//    / _ \/ _` |/ _` |/ _ \ | '_ \| | | | | '__|
//   |  __/ (_| | (_| |  __/ | |_) | | |_| | |   
//    \___|\__,_|\__, |\___| |_.__/|_|\__,_|_|   
//               |___/                           
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader provides blurring operations for edge softening effect in charcoal stylization.
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gEdgeBlurTex;
Texture2D gControlTex;
Texture2D gStylizationTex;
Texture2D gOffsetTex;


// VARIABLES
// Discrete gaussian weights of a 15x15 kernel (sigma 7)
static float gaussianWeights[15] = { 0.048277,	0.055112,	0.061647,	0.067566,	0.07256,	0.076352,	0.078721,	0.079527,	0.078721,	0.076352,	0.07256,	0.067566,	0.061647,	0.055112,	0.048277};


// OUTPUT
struct fragmentOutput {
	float4 blurOutput : SV_Target0;
	float4 edgeOutput : SV_Target1;
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
	//float weight = pow((6.283185*sigma*sigma), -0.5) * exp((-0.5*x*x) / (sigma*sigma));
	return weight;
}



//             _              _     _            
//     ___  __| | __ _  ___  | |__ | |_   _ _ __ 
//    / _ \/ _` |/ _` |/ _ \ | '_ \| | | | | '__|
//   |  __/ (_| | (_| |  __/ | |_) | | |_| | |   
//    \___|\__,_|\__, |\___| |_.__/|_|\__,_|_|   
//               |___/                           

// Contributors: Yee Xin Chiew
// Gaussian blur operation for creating softened edges
fragmentOutput edgeBlur(vertexOutputSampler i, float2 dir){
	fragmentOutput result;

	float4 stylizationTex = gStylizationTex.Sample(gSampler, i.uv);
	float2 ctrlIntensity = gControlTex.Sample(gSampler, i.uv).xy; // controlTargetEdges
	
	float4 edgeTex = gEdgeBlurTex.Sample(gSampler, i.uv);
	float2 edges = edgeTex.xy;

	// For contour drawing (using dynamic kernel)
	float edgeWidthCtrl = gControlTex.Sample(gSampler, i.uv).g;

	float width = edgeWidthCtrl * 10;
	int kernelRadius = width;
	float normalizer = 1.0 / kernelRadius;
	float sigma = kernelRadius / 2.0;
	
	float weight = gaussianWeight(0.0, sigma);
	float contour = 0;
	if (dir.x > 0) {
		contour = edgeTex.g * weight;
	}
	float normDivisor = weight;

	[unroll(50)] for (int o = 1; o < kernelRadius; o++) {
		float edgeTexR = gEdgeBlurTex.Sample(gSampler, saturate(i.uv + float2(o*gTexel*dir))).g;
		float edgeTexL = gEdgeBlurTex.Sample(gSampler, saturate(i.uv + float2(-o*gTexel*dir))).g;
		edgeTexR = pow(edgeTexR, 5.0) * 5.0;
		edgeTexL = pow(edgeTexL, 5.0) * 5.0;
		weight = gaussianWeight(o, sigma);
		contour += weight * (edgeTexR + edgeTexL);
		normDivisor += weight * 2;
	}
	contour = (contour / normDivisor);

	// For edge softening (using fixed kernel)
	if (dir.x > 0) {
		edges = pow(edges, 5.0);
	}

	float4 c = float4(0, 0, 0, 0);
	float4 e = float4(0, 0, 0, 0);
	
	for (int k = -7; k < 8; k++) {
		float2 destUV = saturate(i.uv + float2(k*gTexel*dir));
		float4 destStylizationTex = gStylizationTex.Sample(gSampler, destUV);
		float2 destEdge = gEdgeBlurTex.Sample(gSampler, destUV).xy;
		float destCtrlRed = gControlTex.Sample(gSampler, destUV).r;

		float blendedEdgeR = destEdge.x; 
		if (dir.x > 0) {
			blendedEdgeR = pow(blendedEdgeR, 5.0) * 5.0;
			blendedEdgeR = lerp(0.0f, destCtrlRed, blendedEdgeR);
		}

		float weight = gaussianWeights[k + 7];
		float4 offsetTex = gOffsetTex.Sample(gSampler, destUV);
		c += destStylizationTex * weight;
		e += float4(blendedEdgeR * weight, 0, 0, edgeTex.a);
	}

	// Retain the solid edges from edge tex
	// e += float4(lerp(0.0f, edges.x, ctrlIntensity.x) * 2.0, contour, 0, 0);
	e += float4(0, contour, 0, 0);
	result.blurOutput = c;
	result.edgeOutput = e;
	return result;
}



//    _                _                _        _ 
//   | |__   ___  _ __(_)_______  _ __ | |_ __ _| |
//   | '_ \ / _ \| '__| |_  / _ \| '_ \| __/ _` | |
//   | | | | (_) | |  | |/ / (_) | | | | || (_| | |
//   |_| |_|\___/|_|  |_/___\___/|_| |_|\__\__,_|_|
//    
fragmentOutput blurHorizontal(vertexOutputSampler i) {
	fragmentOutput result;
	result = edgeBlur(i, float2(1, 0));
	return result;
}



//                   _   _           _ 
//   __   _____ _ __| |_(_) ___ __ _| |
//   \ \ / / _ \ '__| __| |/ __/ _` | |
//    \ V /  __/ |  | |_| | (_| (_| | |
//     \_/ \___|_|   \__|_|\___\__,_|_|
//                                     
fragmentOutput blurVertical(vertexOutputSampler i) {
	fragmentOutput result;
	result = edgeBlur(i, float2(0, 1));
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// HORIZONTAL BLUR
technique11 edgeBlurH {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, blurHorizontal()));
	}
}

// VERTICAL BLUR
technique11 edgeBlurV {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, blurVertical()));
	}
}