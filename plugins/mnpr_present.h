#pragma once
///////////////////////////////////////////////////////////////////////////////////
//                                   _                                  _   _             
//    _ __  _ __ ___  ___  ___ _ __ | |_      ___  _ __   ___ _ __ __ _| |_(_) ___  _ __  
//   | '_ \| '__/ _ \/ __|/ _ \ '_ \| __|    / _ \| '_ \ / _ \ '__/ _` | __| |/ _ \| '_ \ 
//   | |_) | | |  __/\__ \  __/ | | | |_    | (_) | |_) |  __/ | | (_| | |_| | (_) | | | |
//   | .__/|_|  \___||___/\___|_| |_|\__|    \___/| .__/ \___|_|  \__,_|\__|_|\___/|_| |_|
//   |_|                                          |_|                                     
//   
//   \brief Present operation
//	 Contains the MPresentTarget that will display the active render target in the viewport
///////////////////////////////////////////////////////////////////////////////////
#include "MRenderTargetList.h"


class PresentTarget : public MHWRender::MPresentTarget {
public:
    PresentTarget(const MString &t_name, MRenderTargetList* t_targetList) :
        MPresentTarget(t_name) {
        mTargets[0] = t_targetList->target(t_targetList->length() - 1);
        mTargets[1] = t_targetList->target(1);  // depth
    }
    ~PresentTarget() {}

    /// target override list
    MHWRender::MRenderTarget* const* targetOverrideList(unsigned int &listSize) {
        if (mTargets) {
            listSize = 2;
            return mTargets;
        }
        listSize = 0;
        return nullptr;
    }

protected:
    MHWRender::MRenderTarget* mTargets[2];  ///< target list that is presented on the viewport
};
