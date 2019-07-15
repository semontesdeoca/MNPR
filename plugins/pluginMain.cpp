///////////////////////////////////////////////////////////////////////////////////
//    __  __    _    ___ _   _ 
//   |  \/  |  / \  |_ _| \ | |
//   | |\/| | / _ \  | ||  \| |
//   | |  | |/ ___ \ | || |\  |
//   |_|  |_/_/   \_\___|_| \_|
//                             
//   \brief MNPR Framework main plugin file
//   Initializes and registers MNPR within Maya
///////////////////////////////////////////////////////////////////////////////////
#include "MPluginUtils.h"
#include "mnpr_cmd.h"
#include "mnpr_nodes.h"
#include "mnpr_renderer.h"
#include <maya/MFnPlugin.h>
#include <maya/MStreamUtils.h>


static MNPROverride* MNPROverrideInstance = NULL;  // render override instance


/// initialize and register all plugin elements
MStatus initializePlugin(MObject obj) {
    MStatus status;
	#if defined(NT_PLUGIN)
		//cout.rdbuf(cerr.rdbuf());  // hack to get error messages out in Maya 2016.5+ when compiling with VS 2015+
		std::cout.set_rdbuf(MStreamUtils::stdOutStream().rdbuf());
		std::cerr.set_rdbuf(MStreamUtils::stdErrorStream().rdbuf());
	#endif


    // create and register override
    MHWRender::MRenderer* theRenderer = MHWRender::MRenderer::theRenderer();
    if (theRenderer) {
        if (!MNPROverrideInstance) {
            MNPROverrideInstance = new MNPROverride(PLUGIN_NAME, RENDERER_NAME);
            status = theRenderer->registerOverride(MNPROverrideInstance);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }

    MFnPlugin fnPlugin(obj, AUTHOR_NAME.asChar(), PLUGIN_NAME.asChar(), "Any");
    // register command
    status = fnPlugin.registerCommand("mnpr", Cmd::creator, Cmd::newSyntax);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    // register node
    status = fnPlugin.registerNode("mnprConfig", ConfigNode::id, ConfigNode::creator, ConfigNode::initialize);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    MNPROverrideInstance->setPlugin(obj);

    cout << "MAYA NON-PHOTOREALISTIC RENDERER (MNPR) PLUGIN INITIALIZED" << endl;
    return status;
}


/// uninitialize and dregister all plugin elements
MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    
    // deregister and delete override
    MHWRender::MRenderer* renderer = MHWRender::MRenderer::theRenderer();
    if (renderer) {
        if (MNPROverrideInstance) {
            status = renderer->deregisterOverride(MNPROverrideInstance);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            delete MNPROverrideInstance;  // delete existing render override instance
            MNPROverrideInstance = nullptr;  // reset pointer
        }
    }

    MFnPlugin fnPlugin(obj);
    // deregister Command
    status = fnPlugin.deregisterCommand("mnpr");
    CHECK_MSTATUS_AND_RETURN_IT(status);
    // deregister Node
    status = fnPlugin.deregisterNode(ConfigNode::id);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    cout << "NON-PHOTOREALISTIC RENDER (MNPR+) PLUGIN TERMINATED" << endl;
    return status;
}


MStatus utils::deregisterNode(MObject obj) {
    MStatus status;
    MFnPlugin fnPlugin(obj);
    status = fnPlugin.deregisterNode(ConfigNode::id);  // deregister node
    cout << "Node has been de-registered" << endl;
    return status;
}


MStatus utils::registerNode(MObject obj) {
    MStatus status;
    // change style of MNPR
    MFnPlugin fnPlugin(obj);
    status = fnPlugin.registerNode("mnprConfig", ConfigNode::id, ConfigNode::creator, ConfigNode::initialize);  // register node again
    cout << "Node has been registered" << endl;
    return status;
}
