#version:ig01
#fk14-atpostxt return False if fail
#gd21-atpostxt wrap
#gh16-plc.data
#id24: try import print fail
#ic24-atpostxt tolerance change from 0.1 to 1
#ig01-speed_fromplc
#ig01-log response of ptz

from io import StringIO
import traceback
def geterrorstring(e):
    sio=StringIO()
    print("An exception occurred:", e, file=sio)
    print("\nStack trace:",file=sio)
    print(traceback.format_exc(),file=sio)
    return sio.getvalue()

import sys
import os
try:
    import SharedArray as sa
except:
    print('fail import SharedArray')
    pass
try:
    import requests
    from requests.auth import HTTPDigestAuth
except:
    print('fail import requests')

from threading import Thread
try:
    from PIL import Image
except:
    print('fail import PIL')
import PIL.ExifTags
import io
import numpy as np
import cv2
import json
import pickle
from memcachehelper import memcacheRW as mcrw
import struct
simulation=os.path.exists('/dev/shm/simARMG')
if simulation:
    from datetime import timedelta
    from datetime import datetime as origdatetime
    import time as origtime
    class time:
        sleep=origtime.sleep
        def time():
            while 1:
                try:
                    return float(open('/dev/shm/sim_timestamp').read())
                except:
                    pass
    class datetime(origdatetime):
        def now():
            return origdatetime.fromtimestamp(time.time())
else:
    from datetime import datetime,timedelta
    import time
b=[1]
for i in range(1,8):
    b.append(b[i-1]<<1)
