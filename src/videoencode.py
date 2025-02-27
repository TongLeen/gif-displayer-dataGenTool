import cv2 as cv
import numpy as np

from pathlib import Path
from typing import Callable

from .videoprocess import process_fullFrame as process
from .videoprocess import getDropedFrameMap

def encodeFrame(mat:cv.typing.MatLike) -> bytes:
    mat = mat.astype(np.uint16)
    blue = mat[:,:,0] >> 3
    green = mat[:,:,1] >> 2
    red = mat[:,:,2] >> 3
    encoded_mat:np.ndarray =  (red << 11) | (green << 5) | blue
    retval = []
    for row in encoded_mat:
        for i in row:
            retval.append(int(i).to_bytes(length=2))
    return b''.join(retval)


def encodeFrameWithDither(mat:cv.typing.MatLike) -> bytes:
    mat = mat.copy().astype(np.uint16)

    for color in range(3):
        ch = mat[:,:,color]
        if color == 1:
            err_mask = 0b0000_0011
        else:
            err_mask = 0b0000_0111

        for i in range(240-1):
            for j in range(1,240-1):
                error = ch[i, j] & err_mask
                ch[i,   j+1] += error * 7 // 16
                ch[i+1, j-1] += error * 3 // 16
                ch[i+1, j  ] += error * 5 // 16
                ch[i+1, j+1] += error * 1 // 16
    
        for i in range(240):
            for j in range(240):
                if ch[i, j] > 255:
                    ch[i, j] = 255
    return encodeFrame(mat.astype(np.uint8))




def encode(inputPath:Path, outputPath:Path, dither:bool = False) -> int:

    cap = cv.VideoCapture(str(inputPath))
    totalFrameCount = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    dropMap = getDropedFrameMap(totalFrameCount, 66)
    
    global encodeFrame
    if dither:
        encodeFrame = encodeFrameWithDither

    FrameCount = 0
    outData = []
    while cap.isOpened():
        ok, frame = cap.read()
        if ok:
            if dropMap[FrameCount]:
                outData.append(encodeFrame(process(frame)))
        else:
            cap.release()
            break
        FrameCount += 1

    outData = b''.join(outData)
    with open(outputPath, 'wb') as f:
        f.write(outData)
    return len(outData)

