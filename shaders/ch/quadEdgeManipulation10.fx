////////////////////////////////////////////////////////////////////////////////////////////////////
// quadEdgeManipulation10.fx (HLSL)
// Brief: Edge manipulation algorithms
// Contributors: Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//             _                                      _             _       _   _             
//     ___  __| | __ _  ___     _ __ ___   __ _ _ __ (_)_ __  _   _| | __ _| |_(_) ___  _ __  
//    / _ \/ _` |/ _` |/ _ \   | '_ ` _ \ / _` | '_ \| | '_ \| | | | |/ _` | __| |/ _ \| '_ \ 
//   |  __/ (_| | (_| |  __/   | | | | | | (_| | | | | | |_) | |_| | | (_| | |_| | (_) | | | |
//    \___|\__,_|\__, |\___|   |_| |_| |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|\___/|_| |_|
//               |___/                                 |_|                                    
////////////////////////////////////////////////////////////////////////////////////////////////////
// Edge manipulation effects for charcoal stylization.
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gEdgeBlurControlTex;
Texture2D gControlTex;
Texture2D gBlendTex;
Texture2D gStylizationTex;
Texture2D gEdgeSoftenTex;


// OUTPUT
struct fragmentOutput {
	float4 blurOutput : SV_Target0;
};


//             _               __ _ _ _            
//     ___  __| | __ _  ___   / _(_) | |_ ___ _ __ 
//    / _ \/ _` |/ _` |/ _ \ | |_| | | __/ _ \ '__|
//   |  __/ (_| | (_| |  __/ |  _| | | ||  __/ |   
//    \___|\__,_|\__, |\___| |_| |_|_|\__\___|_|   
//               |___/                           

// Contributors: Yee Xin Chiew
// Filtering operation for edge softening effect
fragmentOutput edgeBlurFilter(vertexOutput i) : SV_Target {
	int3 loc = int3(i.pos.xy, 0);
	fragmentOutput result;
	
	float4 stylizationTex = gStylizationTex.Load(loc);
	float4 edgeSoftenTex = gEdgeSoftenTex.Load(loc);
	float softenEdges = gEdgeBlurControlTex.Load(loc).r;
	
	result.blurOutput = lerp(stylizationTex, edgeSoftenTex, saturate(softenEdges * 3.0));
	return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// EDGE SOFTENING EFFECT
technique11 edgeFilter {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, edgeBlurFilter()));
	}
}