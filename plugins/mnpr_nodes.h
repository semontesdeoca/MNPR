#pragma once
///////////////////////////////////////////////////////////////////////////////////
//                                                   _           
//    _ __ ___  _ __  _ __  _ __     _ __   ___   __| | ___  ___ 
//   | '_ ` _ \| '_ \| '_ \| '__|   | '_ \ / _ \ / _` |/ _ \/ __|
//   | | | | | | | | | |_) | |      | | | | (_) | (_| |  __/\__ \
//   |_| |_| |_|_| |_| .__/|_|      |_| |_|\___/ \__,_|\___||___/
//                   |_|                                         
//
//   \brief Classes of MNPR nodes
//	 Contains the classes that define different MNPR nodes
///////////////////////////////////////////////////////////////////////////////////
#include <maya/MStatus.h>
#include <maya/MPxNode.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnStringData.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnCompoundAttribute.h>


// helper pre-processors
#define MAKE_INPUT(attr) \
    CHECK_MSTATUS(attr.setKeyable(true)); \
    CHECK_MSTATUS(attr.setStorable(true)); \
    CHECK_MSTATUS(attr.setReadable(true)); \
    CHECK_MSTATUS(attr.setWritable(true));
#define MAKE_OUTPUT(attr) \
    CHECK_MSTATUS(attr.setKeyable(false)); \
    CHECK_MSTATUS(attr.setStorable(false)); \
    CHECK_MSTATUS(attr.setReadable(true)); \
    CHECK_MSTATUS(attr.setWritable(false));


///////////////////////////////////////////////////////////////////////////////////
//	\brief MNPR config node
//	This header file provides a generic node class with its basic methods
///////////////////////////////////////////////////////////////////////////////////
class ConfigNode : public MPxNode {
public:
    static MTypeId id;										  ///< unique id of the node type
    ConfigNode() {};
    virtual ~ConfigNode() {};
    static void* creator() { return new ConfigNode; };		  ///< return pointer to node instance
    
    static MStatus initialize();							  ///< sets up attributes in the node
    static MStatus initializeCustomParameters();              ///< initializes custom parameters
    static MStatus enableAttribute(MObject& attribute);       ///< adds attribute and sets attributAffects
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);   ///< performs the calculations of the node
    static MStatus computeCustomParameters(MDataBlock& data); ///< computes custom parameters

    static MObject aEvaluate;
};