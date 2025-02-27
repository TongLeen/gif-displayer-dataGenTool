import ctypes

from ctypes import c_ubyte, c_ulong, c_void_p, c_bool
from enum import Enum
from typing import Literal


###############################################################################
# load dll when import/run this file
# Windows Only

dll = ctypes.windll.LoadLibrary("CH341DLLA64.dll")
print(f'CH341DLL Version:{dll.CH341GetVersion()}')

dll.CH341OpenDevice.argtypes    = [c_ulong]
dll.CH341OpenDevice.argtypes    = [c_ulong]

dll.CH341CloseDevice.argtypes   = [c_ulong]

dll.CH341StreamSPI4.argtypes    = [c_ulong, c_ulong, c_ulong, c_void_p]
dll.CH341StreamSPI4.restype     = c_bool



###############################################################################
# Configure for SPI transmit

class CH341_SpiConfig:
    SPEED_MAP = {
        '20k' :0b0000_0000,
        '100k':0b0000_0001,
        '400k':0b0000_0010,
        '750k':0b0000_0011,
    }

    FIRST_BIT_MAP = {
        'msb':0b1000_0000,
        'lsb':0b0000_0000,
    }

    def __init__(self, 
                 speed:Literal['20k', '100k', '400k', '750k']='20k', 
                 firstBit:Literal['msb', 'lsb']='msb'):
        self.config = self.SPEED_MAP[speed] | self.FIRST_BIT_MAP[firstBit]
        return
    


###############################################################################
# Device Select

class CH341_SpiChipSelect(Enum):
    D0 = c_ulong(0b1000_0000)
    D1 = c_ulong(0b1000_0001)
    D2 = c_ulong(0b1000_0010)



###############################################################################
# CH341 SPI part wrapper 

class CH341_SpiWrapper:
    def __init__(self, id:int = 0) -> None:
        """Init a CH341 device

        Args:
            id (int, optional): Device id. `0` means the first CH341 plugged in; `1` means the second. Defaults to 0.
        """
        self.id = id
        self.opened = False
        return
    
    def open(self, *, config:CH341_SpiConfig = None) -> None:
        """Open this CH341 for transmitting. Must open before using.

        Args:
            config (CH341_SpiConfig, optional): Transmission configure (speed etc.). Defaults to None.

        Raises:
            OSError: Failed to open this device.
        """
        if self.opened:
            return
    
        ok = dll.CH341OpenDevice(self.id)
        if ok == -1:
            raise OSError(f'Failed to open device CH341@id={self.id}')
        else:
            self.opened = True
        
        if config is None:
            config = CH341_SpiConfig()
        self.config(config)
        return
    
    def config(self, config:CH341_SpiConfig) -> None:
        """Change transmission configure when opened.

        Args:
            config (CH341_SpiConfig): Transmission configure (speed etc.).
        """
        dll.CH341SetStream(c_ulong(self.id), config.config)
        return

    def swap(self, dataForSend:bytes, device:CH341_SpiChipSelect) -> bytes:
        """Transmit bytes using SPI.

        Send argument `dataForSend` and return reveiced data in type `bytes`.

        Args:
            dataForSend (bytes): Data for sending by SPI
            device (CH341_SpiChipSelect): Which device will be selected.

        Returns:
            bytes: Data received.
        """
        buffer = (c_ubyte*len(dataForSend)).from_buffer_copy(dataForSend)
        dll.CH341StreamSPI4(
            self.id,
            device.value,
            len(dataForSend),
            ctypes.cast(ctypes.pointer(buffer), c_void_p)
        )
        return bytes(buffer)


    def close(self) -> None:
        """Close this CH341 device.

        Remember to close this device after using.
        """
        if not self.opened:
            return
        dll.CH341CloseDevice(self.id)
        self.opened = False
        return
    



###############################################################################
# An example shows how to use this.

if __name__ == '__main__':

    cfg = CH341_SpiConfig('100k', 'msb')
    device = CH341_SpiChipSelect.D0

    dataForSend = b'abc'

    # Choose a device for using.
    # Usually id=0. That means the first CH341 plugged in. 
    ch341 = CH341_SpiWrapper(id=0)

    # Open this device.
    # You can configure SPI at this time. 
    # Also you can use `ch341.config(cfg)` to change configure after opening.
    ch341.open(config=cfg)

    # Send data and receive data EASILY.
    # Remenber to choose which device to transmit.
    rcv = ch341.swap(dataForSend, device)

    # Close device after using.
    ch341.close()