dummyimage=np.zeros([3,3,3],dtype=np.uint8)
class PLC:
    lastHoistPos=0
    lastT=0
    speed=0
    def __init__(self, DataR, T):
        if os.path.exists('/tmp/plc.dat'):
            unpacker = struct.Struct('!1i 1h 4c'
             '4i'
             '3h'
             '2i'
             '3h'
             '2i'
             '2h'
             '4h'
             '7h')
            self.fake=1
            DataR = list(unpacker.unpack(open('/tmp/plc.dat','rb').read()))
        else:
            self.fake=0

        self.DataR = DataR
        self.JA = DataR[2][0]&b[1]>0 #job active            
        self.TLOCK = DataR[2][0]&b[3]>0 #twistlock
        self.MI = DataR[5][0]&b[0]>0 #MI
        self.CNRSCompleted = DataR[4][0]&b[6]>0 or DataR[4][0]&b[7]>0 #CNRSCompleted or PMMS Completed
        self.LAND = DataR[2][0]&b[7]>0
        if DataR[3][0]&b[7]>0:
            self.JOBTYPE='OFFLOADING'
        elif DataR[3][0]&b[6]>0:
            self.JOBTYPE='MOUNTING'        
        else:
            self.JOBTYPE = 'OTHERS'

            
        self.HoistPos = DataR[18]
        if T!=PLC.lastT:
            PLC.speed = self.HoistPos - PLC.lastHoistPos
            if PLC.lastT==0:PLC.speed=0
            PLC.lastHoistPos=self.HoistPos
            PLC.lastT=T

            
        self.TrolleyPos = DataR[15]
        self.SIDEINFO = DataR[15] #currentrow during simulation    
        if self.JOBTYPE=='MOUNTING':
            self.SIDEINFO = DataR[17]
        elif self.JOBTYPE=='OFFLOADING':
            self.SIDEINFO = DataR[16]

        self.GantryCurrSlot=DataR[10]
        self.GantrySrcSlot=DataR[11]
        self.GantryDestSlot=DataR[12]
        self.GantryTargetSlot=-99
        if self.JOBTYPE=='MOUNTING':
            self.GantryTargetSlot=self.GantryDestSlot
        elif self.JOBTYPE=='OFFLOADING':
            self.GantryTargetSlot=self.GantrySrcSlot

        if self.SIDEINFO == 0:
            self.SIDE = 's'
        elif self.SIDEINFO == 11:
            self.SIDE = 'l'
        else:
            self.SIDE = 'x'
        self.containerpos = 0
        for i in range(0, 6):
            if DataR[4][0]&b[i]>0:
                self.containerpos = i + 1
                break
        self.size = 0            
        if DataR[2][0]&b[4]>0:
            self.size = 20
        elif DataR[2][0]&b[5]>0:
            self.size = 40
        elif DataR[2][0]&b[6]>0:
            self.size = 45
        
        #self.externalpm = DataR[3][4] == '1'
        self.pmnumber4int=str(DataR[22:26])
        try:
            self.pmnumber=b''.join(list(x.to_bytes(2,'big') for x in DataR[22:26])).decode('utf8').replace('\x00','').replace(' ','')
        except:
            self.pmnumber='ERROR'            
        self.contnum6int=str(DataR[26:32])
        try:
            self.contnum=b''.join(list(x.to_bytes(2,'big') for x in DataR[26:32])).decode('utf8').replace('\x00','').strip()
            if len(self.contnum)==11:
                self.contnum=self.contnum[:4]+' '+self.contnum[-7:]
            elif len(self.contnum)==7:
                self.contnum=' '*5+self.contnum
        except:
            self.contnum='ERROR'
        #self.externalpm = self.pmnumber[:3]!='PPM'
        self.ppm = self.pmnumber[1:3] == 'PM' and self.pmnumber[:1]!='I'
        self.externalpm = not self.ppm
        self.dst = DataR[3][0]&b[3]>0
        self.craneon = DataR[5][0] & b[1] > 0
        self.HNCDS_Validity = DataR[32] & b[0] > 0
        self.TCDS_Validity = DataR[32] & b[1] > 0
        self.PMNRS_Validity = DataR[32] & b[2] > 0
        self.CLPS_Validity = DataR[32] & b[3] > 0
        self.HNCDS_Enable = DataR[32] & b[4] > 0
        self.TCDS_Enable = DataR[32] & b[5] > 0
        self.PMNRS_Enable = DataR[32] & b[6] > 0
        self.CLPS_Enable = DataR[32] & b[7] > 0
        #self.print()
        
       
    def getEstHoistPos(self):
        return self.HoistPos+(time.time()-self.lastT)/0.5*self.speed
    def print(self):
        #for attr in sorted(dir(self)):
        keyattrs=['JA','MI','CNRSCompleted','JOBTYPE','TLOCK','LAND']
        for attr in keyattrs:
            val=self.__getattribute__(attr)
            if attr=='DataR' or attr.startswith('_') or attr=='print':continue
            if attr=='getEstHoistPos':
                attr='EstHoistPos'
                val=self.getEstHoistPos()
            if type(val)==bool:val=val*1
            print(f'{attr}:{val}',end=" ")        
        for attr in sorted(dir(self)):
            if attr in keyattrs:continue
            val=self.__getattribute__(attr)
            if attr=='DataR' or attr.startswith('_') or attr=='print':continue
            if attr=='getEstHoistPos':
                attr='EstHoistPos'
                val=self.getEstHoistPos()
            if type(val)==bool:val=val*1
            print(f'{attr}:{val}',end=" ")
        print()
