////////////////////////////////////////////////////////////////////////////////////////////////////
// quadColorTransform.fxh (HLSL)
// Brief: Common color transformation snippets for MNPR
// Contributors: Amir Semmo, Pierre Bénard
////////////////////////////////////////////////////////////////////////////////////////////////////
//              _                _                        __                      
//     ___ ___ | | ___  _ __    | |_ _ __ __ _ _ __  ___ / _| ___  _ __ _ __ ___  
//    / __/ _ \| |/ _ \| '__|   | __| '__/ _` | '_ \/ __| |_ / _ \| '__| '_ ` _ \ 
//   | (_| (_) | | (_) | |      | |_| | | (_| | | | \__ \  _| (_) | |  | | | | | |
//    \___\___/|_|\___/|_|       \__|_|  \__,_|_| |_|___/_|  \___/|_|  |_| |_| |_|
//                                                                                
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file provides color transformation functions
////////////////////////////////////////////////////////////////////////////////////////////////////
#ifndef _QUADCOLORTRANSFORM_FXH
#define _QUADCOLORTRANSFORM_FXH



//    ____   ____ ____       ____      _   _ ______     __
//   |  _ \ / ___| __ )     / /\ \    | | | / ___\ \   / /
//   | |_) | |  _|  _ \    / /  \ \   | |_| \___ \\ \ / / 
//   |  _ <| |_| | |_) |   \ \  / /   |  _  |___) |\ V /  
//   |_| \_\\____|____/     \_\/_/    |_| |_|____/  \_/   
//                                                        
float3 rgb2hsv(in float3 c)
{
   float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
   //float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));
   //float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));
   float4 p = c.g < c.b ? float4(c.bg, K.wz) : float4(c.gb, K.xy);
   float4 q = c.r < p.x ? float4(p.xyw, c.r) : float4(c.r, p.yzx);
   
   float d = q.x - min(q.w, q.y);
   float e = 1.0e-10;
   
   return float3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}



//    ____   ____ ____       ____     __  ____   _______
//   |  _ \ / ___| __ )     / /\ \    \ \/ /\ \ / /__  /
//   | |_) | |  _|  _ \    / /  \ \    \  /  \ V /  / / 
//   |  _ <| |_| | |_) |   \ \  / /    /  \   | |  / /_ 
//   |_| \_\\____|____/     \_\/_/    /_/\_\  |_| /____|
//                                                      
float3 rgb2xyz(float3 c) {
    float3 tmp;
    tmp.x = (c.r > 0.04045) ? pow((c.r + 0.055) * 0.947867, 2.4) : c.r * 0.077399;
    tmp.y = (c.g > 0.04045) ? pow((c.g + 0.055) * 0.947867, 2.4) : c.g * 0.077399;
    tmp.z = (c.b > 0.04045) ? pow((c.b + 0.055) * 0.947867, 2.4) : c.b * 0.077399;
    return 100.0 * mul(tmp, float3x3(0.4124, 0.3576, 0.1805, 0.2126, 0.7152, 0.0722, 0.0193, 0.1192, 0.9505));
}

float3 xyz2rgb(float3 c) {
    float3 v =  0.01 * mul(c, float3x3(
                               3.2406, -1.5372, -0.4986,
                              -0.9689,  1.8758,  0.0415,
                               0.0557, -0.2040,  1.0570
                             ));
    float3 r;
    r.x = ( v.r > 0.0031308 ) ? (( 1.055 * pow( v.r, 0.416667)) - 0.055 ) : 12.92 * v.r;
    r.y = ( v.g > 0.0031308 ) ? (( 1.055 * pow( v.g, 0.416667)) - 0.055 ) : 12.92 * v.g;
    r.z = ( v.b > 0.0031308 ) ? (( 1.055 * pow( v.b, 0.416667)) - 0.055 ) : 12.92 * v.b;
    return r;
}



//   __  ____   _______     ____      _          _     
//   \ \/ /\ \ / /__  /    / /\ \    | |    __ _| |__  
//    \  /  \ V /  / /    / /  \ \   | |   / _` | '_ \ 
//    /  \   | |  / /_    \ \  / /   | |__| (_| | |_) |
//   /_/\_\  |_| /____|    \_\/_/    |_____\__,_|_.__/ 
//                                                     
float3 xyz2lab(float3 c) {
    float3 n = c / float3(95.047, 100, 108.883);
    float3 v;
    v.x = (n.x > 0.008856) ? pow(n.x, 0.333333) : (7.787 * n.x) + 0.137931;
    v.y = (n.y > 0.008856) ? pow(n.y, 0.333333) : (7.787 * n.y) + 0.137931;
    v.z = (n.z > 0.008856) ? pow(n.z, 0.333333) : (7.787 * n.z) + 0.137931;
    return float3((116.0 * v.y) - 16.0, 500.0 * (v.x - v.y), 200.0 * (v.y - v.z));
}

