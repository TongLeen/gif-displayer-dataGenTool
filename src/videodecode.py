import cv2 as cv
import numpy as np

from pathlib import Path



FRAME_SIZE = 240*240*2
                             

def frameDecode(data:bytes) -> np.ndarray:
    retval = np.empty((240,240,3), np.uint8)
    for i in range(240):         
        for j in range(240):
            msb = data[(i*240+j)*2]
            lsb = data[(i*240+j)*2+1]
            retval[i,j,2] = msb & 0b1111_1000
            retval[i,j,1] = ((msb & 0b0000_0111) << 5) | (((lsb &0b1110_0000)>>3)) 
            retval[i,j,0] = (lsb & 0b0001_1111) << 3
    return retval
    


def decode(inputPath:Path, outputPath:Path) -> None:
    with open(inputPath, 'rb') as f:
        content = f.read()

    frameCount = len(content) // FRAME_SIZE
    if frameCount * FRAME_SIZE != len(content):
        raise RuntimeError('Hex file corrupted...')
    
    out = cv.VideoWriter(str(outputPath.absolute()), cv.VideoWriter.fourcc(*'avc1'), 20, (240, 240))
    for i in range(frameCount):
        frame = frameDecode(content[i*FRAME_SIZE:(i+1)*FRAME_SIZE])   
        out.write(frame)      
        # cv.imshow('frame', frame)
        # cv.imshow('R', frame[:,:,0])
        # cv.imshow('G', frame[:,:,1])
        # cv.imshow('B', frame[:,:,2])
        # if cv.waitKey() == -1:
        #     break
    out.release()
    return


def view(inputPath:Path) -> None:
    with open(inputPath, 'rb') as f:
        content = f.read()

    frameCount = len(content) // FRAME_SIZE
    if frameCount * FRAME_SIZE != len(content):
        raise RuntimeError('Hex file corrupted...')
    
    for i in range(frameCount):
        frame = frameDecode(content[i*FRAME_SIZE:(i+1)*FRAME_SIZE])   
        cv.imshow('frame', frame)
        # cv.imshow('R', frame[:,:,0])
        # cv.imshow('G', frame[:,:,1])
        # cv.imshow('B', frame[:,:,2])
        if cv.waitKey() == -1:
            break
    return
