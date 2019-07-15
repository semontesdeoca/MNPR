///////////////////////////////////////////////////////////////////////////////////
//                                                                                 _ 
//    _ __ ___  _ __  _ __  _ __      ___ ___  _ __ ___  _ __ ___   __ _ _ __   __| |
//   | '_ ` _ \| '_ \| '_ \| '__|    / __/ _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` |
//   | | | | | | | | | |_) | |      | (_| (_) | | | | | | | | | | | (_| | | | | (_| |
//   |_| |_| |_|_| |_| .__/|_|       \___\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|
//                   |_|                                                             
//
//   \brief     MNPR command
//	 Contains all functionalities of the "mnpr" command to communicate with the
//   plugin from scripting languages (MEL and Python)
///////////////////////////////////////////////////////////////////////////////////
#include "mnpr_renderer.h"
#include "mnpr_cmd.h"
#include "MPluginUtils.h"


// argument strings
const char *environmentSN = "-env";
const char *environmentLN = "-environment";
const char *styleSN = "-stl";
const char *styleLN = "-style";
const char *resetStyleSN = "-rSt";
const char *resetStyleLN = "-resetStylization";
const char *listTargetsSN = "-lsT";
const char *listTargetsLN = "-listTargets";
const char *listOperationsSN = "-lsO";
const char *listOperationsLN = "-listOperations";
const char *activeRenderTargetSN = "-rT";
const char *activeRenderTargetLN = "-renderTarget";
const char *renderOpSN = "-rOp";
const char *renderOpLN = "-renderOperation";
const char *reloadOpShadersSN = "-rOS";
const char *reloadOpShadersLN = "-reloadOperationShaders";
const char *stateSN = "-s";
const char *stateLN = "-state";
const char *refreshShadersSN = "-r";
const char *refreshShadersLN = "-refresh";
const char *rendererNameSN = "-n";
const char *rendererNameLN = "-name";
const char *presentChannelsSN = "-ch";
const char *presentChannelsLN = "-channels";
const char *presentColorTransformationSN = "-ct";
const char *presentColorTransformationLN = "-colorTransform";
const char *registerNodeSN = "-rn";
const char *registerNodeLN = "-registerNode";
const char *mnprGammaSN = "-g";
const char *mnprGammaLN = "-gamma";


// constructor and destructor
Cmd::Cmd() { }
Cmd::~Cmd() { }

// command creator
void* Cmd::creator() {
    return new Cmd();
}

// syntax initializer
MSyntax Cmd::newSyntax() {
    MSyntax syntax;

    syntax.enableQuery(true);  // enable query of flags
    syntax.enableEdit(false);
    // get environment flag
    syntax.addFlag(environmentSN, environmentLN, MSyntax::kBoolean);
    // get style flag
    syntax.addFlag(styleSN, styleLN, MSyntax::kString);
    // get style reset flag
    syntax.addFlag(resetStyleSN, resetStyleLN, MSyntax::kNoArg);
    // list render targets flag
    syntax.addFlag(listTargetsSN, listTargetsLN, MSyntax::kBoolean);
    // list render operations flag
    syntax.addFlag(listOperationsSN, listOperationsLN, MSyntax::kBoolean);
    // set active render target flag
    syntax.addFlag(activeRenderTargetSN, activeRenderTargetLN, MSyntax::kUnsigned);
    // get render operation state flag
    syntax.addFlag(renderOpSN, renderOpLN, MSyntax::kUnsigned);
    // get refresh operation shaders index
    syntax.addFlag(reloadOpShadersSN, reloadOpShadersLN, MSyntax::kUnsigned);
    // set render operation state flag
    syntax.addFlag(stateSN, stateLN, MSyntax::kUnsigned);
    // refresh shaders flag
    syntax.addFlag(refreshShadersSN, refreshShadersLN, MSyntax::kNoArg);
    // get renderer name flag
    syntax.addFlag(rendererNameSN, rendererNameLN, MSyntax::kNoArg);
    // set present channels
    syntax.addFlag(presentChannelsSN, presentChannelsLN, MSyntax::kBoolean, MSyntax::kBoolean, MSyntax::kBoolean, MSyntax::kBoolean);
    // set present color transformation
    syntax.addFlag(presentColorTransformationSN, presentColorTransformationLN, MSyntax::kUnsigned);
    // register node
    syntax.addFlag(registerNodeSN, registerNodeLN, MSyntax::kBoolean);
    // freeze gamma
    syntax.addFlag(mnprGammaSN, mnprGammaLN, MSyntax::kBoolean);

    return syntax;
}


