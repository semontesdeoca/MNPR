////////////////////////////////////////////////////////////////////////////////////////////////////
// quadSubstrate10.fx (HLSL)
// Brief: Substrate operations for MNPR
// Contributors: Santiago Montesdeoca, Amir Semmo
////////////////////////////////////////////////////////////////////////////////////////////////////
//              _         _             _       
//    ___ _   _| |__  ___| |_ _ __ __ _| |_ ___ 
//   / __| | | | '_ \/ __| __| '__/ _` | __/ _ \
//   \__ \ |_| | |_) \__ \ |_| | | (_| | ||  __/
//   |___/\__,_|_.__/|___/\__|_|  \__,_|\__\___|
//
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides algorithms for substrate-based effects in MNPR
// 1.- Substrate lighting, adding an external lighting source to the render
// 2.- Substrate distortion, emulating the substrate fingering happening on rough substrates
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"

// TEXTURES
Texture2D gSubstrateTex;
Texture2D gEdgeTex;
Texture2D gControlTex;
Texture2D gDepthTex;


// VARIABLES
float gGamma = 1.0;
float gSubstrateLightDir = 0;
float gSubstrateLightTilt = 45;
float gSubstrateShading = 1.0;
float gSubstrateDistortion;

float gImpastoPhongSpecular = 0.6;
float gImpastoPhongShininess = 16.0;


// BLENDING
float blendOverlay(in float base, in float blend) {
    return base < 0.5 ? (2.0*base*blend) : (1.0 - 2.0*(1.0 - base)*(1.0 - blend));
}

float blendLinearDodge(in float base, in float blend) {
    return base + blend;
}



//    _ _       _     _   _             
//   | (_) __ _| |__ | |_(_)_ __   __ _ 
//   | | |/ _` | '_ \| __| | '_ \ / _` |
//   | | | (_| | | | | |_| | | | | (_| |
//   |_|_|\__, |_| |_|\__|_|_| |_|\__, |
//        |___/                   |___/ 

// Contributor: Santiago Montesdeoca
// Calculates the substrate lighting on top of the rendered imagery
// -> Based on the external substrate lighting model by Montesdeoca et al. 2017
//    [2017] Edge- and substrate-based effects for watercolor stylization
float4 deferredLightingFrag(vertexOutputSampler i) : SV_Target {
	int3 loc = int3(i.pos.xy, 0);
	float4 renderTex = gColorTex.Load(loc);
	float2 substrateNormalTex = gSubstrateTex.Sample(gSampler, i.uv).rg - 0.5;  // bring normals to [-0.5 - 0.5]

	// get light direction
	float dirRadians = gSubstrateLightDir * PI / 180.0;
	float3 lightDir = float3(sin(dirRadians), cos(dirRadians), (gSubstrateLightTilt / 89.0));

	// calculate diffuse illumination
	float3 normals = float3(-substrateNormalTex, 1.0);
	float diffuse = dot(normals, lightDir);  // basic lambert
	//diffuse = 1.0 - acos(diffuse)/PI;  // angular lambert
	//diffuse = (1 + diffuse)*0.5;  // extended lambert

	// modulate diffuse shading
	diffuse = pow(1 - diffuse, 2);  // modify curve 
	diffuse = 1 - (diffuse * gSubstrateShading);

    // gamma correction on output
    if (gGamma < 1) {
        // if viewport is not gamma corrected, at least keep light linearity on substrate
        diffuse = pow(diffuse, 0.454545455);
    }
    renderTex.rgb *= diffuse;
	return renderTex;
}

// Contributor: Amir Semmo
// Calculates the substrate lighting only on parts that have no paint applied (impasto would override any substrate structure)
// -> Extended from the external substrate lighting model by Montesdeoca et al. 2017
//    [2017] Edge- and substrate-based effects for watercolor stylization
float4 deferredImpastoLightingFrag(vertexOutputSampler i) : SV_Target {
    int3 loc = int3(i.pos.xy, 0);
    float4 renderTex = gColorTex.Load(loc);
    float3 substrateNormalTex = float3(clamp(gSubstrateTex.Sample(gSampler, i.uv).rg - 0.5, -0.5, 0.5), 1.0); // bring normals to [-0.5 - 0.5]

    // get light direction
    float dirRadians = gSubstrateLightDir * PI / 180.0;
    float3 lightDir = float3(sin(dirRadians), cos(dirRadians), (gSubstrateLightTilt / 89.0));

    // calculate diffuse illumination
    float3 normals = float3(-substrateNormalTex.xy, 1.0);
    float diffuse = dot(normals, lightDir);  // basic lambert
    //diffuse = 1.0 - acos(diffuse)/PI;  // angular lambert
    //diffuse = (1 + diffuse)*0.5;  // extended lambert
    float2 phong = saturate(float2(diffuse, pow(diffuse, gImpastoPhongShininess) * gImpastoPhongSpecular));  // phong based

    // modulate diffuse shading
    diffuse = pow(1 - diffuse, 2);  // modify curve 
    diffuse = 1 - (diffuse * gSubstrateShading);

    // gamma correction on output
    if (gGamma < 1) {
        // if viewport is not gamma corrected, at least keep light linearity on substrate
        diffuse = pow(diffuse, 0.454545455);
    }
    
    float3 substrateColor = lerp(renderTex.rgb*diffuse, renderTex.rgb, renderTex.a);
    float3 impastoColor = float3(blendOverlay(renderTex.r, phong.x), blendOverlay(renderTex.g, phong.x), blendOverlay(renderTex.b, phong.x)); // blend diffuse component
           impastoColor = float3(blendLinearDodge(phong.y, impastoColor.r), blendLinearDodge(phong.y, impastoColor.g), blendLinearDodge(phong.y, impastoColor.b));  // blend specular component

    // linearly blend with the alpha mask
    renderTex.rgb = lerp(substrateColor, impastoColor, renderTex.a);

    return renderTex;
}