class PLC2:
    # Class variables to track previous state for speed calculation
    lastHoistPos = 0
    lastT = 0
    speed = 0

    def __init__(self, source, T=None):
        """
        Initializes the PLC2 object from either raw byte data or a dictionary.

        Args:
            source: Either a bytes object containing raw PLC data
                    or a dictionary with PLC attribute key-value pairs.
            T: The current time (e.g., from time.time()). Required for
               calculating hoist speed if processing byte data or if
               HoistPos is provided in the dictionary.
        """
        # Initialize attributes to default values first
        self.data = None
        self.fake = 0
        self.JA = False
        self.TLOCK = False
        self.MI = False
        self.CNRSCompleted = False
        self.LAND = False
        self.JOBTYPE = 'OTHERS'
        self.HoistPos = 0
        self.TrolleyPosCurrMM = 0
        self.TrolleyPosTargMM = 0
        self.TrolleyPosSrc = 0
        self.TrolleyPosDest = 0
        self.TrolleyPos = 0 # This seems to be used for currentrow during simulation
        self.SIDEINFO = 0
        self.SIDE = 'x'
        self.GantryCurrSlot = 0
        self.GantrySrcSlot = 0
        self.GantryDestSlot = 0
        self.GantryCurrPosMM = 0
        self.GantryTargPosMM = 0
        self.GantryTargetSlot = -99
        self.containerpos = 0
        self.size = 0
        self.pmnumber = ''
        self.contnum = ''
        self.externalpm = False
        self.ppm = False
        self.dst = False
        self.craneon = False
        self.HNCDS_Validity = False
        self.TCDS_Validity = False
        self.PMNRS_Validity = False
        self.CLPS_Validity = False
        self.HNCDS_Enable = False
        self.TCDS_Enable = False
        self.PMNRS_Enable = False
        self.CLPS_Enable = False
        self.HNCDS_OpsAck = False
        self.PMNRS_NoOpsAck = False
        self.TCDS_OpsAck = False
        self.CLPS_OpsAck = False
        self.heartbeat_echo = 0

        # --- Handle input based on type ---
        if isinstance(source, bytes):
            self.data = source # Store the source bytes regardless of length
            self.fake = 0 # Assume not fake if loaded from provided bytes

            # Check if the byte data is long enough for parsing all expected fields
            # The maximum offset used is 80 for heartbeat_echo, so we need at least 81 bytes.
            if len(source) >= 81:
                # Parse byte data - no need for inner length checks now
                self.JA = (source[6] & b[1]) > 0
                self.TLOCK = (source[6] & b[3]) > 0
                self.MI = (source[9] & b[0]) > 0
                self.CNRSCompleted = (source[8] & b[6]) > 0 or (source[8] & b[7]) > 0
                self.LAND = (source[6] & b[7]) > 0

                if (source[7] & b[7]) > 0:
                    self.JOBTYPE = 'OFFLOADING'
                elif (source[7] & b[6]) > 0:
                    self.JOBTYPE = 'MOUNTING'
                # else remains 'OTHERS'

                self.HoistPos = struct.unpack('>i', source[46:50])[0]

                self.TrolleyPosCurrMM = struct.unpack('>l', source[32:36])[0]
                self.TrolleyPosTargMM = struct.unpack('>l', source[36:40])[0]
                self.TrolleyPosSrc = struct.unpack('>h', source[42:44])[0]
                self.TrolleyPosDest = struct.unpack('>h', source[44:46])[0]
                self.TrolleyPos = struct.unpack('>h', source[40:42])[0] # currentrow during simulation

                self.GantryCurrSlot = struct.unpack('>h', source[26:28])[0]
                self.GantrySrcSlot = struct.unpack('>h', source[28:30])[0]
                self.GantryDestSlot = struct.unpack('>h', source[30:32])[0]
                self.GantryCurrPosMM = struct.unpack('>i', source[10:14])[0]
                self.GantryTargPosMM = struct.unpack('>i', source[14:18])[0]

                # Size bits are mutually exclusive
                if (source[6] & b[4]) > 0:
                    self.size = 20
                elif (source[6] & b[5]) > 0:
                    self.size = 40
                elif (source[6] & b[6]) > 0:
                    self.size = 45
                else:
                    self.size = 0 # Default if no size bit is set

                # Container position bits are mutually exclusive (1-6)
                self.containerpos = 0 # Default
                for i in range(0, 6):
                    if (source[8] & b[i]) > 0:
                        self.containerpos = i + 1
                        break

                try:
                    # Use split(b'\x00')[0] to handle null terminators before decoding
                    self.pmnumber = source[58:66].split(b'\x00')[0].decode('utf8').strip()
                except Exception:
                    self.pmnumber = 'ERROR'

                try:
                    self.contnum = source[66:78].split(b'\x00')[0].decode('utf8').strip()
                    # The original code formatted the string *after* decoding/stripping.
                    # Let's keep the raw decoded string here and format it for display in print().
                    # Or, if the formatted string is the desired attribute value:
                    # if len(self.contnum) == 11:
                    #     self.contnum = self.contnum[:4] + ' ' + self.contnum[-7:]
                    # elif len(self.contnum) == 7:
                    #     self.contnum = ' ' * 5 + self.contnum # Pad with spaces
                except Exception:
                    self.contnum = 'ERROR'

                self.dst = (source[7] & b[3]) > 0
                self.craneon = (source[9] & b[1]) > 0
                self.HNCDS_Validity = (source[78] & b[0]) > 0
                self.TCDS_Validity = (source[78] & b[1]) > 0
                self.PMNRS_Validity = (source[78] & b[2]) > 0
                self.CLPS_Validity = (source[78] & b[3]) > 0
                self.HNCDS_Enable = (source[78] & b[4]) > 0
                self.TCDS_Enable = (source[78] & b[5]) > 0
                self.PMNRS_Enable = (source[78] & b[6]) > 0
                self.CLPS_Enable = (source[78] & b[7]) > 0
                self.HNCDS_OpsAck = (source[79] & b[0]) > 0
                self.PMNRS_NoOpsAck = (source[79] & b[1]) > 0
                self.TCDS_OpsAck = (source[79] & b[2]) > 0
                self.CLPS_OpsAck = (source[79] & b[3]) > 0

                self.heartbeat_echo = struct.unpack('>B', source[80:81])[0]
		#ig01
                self.speed_fromplc = struct.unpack('>h', source[84:86])[0]
            else:
                 # If bytes are too short, attributes remain at default values.
                 print(f"Warning: PLC2 input bytes too short ({len(source)} bytes). Expected at least 81. Attributes will retain default values.")


        elif isinstance(source, dict):
            # New logic: populate from dictionary
            self.data = None # Indicate not loaded from bytes
            self.fake = source.get('fake', 1) # Assume fake if from dict unless specified

            # Set attributes from dictionary if they exist in the initial default set
            for key, value in source.items():
                 if hasattr(self, key):
                      setattr(self, key, value)
                 else:
                      # Ignore unknown keys
                      pass

        else:
            raise TypeError("Source must be bytes or a dictionary")


        # --- Perform derivations and calculations common to both input types ---
        # These derivations rely on attributes being populated from either bytes or dict

        # SIDEINFO derivation based on JOBTYPE (if not explicitly set by dictionary)
        # Check if SIDEINFO was in the dictionary to potentially skip this derivation
        if not (isinstance(source, dict) and 'SIDEINFO' in source):
             if self.JOBTYPE == 'MOUNTING':
                self.SIDEINFO = self.TrolleyPosDest
             elif self.JOBTYPE == 'OFFLOADING':
                self.SIDEINFO = self.TrolleyPosSrc
             else:
                 self.SIDEINFO = self.TrolleyPos # Use TrolleyPos as current row if not MOUNTING/OFFLOADING

        # SIDE derivation based on SIDEINFO
        if self.SIDEINFO == 0:
            self.SIDE = 's' # Ship side?
        elif self.SIDEINFO == 11:
            self.SIDE = 'l' # Land side?
        else:
            self.SIDE = 'x' # Unknown/Other?

        # GantryTargetSlot derivation based on JOBTYPE (if not explicitly set by dictionary)
        # Check if GantryTargetSlot was in the dictionary to potentially skip this derivation
        if not (isinstance(source, dict) and 'GantryTargetSlot' in source):
             if self.JOBTYPE == 'MOUNTING':
                self.GantryTargetSlot = self.GantryDestSlot
             elif self.JOBTYPE == 'OFFLOADING':
                self.GantryTargetSlot = self.GantrySrcSlot
             else:
                 self.GantryTargetSlot = -99 # Default value if neither job type


        # PM/Container number derivations (if not explicitly set by dictionary)
        # Check if externalpm or ppm were in the dictionary to potentially skip this derivation
        if not (isinstance(source, dict) and ('externalpm' in source or 'ppm' in source)):
            self.externalpm = self.pmnumber[:3] != 'PPM'
            self.ppm = self.pmnumber[:3] == 'PPM'


        # Speed calculation (requires T and HoistPos)
        # This uses class variables to track state across instances/calls
        if T is not None and T != PLC2.lastT:
            time_diff = T - PLC2.lastT
            if time_diff > 0: # Avoid division by zero or negative time difference
                 PLC2.speed = (self.HoistPos - PLC2.lastHoistPos) / time_diff
            else: # Time hasn't changed or moved backward
                 PLC2.speed = 0 # Assume no movement if time doesn't advance

            PLC2.lastHoistPos = self.HoistPos
            PLC2.lastT = T
        # If T is None or T == PLC2.lastT, the speed calculation is skipped,
        # and PLC2.speed retains its last calculated value.


    def getEstHoistPos(self):
        """Estimates the current hoist position based on the last known state and calculated speed."""
        current_time = time.time()
        # Only estimate if we have a valid last timestamp to calculate time elapsed
        if PLC2.lastT > 0 and current_time >= PLC2.lastT:
             time_since_last_update = current_time - PLC2.lastT
             return self.HoistPos + time_since_last_update * PLC2.speed
        else:
             # Cannot estimate reliably, return the last known position
             return self.HoistPos

    def print(self):
        """Prints key attributes of the PLC2 object."""
        keyattrs = ['JA', 'MI', 'CNRSCompleted', 'JOBTYPE', 'TLOCK', 'LAND']
        # Print key attributes first
        for attr in keyattrs:
            val = getattr(self, attr)
            if isinstance(val, bool):
                 val = int(val)
            print(f'{attr}:{val}', end=" ")

        # Get all attributes including those set dynamically from dictionary
        # Exclude methods, internal attributes, and keyattrs already printed
        all_attrs = sorted([attr for attr in dir(self)
                            if not attr.startswith('_')
                            and not callable(getattr(self, attr))
                            and attr not in keyattrs])

        for attr in all_attrs:
            try:
                val = getattr(self, attr)
                # Convert bool to int for printing consistency
                if isinstance(val, bool):
                    val = int(val)
                # Handle the estimated position separately if it exists
                if attr == 'HoistPos' and 'getEstHoistPos' in dir(self):
                     # Print the estimated value right after the actual HoistPos
                     print(f'{attr}:{val}', end=" ")
                     print(f'EstHoistPos:{self.getEstHoistPos():.2f}', end=" ")
                elif attr != 'EstHoistPos': # Avoid printing EstHoistPos here if it's somehow in all_attrs
                     print(f'{attr}:{val}', end=" ")
            except Exception as e:
                 print(f'{attr}:ERROR({e})', end=" ")

        print()


    def dumpbytes(self, min_length=81):
        """
        Reverse engineers the object's attributes back into a byte string.

        Args:
            min_length: The minimum length of the output byte string.
                        Defaults to 81 to cover all defined fields.

        Returns:
            A bytes object representing the PLC data, or None if unable to pack.
        """
        # Create a mutable byte array initialized with zeros
        # Ensure it's at least min_length long
        byte_array = bytearray(max(81, min_length))

        try:
            # --- Pack Boolean Flags (Bitwise Operations) ---
            # Byte 6
            if self.JA:
                byte_array[6] |= b[1]
            if self.TLOCK:
                byte_array[6] |= b[3]
            if self.LAND:
                byte_array[6] |= b[7]

            # Size bits (mutually exclusive)
            if self.size == 20:
                byte_array[6] |= b[4]
            elif self.size == 40:
                byte_array[6] |= b[5]
            elif self.size == 45:
                byte_array[6] |= b[6]

            # Byte 7
            if self.JOBTYPE == 'MOUNTING':
                 byte_array[7] |= b[6]
            elif self.JOBTYPE == 'OFFLOADING':
                 byte_array[7] |= b[7]
            # Note: If JOBTYPE is 'OTHERS', neither bit is set (which is the default state of the byte)

            if self.dst:
                 byte_array[7] |= b[3]

            # Byte 8
            # Container position bits (mutually exclusive, 1-6 correspond to bits 0-5)
            if 1 <= self.containerpos <= 6:
                 byte_array[8] |= b[self.containerpos - 1]

            # CNRSCompleted (bit 6 OR bit 7)
            # This is tricky to reverse engineer perfectly. If either bit 6 or 7 was set
            # in the source bytes, CNRSCompleted is True. When dumping, we can't know
            # which one was originally set if both result in the same True value.
            # A simple approach is to set one of them if CNRSCompleted is True.
            # Let's set bit 6 if CNRSCompleted is True.
            if self.CNRSCompleted:
                 byte_array[8] |= b[6]
            # Note: The original parser checks for OR, so setting just one bit (e.g., bit 6)
            # will result in CNRSCompleted being True when parsed back.

            # Byte 9
            if self.MI:
                 byte_array[9] |= b[0]
            if self.craneon:
                 byte_array[9] |= b[1]

            # Byte 78 (Validity/Enable flags)
            if self.HNCDS_Validity: byte_array[78] |= b[0]
            if self.TCDS_Validity: byte_array[78] |= b[1]
            if self.PMNRS_Validity: byte_array[78] |= b[2]
            if self.CLPS_Validity: byte_array[78] |= b[3]
            if self.HNCDS_Enable: byte_array[78] |= b[4]
            if self.TCDS_Enable: byte_array[78] |= b[5]
            if self.PMNRS_Enable: byte_array[78] |= b[6]
            if self.CLPS_Enable: byte_array[78] |= b[7]

            # Byte 79 (OpsAck flags)
            if self.HNCDS_OpsAck: byte_array[79] |= b[0]
            if self.PMNRS_NoOpsAck: byte_array[79] |= b[1] # Note: This flag name was PMNRS_NoOpsAck in init
            if self.TCDS_OpsAck: byte_array[79] |= b[2]
            if self.CLPS_OpsAck: byte_array[79] |= b[3]


            # --- Pack Packed Values (struct.pack) ---
            # Ensure values are within the expected range for the struct format
            # struct.pack handles signed/unsigned and size correctly, but large
            # values might cause OverflowError.
            byte_array[10:14] = struct.pack('>i', self.GantryCurrPosMM)
            byte_array[14:18] = struct.pack('>i', self.GantryTargPosMM)
            byte_array[26:28] = struct.pack('>h', self.GantryCurrSlot)
            byte_array[28:30] = struct.pack('>h', self.GantrySrcSlot)
            byte_array[30:32] = struct.pack('>h', self.GantryDestSlot)
            byte_array[32:36] = struct.pack('>l', self.TrolleyPosCurrMM)
            byte_array[36:40] = struct.pack('>l', self.TrolleyPosTargMM)
            byte_array[40:42] = struct.pack('>h', self.TrolleyPos)
            byte_array[42:44] = struct.pack('>h', self.TrolleyPosSrc)
            byte_array[44:46] = struct.pack('>h', self.TrolleyPosDest)
            byte_array[46:50] = struct.pack('>i', self.HoistPos)
            byte_array[80:81] = struct.pack('>B', self.heartbeat_echo) # Unsigned Byte


            # --- Pack String Values ---
            # pmnumber (8 bytes)
            pmnum_bytes = self.pmnumber.encode('utf8')[:8] # Truncate if too long
            byte_array[58:66] = pmnum_bytes.ljust(8, b'\x00') # Pad with nulls

            # contnum (12 bytes)
            # The attribute contnum might be the formatted string "ABC 1234567".
            # We need to encode the *raw* container number if possible, or handle the formatted one.
            # Assuming the attribute stores the raw or near-raw string before formatting for display.
            # Let's strip spaces if present before encoding and padding.
            contnum_raw = self.contnum.replace(' ', '')
            contnum_bytes = contnum_raw.encode('utf8')[:12] # Truncate if too long
            byte_array[66:78] = contnum_bytes.ljust(12, b'\x00') # Pad with nulls


            # Return the final bytes object
            return bytes(byte_array)

        except struct.error as e:
            print(f"Error packing bytes: {e}. Check attribute values for valid ranges.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during byte dumping: {e}")
            return None


        
