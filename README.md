# gif-displayer-dataGenTool
A tool for converting video to hex data and uploading hex data to flash chip.

# 动图显示器：数据处理

> 该仓库是[动图显示器](https://github.com/TongLeen/gif-displayer)的一部分

本程序用以实现对视频文件的处理，生成所需的二进制文件，并提供将其上传到FLASH芯片的方法。

## 视频文件的处理和编码

本项目中使用的显示屏驱动芯片为ST7789，驱动一个240x240，16bit的LCD显示屏。
对于主控MCU——STM32F103来讲，如此庞大的视频数据，没办法保存到内部FALSH当中，也没法实时运算。
因此，唯一的办法就是将视频直接编码成最终显示屏需要的格式，存储在外部的FLASH芯片当中，
直接将FLASH芯片中的数据搬到显示屏上，以实现视频的播放。

考虑到W25Q64芯片的容量为64Mbit，即8MiB，每一帧画面需要 240x240x2=115200 Byte，确定一共保存66帧图像，这大概相当于3秒的视频。
~~(别问为什么是66，随便选的)~~
使用`opencv`读取视频文件，原始的视频文件进行抽帧，改变分辨率，得到240x240，66帧的视频。

ST7789支持多种色彩格式，这里使用RGB565的格式。
