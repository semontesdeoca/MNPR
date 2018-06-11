////////////////////////////////////////////////////////////////////////////////////////////////////
// quadSeparable10.fx (HLSL)
// Brief: Separable filters for watercolor stylization
// Contributors: Santiago Montesdeoca
////////////////////////////////////////////////////////////////////////////////////////////////////
//                                   _     _                        _                     _            
//    ___  ___ _ __   __ _ _ __ __ _| |__ | | ___    __      ____ _| |_ ___ _ __ ___ ___ | | ___  _ __ 
//   / __|/ _ \ '_ \ / _` | '__/ _` | '_ \| |/ _ \   \ \ /\ / / _` | __/ _ \ '__/ __/ _ \| |/ _ \| '__|
//   \__ \  __/ |_) | (_| | | | (_| | |_) | |  __/    \ V  V / (_| | ||  __/ | | (_| (_) | | (_) | |   
//   |___/\___| .__/ \__,_|_|  \__,_|_.__/|_|\___|     \_/\_/ \__,_|\__\___|_|  \___\___/|_|\___/|_|   
//            |_|                                                                                      
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides separable filters to achieve the following:
// - Bleeding blur that will be blended later on to generate color bleeding
// - Extend the edges to converge edges into gaps and overlaps
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "..\\include\\quadCommon.fxh"

// TEXTURES
Texture2D gEdgeTex;
Texture2D gDepthTex;
Texture2D gEdgeControlTex;
Texture2D gAbstractionControlTex;


// VARIABLES
float gRenderScale = 1.0;
float gBleedingThreshold = 0.0002;
float gEdgeDarkeningKernel = 3;
float gGapsOverlapsKernel = 3;
float gBleedingRadius = 20;
float gGaussianWeights[161];  // max 40 bleeding radius (supersampled would be 80)


// MRT output struct
struct fragmentOutput {
    float4 bleedingBlur : SV_Target0;
    float4 darkenedEdgeBlur : SV_Target1;
};



//     __                  _   _                 
//    / _|_   _ _ __   ___| |_(_) ___  _ __  ___ 
//   | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
//   |  _| |_| | | | | (__| |_| | (_) | | | \__ \
//   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
//
// SIGMOID WEIGHT
float sigmoidWeight(float x) {
    float weight = 1.0 - x;  // inverse normalized gradient | 0...0,5...1...0,5...0

    weight = weight * 2.0 - 1.0;  // increase amplitude by 2 and shift by -1 | -1...0...1...0...-1 (so that 0,5 in the gradient is not 0
    weight = (-weight * abs(weight) * 0.5) + weight + 0.5;  // square the weights(fractions) and multiply them by 0.5 to accentuate sigmoid
    //return dot(float3(-weight, 2.0, 1.0 ),float3(abs(weight), weight, 1.0)) * 0.5;  // possibly faster version?

    return weight;
}


// COSINE WEIGHT
float cosineWeight(float x) {
    float weight = cos(x * PI / 2);
    return weight;
}


// GAUSSIAN WEIGHT
float gaussianWeight(float x, float sigma) {
    float weight = 0.15915*exp(-0.5*x*x / (sigma*sigma)) / sigma;
    //float weight = pow((6.283185*sigma*sigma), -0.5) * exp((-0.5*x*x) / (sigma*sigma));
    return weight;
}


// LINEAR WEIGHT
float linearWeight(float x) {
    float weight = 1.0 - x;
    return weight;
}



//             _                _     _            
//     ___  __| | __ _  ___    | |__ | |_   _ _ __ 
//    / _ \/ _` |/ _` |/ _ \   | '_ \| | | | | '__|
//   |  __/ (_| | (_| |  __/   | |_) | | |_| | |   
//    \___|\__,_|\__, |\___|   |_.__/|_|\__,_|_|   
//               |___/                             