class AxisCamera:
    def __init__(self, ip, uname, passwd):
        self.ip = ip
        self.auth = HTTPDigestAuth(uname, passwd)

    def ptz(self, args):
        return requests.get(f'http://{self.ip}/axis-cgi/com/ptz.cgi?{args}', auth=self.auth, timeout=1).content

    def setposition(self, pos):
        if 0:
            self.ptz(f'pan={pos["pan"]}')
            time.sleep(0.1)
            self.ptz(f'tilt={pos["tilt"]}')
            time.sleep(0.1)
            self.ptz(f'zoom={pos["zoom"]}')
        self.ptz(f'pan={pos["pan"]}&tilt={pos["tilt"]}&zoom={pos["zoom"]}')

    def position(self):
        s = self.ptz('query=position').decode('utf8')
        D = {}
        for line in s.split():
            k, v = line.split('=')
            if v in ['on', 'off']:
                # D[k]=(v=='on')
                D[k] = v
            else:
                try:
                    D[k] = int(v)
                except:
                    D[k] = float(v)
        return D

    def savepos(self, fname):
        open(fname, 'w').write(json.dumps(self.position()))

    def loadposthread(self, pos):
        #ig01
        if simulation:
            return True
        for i in range(3):
            try:
                NOW=datetime.now()
                YMD=NOW.strftime('%Y-%m-%d')
                os.makedirs(f'/opt/captures/ptzlog',exist_ok=True)
                logname=f'/opt/captures/ptzlog/{YMD}.txt'
                print(NOW,'ptzlog',self.ip,i,'setpos',pos,file=open(logname,'a'))
                self.setposition(pos)
                print(NOW,'ptzlog',self.ip,i,'success',file=open(logname,'a'))
                break
            except Exception as e:
                print(NOW,'ptzlog',self.ip,i,geterrorstring(e),'set position error redo',file=open(logname,'a'))
                print('set position', 'error redo')
                time.sleep(0.05)

    def loadpos(self, fname):
        """load pos from json file"""
        if simulation:
            return True
        pos = json.loads(open(fname).read())
        thread = Thread(target=self.loadposthread, args=(pos,), daemon=True)
        thread.start()

    def loadpostxt(self, fname, tiltoffset=None, forcezoom=None):
        """load pos from text file"""
        if simulation:
            return True
        pos = dict()
        for line in open(fname).read().strip().split():
            k, v = line.split('=')
            pos[k] = v
        if tiltoffset is not None:
            pos['tilt']=float(pos['tilt'])+tiltoffset
        if forcezoom is not None:
            pos['zoom']=forcezoom
        thread = Thread(target=self.loadposthread, args=(pos,), daemon=True)
        thread.start()
    
    def atpostxt(self, fname, tiltoffset=None, forcezoom=None):
        """load pos from text file"""
        if simulation:
            return True
        pos = dict()
        for line in open(fname).read().strip().split():
            k, v = line.split('=')
            pos[k] = float(v)
        if tiltoffset is not None:
            pos['tilt']=float(pos['tilt'])+tiltoffset
        if forcezoom is not None:
            pos['zoom']=float(forcezoom)
        try:
            postarget=self.position()
            #gd21
            return min((postarget['pan']-pos['pan'])%360,(pos['pan']-postarget['pan'])%360)<=1 and abs(postarget['tilt']-pos['tilt'])<=1 and abs(postarget['zoom']-pos['zoom'])<=1
        except:
            return False
    def loadposstr(self, s):
        """load pos from string"""
        if simulation:
            return True
        pos = dict()
        for line in s.strip().split():
            k, v = line.split('=')
            pos[k] = v
        thread = Thread(target=self.loadposthread, args=(pos,), daemon=True)
        thread.start()

    def positiontxt(self):
        if simulation:
            return 'pan=0\ntilt=0\nzoom=0'
        s=(self.ptz('query=position').decode('utf8'))
        print(s)
        return(s)

    def snapshotthread(self, filename,delay):
        try:
            time.sleep(delay)
            image=requests.get(f'http://{self.ip}/axis-cgi/jpg/image.cgi?resolution=1280x720', auth=self.auth, timeout=1).content
            open(filename,'wb').write(image)
        except:
            pass

    def snapshot(self,filename,delay=0):
        DIR=os.path.dirname(filename)
        if DIR!='':
            os.makedirs(DIR,exist_ok=True)
        thread = Thread(target=self.snapshotthread, args=(filename,delay), daemon=True)
        thread.start()

    def snapshotimage(self):
        try:
            image=requests.get(f'http://{self.ip}/axis-cgi/jpg/image.cgi?resolution=1280x720', auth=self.auth, timeout=1).content
            return image
        except:
            return None
            pass
        
    def nonptzautofocusthread(self):
        return requests.get(f'http://{self.ip}/axis-cgi/opticssetup.cgi?autofocus=perform', auth=self.auth, timeout=20).content

    def nonptzautofocus(self):
        thread = Thread(target=self.nonptzautofocusthread, daemon=True)
        thread.start()