float3 lab2xyz(float3 c) {
    float fy = ( c.x + 16.0 ) * 0.008620;
    float fx = c.y * 0.002 + fy;
    float fz = fy - c.z * 0.005;
    return float3(
                95.047 *  (( fx > 0.206897 ) ? fx * fx * fx : ( fx - 16.0 * 0.008620 ) * 0.128419),
                100.000 * (( fy > 0.206897 ) ? fy * fy * fy : ( fy - 16.0 * 0.008620 ) * 0.128419),
                108.883 * (( fz > 0.206897 ) ? fz * fz * fz : ( fz - 16.0 * 0.008620 ) * 0.128419)
               );
}



//    ____   ____ ____       ____      _          _     
//   |  _ \ / ___| __ )     / /\ \    | |    __ _| |__  
//   | |_) | |  _|  _ \    / /  \ \   | |   / _` | '_ \ 
//   |  _ <| |_| | |_) |   \ \  / /   | |__| (_| | |_) |
//   |_| \_\\____|____/     \_\/_/    |_____\__,_|_.__/ 
//                                                      
float3 rgb2lab(float3 color) {
    float3 lab = xyz2lab(rgb2xyz(color));
    return float3(lab.x * 0.01, 0.5 + lab.y * 0.003937, 0.5 + lab.z * 0.003937);
}

float3 lab2rgb(float3 color) {
    return xyz2rgb(lab2xyz(float3(100.0 * color.x, 2.0 * 127.0 * (color.y - 0.5), 2.0 * 127.0 * (color.z - 0.5)) ) );
}



//    ____   ____ ____       ____      ______   ______  
//   |  _ \ / ___| __ )     / /\ \    |  _ \ \ / / __ ) 
//   | |_) | |  _|  _ \    / /  \ \   | |_) \ V /|  _ \ 
//   |  _ <| |_| | |_) |   \ \  / /   |  _ < | | | |_) |
//   |_| \_\\____|____/     \_\/_/    |_| \_\|_| |____/ 
//                                                      
//  Contributor: Pierre Bénard
//  Convert between RGB (red, green, blue) to RYB (red, yellow, blue)

float3 rgb2ryb(float3 rgb_color) {
    // remove the white from the color
    float white = min(min(rgb_color.r, rgb_color.g), rgb_color.b);
    rgb_color -= white.xxx;

    float max_green = max(max(rgb_color.r, rgb_color.g), rgb_color.b);

    // get the yellow out of the red & green		
    float yellow = min(rgb_color.r, rgb_color.g);
    rgb_color.r -= yellow;
    rgb_color.g -= yellow;

    // if this unfortunate conversion combines blue and green, then cut each in half to preserve the value's maximum range.
    if (rgb_color.b > 0. && rgb_color.g > 0.) {
        rgb_color.b /= 2.;
        rgb_color.g /= 2.;
    }

    // redistribute the remaining green.
    yellow += rgb_color.g;
    rgb_color.b += rgb_color.g;

    // normalize to values.
    float max_yellow = max(max(rgb_color.r, yellow), rgb_color.b);

    if (max_yellow > 0.) {
        float n = max_green / max_yellow;

        rgb_color.r *= n;
        yellow *= n;
        rgb_color.b *= n;
    }

    // add the white back in.
    rgb_color.r += white;
    yellow += white;
    rgb_color.b += white;

    return float3(rgb_color.r, yellow, rgb_color.b);
}

float3 ryb2rgb(float3 ryb_color) {
    // remove the white from the color
    float white = min(min(ryb_color.r, ryb_color.g), ryb_color.b);
    ryb_color -= white.xxx;

    float max_yellow = max(max(ryb_color.r, ryb_color.g), ryb_color.b);

    // get the green out of the yellow & blue
    float green = min(ryb_color.g, ryb_color.b);
    ryb_color.g -= green;
    ryb_color.b -= green;

    if (ryb_color.b > 0. && green > 0.) {
        ryb_color.b *= 2.;
        green *= 2.;
    }

    // redistribute the remaining yellow.
    ryb_color.r += ryb_color.g;
    green += ryb_color.g;

    // normalize to values.
    float max_green = max(max(ryb_color.r, green), ryb_color.b);

    if (max_green > 0.) {
        float n = max_yellow / max_green;

        ryb_color.r *= n;
        green *= n;
        ryb_color.b *= n;
    }

    // add the white back in.
    ryb_color.r += white;
    green += white;
    ryb_color.b += white;

    return float3(ryb_color.r, green, ryb_color.b);
}

#endif /* _QUADCOLORTRANSFORM_FXH */
