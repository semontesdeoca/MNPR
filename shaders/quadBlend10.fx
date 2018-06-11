////////////////////////////////////////////////////////////////////////////////////////////////////
// quadBlend10.fx (HLSL)
// Brief: Blending algorithms
// Contributors: Santiago Montesdeoca
////////////////////////////////////////////////////////////////////////////////////////////////////
//    _     _                _ _             
//   | |__ | | ___ _ __   __| (_)_ __   __ _ 
//   | '_ \| |/ _ \ '_ \ / _` | | '_ \ / _` |
//   | |_) | |  __/ | | | (_| | | | | | (_| |
//   |_.__/|_|\___|_| |_|\__,_|_|_| |_|\__, |
//                                     |___/ 
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader provides alorithms for blending images such as:
// 1.- Blending from alpha of the blend texture
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
Texture2D gBlendTex;



//    _     _                _      __                               _       _           
//   | |__ | | ___ _ __   __| |    / _|_ __ ___  _ __ ___       __ _| |_ __ | |__   __ _ 
//   | '_ \| |/ _ \ '_ \ / _` |   | |_| '__/ _ \| '_ ` _ \     / _` | | '_ \| '_ \ / _` |
//   | |_) | |  __/ | | | (_| |   |  _| | | (_) | | | | | |   | (_| | | |_) | | | | (_| |
//   |_.__/|_|\___|_| |_|\__,_|   |_| |_|  \___/|_| |_| |_|    \__,_|_| .__/|_| |_|\__,_|
//                                                                    |_|                

// Contributor: Santiago Montesdeoca
// Blend image from alpha channel of blend texture
float4 blendCtrlAlphaFrag(vertexOutput i) : SV_Target {
	int3 loc = int3(i.pos.xy, 0);

	// get pixel values
	float4 renderTex = gColorTex.Load(loc);
	float4 blendTex = gBlendTex.Load(loc);
	float blendCtrl = saturate(blendTex.a*5.0);

	// blend colors
	float3 blendColor = lerp(renderTex.rgb, blendTex.rgb, blendCtrl.xxx);

	return float4(blendColor, renderTex.a+saturate(blendTex.a));
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// BLEND FROM ALPHA OF gBlendTex
technique11 blendFromAlpha {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVert()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, blendCtrlAlphaFrag()));
	}
}