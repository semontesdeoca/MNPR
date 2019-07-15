**For a production-ready version of MNPR, please refer to [MNPRX](https://artineering.io/projects/MNPRX/)**

---------------

# MNPR
MNPR is an expressive non-photorealistic rendering framework for real-time, filter-based stylization pipelines within Maya (2016.5+). It extends the Maya API and simplifies the creation of Viewport 2.0 render overrides, while still preserving all the low-level options that the Maya API provides.

The framework was originally created by [Santiago E. Montesdeoca](http://artineering.io/) during his PhD studies at the [Nanyang Technological University](http://www.ntu.edu.sg) (Singapore), as a product of his conducted research in:

* [_Real-Time Watercolor Rendering of 3D Objects and Animation with Enhanced Control_](https://artineering.io/research/Real-time-watercolor-rendering-of-3D-objects-and-animation-with-enhanced-control/).

His research was supervised in Singapore by Hock Soon Seah, Hans-Martin Rall and Davide Benvenuti, joined later with supervision in France from Joëlle Thollot, Pierre Bénard and Romain Vergne.

MNPR is now open-sourced under the MIT-license through the publication:

* [_MNPR: A Framework for Real-Time Expressive Non-Photorealistic Rendering of 3D Computer Graphics_](https://artineering.io/research/MNPR/)

Valuable contributions coding MNPR were given by:
* Pierre Bénard
* Amir Semmo
* Yee Xin Chiew


## Downloading MNPR
For animated projects, please refer to the actively maintained [MNPRX](https://artineering.io/projects/MNPRX/).

The latest stable release of the MNPR prototype can be found here (Maya 2017 and 2018):
* [MNPR 1.0](https://github.com/semontesdeoca/MNPR/releases/latest)


## Building from source
The easiest way to build MNPR is using [CMake](https://cmake.org/), just make sure _cmake_ is added to the system PATH.

_If you've never built anything with CMAKE, please consider watching Chad Vernon's [Compiling Maya Plug-ins with CMake](http://www.chadvernon.com/blog/compiling-maya-plug-ins-with-cmake/) tutorial._


### Windows
**Simple:** Double click on the _\_buildWindows.bat_ file under plugins and follow instructions.

**Advanced:**: Open the command prompt (or PowerShell) and run the following commands
```
cd %MNPR_LOCATION%/plugins/build/
cmake ../ -G "Visual Studio 15 2017 Win64" -DMAYA_VERSION=%YEAR%
cmake --build . --config Release
```
You need to replace _%MNPR_LOCATION%_ and _%YEAR%_ with the location of MNPR on your computer and the Maya version year, respectively. You can also choose to build with _Debug_ configuration, which enables the MSVC debugging tools.

Note: When building with _Release_ configuration, the shaders need to be built, as well. Run or refer to the _\_compileHLSL.bat_ to compile the HLSL shaders.


### MacOS
```
cd %MNPR-LOCATION%/plugins/build/
cmake -G "Unix Makefiles" -DMAYA_VERSION=%YEAR% %MNPR-LOCATION%/plugins
cmake --build . --config Release
```
You need to replace _%MNPR_LOCATION%_ and _%YEAR%_ with the location of MNPR on your computer and the Maya version year, respectively.


### Linux
```
cd %MNPR-LOCATION%/plugins/build/
cmake -G "Unix Makefiles" -DMAYA_VERSION=%YEAR% %MNPR-LOCATION%/plugins
cmake --build . --config Release
```
You need to replace _%MNPR_LOCATION%_ and _%YEAR%_ with the location of MNPR on your computer and the Maya version year, respectively.



## Stylization Semantics
Visual effects in non-photorealistic rendering can be generalized into four distinct categories:

* Pigment-based effects
* Substrate-based effects
* Edge-based effects
* Abstraction-based effects

These four groups can be used to directly correlate the stylization control parameters between different styles, using common semantics.
The semantics need to be sufficiently generic, yet semantically meaningful to be adapted to different styles and accepted by the NPR development community.
Additionally, these effects need to adhere to a control scheme, which defines what semantics goes to which channel in the stylization map---so that these can be interpreted by other styles.

The stylization control parameters are rendered by the MNPR object-space shaders into stylization maps, representing each effect group and following the following control scheme:

| Channel | Pigment-based effects | Substrate-based effects | Edge-based effects | Abstraction-based effects |
|---------|-----------------------|-------------------------|--------------------|---------------------------|
|  **R**  | Pigment variation | Substrate distortion    | Edge intensity     | Detail                    |
|  **G**  | Pigment application   | U-inclination | Edge width         | Shape               |
|  **B**  | Pigment density       | V-inclination | Edge transition    | Blending                  |

Stylization pipelines supporting the same effect categories, respecting the semantics and following the control scheme, would enable e.g., to map an art-directed rendering in a watercolor style to an oil or charcoal style.



### Effect semantics, explained

#### Pigment-based effects
- **R**: _Pigment variation_, controls the degree at which the reflected color of a pigment deviates towards one or another color. E.g., green pigmentation that deviates to a more blue or yellow color in certain parts.
- **G**: _Pigment application_, controls how the pigment is placed over a substrate. This can be interpreted as the amount or pressure at which pigment is applied to achieve an effect. E.g., dry-brush application, thick application.
- **B**: _Pigment density_, controls the concentration of the pigment placed over a substrate. This is especially relevant to transparent and translucent media ( i.e., watercolor, ink, colored pencils), but can also influence opaque media. E.g., dilution, lightness, saturation.

#### Substrate-based effects
- **R**: _Substrate distortion_, controls the distortion caused by the substrate roughness on the rendered image. This is especially relevant for fluid media (i.e., watercolor, graffiti).
- **G** and **B**: _U-inclination_ and _V-inclination_, control the inclination of the substrate, which generally affects the direction at which patterns or marks from fluid media evolve. However, generalizing upon this, these parameters are used to define the offset of existing patterns or marks in a horizontal or vertical direction. E.g., bleeding direction, cross-hatching direction, stroke direction.

#### Edge-based effects
- **R**: _Edge intensity_, controls the edge strength/intensity within the stylized render. E.g., linework darkness, edge darkening.
- **G**: _Edge width_, controls the edge thickness of the stylized render. E.g., linework width, edge darkening width.
- **B**: _Edge transition_, controls the edge transition of the subject in relation to neighboring elements. E.g., edge softening, gaps and overlaps.

#### Abstraction-based effects
- **R**: _Detail_, controls the amount of detail at different parts of the stylized render within the subject. E.g., detail blur.
- **G**: _Shape_, Controls the amount of shape abstraction/distortion of the subjects. E.g., hand tremors.
- **B**: _Blending_, controls the color blending at different parts of the stylized render. E.g., smudges, color bleeding.

By adhering to these semantics throughout the stylization pipeline, art-directed scenes can predictably change style and, for the most part, keep the intended effects and look of the expressive render. While these semantics are neither final, nor applicable to all styles and effects, they provide a starting point to address cross-stylization paradigms in expressive rendering.


## Modifying MNPR

Creating your own stylization pipeline is quite straightforward, but it's best to learn by doing and taking a look at how existing stylizations are made. Here is a small breakdown of how things are set up in MNPR.

**Please also read the Coding Guidelines and the Tips & Tricks**

#### Add style to Framework
1. Add style string to _STYLES_ global variable (mnpr_renderer.cpp)
1. Add your style as the default value in the engine settings (mnpr_renderer.h)

#### Create your stylization pipeline
1. Copy and rename a style file (e.g., style_watercolor.hpp -> style_crosshatching.hpp)
2. Adapt the new style source file
	- Change to a custom namespace
	- Add the desired render target(s)
	- Add the desired render operation(s)
3. Add switch clause in _addCustomTargets()_ and _addCustomOperations()_ (mnpr_renderer.cpp)

#### Create custom attributes in the config node
1. Add attributes as engine settings (_EngineSettings_) or effect parameters (_FXParameters_) (mnpr_renderer.h)
2. Copy and rename the node_watercolor.hpp file e.g., node_crosshatching.hpp
3. Adapt the new node source file
	- Add MObject representing the new attribute(s)
	- Change to a custom namespace
	- Initialize the attribute(s) in _initializeParameters()_
	- Parse attribute(s) in _computeParameters()_
4. Add switch clause in _initializeCustomParameters()_ and _computeCustomParameters()_ (mnpr_configNode.cpp)

#### Add a flag to the mnpr command
1. Add short name and long name strings (mnpr_cmd.cpp)
2. Add flag to _newSyntax()_
3. Parse command in _doIt()_

#### Create your custom quad shaders
1. Copy and rename a shader file (e.g., quadBlend10.fx -> quadHatch10.fx)
2. Write your fragment shader
3. Create a technique that uses your fragment shader

Note: as MNPR evolves and more stylizations are implemented within it, more shaders will be available for general use. Try to always reuse existing shader code, as this will enable you to iterate faster towards your stylistic goals.

#### Creating mapped and material effect control widgets for paintFX and noiseFX
1. Open _mnpr\_FX.py_ and carefully read the schema
2. Define your MNPR_FXs in the `getStyleFX()` function
3. Add the switch clause at the bottom of the `getStyleFX()` function
4. Double click on pFx and nFx buttons in the shelf to reload the python file and UI


## Coding Guidelines
Some brief coding guidelines for the framework to have a consisting style.


### Shader code (HLSL and GLSL)
Shader source code in MNPR is found in the _shaders_ folder. In general, we recommend coding shaders mostly in HLSL and translating them to GLSL afterwards. Maya is not helpful when programming GLSL shaders, as it doesn't print out where some errors might be. This leads to a lot of trial and error and lost time finding the culprit of a single syntax error. HLSL development is straightforward to debug and altogether better supported within Maya.

Shader code in MNPR is sorted by operation type and is managed by techniques which run the required vertex and pixel shaders (and tesselation/geometry shaders if you set them up). The _technique_ approach towards shader writing is inspired by the now deprecated effect files in DirectX. Autodesk seems to strongly advocate to this shader-writing convention, even proposing their own solution for techniques within GLSL shaders, as well.

There are convenience functions/shaders for quad (screen-space) shaders in both, HLSL and GLSL in the _quadCommon_ shader files. These facilitate the development of shader code and avoid code repetition in technique based files.

#### Merging requirements
Shader code will only be merged into the Master branch if the shaders are working in both DirectX and OpenGL versions of the viewport. This is required to maximize the usability of the code in all platforms by artists and developers.

#### Naming convention
* _camelCase_ is strongly encouraged throughout all coding languages used in MNPR. This means that files, variables and any kind of functions should respect the camelCase naming convention.
* Shader names should have their type at the end, e.g. `quadVert()`, `resampleFrag()`.
* Variables sent to the shader (uniforms) contain a `g` prefix, e.g. `gColorTex`.

##### File names
By default, _MShaderManager_ within the Maya API will append the file type extension depending on which drawing API the viewport is currently using. For HLSL, it will append `10.fx`, whereas for GLSL, `.ogsfx` will be appended. For this reason, shader file names must present these suffixes in their names.

* Shader file in the root shader directory are general MNPR shaders
* Shader files that are specific to one stylization pipeline should be in their own folder (e.g., ch, op, wc)

#### Commenting
* Comments should be written following two forward slashes and a white space.
`// This is a comment`
* Inline comments should be written in small-caps (except names) following two spaces, two forward slashes and a white space.
`Texture2D gSubstrateTex;  // substrate texture (paper, canvas, etc)`

#### Code file headers
Code file headers should be formatted as follows:
* File name with language in brackets
* _Brief_ description of what the file contains
* _Contributors_ that have added or fixed things in the shader code
* [ASCII headers](http://patorjk.com/software/taag/#p=display&c=c%2B%2B&f=Ivrit&t=header) stating the type of operations available in the shader file
* _Description_ of what kind of shaders the file contains.

The file header should look something like this:
```
////////////////////////////////////////////////////////////////////////////////////////////////////
// quadAdjustLoadMNPR10.fx (HLSL)
// Brief: Adjusting and loading render targets
// Contributors:
////////////////////////////////////////////////////////////////////////////////////////////////////
//              _  _           _        _                 _
//     __ _  __| |(_)_   _ ___| |_     | | ___   __ _  __| |
//    / _` |/ _` || | | | / __| __|____| |/ _ \ / _` |/ _` |
//   | (_| | (_| || | |_| \__ \ ||_____| | (_) | (_| | (_| |
//    \__,_|\__,_|/ |\__,_|___/\__|    |_|\___/ \__,_|\__,_|
//              |__/
////////////////////////////////////////////////////////////////////////////////////////////////////
// This shader file adjusts and loads any required elements for future stylization in MNPR
////////////////////////////////////////////////////////////////////////////////////////////////////
#include "include\\quadCommon.fxh"
```

#### Sections
Sections are used to separate different fragment shaders that belong to the same group (e.g., edge detection -> sobel, DoG). Shader code sections feature the following
* [ASCII headers](http://patorjk.com/software/taag/#p=display&c=c%2B%2B&f=Ivrit&t=header) followed by a description of the shader
* Three empty lines separate each section

```
//                                        _      
//    _ __ ___  ___  __ _ _ __ ___  _ __ | | ___
//   | '__/ _ \/ __|/ _` | '_ ` _ \| '_ \| |/ _ \
//   | | |  __/\__ \ (_| | | | | | | |_) | |  __/
//   |_|  \___||___/\__,_|_| |_| |_| .__/|_|\___|
//                                 |_|           

// Contributors:
// Resamples any up- or down-sampled target to fit the viewport dimensions.
// Anti-aliasing is achieved by using bilinear filtering when sampling.
float4 resampleFrag(vertexOutputSampler i) : SV_Target {
	return gColorTex.Sample(gSampler, i.uv);
}



//    _______  __    _        _    
//   |  ___\ \/ /   / \      / \   
//   | |_   \  /   / _ \    / _ \  
//   |  _|  /  \  / ___ \  / ___ \
//   |_|   /_/\_\/_/   \_\/_/   \_\
//                                 

// Contributors:
// Perform FXAA v3.11 anti-aliasing
// -> Based on FXAA of Timothy Lottes 2009
//    [2009] FXAA
float4 FXAAFrag(vertexOutputSampler i) : SV_Target {
	// etc
}
```

#### Groups
Shader code can also be grouped into specific assignment/operations as such:
* Use ALL-CAPS when grouping operations
* Two empty lines separate groups

```
// MAYA VARIABLES
float gNCP : NearClipPlane;  // near clip plane distance


// TEXTURES
Texture2D gZBuffer;       // ZBuffer
Texture2D gSubstrateTex;  // substrate texture (paper, canvas, etc)


// VARIABLES
// post-processing effects
float gSaturation = 1.0;
float gContrast = 1.0;
float gBrightness = 1.0;

// engine settings
float2 gDepthRange = float2(8.0, 50.0);
float3 gSubstrateColor = float3(1.0, 1.0, 1.0);
float gSubstrateRoughness;
float gSubstrateTexScale;
float2 gSubstrateTexDimensions;
float2 gSubstrateTexUVOffset;


// MRT
struct fragmentOutput {
	float4 stylizationOutput : SV_Target0;
	float3 substrateOutput : SV_Target1;
	float depthOutput : SV_Target2;
};
```

This documentation is still in progress...
	<!--
	## Modifying the object-space shader
-->


### C++ code
C++ source code in MNPR is found in the _plugin_ folder, sorted by the type of code it contains and defined by its prefix.

* _mnpr_ prefix is for MNPR source files required by the framework.
* _node_ prefix is for custom stylization nodes.
* _style_ prefix is for custom stylization pipelines.
* _M_ prefix is for classes that extend the Maya API (following the convention of Autodesk).

You will mostly be working with _style_ and _node_ files to specify your stylization pipeline. However, you will also be including effect parameters and engine settings into the _mnpr\_renderer.h_ header file.


#### Merging requirements
Merging _mnpr_ files will affect all stylizations. Therefore, these files will only be merged if edits are thoroughly tested, organized and generalized towards more than just a specific stylization.


#### Naming convention
* _camelCase_ is strongly encouraged throughout all coding languages used in MNPR. This means that files, variables and any kind of functions should respect the _camelCase_ naming convention.
* Custom node source files need to have the _node_ prefix
* Custom stylizations source files need to have the _style_ prefix
* _MObject_ is prefixed with _o_ e.g., `oData`
* Attribute _MObjects_ are prefixed with _a_ e.g., `aContrast`
* In general, please try to keep the naming conventions consistent with the rest of the code.


#### Commenting
* Comments should be written following two forward slashes and a white space.
`// This is a comment`
* Inline comments should be written in small-caps (except names) following two spaces, two forward slashes and a white space.
`Texture2D gSubstrateTex;  // substrate texture (paper, canvas, etc)`


#### Code file headers
Code file headers should be formatted as follows:
* [ASCII headers](http://patorjk.com/software/taag/#p=display&c=c%2B%2B&f=Ivrit&t=header) stating the source file header
* _Brief_ description of what the file contains
* _Description_ of what kind of code the file contains.

The file header should look something like this:
```
///////////////////////////////////////////////////////////////////////////////////
//                     __ _                           _
//     ___ ___  _ __  / _(_) __ _     _ __   ___   __| | ___
//    / __/ _ \| '_ \| |_| |/ _` |   | '_ \ / _ \ / _` |/ _ \
//   | (_| (_) | | | |  _| | (_| |   | | | | (_) | (_| |  __/
//    \___\___/|_| |_|_| |_|\__, |   |_| |_|\___/ \__,_|\___|
//                          |___/
//
//   \brief Configuration node
//   Contains the configuration parameters to define engine settings and fx parameters
///////////////////////////////////////////////////////////////////////////////////
```


#### Functions, methods and groups
Functions and groups are separated by two empty lines, methods (class functions) are separated by one empty line.



### Python code
Python source code developed for MNPR is found in the _scripts_ directory and manages the frontend communication with the plugin.

#### Merging requirements
Merging _mnpr_ python files will affect the stylization workflow of all artists. Therefore, these files will only be merged if edits are thoroughly tested, organized and generalized towards more than just a specific stylization.

#### Naming convention
* _camelCase_ is strongly encouraged throughout all coding languages used in MNPR. This means that files, variables and any kind of functions should respect the _camelCase_ naming convention.
* Python code files developed for MNPR should have the prefix _mnpr_
* In general, please try to keep the naming conventions consistent with the rest of the code.


#### Commenting
* Use Google python docstring format when documenting your functions, classes and methods (PyCharm: `Settings -> Python Integrated Tools -> Docstrings -> Docstring format -> Google`).
* Comments should be written following one hashtag and a white space.
`# This is a comment`
* Inline comments should be written in small-caps (except names) following two spaces, one hashtag and a white space.
`cmds.mnpr(renderOperation=mnprOperations-2, s=0)  # UI`


#### Code file headers
Code file headers should be formatted as follows:
* license: MIT
* repository: https://github.com/semontesdeoca/MNPR
* [ASCII headers](http://patorjk.com/software/taag/#p=display&c=bash&f=Ivrit&t=header) representing the source file
* _Summary_ description of what the file contains

The file header should look something like this:
```
"""
@license:       MIT
@repository:    https://github.com/semontesdeoca/MNPR
                                 _   _ ___
  _ __ ___  _ __  _ __  _ __    | | | |_ _|___
 | '_ ` _ \| '_ \| '_ \| '__|   | | | || |/ __|
 | | | | | | | | | |_) | |      | |_| || |\__ \
 |_| |_| |_|_| |_| .__/|_|       \___/|___|___/
                 |_|
@summary:       Contains the pass breakdown and MNPR viewport renderer interfaces
"""
```

#### Functions, methods and groups
Spacing follow the PEP 8 blank line conventions, but names should be in _camelCase_.



## Tips & Tricks
- You cannot render to multiple render targets of different sizes.
- There is no need to try to get Maya's own post-processing effects to work as parameter targets should also present these.
- If for some unknown reason rendering is slower than previously, restart your computer and check again (WINDOWS).
- Developing ogsfx shaders inside of Maya are a pain, but if you have to:
	- Syntax errors won't show, the targets will simply display white and you need to find out where the error is. (`/**/` and a proper IDE are your best friends)
	- Loading the shader as an ogsfx (GLSL) material might give better information to troubleshoot.
	- `if (color.a) {}` won't work without any error message, you need to explicitly state `if (color.a > 0) {}`
	- A Texture2D must have a sampler, otherwise Maya will crash
