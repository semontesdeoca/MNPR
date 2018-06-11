#pragma once
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
#include <chrono>
#include "MRenderTargetList.h"


class HUDOperation : public MHWRender::MHUDRender {
public:
    HUDOperation(MRenderTargetList* t_targetList, const MString& t_rendererName);
    ~HUDOperation();

    virtual bool hasUIDrawables() const;  ///< enables addUIDrawables
    virtual void addUIDrawables(MHWRender::MUIDrawManager& drawManager2D, const MHWRender::MFrameContext& frameContext);  ///< sets up custom HUD elements

    virtual MHWRender::MRenderTarget* const* targetOverrideList(unsigned int &listSize);  ///< targets to render operation to

protected:
    const MString& mRendererName;			   ///< render override name
    MRenderTargetList* mTargetList = nullptr;  ///< target list of renderer

    /// variables for time statistics
    std::chrono::high_resolution_clock::time_point previousFrame;
    std::chrono::high_resolution_clock::time_point currentFrame;
    unsigned int timeAccu;
    unsigned int frameAccu;
    unsigned int frameDuration;
    unsigned int frameAverage;
    unsigned int durationAverage;
    char mHUDStatsBuffer[120];
};