// Contributors: Santiago Montesdeoca
// Extends the edges for darkened edges and gaps and overlaps
float3 edgeBlur(float2 uv, float2 dir) {

    // sample center pixel
    float3 sEdge = gEdgeTex.Sample(gSampler, uv).rgb;

    // calculate darkening width
    float edgeWidthCtrl = gEdgeControlTex.Sample(gSampler, uv).g;  // edge control target (g)

    float paintedWidth = lerp(0, gEdgeDarkeningKernel * 3, edgeWidthCtrl);  // 3 times wider through local control
    int kernelRadius = max(1, (gEdgeDarkeningKernel + paintedWidth));  // global + local control
    float normalizer = 1.0 / kernelRadius;

    /// experimental weights
    //sigmoid blur
    //float weight = sigmoidWeight(0.0);
    //cosine blur
    //float weight = cosineWeight(0.0);
    //gaussian blur
    float sigma = kernelRadius / 2.0;
    float weight = gaussianWeight(0.0, sigma);

    float darkEdgeGradient = sEdge.g * weight;
    float normDivisor = weight;

    //EDGE DARKENING GRADIENT
    //continue with lateral pixels (unroll is used to fix the dynamic loop at a certain amount)
    [unroll(100)] for (int o = 1; o < kernelRadius; o++) {
    //for (int o = 1; o < gEdgeDarkeningKernel; o++) {
        float offsetColorR = gEdgeTex.Sample(gSampler, saturate(uv + float2(o*dir))).g;
        float offsetColorL = gEdgeTex.Sample(gSampler, saturate(uv + float2(-o*dir))).g;

        // using a sigmoid weight
        //float normGradient = (abs(o) * normalizer); //normalized gradient | 1...0,5...0...0,5...1
        //weight = sigmoidWeight(normGradient);
        // using a sinusoidal weight
        //weight = cosineWeight(normGradient);
        // using a gaussian weight
        weight = gaussianWeight(o, sigma);

        darkEdgeGradient += weight * (offsetColorL + offsetColorR);
        normDivisor += weight * 2;
    }
    darkEdgeGradient = (darkEdgeGradient / normDivisor);


    //GAPS AND OVERLAPS GRADIENT
    weight = linearWeight(0.0);
    float linearGradient = sEdge.b * weight;
    normDivisor = weight;
    normalizer = 1.0 / gGapsOverlapsKernel;

    for (int l = 1; l < gGapsOverlapsKernel; l++) {
        float offsetColorR = gEdgeTex.Sample(gSampler, saturate(uv + float2(l*dir))).b;
        float offsetColorL = gEdgeTex.Sample(gSampler, saturate(uv + float2(-l*dir))).b;
        float normGradient = (l * normalizer); //normalized gradient | 1...0,5...0...0,5...1

        weight = linearWeight(normGradient);

        linearGradient += weight * (offsetColorL + offsetColorR);
        normDivisor += weight * 2;
    }

    linearGradient = linearGradient / normDivisor;

    return float3(sEdge.r, darkEdgeGradient, linearGradient);
}



//              _                _     _               _ _             
//     ___ ___ | | ___  _ __    | |__ | | ___  ___  __| (_)_ __   __ _ 
//    / __/ _ \| |/ _ \| '__|   | '_ \| |/ _ \/ _ \/ _` | | '_ \ / _` |
//   | (_| (_) | | (_) | |      | |_) | |  __/  __/ (_| | | | | | (_| |
//    \___\___/|_|\___/|_|      |_.__/|_|\___|\___|\__,_|_|_| |_|\__, |
//                                                               |___/ 

