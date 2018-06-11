////////////////////////////////////////////////////////////////////////////////////////////////////
// quadEdgeDetection10.fx (HLSL)
// Brief: Edge detection operations
// Contributors: Santiago Montesdeoca
////////////////////////////////////////////////////////////////////////////////////////////////////
//             _                    _      _            _   _
//     ___  __| | __ _  ___      __| | ___| |_ ___  ___| |_(_) ___  _ __
//    / _ \/ _` |/ _` |/ _ \    / _` |/ _ \ __/ _ \/ __| __| |/ _ \| '_ \
//   |  __/ (_| | (_| |  __/   | (_| |  __/ ||  __/ (__| |_| | (_) | | | |
//    \___|\__,_|\__, |\___|    \__,_|\___|\__\___|\___|\__|_|\___/|_| |_|
//               |___/
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides different algorithms for edge detection in MNPR
// 1.- Sobel edge detection
// 2.- DoG edge detection
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
Texture2D gDepthTex;



//     __                  _   _
//    / _|_   _ _ __   ___| |_(_) ___  _ __  ___
//   | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
//   |  _| |_| | | | | (__| |_| | (_) | | | \__ \
//   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
//
float4 rgbd(int3 loc) {
	float3 renderTex = gColorTex.Load(loc).rgb;
	float linearDepth = gDepthTex.Load(loc).r;
	return float4(renderTex, linearDepth);
}



//              _          _     ____   ____ ____  ____
//    ___  ___ | |__   ___| |   |  _ \ / ___| __ )|  _ \
//   / __|/ _ \| '_ \ / _ \ |   | |_) | |  _|  _ \| | | |
//   \__ \ (_) | |_) |  __/ |   |  _ <| |_| | |_) | |_| |
//   |___/\___/|_.__/ \___|_|   |_| \_\\____|____/|____/
//

// Contributor: Santiago Montesdeoca
// Performs a sobel edge detection on RGBD channels
// -> Based on the sobel image processing operator by Sobel and Feldman 1968 
//    [1968] A 3x3 Isotropic Gradient Operator for Image Processing
float3 sobelRGBDFrag(vertexOutput i) : SV_Target{
	int3 loc = int3(i.pos.xy, 0);  // for load sampling

	// get rgb values at kernel area
	float4 topLeft = rgbd(loc + int3(-1, -1, 0));
	float4 topMiddle = rgbd(loc + int3(0, -1, 0));
	float4 topRight = rgbd(loc + int3(1, -1, 0));
	float4 midLeft = rgbd(loc + int3(-1, 0, 0));
	float4 middle = rgbd(loc);
	float4 midRight = rgbd(loc + int3(1, 0, 0));
	float4 bottomLeft = rgbd(loc + int3(-1, 1, 0));
	float4 bottomMiddle = rgbd(loc + int3(0, 1, 0));
	float4 bottomRight = rgbd(loc + int3(1, 1, 0));

	// convolve with kernel
	// HORIZONTAL        VERTICAL
	// -1  -2  -1       -1   0   1
	//  0   0   0       -2   0   2
	//  1   2   1       -1   0   1

	float4 hKernelMul = (1 * topLeft) + (2 * topMiddle) + (1 * topRight) + (-1 * bottomLeft) + (-2 * bottomMiddle) + (-1 * bottomRight);
	float4 vKernelMul = (1 * topLeft) + (-1 * topRight) + (2 * midLeft) + (-2 * midRight) + (1 * bottomLeft) + (-1 * bottomRight);

	hKernelMul.a *= 5;  // modulate depth
	float rgbdHorizontal = length(hKernelMul);
	//float rgbdHorizontal = max(max(hKernel.r, hKernel.b), hKernel.g);
	vKernelMul.a *= 5;  // modulate depth
	float rgbdVertical = length(vKernelMul);
	//float rgbdVertical = max(max(vKernel.r, vKernel.b), vKernel.g);

	float edgeMagnitude = length(float2(rgbdHorizontal, rgbdVertical));

	return edgeMagnitude.xxx;
}



//    ____         ____     ____   ____ ____  ____
//   |  _ \  ___  / ___|   |  _ \ / ___| __ )|  _ \
//   | | | |/ _ \| |  _    | |_) | |  _|  _ \| | | |
//   | |_| | (_) | |_| |   |  _ <| |_| | |_) | |_| |
//   |____/ \___/ \____|   |_| \_\\____|____/|____/
//

// Contributor: Santiago Montesdeoca
// Performs a Difference of Gaussians edge detection on RGBD channels
float3 dogRGBDFrag(vertexOutput i) : SV_Target{
	int3 loc = int3(i.pos.xy, 0);  // for load sampling

	// get rgb values at kernel area
	float4 topLeft = rgbd(loc + int3(-1, -1, 0));
	float4 topMiddle = rgbd(loc + int3(0, -1, 0));
	float4 topRight = rgbd(loc + int3(1, -1, 0));
	float4 midLeft = rgbd(loc + int3(-1, 0, 0));
	float4 middle = rgbd(loc);
	float4 midRight = rgbd(loc + int3(1, 0, 0));
	float4 bottomLeft = rgbd(loc + int3(-1, 1, 0));
	float4 bottomMiddle = rgbd(loc + int3(0, 1, 0));
	float4 bottomRight = rgbd(loc + int3(1, 1, 0));

	// convolve with kernel
	//           SIGMA 1.0
	// 0.077847   0.123317   0.077847
	// 0.123317   0.195346   0.123317
	// 0.077847   0.123317   0.077847

	float4 gaussianKernelMul = (0.077847 * topLeft) + (0.123317 * topMiddle) + (0.077847 * topRight) +
		(0.123317 * midLeft) + (0.195346 * middle) + (0.123317 * midRight) +
		(0.077847 * bottomLeft) + (0.123317 * bottomMiddle) + (0.077847 * bottomRight);

	// calculate difference of gaussians
	float4 dog = saturate(middle - gaussianKernelMul);
	dog.a *= 3.0;  // modulate depth
	float edgeMagnitude = length(dog);
	//float edgeMagnitude = max(max(max(dog.r, dog.b), dog.g), dog.a);

	if (edgeMagnitude>0.05) {
		edgeMagnitude = 1.0;
	}

	return edgeMagnitude.xxx;
}



//    _            _           _
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|
// Sobel RGBD edge detection
technique11 sobelRGBDEdgeDetection {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVert()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, sobelRGBDFrag()));
	}
}

// Difference of Gaussians RGBD edge detection
technique11 dogRGBDEdgeDetection {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVert()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, dogRGBDFrag()));
	}
}
