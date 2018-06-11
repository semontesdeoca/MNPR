////////////////////////////////////////////////////////////////////////////////////////////////////
// quadEdgeManipulation10.fx (HLSL)
// Brief: Edge manipulation algorithms
// Contributors: Santiago Montesdeoca
////////////////////////////////////////////////////////////////////////////////////////////////////
//             _                                      _             _       _   _             
//     ___  __| | __ _  ___     _ __ ___   __ _ _ __ (_)_ __  _   _| | __ _| |_(_) ___  _ __  
//    / _ \/ _` |/ _` |/ _ \   | '_ ` _ \ / _` | '_ \| | '_ \| | | | |/ _` | __| |/ _ \| '_ \ 
//   |  __/ (_| | (_| |  __/   | | | | | | (_| | | | | | |_) | |_| | | (_| | |_| | (_) | | | |
//    \___|\__,_|\__, |\___|   |_| |_| |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|\___/|_| |_|
//               |___/                                 |_|                                    
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader provides alorithms for edge manipulation such as:
// 1.- Gradient edge darkening commonly found in Watercolors [WC]
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
Texture2D gEdgeTex;
Texture2D gControlTex;


// VARIABLES
float3 gSubstrateColor = float3(1.0, 1.0, 1.0);
float gEdgeIntensity = 1.0;



//                        _ _            _                _                 
//     __ _ _ __ __ _  __| (_) ___ _ __ | |_      ___  __| | __ _  ___  ___ 
//    / _` | '__/ _` |/ _` | |/ _ \ '_ \| __|    / _ \/ _` |/ _` |/ _ \/ __|
//   | (_| | | | (_| | (_| | |  __/ | | | |_    |  __/ (_| | (_| |  __/\__ \
//    \__, |_|  \__,_|\__,_|_|\___|_| |_|\__|    \___|\__,_|\__, |\___||___/
//    |___/                                                 |___/           

// Contributor: Santiago Montesdeoca
// [WC] - Modifies the color at the edges using previously calculated edge gradients
// -> Based on the gaps & overlaps model by Montesdeoca et al. 2017
//    [2017] Art-directed watercolor stylization of 3D animations in real-time
float4 gradientEdgesWCFrag(vertexOutput i) : SV_Target{
	int3 loc = int3(i.pos.xy, 0); // coordinates for loading

	// get pixel values
	float4 renderTex = gColorTex.Load(loc);
	float2 edgeBlur = gEdgeTex.Load(loc).ga;
	float ctrlIntensity = gControlTex.Load(loc).r;  // edge control target (r)
	
	// calculate edge intensity
	if (ctrlIntensity > 0) {
		ctrlIntensity *= 5;
	}
	float paintedIntensity = 1 + ctrlIntensity;
	float dEdge = edgeBlur.x * gEdgeIntensity * paintedIntensity;


	// EDGE MODULATION
	// get rid of edges with color similar to substrate
	dEdge = lerp(0.0, dEdge, saturate(length(renderTex.rgb - gSubstrateColor)*5.0));
	// get rid of edges at bleeded areas
	dEdge = lerp(0.0, dEdge, saturate(1.0 - (edgeBlur.y*3.0)));

	// color modification model
	float density = 1.0 + dEdge;
	float3 darkenedEdgeCM = pow(renderTex.rgb, density);

	return float4(darkenedEdgeCM, renderTex.a);
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// [WC] - GRADIENT EDGES (EDGE DARKENING)
technique11 gradientEdgesWC {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVert()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, gradientEdgesWCFrag()));
	}
}