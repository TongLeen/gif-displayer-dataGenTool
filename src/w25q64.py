from pathlib import Path

from .ch341wrapper import CH341_SpiWrapper, CH341_SpiChipSelect, CH341_SpiConfig





def dummy(length:int) -> bytes:
    return b'\xff' * length 


class W25Q64wrapper:
    def __init__(self, SPI_id:int, device:int):
        self._device = device
        self._spi = CH341_SpiWrapper(SPI_id)
        self._opened = False
        return
        


    def open(self):
        if not self._opened:
            self._spi.open()
        rcv = self._spi.swap(b'\x9f' + dummy(3), self._device)
        print(f'Device ID:\t{hex(int.from_bytes(rcv[2:]))}')
        self._opened = True
        return
    

    def read(self, startAddress:int, size:int) -> bytes:
        self.waitForBusy()
        
        inst = b'\x03'
        addr = startAddress.to_bytes(3)
        dummy = b'\x00' * size

        rcv = self._spi.swap(inst + addr + dummy, self._device)

        return rcv[4:]


    # page : 0 ~ 65535
    def writePage(self, page:int, data:bytes):
        if page < 0 or page > 65535:
            raise RuntimeError(f'Invalid page:{page}')
        if len(data) != 256:
            raise RuntimeWarning(f'Data length != 256 : {len(data)}')
        
        self.waitForBusy()

        
        # write enable
        self._spi.swap(b'\x06', self._device)

        inst = b'\x02'
        addr = page.to_bytes(2) + b'\x00'
        self._spi.swap(inst + addr + data, self._device)
        self.waitForBusy()
        return
    



    def eraserAll(self):
        # write enable
        self._spi.swap(b'\x06', self._device)

        self.waitForBusy()
        inst = b'\xc7'
        self._spi.swap(inst, self._device)
        self.waitForBusy()
        return


    def waitForBusy(self):
        inst = b'\x05'
        while True:
            rcv = self._spi.swap(inst + dummy(1), self._device)
            if rcv[1] & 0b0000_0001 == 0:
                break
        return
    

    def close(self):
        if self._opened:
            self._spi.close()
        self._opened = False
        return



class DataLoader:
    def __init__(self, data:bytes, blockSize:int):
        self.data = data
        self.pointer = 0
        self.pointer_max = len(data)
        self.blockSize = blockSize
        return

    def __iter__(self):
        self.pointer = 0
        return self
    
    def __next__(self):
        if self.pointer == -1:
            raise StopIteration
        if self.pointer + self.blockSize < self.pointer_max:
            retval = self.data[self.pointer:self.pointer + self.blockSize]
            self.pointer += self.blockSize
        else:
            retval = self.data[self.pointer: self.pointer_max]
            self.pointer = -1
        return retval



DEVICE = CH341_SpiChipSelect.D0


def upload(inputPath:Path, port:int) -> None:
    

    with open(inputPath, 'rb') as f:
        data = f.read()

    if len(data) != 7603200:
        print('HEX file is corrupted.')
        return

    match port:
        case 0:
            device = CH341_SpiChipSelect.D0
        case 1:
            device = CH341_SpiChipSelect.D1
        case 2:
            device = CH341_SpiChipSelect.D2
    
    w25q64 = W25Q64wrapper(0, device)
    w25q64.open()

    w25q64.eraserAll()
    print('已全部清空')

    pageCount = 0
    for i in DataLoader(data, 256):
        w25q64.writePage(pageCount, i)
        pageCount += 1
        print(f'已写入{pageCount}页')

        rcv = w25q64.read((pageCount-1)*256, 256)
        if rcv != i:
            print('写入出错')
            print(f'原始数据\t{i}')
            print(f'写入数据\t{rcv}')
            break
    
    # pageCount = 0
    # full = []
    # for i in DataLoader(data, 256):
    #     full.append(w25q64.read(pageCount*256, 256))
    #     pageCount += 1
    #     print(f'已读取{pageCount}页')
    
    # with open('./read.hex', 'wb') as f:
    #     f.write(b''.join(full))

    
    w25q64.close()
    return

    
