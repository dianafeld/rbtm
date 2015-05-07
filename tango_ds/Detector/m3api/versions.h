//****************************************************************************
//** Copyright (c) 2007 SoftHard Technology, Ltd. ****************************
//****************************************************************************
//** CCM Versions defenitions: 
//**
//**  MV40_DLL_VERSION_HIGH
//**  MV40_DLL_VERSION_LOW
//**  MV40_DLL_VERSION_COMPILE
//**  MV40_DLL_VERSION
//**
//**
//****************************************************************************
//****************************************************************************
//****************************************************************************

#ifndef _VERSIONS_
#define _VERSIONS_

#define	MV40_DLL_VERSION_HIGH 4
#define	MV40_DLL_VERSION_LOW 4
#define	MV40_DLL_VERSION_COMPILE 0

#define	MV40_DLL_VERSION	((MV40_DLL_VERSION_HIGH<<24)|(MV40_DLL_VERSION_LOW<<16)|(MV40_DLL_VERSION_COMPILE))

#define	MV40_SYS_VERSION_HIGH		2
#define	MV40_SYS_VERSION_LOW		1
#define	MV40_SYS_VERSION_COMPILE	32

#define	MV40_SYS_VERSION	((MV40_SYS_VERSION_HIGH<<24)|(MV40_SYS_VERSION_LOW<<16)|(MV40_SYS_VERSION_COMPILE))

#define	MU_SYS_VERSION_HIGH			1
#define	MU_SYS_VERSION_LOW			0
#define	MU_SYS_VERSION_COMPILE		3

#define	MU_SYS_VERSION	((MU_SYS_VERSION_HIGH<<24)|(MU_SYS_VERSION_LOW<<16)|(MU_SYS_VERSION_COMPILE))

#define	MQ_SYS_VERSION_HIGH			2
#define	MQ_SYS_VERSION_LOW			0
#define	MQ_SYS_VERSION_COMPILE		0

#define	MQ_SYS_VERSION	((MQ_SYS_VERSION_HIGH<<24)|(MQ_SYS_VERSION_LOW<<16)|(MQ_SYS_VERSION_COMPILE))

#define	API_INST_PACKAGE_VERSION_HIGH 4
#define	API_INST_PACKAGE_VERSION_LOW 04
#define	API_INST_PACKAGE_COMPILE 00

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define API_INST_PACKAGE_VERSION_STRING "V" TOSTRING(API_INST_PACKAGE_VERSION_HIGH) "." TOSTRING(API_INST_PACKAGE_VERSION_LOW) "." TOSTRING(API_INST_PACKAGE_COMPILE)

#endif
