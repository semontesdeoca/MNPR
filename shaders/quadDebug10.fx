////////////////////////////////////////////////////////////////////////////////////////////////////
// quadDebug10.fx (HLSL)
// Brief: Debugging operations for MNPR
// Contributors: Santiago Montesdeoca, Amir Semmo
////////////////////////////////////////////////////////////////////////////////////////////////////
//        _      _                 
//     __| | ___| |__  _   _  __ _ 
//    / _` |/ _ \ '_ \| | | |/ _` |
//   | (_| |  __/ |_) | |_| | (_| |
//    \__,_|\___|_.__/ \__,_|\__, |
//                           |___/ 
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides some debugging operations for MNPR
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"
#include "include\\quadColorTransform.fxh"

// VARIABLES
float gMnprGamma;
float4 gColorChannels = float4( 1.0, 1.0, 1.0, 0.0 );
float  gColorTransform = 0.0; // 0.0: keep input, 1.0: RGB -> Lab, 2.0: Lab -> RGB



//        _      _                          _                            _     
//     __| | ___| |__  _   _  __ _      ___| |__   __ _ _ __  _ __   ___| |___ 
//    / _` |/ _ \ '_ \| | | |/ _` |    / __| '_ \ / _` | '_ \| '_ \ / _ \ / __|
//   | (_| |  __/ |_) | |_| | (_| |   | (__| | | | (_| | | | | | | |  __/ \__ \
//    \__,_|\___|_.__/ \__,_|\__, |    \___|_| |_|\__,_|_| |_|_| |_|\___|_|___/
//                           |___/                                             

// Contributors: Santiago Montesdeoca, Amir Semmo
// debugs the individual channels, presenting only selected channels and performing 
// simple operations on them to visualize wrong values
float4 debugPresentFrag(vertexOutput i) : SV_Target {
    int3 loc = int3(i.pos.xy, 0);
    float4 renderTex = gColorTex.Load(loc);
    
    if(gColorTransform == 1.0) {
        renderTex = float4(rgb2lab(renderTex.rgb), renderTex.a);
    }
    else if(gColorTransform == 2.0) {
        renderTex = float4(lab2rgb(renderTex.rgb), renderTex.a);
    }

    if (gMnprGamma > 0.5) {
        renderTex.rgb = pow(renderTex.rgb, 0.454545455);  // [1/2.2]
    }

    if (gColorChannels.a > 0) {
        return float4(renderTex.a, renderTex.a, renderTex.a, renderTex.a);
    } else {
        return float4(gColorChannels.r * renderTex.r, gColorChannels.g * renderTex.g, gColorChannels.b * renderTex.b, renderTex.a);
    }


}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// MNPR debug present
technique11 debugPresentMNPR {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVert()));
        SetPixelShader(CompileShader(ps_5_0, debugPresentFrag()));
    }
}
