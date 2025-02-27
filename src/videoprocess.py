import cv2 as cv
import numpy as np



ORIGIN_VIDEO    = './data/koharu.mp4'
PROCESSED_VIDEO = './data/koharu_cutted.mp4'


TARGET_FREME_COUNT = 66


def process(frame:cv.typing.MatLike) -> cv.typing.MatLike:
    width = 600
    height = 600

    xStart = 200
    yStart = 430
    frame = frame[xStart:xStart+width,yStart:yStart+height]
    frame = cv.resize(frame, (240, 240))
    return frame

def process_fullFrame(frame:cv.typing.MatLike) -> cv.typing.MatLike:
    return cv.resize(frame, (240, 240))

def getDropedFrameMap(total:int, target:int) -> list[bool]:
    retval = [False] * total
    a = (total+1)/(target+1)
    for i in range(target):
        retval[int(a*i+0.5)] = True
    return retval



if __name__ == '__main__':
    cap = cv.VideoCapture(ORIGIN_VIDEO)
    out = cv.VideoWriter(PROCESSED_VIDEO, cv.VideoWriter.fourcc(*'H264'), cap.get(cv.CAP_PROP_FPS), (240, 240))

    totalFrameCount = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    dropMap = getDropedFrameMap(totalFrameCount, 66)
    
    frameCounter = 0
    key = None
    
    while cap.isOpened():
        ok, frame = cap.read()
        if ok:
            if key is None:
                pframe = process(frame)
                cv.imshow('view', pframe)
                while True:
                    key = cv.waitKey()
                    if key == -1 or key == 27:
                        exit()
                    if key == 13:
                        break

            frameCounter += 1
            if dropMap[frameCounter-1]:
                frame = process(frame)
                out.write(frame)
        else:
            cap.release()
            break

    out.release()
    

