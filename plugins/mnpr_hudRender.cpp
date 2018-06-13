#pragma warning(disable : 4996)  // sprintf warning in VS
///////////////////////////////////////////////////////////////////////////////////
//    _   _ _   _ ____                                 _   _             
//   | | | | | | |  _ \      ___  _ __   ___ _ __ __ _| |_(_) ___  _ __  
//   | |_| | | | | | | |    / _ \| '_ \ / _ \ '__/ _` | __| |/ _ \| '_ \ 
//   |  _  | |_| | |_| |   | (_) | |_) |  __/ | | (_| | |_| | (_) | | | |
//   |_| |_|\___/|____/     \___/| .__/ \___|_|  \__,_|\__|_|\___/|_| |_|
//                               |_|                       
//
//	 \brief Heads up display operation
//	 Contains the MHUDRender operation that creates the custom HUD of MNPR
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_hudRender.h"
#include "MOperationShader.h"
#include <cstring>


HUDOperation::HUDOperation(MRenderTargetList* t_targetList, const MString& t_rendererName) : mRendererName(t_rendererName) {
    previousFrame = std::chrono::high_resolution_clock::now();
    frameAverage = 0;
    frameAccu = 0;
    timeAccu = 0LL;
    mTargetList = t_targetList;
    strcpy(mHUDStatsBuffer, "");
}


HUDOperation::~HUDOperation() {}


// enables addUIDrawables
bool HUDOperation::hasUIDrawables() const { return true; }


// sets up custom HUD elements
void HUDOperation::addUIDrawables(MHWRender::MUIDrawManager& drawManager2D, const MHWRender::MFrameContext& frameContext) {
    // get viewport information
    int x = 0, y = 0, w = 0, h = 0;
    frameContext.getViewportDimensions(x, y, w, h);

    // get render information
    int width = mTargetList->operator[](0)->width();
    int height = mTargetList->operator[](0)->height();

    // setup drawManager
    drawManager2D.beginDrawable();
    drawManager2D.setColor(MColor(0.3f, 0.3f, 0.3f));  // set font color
    drawManager2D.setFontSize(MHWRender::MUIDrawManager::kSmallFontSize);  // set font size

    // draw renderer name
    drawManager2D.text(MPoint(w*0.01f, h*0.97f), mRendererName, MHWRender::MUIDrawManager::kLeft);

    // draw viewport size and FPS information
    currentFrame = std::chrono::high_resolution_clock::now();
    frameDuration = (unsigned int)std::chrono::duration_cast<std::chrono::microseconds>(currentFrame - previousFrame).count();
    timeAccu += frameDuration;
    frameAccu++;
    if (timeAccu > 1000000) {
        frameAverage = frameAccu;
        durationAverage = timeAccu / frameAccu;
        sprintf(mHUDStatsBuffer, "Resolution [%d, %d]      FPS: %d -> each frame: %d us", width, height, frameAverage, durationAverage);
        // reset values
        frameAccu = 0; timeAccu = 0;
    }

    drawManager2D.text(MPoint(w*0.01f, h*0.95f), mHUDStatsBuffer, MHWRender::MUIDrawManager::kLeft);
    previousFrame = currentFrame;

    // end draw UI
    drawManager2D.endDrawable();
}


// targets to render operation to
MHWRender::MRenderTarget* const* HUDOperation::targetOverrideList(unsigned int &listSize) {
    if (mTargetList->length()) {
        listSize = 2;
        return &mTargetList->presentTarget[0];
    }
    listSize = 0;
    return nullptr;
}