def readplc():
    if simulation:
        T, data = mcrw.raw_read('simARMGplcdata',[0,None])
        plc=PLC2(data,T)
        return plc
    while True:
        try:
            T, data = mcrw.raw_read('plcdata',[0,None])
            if os.path.exists('/tmp/plc.dat'):
                T=time.time()
            if time.time()-T>1:
                raise Exception(f'PLC stale by {time.time()-T}')
            break
        except Exception as e:
            print(e)
            pass
        time.sleep(0.5)
    plc = PLC2(data, T)
    return plc


def createShm(fbasename, shape=(720,1280,3), dtype=np.uint8):
    try:
        if os.path.exists(f'/dev/shm/{fbasename}'):
            os.unlink(f'/dev/shm/{fbasename}')
        fname = f"shm://{fbasename}"
        sa.create(fname, shape, dtype=dtype)
        print(fname, "created")
    except FileExistsError:
        print(fname, "already exists")
    finally:
        shmarray = sa.attach(fname)
        return shmarray

def assignimage(x,img):
    if img.shape==x.shape:
        x[:] = img
    else:
        x[:] = cv2.resize(img, (x.shape[1],x.shape[0]))

def assignscaleimage(x,img):
    H,W=x.shape[:2]
    imgout=scaleimage(img,W,H)
    Hout,Wout=imgout.shape[:2]
    x[:]=0
    x[:Hout,:Wout]=imgout

