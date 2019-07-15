#pragma once
///////////////////////////////////////////////////////////////////////////////////
//    _                       _       _ _     _
//   | |_ __ _ _ __ __ _  ___| |_    | (_)___| |_
//   | __/ _` | '__/ _` |/ _ \ __|   | | / __| __|
//   | || (_| | | | (_| |  __/ |_    | | \__ \ |_
//    \__\__,_|_|  \__, |\___|\__|   |_|_|___/\__|
//                 |___/
//
//    \brief Target list struct designed to work like MRenderOperationList for render targets
//    Contains and manages all targets, target descriptions and target outputs of operations
///////////////////////////////////////////////////////////////////////////////////
#include <map>
#include <vector>
#include <maya/MRenderTargetManager.h>
#include <maya/MShaderManager.h>


struct MRenderTargetList {
    const MHWRender::MRenderTargetManager* targetManager = MHWRender::MRenderer::theRenderer()->getRenderTargetManager();  ///< target manager

    /// target lists
    std::vector<MHWRender::MRenderTargetDescription> targetDescriptions;             ///< render target descriptions
    std::vector<MHWRender::MRenderTarget*> renderTargets;                            ///< render targets
    std::map<std::string, std::vector<MHWRender::MRenderTarget*>> operationOutputs;  ///< operation output targets

    /// override [] operator to return description of target
    MHWRender::MRenderTargetDescription* operator[] (int t_index) {
        if (t_index<length()) {
            return &targetDescriptions[t_index];
        }
        cout << "Render target index out of range ([] operator)" << endl;
        return nullptr;
    }

    /// append description and target to target list
    void append(MHWRender::MRenderTargetDescription t_targetDesc, MHWRender::MRenderTarget* t_target = nullptr) {
        targetDescriptions.push_back(t_targetDesc);
        if (t_target) {
            renderTargets.push_back(t_target);
        } else {
            renderTargets.push_back(targetManager->acquireRenderTarget(t_targetDesc));
        }
    }

    /// return length of the list
    int length() {
        return (unsigned int)targetDescriptions.size();
    }

    /// get index of a render target description
    int indexOf(MString t_descName) {
        for (int i = 0; i < length(); i++) {
            if (t_descName == targetDescriptions[i].name())
                return i;
        }
        cout << "ERROR: " << t_descName << "not found in render targets" << endl;
        return -1;
    }

    /// return target found in index
    MHWRender::MRenderTarget* target(int t_index) {
        if (t_index<length()) {
            return renderTargets[t_index];
        }
        cout << " ERROR: [idx: " << t_index << "] - Render target index out of range (target())" << endl;
        return nullptr;
    }

    /// update targets with their respective description
    void updateTargetDescriptions() {
        for (int i = 0; i < length(); i++) {
            target(i)->updateDescription(targetDescriptions[i]);
        }
    }

    /// clear(release) all render targets
    void clear() {
        for (int i = 0; i < length(); i++) {
            targetManager->releaseRenderTarget(renderTargets[i]);
            renderTargets[i] = nullptr;
        }
        targetDescriptions.clear();
        renderTargets.clear();
        operationOutputs.clear();
    }

    /// OPERATION RELATED METHODS
    /// set the targets desired as operation outputs
    void setOperationOutputs(MString t_opName, std::vector<MString> t_targetDescNames) {
        std::vector<MHWRender::MRenderTarget*> operationTargets;
        for (unsigned int i = 0; i< t_targetDescNames.size(); i++) {
            unsigned int t_targetIndex = indexOf(t_targetDescNames[i]);
            MHWRender::MRenderTarget* t_target = target(t_targetIndex);
            operationTargets.push_back(t_target);
        }
        operationOutputs[t_opName.asChar()] = operationTargets;
    }

    /// return outputs for a specific operation
    std::vector<MHWRender::MRenderTarget*> getOperationOutputs(MString t_name) {
        return operationOutputs[t_name.asChar()];
    }

    /// PRESENT RELATED METHODS
    MHWRender::MRenderTarget* presentTarget[2];  ///< target list that is presented on the viewport

    /// set active target
    void setPresentTarget(unsigned int t_index) {
        presentTarget[0] = target(t_index);
        presentTarget[1] = target(1);  // depth
    }

    MStatus saveTarget(unsigned int t_index) {
        // WIP (at a later date)
        MStatus status;
        MHWRender::MRenderer* renderer = MHWRender::MRenderer::theRenderer();
        MHWRender::MTextureManager* texManager = renderer->getTextureManager();
        if (!texManager) return MS::kFailure;
        MHWRender::MRenderTarget* target2Save = target(t_index);
        MHWRender::MRenderTargetDescription targetDesc = targetDescriptions[t_index];

        MString directory = "C:/";
        MString frameName = "screenshot";
        MString frameExtension = ".jpg";

        // Get the render target data
        int rowPitch = 0;
#if MAYA_API_VERSION >= 20180000
        size_t slicePitch = 0;
#else
        int slicePitch = 0;
#endif
        char* targetData = (char*)target2Save->rawData(rowPitch, slicePitch);
        // Create a texture with same size and format as the render target
        MHWRender::MTexture* texture = NULL;
        if (targetData != NULL) {
            MHWRender::MTextureDescription textureDesc;
            textureDesc.fWidth = targetDesc.width();
            textureDesc.fHeight = targetDesc.height();
            textureDesc.fDepth = 1;
            textureDesc.fBytesPerRow = rowPitch;
            textureDesc.fBytesPerSlice = (unsigned int)slicePitch;
            textureDesc.fMipmaps = 1;
            textureDesc.fArraySlices = targetDesc.arraySliceCount();
            textureDesc.fFormat = targetDesc.rasterFormat();
            textureDesc.fTextureType = MHWRender::kImage2D;
            textureDesc.fEnvMapType = MHWRender::kEnvNone;
            // Construct the texture with the screen pixels
            texture = texManager->acquireTexture(MString("hwApiTextureTest"), textureDesc, targetData);
        }
        delete targetData;
        MString fileDir = directory + frameName + frameExtension;
        status = texManager->saveTexture(texture, fileDir);
        texManager->releaseTexture(texture);

        if (status) {
            cout << "Captured target" << endl;
        } else {
            cout << "Capture failed" << endl;
        }
        return MS::kSuccess;
    }


    /// DEBUG METHODS
    /// print the operation outputs (DEBUG)
    void dPrintOperationOutputs(MString t_name) {
        MHWRender::MRenderTargetDescription targetDesc;
        cout << t_name << " -> outputs to these targets:" << endl;
        std::vector<MHWRender::MRenderTarget*> opOutputs = operationOutputs[t_name.asChar()];
        for (unsigned int i = 0; i < opOutputs.size(); i++) {
            opOutputs[i]->targetDescription(targetDesc);
            cout << targetDesc.name() << endl;
        }
    }
};
