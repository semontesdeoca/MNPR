#pragma once
///////////////////////////////////////////////////////////////////////////////////
//                        _ _               
//    ___  __ _ _ __   __| | |__   _____  __
//   / __|/ _` | '_ \ / _` | '_ \ / _ \ \/ /
//   \__ \ (_| | | | | (_| | |_) | (_) >  < 
//   |___/\__,_|_| |_|\__,_|_.__/ \___/_/\_\
//                                          
//	 \brief Sandbox stylization pipeline
//	 Contains the sandbox stylization pipeline with all necessary targets and operations
//	 Use this style to develop whatever stylization you'd like
//
//   Developed by: You!
//
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"

namespace sb {

	void addTargets(MRenderTargetList &targetList) {
		// add style specific targets

		unsigned int tWidth = targetList[0]->width();
		unsigned int tHeight = targetList[0]->height();
		int MSAA = targetList[0]->multiSampleCount();
		unsigned arraySliceCount = 0;
		bool isCubeMap = false;
		MHWRender::MRasterFormat rgba8 = MHWRender::kR8G8B8A8_SNORM;
		MHWRender::MRasterFormat rgb8 = MHWRender::kR8G8B8X8;

		targetList.append(MHWRender::MRenderTargetDescription("testTarget", tWidth, tHeight, 1, rgba8, arraySliceCount, isCubeMap));
	}


	void addOperations(MHWRender::MRenderOperationList &mRenderOperations, MRenderTargetList &mRenderTargets,
		EngineSettings &mEngSettings, FXParameters &mFxParams) {
		MString opName = "";

		opName = "[quad] test pass";
		auto opShader = new MOperationShader("quadTest", "testTechnique");
		opShader->addTargetParameter("gColorTex", mRenderTargets.target(mRenderTargets.indexOf("stylizationTarget")));
		opShader->addParameter("gAwesomeParameter", mFxParams.awesomeParameter);
		auto quadOp = new QuadRender(opName,
			MHWRender::MClearOperation::kClearNone,
			mRenderTargets,
			*opShader);
		mRenderOperations.append(quadOp);
		mRenderTargets.setOperationOutputs(opName, { "stylizationTarget" });
	}
};