// command parser
MStatus Cmd::doIt(const MArgList& args) {
    MStatus	status;
    MHWRender::MRenderer* theRenderer = MHWRender::MRenderer::theRenderer();
    MNPROverride* MNPR = (MNPROverride*)theRenderer->findRenderOverride(PLUGIN_NAME);
    if (!MNPR) {
        cout << "WARNING: No render override instance was found" << endl;
        return MStatus::kFailure;
    }

    // parse arguments
    MArgDatabase argData(syntax(), args);  // so that is works with python
    bool query = argData.isQuery();

    // check for environment flag
    if (argData.isFlagSet(environmentSN)) {
        setResult(utils::pluginEnv(""));
    }
    // check for style flag
    if (argData.isFlagSet(styleSN)) {
        if (query) {
            //cout << "querying current style" << endl;
            setResult(MNPR->mEngSettings.style);
        } else {
            setResult(utils::indexOfMString(STYLES, MNPR->mEngSettings.style));
        }

    }
    // check for style reset
    if (argData.isFlagSet(resetStyleSN)) {
        //cout << "resetting style" << endl;
        MNPR->resetStylization();
    }
    // check for requesting targets
    if (argData.isFlagSet(listTargetsSN)) {
        setResult(MNPR->renderTargets());
    }
    // check for requesting operations
    if (argData.isFlagSet(listOperationsSN)) {
        setResult(MNPR->renderOperations());
    }
    // check if active render target is changed
    if (argData.isFlagSet(activeRenderTargetSN)) {
        unsigned int targetIndex;
        argData.getFlagArgument(activeRenderTargetSN, 0, targetIndex);
        //cout << "Changing active render target to: " << targetIndex << endl;
        MNPR->changeActiveTarget(targetIndex);
    }
    // check if renderOperation state is changed
    if (argData.isFlagSet(renderOpSN)) {
        unsigned renderOp;
        argData.getFlagArgument(renderOpSN, 0, renderOp);
        if (argData.isFlagSet(stateSN)) {
            bool opState;
            argData.getFlagArgument(stateSN, 0, opState);
            // set operation state
            MNPR->mRenderOperations[renderOp]->setEnabled(opState);
        }
        // get render operation state
        setResult(MNPR->mRenderOperations[renderOp]->enabled());
    }
    // check if operation shaders need to be refreshed
    if (argData.isFlagSet(reloadOpShadersSN)) {
        unsigned renderOpIndex;
        argData.getFlagArgument(reloadOpShadersSN, 0, renderOpIndex);
        cout << "Shaders of operation index " << renderOpIndex << " will be refreshed" << endl;
        MNPR->resetShaderInstances(renderOpIndex);
    }
    // check if shaders need to be refreshed
    if (argData.isFlagSet(refreshShadersSN)) {
        //cout << "Shaders will be refreshed" << endl;
        MNPR->resetShaderInstances();
    }
    // check if renderer name was requested
    if (argData.isFlagSet(rendererNameSN)) {
        cout << "Requesting renderer name" << endl;
        setResult(MNPR->uiName());
    }
    // check if the present channels are being set
    if (argData.isFlagSet(presentChannelsSN)) {
        //cout << "Changing the channels to present" << endl;
        int r, g, b, a;
        argData.getFlagArgument(presentChannelsSN, 0, r);
        argData.getFlagArgument(presentChannelsSN, 1, g);
        argData.getFlagArgument(presentChannelsSN, 2, b);
        argData.getFlagArgument(presentChannelsSN, 3, a);
        cout << "( " << r << ", " << g << ", " << b << ", " << a << ")" << endl;
        MNPR->debugOperation(float(r), float(g), float(b), float(a));
    }
    // check if the present color transformation is being set
    if (argData.isFlagSet(presentColorTransformationSN)) {
        //cout << "Transforming the color model to present" << endl;
        int ctMode;
        argData.getFlagArgument(presentColorTransformationSN, 0, ctMode);
        cout << "Changing the color transformation mode to present to: " << ctMode << endl;
        MNPR->debugColorTransform(float(ctMode));
    }
    // check for node registration
    if (argData.isFlagSet(registerNodeSN)) {
        bool registration;
        argData.getFlagArgument(registerNodeSN, 0, registration);
        if (registration) {
            //cout << "Registering node" << endl;
            utils::registerNode(MNPR->mPlugin);
        } else {
            //cout << "Deregistering node" << endl;
            utils::deregisterNode(MNPR->mPlugin);
        }
    }
    // check if gamma needs to be frozen
    if (argData.isFlagSet(mnprGammaSN)) {
        bool mnprGamma;
        argData.getFlagArgument(mnprGammaSN, 0, mnprGamma);
        if (mnprGamma) {
            if (MNPR->mEngSettings.mayaGamma[0] == 0.0) {
                // freeze Maya gamma update but don't perform MNPR gamma correction
                MNPR->mEngSettings.mnprGamma[0] = 0.5;
            } else {
                // perform MNPR gamma correction
                MNPR->mEngSettings.mnprGamma[0] = 1.0;
            }
        } else {
            MNPR->mEngSettings.mnprGamma[0] = 0.0;
        }
    }

    return redoIt();  // normally a command should execute here
}

// command execution (not needed as it is undoable)
MStatus Cmd::redoIt() {
    MStatus	status;

    // cause a refresh to occur so that viewports will update
    MGlobal::executeCommandOnIdle("refresh");

    return MS::kSuccess;
}

// undoable state of command
bool Cmd::isUndoable() const {
    return false;  // this command doesnt need to be undoable
}

// command undoer (not needed as it is undoable)
MStatus Cmd::undoIt() {;
    return MS::kSuccess;  // we don't provide any undo procedure
}
