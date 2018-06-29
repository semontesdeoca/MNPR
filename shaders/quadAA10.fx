////////////////////////////////////////////////////////////////////////////////////////////////////
// quadAA10.fx (HLSL)
// Brief: Anti-aliasing algorithms for MNPR
// Contributors: Shi Hezi, Vinayak Teoh
////////////////////////////////////////////////////////////////////////////////////////////////////
//                _   _             _ _           _             
//     __ _ _ __ | |_(_)       __ _| (_) __ _ ___(_)_ __   __ _ 
//    / _` | '_ \| __| |_____ / _` | | |/ _` / __| | '_ \ / _` |
//   | (_| | | | | |_| |_____| (_| | | | (_| \__ \ | | | | (_| |
//    \__,_|_| |_|\__|_|      \__,_|_|_|\__,_|___/_|_| |_|\__, |
//                                                        |___/ 
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides different anti-aliasing algorithms for MNPR
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

static float2 inverseScreenSize = float2(1.0 / gScreenSize.x, 1.0 / gScreenSize.y);

#define EDGE_THRESHOLD_MIN 0.0312
#define EDGE_THRESHOLD_MAX 0.125
#define THRESHOLD (1.0/4.0)
#define ITERATIONS 12
#define SUBPIXEL_QUALITY 0.75

// VARIABLES
float gRenderScale = 1.0;
float gAntialiasingQuality = 1.0f;

static float fxaaQualityPs[12] = {2.0, 2.0, 2.0, 2.0, 2.0, 3.0, 4.0, 4.0, 4.0, 4.0, 8.0, 16.0};



//                                        _      
//    _ __ ___  ___  __ _ _ __ ___  _ __ | | ___ 
//   | '__/ _ \/ __|/ _` | '_ ` _ \| '_ \| |/ _ \
//   | | |  __/\__ \ (_| | | | | | | |_) | |  __/
//   |_|  \___||___/\__,_|_| |_| |_| .__/|_|\___|
//                                 |_|           
// Resample any up- or down-sampled target to fit the viewport dimensions.
// Anti-aliasing is achieved by using a bilinear filtering when sampling the targets.
float4 resampleFrag(vertexOutputSampler i) : SV_Target {
	return gColorTex.Sample(gSampler, i.uv);
}



//    _______  __    _        _    
//   |  ___\ \/ /   / \      / \   
//   | |_   \  /   / _ \    / _ \  
//   |  _|  /  \  / ___ \  / ___ \ 
//   |_|   /_/\_\/_/   \_\/_/   \_\
//                                 
// Contributors: Shi Hezi, Vinayak Teoh
// Perform FXAA v3.11 anti-aliasing
// -> Based on FXAA of Timothy Lottes 2009
//    [2009] FXAA

// Computations in FXAA rely on luminosity of pixels read from the main render target,
// expressed as grey levels between 0 -> 1. 
float rgb2lum(float3 rgb) {
	return sqrt(dot(rgb, float3(0.299, 0.587, 0.114)));
}

float4 texOffset(Texture2D tex, SamplerState texSmpl, float2 uv, in float2 offset) {
	float4 color = tex.Sample(texSmpl, uv + (offset / gScreenSize));
	return color;
}

float fxaaQuality(int i) {
	return fxaaQualityPs[i] / gAntialiasingQuality;
}

