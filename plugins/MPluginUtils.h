#pragma once
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
#include <vector>
#include <maya/MGlobal.h>


class utils {
public:
    static MString pluginEnv(MString t_folder);  ///< Gets the plugin environment (path)
    static void setPluginEnv(const MString& t_pluginName);  ///< Sets the plugin environment
    static short indexOfMString(std::vector<MString> v, const MString &s);  ///< Returns the index of an MString in vector
    static MStatus registerNode(MObject obj);  ///< register plugin node
    static MStatus deregisterNode(MObject obj);  ///< deregister plugin node
protected:
    static MString mEnvironment;  ///< path where the plugin is located
};
