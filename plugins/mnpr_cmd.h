#pragma once
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
#include <maya/MSyntax.h>
#include <maya/MPxCommand.h>
#include <maya/MArgDatabase.h>


class Cmd : public MPxCommand {
public:
    Cmd();
    ~Cmd();
    static void* creator();						 ///< command creator
    static MSyntax newSyntax();					 ///< define syntax of command
    virtual MStatus doIt(const MArgList& args);  ///< compute the command  
    virtual MStatus redoIt();					 ///< compute the command (what should happen when you redo)
    virtual MStatus undoIt();					 ///< command undoer
    bool isUndoable() const;					 ///< can you undo it?
};