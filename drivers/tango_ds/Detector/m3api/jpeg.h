#ifndef __JPEG_H__
#define __JPEG_H__



#ifdef __cplusplus
    extern "C" {
#endif



#define DLL __declspec(dllexport) __cdecl



////////////////////////////////////////////////////////////////////////////////
// Basic data types
////////////////////////////////////////////////////////////////////////////////
#define JPEG_ALIGNMENT 4U

typedef enum{
    JPEG_OK,                           //No error
    JPEG_INVALID_DEVICE,               //Incompatible device or no CUDA-capable devices present
    JPEG_INSUFFICIENT_DEVICE_MEMORY,   //Insufficient device memory
    JPEG_INSUFFICIENT_HOST_MEMORY,     //Insufficient host memory
    JPEG_INVALID_HANDLE,               //Invalid JPEG encoder / decoder handle
    JPEG_INVALID_VALUE,                //Invalid API enum value
    JPEG_INVALID_SIZE,                 //Invalid image dimensions
    JPEG_UNALIGNED_DATA,               //Buffer base pointers or pitch not properly aligned
    JPEG_INVALID_TABLE,                //Invalid quantization / Huffman table
    JPEG_BUFFER_OVERRUN,               //Encoding destination buffer is not large enough to store encoded data
    JPEG_BITSTREAM_CORRUPT,            //Decoding error
    JPEG_EXECUTION_FAILURE,            //Device execution failure (TDR watchdog?)
    JPEG_INTERNAL_ERROR,               //Internal error

    JPEG_IO_ERROR,                     //Failed to open/access file
    JPEG_INVALID_FORMAT,               //Invalid file format
    JPEG_UNSUPPORTED_FORMAT,           //File format is unsupported by the current version of FVJPEG

    JPEG_UNKNOWN_ERROR                 //Unrecognized error
} jpegStatus_t;



typedef enum{
    JPEG_I8,
    JPEG_RGB8,
    JPEG_BGR8,
    JPEG_CrCbY8,
    JPEG_YCbCr8,
    JPEG_BAYER_RGGB8,
    JPEG_BAYER_BGGR8,
    JPEG_BAYER_GBRG8,
    JPEG_BAYER_GRBG8
} jpegSurfaceFormat_t;



typedef enum{
    //JPEG_TOP_BOTTOM = 0x0U,
    //JPEG_BOTTOM_TOP = 0x1U
} jpegSurfaceOrientation_t;

typedef enum{
    JPEG_Y, JPEG_444, JPEG_422, JPEG_420
} jpegSubsamplingFormat_t;

typedef enum{
	JPEG_ADD, JPEG_SUB, JPEG_MUL, JPEG_DIV
} jpegMatrixOperationType_t;

////////////////////////////////////////////////////////////////////////////////
// 
////////////////////////////////////////////////////////////////////////////////
typedef struct jpegEncoderHandleStruct *jpegEncoderHandle_t;
typedef struct jpegDecoderHandleStruct *jpegDecoderHandle_t;


typedef struct{
    unsigned char data[64];
} jpegQuantTable_t;

typedef struct{
    jpegQuantTable_t table[4];
} jpegQuantState_t;


typedef struct{
    unsigned char bucket[16];
    unsigned char alphabet[256];
} jpegHuffmanTable_t;

typedef struct{
    jpegHuffmanTable_t table[2][2];
} jpegHuffmanState_t;



typedef struct{
    unsigned channels;
    unsigned grouping;
} jpegScanMask_t;

typedef struct{
    unsigned quant;
    unsigned huffman[2];
} jpegTableMask_t;



typedef struct{
    unsigned                   height;
    unsigned                   width;
    jpegSurfaceFormat_t      format;
    jpegSurfaceOrientation_t orientation;
} jpegSurface_t;



typedef struct{
    unsigned   quantTableMask;
    unsigned huffmanTableMask[2];
    unsigned  scanChannelMask;
    unsigned    scanGroupMask;
} jpegScanStruct_t;


typedef struct {
	float blackShift;
	float redScale;
	float greenScale;
	float blueScale;
} jpegCorrectionCoefficients_t;


///////////////////////////////////////////////////////////////////////////////
// Core encoding/decoding calls
///////////////////////////////////////////////////////////////////////////////
extern jpegStatus_t DLL jpegInit(unsigned affinity);

extern jpegStatus_t DLL jpegCreateEncoderHandle(
    jpegEncoderHandle_t *handle,
    jpegSurfaceFormat_t  surfaceFmt,
    jpegSubsamplingFormat_t samplingFmt,
    unsigned               surfaceHeight,
    unsigned               surfaceWidth,
    unsigned               surfacePitch8
);

extern jpegStatus_t DLL jpegCreateDecoderHandle(
    jpegDecoderHandle_t *handle,
    jpegSurfaceFormat_t  surfaceFmt,
    jpegSubsamplingFormat_t samplingFmt,
    unsigned               surfaceHeight,
    unsigned               surfaceWidth,
    unsigned               surfacePitch8
);

extern jpegStatus_t DLL jpegEncodeSetBlackShift(
	jpegEncoderHandle_t  handle,

	const jpegSurfaceFormat_t surfaceFmt,
	const unsigned char *h_BlackMask
);

extern jpegStatus_t DLL jpegEncodeSetCorrectionCoefficients(
	jpegEncoderHandle_t  handle,

	jpegCorrectionCoefficients_t *correctionCoefficients
);

extern jpegStatus_t DLL jpegEncodeSetCorrectionMatrix(
	jpegEncoderHandle_t  handle,

	const unsigned char *h_Matrix,
	jpegMatrixOperationType_t matrixType
);

extern jpegStatus_t DLL jpegEncode(
    jpegEncoderHandle_t handle,

    unsigned char        *h_Bytestream,
    unsigned             *bytestreamSize,

    jpegQuantState_t   *quantTableState,
    jpegHuffmanState_t *huffmanTableState,
    jpegScanStruct_t      *scanMap,

    unsigned              quality,
    unsigned              restartInterval,
    const unsigned char   *h_Surface
);

extern jpegStatus_t DLL jpegDecode(
    jpegDecoderHandle_t       handle,

    unsigned char              *h_Surface,

    const unsigned char        *h_Bytestream,
    unsigned                    bytestreamSize,

    const jpegQuantState_t   *quantState,
    const jpegHuffmanState_t *huffmanState,
    const jpegScanStruct_t   *scanMap,

    unsigned                    restartInterval
);

extern jpegStatus_t DLL jpegDestroyEncoderHandle(jpegEncoderHandle_t handle);

extern jpegStatus_t DLL jpegDestroyDecoderHandle(jpegDecoderHandle_t handle);

extern jpegStatus_t DLL jpegMalloc(void **buffer, size_t size);

extern jpegStatus_t DLL jpegFree(void *buffer);

extern jpegStatus_t DLL jpegPrintMemo();



////////////////////////////////////////////////////////////////////////////////
// File handling
////////////////////////////////////////////////////////////////////////////////
extern jpegStatus_t DLL fvjfifStore(
    const char                  *filename,

    const unsigned char         *h_Bytestream,
    unsigned                     bytestreamSize,

    const jpegQuantState_t    *quantState,
    const jpegHuffmanState_t  *huffmanState,
    const jpegScanStruct_t    *scanMap,

    unsigned                     surfaceHeight,
    unsigned                     surfaceWidth,
    jpegSubsamplingFormat_t      samplingFmt,
    unsigned                     restartInterval
);

extern jpegStatus_t DLL fvjfifLoad(
    const char             *filename,

    unsigned char         **h_Bytestream,
    unsigned               *bytestreamSize,

    jpegQuantState_t     *quantState,
    jpegHuffmanState_t   *huffmanState,
    jpegScanStruct_t     *scanMap,

    unsigned               *surfaceHeight,
    unsigned               *surfaceWidth,
    jpegSubsamplingFormat_t *samplingFmt,
    unsigned               *restartInterval
);



#ifdef __cplusplus
}
#endif



#endif