// Contributors: Santiago Montesdeoca
// Blurs certain parts of the image for color bleeding
float4 colorBleeding(float2 uv, float2 dir) {
    float4 blurPixel = float4(0.0, 0.0, 0.0, 0.0);
    
    // get source pixel values
    float sDepth = gDepthTex.Sample(gSampler, uv).r;
    float sBlurCtrl = 0;
    if (dir.y > 0) {
        sBlurCtrl = gColorTex.Sample(gSampler, uv).a;
    } else {
        sBlurCtrl = gAbstractionControlTex.Sample(gSampler, uv).b;  // abstraction control target (b)
    }
    float4 sColor = float4(gColorTex.Sample(gSampler, uv).rgb, sBlurCtrl);

    // go through neighborhood
    for (int a = -gBleedingRadius; a <= gBleedingRadius; a++) {
        float2 offsetUV = saturate(uv + float2(a*dir));

        // get destination values
        float dBlurCtrl = 0;
        if (dir.y > 0) {
            dBlurCtrl = gColorTex.Sample(gSampler, offsetUV).a;
        } else {
            dBlurCtrl = gAbstractionControlTex.Sample(gSampler, offsetUV).b;  // abstraction control target (b)
        }
        float dDepth = gDepthTex.Sample(gSampler, offsetUV).r;


        // BILATERAL DEPTH BASED BLEEDING
        float weight = gGaussianWeights[a + gBleedingRadius];
        
        float ctrlScope = max(dBlurCtrl, sBlurCtrl);
        float filterScope = abs(a) / gBleedingRadius;
        // check if source or destination pixels are bleeded
        //if ((dBlurCtrl > 0) || (sBlurCtrl > 0)) {
        if (ctrlScope >= filterScope) {

            float bleedQ = 0;
            bool sourceBehindQ = false;
            // check if source pixel is behind
            if ((sDepth - gBleedingThreshold) > dDepth) {
                sourceBehindQ = true;
            }

            // check bleeding cases
            if ((dBlurCtrl) && (sourceBehindQ)) {
                bleedQ = 1;
            } else {
                if ((sBlurCtrl) && (!sourceBehindQ)) {
                    bleedQ = 1;
                }
            }

            // bleed if necessary
            if (bleedQ) {
                float4 dColor = float4(gColorTex.Sample(gSampler, offsetUV).rgb, dBlurCtrl);
                blurPixel += dColor * weight;  // bleed
            } else {
                blurPixel += sColor * weight;  // get source pixel color
            }
        } else {
            blurPixel += sColor * weight;
        }
    }

    return blurPixel;
}



//    _                _                _        _ 
//   | |__   ___  _ __(_)_______  _ __ | |_ __ _| |
//   | '_ \ / _ \| '__| |_  / _ \| '_ \| __/ _` | |
//   | | | | (_) | |  | |/ / (_) | | | | || (_| | |
//   |_| |_|\___/|_|  |_/___\___/|_| |_|\__\__,_|_|
//                                                 
fragmentOutput horizontalFrag(vertexOutputSampler i) {
    fragmentOutput result;

    float2 offset = gTexel * float2(1.0f, 0.0f);

    // run different blurring algorithms
    result.bleedingBlur = colorBleeding(i.uv, offset);
    result.darkenedEdgeBlur = float4(edgeBlur(i.uv, offset), 0);

    //result.bleedingBlur = float4(1.0, 0, 0, 1.0);
    return result;
}



//                   _   _           _ 
//   __   _____ _ __| |_(_) ___ __ _| |
//   \ \ / / _ \ '__| __| |/ __/ _` | |
//    \ V /  __/ |  | |_| | (_| (_| | |
//     \_/ \___|_|   \__|_|\___\__,_|_|
//                                     
fragmentOutput verticalFrag(vertexOutputSampler i) {
    fragmentOutput result;

    float2 offset = gTexel * float2(0.0f, 1.0f);

    // run different blurring algorithms
    result.bleedingBlur = colorBleeding(i.uv, offset);
    result.darkenedEdgeBlur = float4(edgeBlur(i.uv, offset), result.bleedingBlur.a);
    result.darkenedEdgeBlur.b = pow(result.darkenedEdgeBlur.b, 1 / result.darkenedEdgeBlur.b);  // get rid of weak gradients
    result.darkenedEdgeBlur.b = pow(result.darkenedEdgeBlur.b, 2 / gGapsOverlapsKernel);  // adjust gamma depending on kernel size

    return result;
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|       
// Horizontal Blur
technique11 blurH {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, horizontalFrag()));
    }
}

// Vertical Blur
technique11 blurV {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, verticalFrag()));
    }
}
