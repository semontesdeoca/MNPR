////////////////////////////////////////////////////////////////////////////////////////////////////
// quadTest10.fx (HLSL)
// Brief: test shader for MNPR
// Contributors: You!
////////////////////////////////////////////////////////////////////////////////////////////////////
//    _            _
//   | |_ ___  ___| |_
//   | __/ _ \/ __| __|
//   | ||  __/\__ \ |_
//    \__\___||___/\__|
//
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides a testing ground for MNPR shader passes
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
// Texture2D gSubstrateTex;
// Texture2D gControlTex;

// VARIABLES
float gAwesomeParameter = 1.0;

// FUNCTIONS (just an example)
float awesomeMultiplier(float4 color) {
    return color * gAwesomeParameter;
}


//        _               _
//    ___| |__   __ _  __| | ___ _ __ ___
//   / __| '_ \ / _` |/ _` |/ _ \ '__/ __|
//   \__ \ | | | (_| | (_| |  __/ |  \__ \
//   |___/_| |_|\__,_|\__,_|\___|_|  |___/
//
// Fragment/pixel shaders are functions that runs at each pixels. These can write
// on up to 8 render targets at the same time. Check the quadAdjustLoad10.fx
// shader for an example of multiple render target (MRT) shaders
float4 testFrag(vertexOutputSampler i) : SV_Target {
	int3 loc = int3(i.pos.xy, 0);
  // loading pixel color is typically faster than sampling
	float4 renderTex = gColorTex.Load(loc);
  // Sampling pixel color is more powerful than loading and is in UV space [0-1]
  // float4 renderTex = gColorTex.Sample(gSampler, i.uv);

  // you can perform any type of operation within a shader, this one is written
  // in HLSL, you can find a Reference Guide at the link below:
  // https://docs.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-reference

  // here we simply return the same pixel color that we previously read
	return renderTex;
}


//    _            _           _
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|
// A technique defines the combination of Vertex, Geometry and Fragment/Pixel
// shader that runs to draw whatever is assigned with the shader.
technique11 testTechnique {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, testFrag()));
	}
}
