import argparse
import os

from pathlib import Path

from src.videodecode import decode
from src.videoencode import encode
from src.w25q64 import upload


def main():
    parser = argparse.ArgumentParser(description="A tool for encode video to hex data for LCD screen.")

    function_group = parser.add_argument_group('Function Select')
    g = function_group.add_mutually_exclusive_group(required=True)
    g.add_argument('-e', action='store_true', help='Encode video file to HEX file.')
    g.add_argument('-d', action='store_true', help='Decode video file from HEX file.')
    g.add_argument('-u', action='store_true', help='Upload HEX file to FLASH chip(W25Q64).')

    info_group = parser.add_argument_group('Parameter')
    info_group.add_argument('-f', type=str, metavar='Path', required=True, help='Input file path.')
    info_group.add_argument('-o', type=str, metavar='Path', help='Output file path.')
    info_group.add_argument('-p', type=int, metavar='PORT', help='Upload port on CH341. Required when "-u" assertted.', choices=[0,1,2])

    args = parser.parse_args()


    inputPath = Path(args.f)
    if not inputPath.exists():
        print('Input file dose not exist.')
        return


    if args.u:
        upload(inputPath, args.p)
        print(f'Upload finished to PORT{args.p}.')
        return

    if args.o is None:
        if args.e:
            output = 'out.hex'
        elif args.d:
            output = 'out.mp4'
    else:
        output = args.o
    
    outputPath = Path(output)
    if not outputPath.parent.exists():
        os.makedirs(str(outputPath.absolute()))
        print(f'Created new dir:{str(outputPath.absolute())}')
    

    if args.e:
        encode(inputPath, outputPath)
    else:
        decode(inputPath, outputPath)
    
    print(f'Finished. Output file:{str(outputPath)}')
    return

    
if __name__ == '__main__':
    main()