float4 FXAAFrag(vertexOutputSampler i) : SV_Target
{
	if (gAntialiasingQuality == 0.0f) {
		return gColorTex.Sample(gSampler, i.uv);
	}
	
	// DEBUG:
	//return gColorTex.Sample(gSampler, i.uv);

	float4 outputColor;
	float offsetScale = 1.0 / pow(gRenderScale, 2.0);

	/*----------------------------------------------------------------------------
	DETECT WHERE TO APPLY AA
	Early exit if local contrast is below edge detection limit
	------------------------------------------------------------------------------*/
	float4 colorCenter = texOffset(gColorTex, gSampler, i.uv, float2(0, 0) * offsetScale); // south (down)
	float3 colorN = texOffset(gColorTex, gSampler, i.uv, float2(0.0, 1.0) * offsetScale).xyz; // north (up)
	float3 colorS = texOffset(gColorTex, gSampler, i.uv, float2(0.0, -1.0) * offsetScale).xyz; // south (down)
	float3 colorE = texOffset(gColorTex, gSampler, i.uv, float2(1.0, 0.0) * offsetScale).xyz; // east (right)
	float3 colorW = texOffset(gColorTex, gSampler, i.uv, float2(-1.0, 0.0) * offsetScale).xyz; // left (west)

	// luminance at the center & four direct neighbours of the current fragment
	float lumCenter = rgb2lum(colorCenter.rgb);
	float lumN = rgb2lum(colorN);
	float lumS = rgb2lum(colorS);
	float lumE = rgb2lum(colorE);
	float lumW = rgb2lum(colorW);

	// find the maximum and minumum luminance around the current fragments through the use of the NSEW lums
	float lumRangeMin = min(lumCenter, min(min(lumS, lumE), min(lumS, lumW)));
	float lumRangeMax = max(lumCenter, max(max(lumS, lumE), max(lumS, lumW)));

	// compute the luminosity range delta between max and min
	float lumRange = lumRangeMax - lumRangeMin;

	// if the luminosity variation is lower than that a threshold (or if we are in a really dark area), 
	// we are definitely NOT on an edge, do not apply AA.
	if (lumRange < max(EDGE_THRESHOLD_MIN, lumRangeMax * EDGE_THRESHOLD_MAX))
	{
		outputColor = float4(colorCenter);
		return outputColor;
	}


	/*----------------------------------------------------------------------------
	CHOOSE VERTICAL OR HORIZONTAL SEARCH
	Estimating gradient and choosing edge direction for each
	pixel detected as being part of an edge, check if the edge is
	vertical or horizontal.
	------------------------------------------------------------------------------*/
	float3 colorNW = texOffset(gColorTex, gSampler, i.uv, float2(-1.0, 1.0) * offsetScale).rgb;
	float3 colorNE = texOffset(gColorTex, gSampler, i.uv, float2(1.0, 1.0) * offsetScale).rgb;
	float3 colorSW = texOffset(gColorTex, gSampler, i.uv, float2(-1.0, -1.0) * offsetScale).rgb;
	float3 colorSE = texOffset(gColorTex, gSampler, i.uv, float2(1.0, -1.0) * offsetScale).rgb;

	// query the 4 remaining corner lums (6 axis style)
	float lumNW = rgb2lum(colorNW); // northwest (up left)
	float lumNE = rgb2lum(colorNE); // northeast (up right)
	float lumSW = rgb2lum(colorSW); // southwest (down left)
	float lumSE = rgb2lum(colorSE); // southeast (down right)

	// combine the four edge lums using intermediary vars for future computations with the same values.
	float lumNS = lumN + lumS; // up + down
	float lumEW = lumE + lumW; // right + left

	// combine for the corners as well
	float lumWCorners = lumSW + lumNW; // west corners (south west + north west)
	float lumSCorners = lumSW + lumSE; // south corners (south west + south east)
	float lumECorners = lumSE + lumNE; // east corners (south east + north east)
	float lumNCorners = lumNE + lumNW; // north corners (north east + south west)

	// compute an estimation of the gradient along the horizontal and vertical axis
	float edgeHorizontal =
		abs(-2.0 * lumW + lumWCorners) +
		abs(-2.0 * lumCenter + lumNS) * 2.0 +
		abs(-2.0 * lumE + lumECorners);
	float edgeVertical =
		abs(-2.0 * lumN + lumNCorners) +
		abs(-2.0 * lumCenter + lumEW) * 2.0 +
		abs(-2.0 * lumS + lumSCorners);


	/*----------------------------------------------------------------------------
	CHOOSING THE EDGE ORIENTATION
	the current pixel is not necessarily exactly on the edge, so we need
	to determine in which orientation, orthogonal to the edge direction is
	the real edge border. the gradient on each side of the current pixel
	is computed, where it is the steepest probably lies at the edge border.
	------------------------------------------------------------------------------*/
	// is the local edge horizontal or vertical?
	bool bIsHorizontal = edgeHorizontal >= edgeVertical;
	float lum1 = bIsHorizontal ? lumS : lumW;
	float lum2 = bIsHorizontal ? lumN : lumE;

	// compute the gradients in this direction
	float grad1 = lum1 - lumCenter;
	float grad2 = lum2 - lumCenter;

	// which direction is the steepest?
	bool bIsLum1Steepest = abs(grad1) >= abs(grad2);

	// gradient in the corresponding direction, normalized.
	float gradScaled = 0.25 * max(abs(grad1), abs(grad2));

	// choose the step size (one pixel per step) according to the edge direction
	float stepSize = bIsHorizontal ? inverseScreenSize.y : inverseScreenSize.x;

	// average luminance in the correct direction
	float lumLocalAvg = 0.0;

	if (bIsLum1Steepest)
	{
		// switch the direction
		stepSize = -stepSize;
		lumLocalAvg = 0.5 * (lum1 + lumCenter);
	}
	else
	{
		lumLocalAvg = 0.5 * (lum2 + lumCenter);
	}

	// shift the UV in the correct direction by half a pixel [or maybe a quarter of a pixel (?)]
	float2 currentUV = i.uv;
	if (bIsHorizontal)
	{
		currentUV.y += stepSize * 0.5;
	}
	else
	{
		currentUV.x += stepSize * 0.5;
	}


	/*----------------------------------------------------------------------------
	FIRST ITERATION EXPLORATION
	explore along the main axis of the edge, step one pixel in both
	direction & query the luminance at the new coordinates. then compute
	the variation of the luminance with respect to the average luminance
	from the previous step. if the variation is greater than the local
	gradient, we have reached the end of the edge in this direction and we
	should stop. otherwise, keep increase UV offset by one px.
	------------------------------------------------------------------------------*/
	// compute offset (for each iteration step) in the right direction
	float2 offset = bIsHorizontal ? float2(inverseScreenSize.x, 0.0) : float2(0.0, inverseScreenSize.y);

	// compute the UVs to explore on each side of the edge, orthogonally. (is multiplying by the offsetScale necessary?)
	float2 uv1 = currentUV - offset * offsetScale;
	float2 uv2 = currentUV + offset * offsetScale;

	// read the luminance at both current extremities of the exploration segment, and compute the delta WRT to the local average luminance.
	float lumEnd1 = rgb2lum(gColorTex.Sample(gSampler, uv1).rgb);
	float lumEnd2 = rgb2lum(gColorTex.Sample(gSampler, uv2).rgb);
	lumEnd1 -= lumLocalAvg;
	lumEnd2 -= lumLocalAvg;

	// if the luminance deltas at the current extremities are larger than the local gradient, we have reached the side of the edge.
	bool bReached1 = abs(lumEnd1) >= gradScaled;
	bool bReached2 = abs(lumEnd2) >= gradScaled;
	bool bReachedBoth = bReached1 && bReached2;

	// if the side if not reached, we continue to explore in this direction
	if (!bReached1)
	{
		uv1 -= offset;
	}

	if (!bReached2)
	{
		uv2 += offset;
	}


	/*----------------------------------------------------------------------------
	ITERATING
	------------------------------------------------------------------------------*/
	if (!bReachedBoth)
	{
		for (int i = 0; i < ITERATIONS; i++)
		{
			// if needed, read luminance in the 1st direction and compute delta
			if (!bReached1)
			{
				float3 c1 = gColorTex.Sample(gSampler, uv1).rgb;
				lumEnd1 = rgb2lum(c1);
				lumEnd1 = lumEnd1 - lumLocalAvg;
			}

			// if needed, read luminance in the opposite direction and compute delta
			if (!bReached2)
			{
				float3 c2 = gColorTex.Sample(gSampler, uv2).rgb;
				lumEnd2 = rgb2lum(c2);
				lumEnd2 = lumEnd2 - lumLocalAvg;
			}

			// if the luminance deltas at the current extremities are larger than the local gradient, we have reached the side of the edge.
			bReached1 = abs(lumEnd1) >= gradScaled;
			bReached2 = abs(lumEnd2) >= gradScaled;
			bReachedBoth = bReached1 && bReached2;

			// if the side if not reached, we continue to explore in this direction, with a variable quality.
			if (!bReached1)
			{
				uv1 -= offset * fxaaQualityPs[i];
			}

			if (!bReached2)
			{
				uv2 += offset * fxaaQualityPs[i];
			}

			// if both sides have been reached, stop the exploration
			if (bReachedBoth)
			{
				break;
			}
		}
	}


	/*----------------------------------------------------------------------------
	ESTIMATING OFFSET
	------------------------------------------------------------------------------*/
	// compute the distances to each extremity of the edge
	float dist1 = bIsHorizontal ? (i.uv.x - uv1.x) : (i.uv.y - uv1.y);
	float dist2 = bIsHorizontal ? (uv2.x - i.uv.x) : (uv2.y - i.uv.y);

	// in which direction is the extremity of the edge closer?
	bool bIsDirection1 = dist1 < dist2;
	float distFinal = min(dist1, dist2);

	// length of the edge
	float edgeThickness = (dist1 + dist2);

	// uv offset: read in the direction of the closest side of the edge
	float pixelOffset = -distFinal / edgeThickness + 0.5;

	// is the luminance at center smaller than the local average?
	bool bIsLumCenterSmaller = lumCenter < lumLocalAvg;

	// if the luminance at the center is smaller than at its neighbour,
	// the delta luminance at each end should be positive
	// (same variation)
	// (in the direction of the closer side of the edge)
	bool bCorrectVariation = ((bIsDirection1 ? lumEnd1 : lumEnd2) < 0.0) != bIsLumCenterSmaller;
	//if (bCorrectVariation)
	//{	
	//    outputColor = float4(0.0, 0.0, 1.0, 1.0);
	//    return outputColor;
	//}

	// if the luminance variation is incorrect, do not offset.
	float finalOffset = bCorrectVariation ? pixelOffset : 0.0;


	/*----------------------------------------------------------------------------
	SUBPIXEL ANTI-ALIASING
	------------------------------------------------------------------------------*/
	// sub-pixel shifting
	// full weighted average of the luminance over the 3x3 neighbourhood
	float lumAverage = (1.0 / 12.0) * (2.0 * (lumNS + lumEW) + lumWCorners + lumECorners);

	// ratio of the delta between the global average and the center luminance, 
	// over the luminance range in the 3x3 neighborhood.
	float subPixelOffset1 = clamp(abs(lumAverage - lumCenter) / lumRange, 0.0, 1.0);
	float subPixelOffset2 = (-2.0 * subPixelOffset1 + 3.0) * subPixelOffset1 * subPixelOffset1;

	// compute a sub-pixel offset based on this delta
	float subPixelOffsetFinal = subPixelOffset2 * subPixelOffset2 * SUBPIXEL_QUALITY;

	// pick the biggest of the two offsets
	finalOffset = max(finalOffset, subPixelOffsetFinal);


	/*----------------------------------------------------------------------------
	FINAL READ
	------------------------------------------------------------------------------*/
	float2 finalUV = i.uv;
	if (bIsHorizontal)
	{
		finalUV.y += finalOffset * stepSize;
	}
	else
	{
		finalUV.x += finalOffset * stepSize;
	}

	// read the color at the new uv coordinates and use it
	return gColorTex.SampleLevel(gSampler, finalUV, 0.0);
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// RESAMPLE (DOWN/UPSAMPLE)
technique11 resample {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetPixelShader(CompileShader(ps_5_0, resampleFrag()));
	}
}

// FXAA
technique11 FXAA {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetPixelShader(CompileShader(ps_5_0, FXAAFrag()));
	}
}
