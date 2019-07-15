cmake_minimum_required(VERSION 2.6)
project(MNPR)

# FindMaya.cmake and Utils.cmake directory
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake" )

include(Utils)

# Enable C++11
if(CMAKE_VERSION VERSION_GREATER 3.1)
    set(CMAKE_CXX_STANDARD 11) # C++11...
    set(CMAKE_CXX_STANDARD_REQUIRED ON) #...is required...
else()
    add_compile_options(-std=c++11)
endif()

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# FindMaya (required)
set(MAYA_VERSION 2017 CACHE STRING "Maya version")
find_package( Maya REQUIRED )

# Add source directory (if source not in current source dir)
# add_subdirectory(src)

include_directories(${MAYA_INCLUDE_DIR})  # define a list of preprocessor include file search directories
include_directories("/")  # header files should also be included

link_directories(${MAYA_LIBRARY_DIR}) #specifies a directory where a linker should search for libraries

# Set source files
file( GLOB SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.cpp *.c *.hpp )
file( GLOB HEADERS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} *.h )
file( GLOB SCRIPTS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ../scripts/*.py )
file( GLOB_RECURSE SHADERS_HLSL RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ../shaders/*.fx ../shaders/*.fxh )
file( GLOB_RECURSE SHADERS_GLSL RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} ../shaders/*.ogsfx ../shaders/*.ogsfh )

# TODO: CMAKE only supports .hlsl suffixes. We have to override the tool. However, this way the shader type and model will be ignored.
#set_source_files_properties( ${SHADERS_HLSL} PROPERTIES VS_TOOL_OVERRIDE FXCompile VS_SHADER_TYPE Effect VS_SHADER_MODEL 5.0 )

# Set platform-specific sources
if(WIN32)
	file( GLOB PLATFORM_SRCS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} platform/win32/*.cpp)
else()
	# TODO I guess
endif()

set( SRCS ${SRCS} ${HEADERS} ${SCRIPTS} ${SHADERS_HLSL} ${SHADERS_GLSL} )

# Use utility function to group source files
SOURCE_GROUP_BY_PATH(${SRCS})

# Plugin as a library
ADD_LIBRARY( ${PROJECT_NAME} SHARED ${SRCS})

get_filename_component(PARENT_DIR ${CMAKE_CURRENT_SOURCE_DIR} PATH)
if(WIN32)
    #Windows
    MESSAGE(STATUS "Compiling for Windows")
    set_target_properties( ${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/win )
    if (MSVC)
        set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/win )
        set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/win )
        set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/win )
        set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/win )
        set_target_properties( ${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/win )
    endif()
    set(INSTALL_PATH ${PARENT_DIR}/dist/plugins/${MAYA_VERSION}/win)
elseif(APPLE)
    #macOS
    MESSAGE(STATUS "Compiling for macOS")
    # Set destination of plugin
    set_target_properties( ${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/mac )
    set(INSTALL_PATH ${PARENT_DIR}/dist/plugins/${MAYA_VERSION}/mac)
else()
    # Linux
    MESSAGE(STATUS "Compiling for Linux")
    set_target_properties( ${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${MAYA_VERSION}/linux )
    set(INSTALL_PATH ${PARENT_DIR}/dist/plugins/${MAYA_VERSION}/linux)
endif()

# Link Maya libraries
TARGET_LINK_LIBRARIES( ${PROJECT_NAME} ${MAYA_LIBRARIES})

# Compile (set in FindMaya.cmake)
MAYA_PLUGIN(${PROJECT_NAME})

install(TARGETS ${PROJECT_NAME} DESTINATION ${INSTALL_PATH} )
