///////////////////////////////////////////////////////////////////////////////////
//          _             _                 _   _ _     
//    _ __ | |_   _  __ _(_)_ __      _   _| |_(_) |___ 
//   | '_ \| | | | |/ _` | | '_ \    | | | | __| | / __|
//   | |_) | | |_| | (_| | | | | |   | |_| | |_| | \__ \
//   | .__/|_|\__,_|\__, |_|_| |_|    \__,_|\__|_|_|___/
//   |_|            |___/                               
//
//	 \brief Plugin utilities
//	 Contains the general plugin utilities for Maya C++ API development
///////////////////////////////////////////////////////////////////////////////////
#include "MPluginUtils.h"
#include <algorithm>

MString utils::mEnvironment = "";


MString utils::pluginEnv(MString t_folder) {
    if (t_folder.length() == 0) { return mEnvironment; }
    return mEnvironment + t_folder + "/";
}


void utils::setPluginEnv(const MString& t_pluginName) {
    MString command = "pluginInfo -query -path \"" + t_pluginName + "\";";
    MString pluginDir = MGlobal::executeCommandStringResult(command);
    int mpos = pluginDir.indexW("plugin");
    mEnvironment = pluginDir.substringW(0, mpos - 1);
    cout << "-> Plugin environment set to: " << utils::mEnvironment << endl;
}


short utils::indexOfMString(std::vector<MString> v, const MString& s) {
    return (short)std::distance(v.begin(), std::find(v.begin(), v.end(), s));
}