def scaleimage(x,W,H):
    h,w=x.shape[:2]
    if w/h<W/H:
        wout=H*w//h
        hout=H
    else:
        wout=W
        hout=W*h//w
    if (wout,hout)==(w,h):
        return x
    else:
        #print(w,h,W,H,wout,hout)
        return cv2.resize(x,(wout,hout))

def makedirsopen(file,mode):
    DIR=os.path.dirname(file)
    if DIR!='':
        os.makedirs(DIR,exist_ok=True)
    return open(file,mode)

def makedirsimwrite(file,img):
    thread = Thread(target=_makedirsimwrite, args=(file,img), daemon=True)
    thread.start()

def _makedirsimwrite(file,img,overwrite=False):
    if not overwrite and os.path.exists(file):return
    DIR=os.path.dirname(file)
    if DIR!='':
        os.makedirs(DIR,exist_ok=True)
    return cv2.imwrite(file,img)

def printandlog(*x,file=None,sep=None):
    thread = Thread(target=_printandlog, args=x, kwargs={'file':file,'sep':sep}, daemon=True)
    thread.start()

def _printandlog(*x,file=None,sep=None):
    print(*x,sep=sep)
    print(*x,file=file,sep=sep)

def procimage(procname,img=dummyimage,timeout=10):
    T=time.time()
    os.makedirs(f'/dev/shm/{procname}/',exist_ok=True)
    cv2.imwrite(f'/dev/shm/{procname}/{T}.jpg',img)
    fout=f'/dev/shm/{procname}/{T}.pkl'
    while True:
        if time.time()-T>=timeout:
            raise Exception('procimage',procname,'timeout')
        try:
            res=pickle.load(open(fout,'rb'))
            os.unlink(fout)
            break
        except:
            time.sleep(0.001)
    return res

def waittillvalidimage(f,timeout=0.1):
    T=time.time()
    while True:
        if time.time()-T>=timeout:
            print('timeout', time.time() - T)
            return 0            
        try:            
            if open(f,'rb').read()[-2:]==b'\xff\xd9':
                print('waited',time.time()-T)            
                return 1
        except:
            pass
        time.sleep(0.001)
            
def putText(frame,text,position,thickness=3,color=(255,0,0),font_scale=1,font = None,line_type = None):
    if font is None:font=cv2.FONT_HERSHEY_SIMPLEX
    if line_type is None:line_type=cv2.LINE_AA
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    line_height = (text_size[1] + 5)*6//5
    x, y0 = position
    for i, line in enumerate(text.split("\n")):
        y = y0 + i * line_height
        cv2.putText(frame,
                    line,
                    (x, y),
                    font,
                    font_scale,
                    color,
                    thickness,
                    line_type)