//        _ _     _             _   _             
//     __| (_)___| |_ ___  _ __| |_(_) ___  _ __  
//    / _` | / __| __/ _ \| '__| __| |/ _ \| '_ \ 
//   | (_| | \__ \ || (_) | |  | |_| | (_) | | | |
//    \__,_|_|___/\__\___/|_|   \__|_|\___/|_| |_|
//                                                

// Contributor: Santiago Montesdeoca
// Calculates the substrate distortion generated by its roughness
// -> Based on the paper distortion approach by Montesdeoca et al. 2017
//    [2017] Art-directed watercolor stylization of 3D animations in real-time
float4 substrateDistortionFrag(vertexOutputSampler i) : SV_Target{
    int3 loc = int3(i.pos.xy, 0); // coordinates for loading

    // get pixel values
    float2 normalTex = (gSubstrateTex.Load(loc).rg * 2 - 1);  // to transform float values to -1...1
    float distortCtrl = saturate(gControlTex.Load(loc).r + 0.2);  // control parameters, unpack substrate control target (y)
    float linearDepth = gDepthTex.Load(loc).r;

    // calculate uv offset
    float controlledDistortion = lerp(0, gSubstrateDistortion, 5.0*distortCtrl);  // 0.2 is default
    float2 uvOffset = normalTex * (controlledDistortion * gTexel);

    // check if destination is in front
    float depthDest = gDepthTex.Sample(gSampler, i.uv + uvOffset).r;
    if (linearDepth - depthDest > 0.01) {
        uvOffset = float2(0.0f, 0.0f);
    }

    float4 colorDest = gColorTex.Sample(gSampler, i.uv + uvOffset);
    return colorDest;
}

// Contributor: Amir Semmo
// Calculates the substrate distortion generated by its roughness only close to edges
// -> Extended from the paper distortion approach by Montesdeoca et al. 2017
//    [2017] Art-directed watercolor stylization of 3D animations in real-time
float4 substrateDistortionEdgesFrag(vertexOutputSampler i) : SV_Target{
	int3 loc = int3(i.pos.xy, 0); // coordinates for loading

	// get pixel values
	float2 normalTex = (gSubstrateTex.Load(loc).rg * 2 - 1);  // to transform float values to -1...1
	float distortCtrl = saturate(gControlTex.Load(loc).r + 0.2);  // control parameters, substrate control target (r)

	// calculate uv offset
	float controlledDistortion = lerp(0, gSubstrateDistortion, 5.0*distortCtrl);  // 0.2 is default
	float2 uvOffset = normalTex * (controlledDistortion * gTexel);
	float4 colorDest = gColorTex.Sample(gSampler, i.uv + uvOffset);

    // only distort at edges
    float e = gEdgeTex.Load(int3(i.pos.xy, 0)).x;

    return lerp(gColorTex.Sample(gSampler, i.uv), colorDest, e);
}



//    _            _           _                       
//   | |_ ___  ___| |__  _ __ (_) __ _ _   _  ___  ___ 
//   | __/ _ \/ __| '_ \| '_ \| |/ _` | | | |/ _ \/ __|
//   | ||  __/ (__| | | | | | | | (_| | |_| |  __/\__ \
//    \__\___|\___|_| |_|_| |_|_|\__, |\__,_|\___||___/
//                                  |_|                
// DEFERRED SUBSTRATE LIGHTING
technique11 deferredLighting {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, deferredLightingFrag()));
	}
}
technique11 deferredImpastoLighting {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, deferredImpastoLightingFrag()));
    }
}


// SUBSTRATE DISTORTION
technique11 substrateDistortion {
	pass p0 {
		SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
		SetGeometryShader(NULL);
		SetPixelShader(CompileShader(ps_5_0, substrateDistortionFrag()));
	}
}
technique11 substrateDistortionEdges {
    pass p0 {
        SetVertexShader(CompileShader(vs_5_0, quadVertSampler()));
        SetGeometryShader(NULL);
        SetPixelShader(CompileShader(ps_5_0, substrateDistortionEdgesFrag()));
    }
}