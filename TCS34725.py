# Here's a probably-not-very-good port of the Adafruit Arduino library for
# this sensor. The Adafruit library is located here:
# https://github.com/adafruit/Adafruit_TCS34725
# This port is for the Beaglebone Black and the Adafruit_BBIO and Adafruit_I2C
# libraries. By AKA MEDIA SYSTEM

from Adafruit_I2C import Adafruit_I2C
import time

class TCS34725():

    TCS34725_ADDRESS          = 0x29)

    TCS34725_COMMAND_BIT      = 0x80

    TCS34725_ENABLE           = 0x00
    TCS34725_ENABLE_AIEN      = 0x10    # RGBC Interrupt Enable 
    TCS34725_ENABLE_WEN       = 0x08    # Wait enable - Writing 1 activates the wait timer 
    TCS34725_ENABLE_AEN       = 0x02    # RGBC Enable - Writing 1 actives the ADC, 0 disables it 
    TCS34725_ENABLE_PON       = 0x01    # Power on - Writing 1 activates the internal oscillator, 0 disables it 
    TCS34725_ATIME            = 0x01    # Integration time 
    TCS34725_WTIME            = 0x03    # Wait time (if TCS34725_ENABLE_WEN is asserted 
    TCS34725_WTIME_2_4MS      = 0xFF    # WLONG0 = 2.4ms   WLONG1 = 0.029s 
    TCS34725_WTIME_204MS      = 0xAB    # WLONG0 = 204ms   WLONG1 = 2.45s  
    TCS34725_WTIME_614MS      = 0x00    # WLONG0 = 614ms   WLONG1 = 7.4s   
    TCS34725_AILTL            = 0x04    # Clear channel lower interrupt threshold 
    TCS34725_AILTH            = 0x05
    TCS34725_AIHTL            = 0x06    # Clear channel upper interrupt threshold 
    TCS34725_AIHTH            = 0x07
    TCS34725_PERS             = 0x0C    # Persistence register - basic SW filtering mechanism for interrupts 
    TCS34725_PERS_NONE        = 0b0000  # Every RGBC cycle generates an interrupt                                
    TCS34725_PERS_1_CYCLE     = 0b0001  # 1 clean channel value outside threshold range generates an interrupt   
    TCS34725_PERS_2_CYCLE     = 0b0010  # 2 clean channel values outside threshold range generates an interrupt  
    TCS34725_PERS_3_CYCLE     = 0b0011  # 3 clean channel values outside threshold range generates an interrupt  
    TCS34725_PERS_5_CYCLE     = 0b0100  # 5 clean channel values outside threshold range generates an interrupt  
    TCS34725_PERS_10_CYCLE    = 0b0101  # 10 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_15_CYCLE    = 0b0110  # 15 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_20_CYCLE    = 0b0111  # 20 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_25_CYCLE    = 0b1000  # 25 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_30_CYCLE    = 0b1001  # 30 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_35_CYCLE    = 0b1010  # 35 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_40_CYCLE    = 0b1011  # 40 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_45_CYCLE    = 0b1100  # 45 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_50_CYCLE    = 0b1101  # 50 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_55_CYCLE    = 0b1110  # 55 clean channel values outside threshold range generates an interrupt 
    TCS34725_PERS_60_CYCLE    = 0b1111  # 60 clean channel values outside threshold range generates an interrupt 
    TCS34725_CONFIG           = 0x0D
    TCS34725_CONFIG_WLONG     = 0x02    # Choose between short and long (12x wait times via TCS34725_WTIME 
    TCS34725_CONTROL          = 0x0F    # Set the gain level for the sensor 
    TCS34725_ID               = 0x12    # 0x44 = TCS34721/TCS34725, 0x4D = TCS34723/TCS34727 
    TCS34725_STATUS           = 0x13
    TCS34725_STATUS_AINT      = 0x10    # RGBC Clean channel interrupt 
    TCS34725_STATUS_AVALID    = 0x01    # Indicates that the RGBC channels have completed an integration cycle 
    TCS34725_CDATAL           = 0x14    # Clear channel data 
    TCS34725_CDATAH           = 0x15
    TCS34725_RDATAL           = 0x16    # Red channel data 
    TCS34725_RDATAH           = 0x17
    TCS34725_GDATAL           = 0x18    # Green channel data 
    TCS34725_GDATAH           = 0x19
    TCS34725_BDATAL           = 0x1A    # Blue channel data 
    TCS34725_BDATAH           = 0x1B
 
  # TCS34725_INTEGRATIONTIME_2_4MS  = 0xFF,   /**<  2.4ms - 1 cycle    - Max Count: 1024  
  # TCS34725_INTEGRATIONTIME_24MS   = 0xF6,   /**<  24ms  - 10 cycles  - Max Count: 10240 
  # TCS34725_INTEGRATIONTIME_50MS   = 0xEB,   /**<  50ms  - 20 cycles  - Max Count: 20480 
  # TCS34725_INTEGRATIONTIME_101MS  = 0xD5,   /**<  101ms - 42 cycles  - Max Count: 43008 
  # TCS34725_INTEGRATIONTIME_154MS  = 0xC0,   /**<  154ms - 64 cycles  - Max Count: 65535 
  # TCS34725_INTEGRATIONTIME_700MS  = 0x00    /**<  700ms - 256 cycles - Max Count: 65535 

    _tcs34725Initialised = False
    _tcs34725Gain = 0
    _tcs34725IntegrationTime = 0x00

    def __init__(self, *args, **kwargs):
        self.i2c = Adafruit_I2C(self.TCS34725_ADDRESS)

    def begin(self):
        x = self.i2c.readU8(self.TCS34725_ID)
        if x != 0x44:
            print 'did not get the expected response from sensor'
            return False
        self._tcs34725Initialised = True
        self.setIntegrationTime(self._tcs34725IntegrationTime)
        self.setGain(0)
        self.enable()
        return True

    def setIntegrationTime(self, theTime):
        if theTime not in [0xFF,0xF6,0xEB,0xD5,0xC0,0x00]:
            theTime = 0x00
        self.i2c.write8(self.TCS34725_ATIME)
        self._tcs34725IntegrationTime = theTime

    def setGain(self, gain):
        # TCS34725_GAIN_1X                = 0x00,   /**<  No gain  
        # TCS34725_GAIN_4X                = 0x01,   /**<  2x gain  
        # TCS34725_GAIN_16X               = 0x02,   /**<  16x gain 
        # TCS34725_GAIN_60X               = 0x03    /**<  60x gain 
        if gain not in [0,1,2,3]:
            gain = 0
        self.i2c.write8(self.TCS34725_CONTROL, gain)
        self._tcs34725Gain = gain

    def getRawData(self):
        c = self.i2c.readU16(self.TCS34725_CDATAL)
        r = self.i2c.readU16(self.TCS34725_RDATAL)
        g = self.i2c.readU16(self.TCS34725_GDATAL)
        b = self.i2c.readU16(self.TCS34725_BDATAL)
        if self._tcs34725IntegrationTime == 0xFF:
            time.sleep(0.0024)
        elif self._tcs34725IntegrationTime == 0xF6:
            time.sleep(0.024)
        elif self._tcs34725IntegrationTime == 0xEB:
            time.sleep(0.050)
        elif self._tcs34725IntegrationTime == 0xD5:
            time.sleep(0.101)
        elif self._tcs34725IntegrationTime == 0xC0:
            time.sleep(0.154)
        elif self._tcs34725IntegrationTime == 0x00:
            time.sleep(0.700)
        else:
            time.sleep(0.700)
        return c, r, g, b

    def calculateColorTemperature(self, r, g, b):
        # this is all from the Adafruit C library
        # 1. Map RGB values to their XYZ counterparts.
        # Based on 6500K fluorescent, 3000K fluorescent
        # and 60W incandescent values for a wide range.
        # Note: Y = Illuminance or lux                 
        X = (-0.14282 * r) + (1.54924 * g) + (-0.95641 * b);
        Y = (-0.32466 * r) + (1.57837 * g) + (-0.73191 * b);
        Z = (-0.68202 * r) + (0.77073 * g) + ( 0.56332 * b);

        # 2. Calculate the chromaticity co-ordinates      
        xc = (X) / (X + Y + Z);
        yc = (Y) / (X + Y + Z);

        # 3. Use McCamy's formula to determine the CCT    
        n = (xc - 0.3320) / (0.1858 - yc);

        # Calculate the final CCT 
        cct = (449.0 * pow(n, 3)) + (3525.0 * pow(n, 2)) + (6823.3 * n) + 5520.33;
        return cct

    def calculateLux(self, r, g, b):
        return ((-0.32466 * r) + (1.57837 * g) + (-0.73191 * b))

    def setInterrupt(self, bool):
        r = self.i2c.readU8(self.TCS34725_ENABLE)
        if bool:
            r |= self.TCS34725_ENABLE_AIEN
        else:
            r &= ~self.TCS34725_ENABLE_AIEN
        self.i2c.write8(self.TCS34725_ENABLE, r)

    def clearInterrupt(self):
        self.i2c.write8(self.TCS34725_ADDRESS, 0x66)

    def enable(self):
        self.i2c.write8(self.TCS34725_ENABLE, self.TCS34725_ENABLE_PON)
        time.sleep(0.003)
        self.i2c.write8(self.TCS34725_ENABLE, self.TCS34725_ENABLE_PON | self.TCS34725_ENABLE_AEN)

    def disable(self):
        reg = 0
        reg = self.i2c.readU8(self.TCS34725_ENABLE)
        self.i2c.write8(self.TCS34725_ENABLE, reg & ~(self.TCS34725_ENABLE_PON | self.TCS34725_ENABLE_AEN))

    def setInterruptLimits(self, lo, hi):
        pass