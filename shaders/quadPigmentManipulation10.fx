////////////////////////////////////////////////////////////////////////////////////////////////////
// quadPigmentManipulation10.fx (HLSL)
// Brief: Pigment manipulation algorithms
// Contributors: Santiago Montesdeoca, Amir Semmo, Yee Xin Chiew
////////////////////////////////////////////////////////////////////////////////////////////////////
//          _                            _                             _             _       _   _             
//    _ __ (_) __ _ _ __ ___   ___ _ __ | |_     _ __ ___   __ _ _ __ (_)_ __  _   _| | __ _| |_(_) ___  _ __  
//   | '_ \| |/ _` | '_ ` _ \ / _ \ '_ \| __|   | '_ ` _ \ / _` | '_ \| | '_ \| | | | |/ _` | __| |/ _ \| '_ \ 
//   | |_) | | (_| | | | | | |  __/ | | | |_    | | | | | | (_| | | | | | |_) | |_| | | (_| | |_| | (_) | | | |
//   | .__/|_|\__, |_| |_| |_|\___|_| |_|\__|   |_| |_| |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|\___/|_| |_|
//   |_|      |___/                                                     |_|                                    
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides algorithms for pigment manipulation such as:
// 1.- Pigment density variations commonly found in transparent media (e.g. watercolor)
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
Texture2D gFilterTex;
Texture2D gControlTex;  // pigment control target


// VARIABLES
float3 gSubstrateColor = float3(1.0, 1.0, 1.0);


// MRT
struct fragmentOutput {
    float4 colorOutput : SV_Target0;
    float alphaOutput : SV_Target1;
};



//          _                            _           _                _ _         
//    _ __ (_) __ _ _ __ ___   ___ _ __ | |_      __| | ___ _ __  ___(_) |_ _   _ 
//   | '_ \| |/ _` | '_ ` _ \ / _ \ '_ \| __|    / _` |/ _ \ '_ \/ __| | __| | | |
//   | |_) | | (_| | | | | | |  __/ | | | |_    | (_| |  __/ | | \__ \ | |_| |_| |
//   | .__/|_|\__, |_| |_| |_|\___|_| |_|\__|    \__,_|\___|_| |_|___/_|\__|\__, |
//   |_|      |___/                                                         |___/ 

// Contributor: Santiago Montesdeoca
// Modifies the color based on the accumulated density (watercolor)
// -> Based on the color transmittance modification model of Bousseau et al. 2006 
//    and pigment turbulence model by Montesdeoca et al. 2017
//    [2006] Interactive Watercolor Rendering with Temporal Coherence and Abstraction
//    [2017] Art-directed watercolor stylization of 3D animations in real-time
float4 pigmentDensityWCFrag(vertexOutput i) : SV_Target {
    int3 loc = int3(i.pos.xy, 0);

    // get color target
    float4 renderTex = gColorTex.Load(loc);

    // get local density parameters
    float control = gControlTex.Load(loc).b;  // pigment control target (b)

    // calculate density
    float density = control + 1.0;

    // modify color
    float3 colorOutput = pow(abs(renderTex.rgb), density);  // color transmittance modification model
    colorOutput = lerp(gSubstrateColor, colorOutput, saturate(density));  // low density towards substrate color

    return float4(colorOutput, renderTex.a);
}

// Contributor: Amir Semmo
// Modifies the color based on the accumulated density (oil paint)
// -> Based on the color transmittance modification model of Bousseau et al. 2006 
//    and pigment turbulence model by Montesdeoca et al. 2017
//    [2006] Interactive Watercolor Rendering with Temporal Coherence and Abstraction
//    [2017] Art-directed watercolor stylization of 3D animations in real-time
fragmentOutput pigmentDensityOPFrag(vertexOutput i) : SV_Target{
    fragmentOutput result;
    int3 loc = int3(i.pos.xy, 0);

    // get color target
    float4 renderTex = gColorTex.Load(loc);
    float filterTex = gFilterTex.Load(loc).x;

    // get local density parameters
    float control = gControlTex.Load(loc).b;  // pigment control target (b)

    // calculate density
    float density = lerp(1.0, 2.0, control);

    // modify color
    float3 colorOut = pow(abs(renderTex.rgb), density);  // color transmittance modification model
    colorOut = lerp(gSubstrateColor, colorOut, saturate(1 + control));  // pigment turbulence model

    result.colorOutput = float4(colorOut, renderTex.a);
    result.alphaOutput = saturate(filterTex + control);

    return result;
}

// Contributor: Yee Xin Chiew
// Modifies the color based on the accumulated density (charcoal)
// -> Based on the color transmittance modification model of Bousseau et al. 2006 
//    and pigment turbulence model by Montesdeoca et al. 2017
//    [2006] Interactive Watercolor Rendering with Temporal Coherence and Abstraction
//    [2017] Art-directed watercolor stylization of 3D animations in real-time
float4 pigmentDensityCCFrag(vertexOutput i) : SV_Target{
    int3 loc = int3(i.pos.xy, 0);

    // get color target
    float4 renderTex = gColorTex.Load(loc);

    // get local density parameters
    float control = gControlTex.Load(loc).b;  // pigment control target (b)

    // calculate density
    float density = lerp(1.0, 2.0, control);

    // modify color
    float3 colorOutput = pow(abs(renderTex.rgb), density);  // color transmittance modification model
    colorOutput = lerp(gSubstrateColor, colorOutput, saturate(1 + (control*0.2)));  // pigment turbulence model

    return float4(colorOutput, renderTex.a);
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// [WC] - PIGMENT DENSITY
technique11 pigmentDensityWC {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVert()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, pigmentDensityWCFrag()));
    }
}

// [OP] - PIGMENT DENSITY
technique11 pigmentDensityOP {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVert()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, pigmentDensityOPFrag()));
    }
}

// [CC] - PIGMENT DENSITY
technique11 pigmentDensityCC {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVert()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, pigmentDensityCCFrag()));
    }
}