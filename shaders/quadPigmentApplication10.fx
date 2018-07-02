////////////////////////////////////////////////////////////////////////////////////////////////////
// quadPigmentApplication10.fx (HLSL)
// Brief: Defining how pigments are applied
// Contributors: Santiago Montesdeoca, Amir Semmo
////////////////////////////////////////////////////////////////////////////////////////////////////
//          _                            _                         _ _           _   _
//    _ __ (_) __ _ _ __ ___   ___ _ __ | |_      __ _ _ __  _ __ | (_) ___ __ _| |_(_) ___  _ __
//   | '_ \| |/ _` | '_ ` _ \ / _ \ '_ \| __|    / _` | '_ \| '_ \| | |/ __/ _` | __| |/ _ \| '_ \
//   | |_) | | (_| | | | | | |  __/ | | | |_    | (_| | |_) | |_) | | | (_| (_| | |_| | (_) | | | |
//   | .__/|_|\__, |_| |_| |_|\___|_| |_|\__|    \__,_| .__/| .__/|_|_|\___\__,_|\__|_|\___/|_| |_|
//   |_|      |___/                                   |_|   |_|
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides different algorithms for pigment application in different media
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
Texture2D gFilterTex;
Texture2D gSubstrateTex;
Texture2D gControlTex;


// VARIABLES
float3 gSubstrateColor = float3(1.0, 1.0, 1.0);
float gPigmentDensity;
float gDryBrushThreshold;


// MRT
struct fragmentOutput {
    float4 colorOutput : SV_Target0;
    float alphaOutput : SV_Target1;
};



//                 _                            _         _                  _                    _
//   __      _____| |_           __ _ _ __   __| |     __| |_ __ _   _      | |__  _ __ _   _ ___| |__
//   \ \ /\ / / _ \ __|____     / _` | '_ \ / _` |    / _` | '__| | | |_____| '_ \| '__| | | / __| '_ \
//    \ V  V /  __/ ||_____|   | (_| | | | | (_| |   | (_| | |  | |_| |_____| |_) | |  | |_| \__ \ | | |
//     \_/\_/ \___|\__|         \__,_|_| |_|\__,_|    \__,_|_|   \__, |     |_.__/|_|   \__,_|___/_| |_|
//                                                               |___/
// Contributor: Santiago Montesdeoca
// [WC] - Defines how watercolor is applied:
// - Wet, accumulating pigments at the valleys of the paper (aka substrate granulation)
// - Dry, showing pigments that have only been applied at the peaks of the paper
// -> Based on the pigment application model by Montesdeoca et al. 2017
//    [2017] Edge- and substrate-based effects for watercolor stylization
float4 pigmentApplicationWCFrag(vertexOutput i) : SV_Target {
    int3 loc = int3(i.pos.xy, 0);  // coordinates for loading

    float4 renderTex = gColorTex.Load(loc);
    float heightMap = gSubstrateTex.Load(loc).b;  // heightmap is embedded in the blue channel of the surfaceTex
    float application = gControlTex.Load(loc).g;  // dry brush --- wet brush, pigments control target (r)
    float mask = renderTex.a;

    // check if its not the substrate color
    if (mask < 0.01) {
        return renderTex;
    }

    //calculate drybrush
    float dryDiff = heightMap + application;
    if (dryDiff < 0) {
        return lerp(renderTex, float4(gSubstrateColor, renderTex.a), saturate(abs(dryDiff)*gDryBrushThreshold));
    } else {
        // calculate density accumulation (1 granulate, 0 default)
        application = (abs(application) + 0.2);  // default is granulated (// 1.2 granulate, 0.2 default)

        //more accumulation on brighter areas
        application = lerp(application, application * 5, luminance(renderTex.rgb));  // deprecated
        //application = lerp(application, application * 4, luminance(renderTex.rgb));  // new approach

        //modulate heightmap to be between 0.8-1.0 (for montesdeoca et al. 2016)
        heightMap = (heightMap * 0.2) + 0.8;  // deprecated
    }

    //montesdeoca et al.
    float accumulation = 1 + (gPigmentDensity * application * (1 - (heightMap)));

    //calculate denser color output
    float3 colorOut = pow(abs(renderTex.rgb), accumulation);

    // don't granulate/dry-brush if the renderTex is similar to substrate color
    float colorDiff = saturate(length(renderTex - gSubstrateColor) * 5);
    colorOut = lerp(renderTex, colorOut, colorDiff.xxx);
    return float4(colorOut, renderTex.a);
}



