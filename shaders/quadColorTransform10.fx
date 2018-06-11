////////////////////////////////////////////////////////////////////////////////////////////////////
// quadColorTransform10.fx (HLSL)
// Brief: Color space transformations
// Contributors: Amir Semmo
////////////////////////////////////////////////////////////////////////////////////////////////////
//              _              _                        __                            _   _             
//     ___ ___ | | ___  _ __  | |_ _ __ __ _ _ __  ___ / _| ___  _ __ _ __ ___   __ _| |_(_) ___  _ __  
//    / __/ _ \| |/ _ \| '__| | __| '__/ _` | '_ \/ __| |_ / _ \| '__| '_ ` _ \ / _` | __| |/ _ \| '_ \ 
//   | (_| (_) | | (_) | |    | |_| | | (_| | | | \__ \  _| (_) | |  | | | | | | (_| | |_| | (_) | | | |
//    \___\___/|_|\___/|_|     \__|_|  \__,_|_| |_|___/_|  \___/|_|  |_| |_| |_|\__,_|\__|_|\___/|_| |_|
//                                                                                                      
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides techniques for color space transformations in MNPR
// 1.- RGB -> LAB
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"
#include "include\\quadColorTransform.fxh"

// TEXTURES


// VARIABLES



//              _    ____  _       _     
//    _ __ __ _| |__|___ \| | __ _| |__  
//   | '__/ _` | '_ \ __) | |/ _` | '_ \ 
//   | | | (_| | |_) / __/| | (_| | |_) |
//   |_|  \__, |_.__/_____|_|\__,_|_.__/ 
//        |___/                          

// Contributor: Amir Semmo
// Color transformation
float4 rgb2labFrag(vertexOutputSampler i) : SV_Target{
	float4 c_rgb = gColorTex.Sample(gSampler, i.uv);
	float4 c_lab = float4(rgb2lab(c_rgb.rgb), c_rgb.a);

	return c_lab;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// RGB2LAB COLOR TRANSFORMATION
technique11 rgb2labTransform {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, rgb2labFrag()));
	}
}