//        _              _                    _
//     __| |_ __ _   _  | |__  _ __ _   _ ___| |__
//    / _` | '__| | | | | '_ \| '__| | | / __| '_ \
//   | (_| | |  | |_| | | |_) | |  | |_| \__ \ | | |
//    \__,_|_|   \__, | |_.__/|_|   \__,_|___/_| |_|
//               |___/
// [OP] - Defines how oil is applied:
// - Thick, accumulating pigments at the valleys of the paper
// - Dry, showing pigments that have only been applied at the peaks of the paper
// -> Based on the watercolor dry brush, from the pigment application model by Montesdeoca et al. 2017
//    [2017] Edge- and substrate-based effects for watercolor stylization
fragmentOutput pigmentApplicationOPFrag(vertexOutput i) {
    fragmentOutput result;
    int3 loc = int3(i.pos.xy, 0);  // coordinates for loading

    float4 renderTex = gColorTex.Load(loc);
    float filterTex = gFilterTex.Load(loc).x;
    float heightMap = gSubstrateTex.Load(loc).b;  // heightmap is embedded in the blue channel of the surfaceTex
    float application = gControlTex.Load(loc).g;  // dry brush --- wet brush, unpack pigments control target (x)
    float mask = renderTex.a;

    // check if its not the substrate
    if (mask < 0.01) {
        result.colorOutput = renderTex;
        result.alphaOutput = filterTex;
        return result;
    }

    //calculate drybrush
    float dryBrush = -application;
    float dryDiff = heightMap - dryBrush;
    if (dryDiff < 0) {
        float alpha = saturate(abs(dryDiff)*gDryBrushThreshold);
        result.colorOutput = lerp(renderTex, float4(gSubstrateColor, renderTex.a), alpha);
        result.alphaOutput = filterTex * (1.0 - alpha);
        return result;
    }
    else {
        // calculate density accumulation (-1 granulate, 0 default)
        dryBrush = (abs(dryBrush) + 0.2);  // default is granulated (// 1.2 granulate, 0.2 default)

        //more accumulation on brighter areas
        dryBrush = lerp(dryBrush, dryBrush * 5, luminance(renderTex.rgb));

        //modulate heightmap to be between 0.8-1.0 (for montesdeoca et al.)
        heightMap = (heightMap * 0.2) + 0.8;
    }

    //montesdeoca et al.
    float accumulation = 1 + (dryBrush * (1 - (heightMap)) * gPigmentDensity);

    //calculate denser color output
    float3 colorOut = pow(abs(renderTex.rgb), accumulation);

    // don't granulate/dry-brush if the renderTex is similar to substrate color
    float colorDiff = saturate(length(renderTex - gSubstrateColor) * 5);
    colorOut = lerp(renderTex, colorOut, colorDiff.xxx);

    result.colorOutput = float4(colorOut, renderTex.a);
    result.alphaOutput = filterTex;
    return result;
}



//    _            _           _
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|
// [WC] - PIGMENT APPLICATION
technique11 pigmentApplicationWC {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVert()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, pigmentApplicationWCFrag()));
    }
}
// [OP] - PIGMENT APPLICATION
technique11 pigmentApplicationOP {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVert()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, pigmentApplicationOPFrag()));
    }
}
