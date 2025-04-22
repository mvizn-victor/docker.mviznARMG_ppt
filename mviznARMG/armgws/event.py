#version:1
from datetime import datetime,timedelta
import time
import json
import base64
from os import path
import armgws.armgwsconfig as config

class Event:
    def __init__(self, armg, pmn, tstamp, severity, source, camimagelist, block, slot, row, container):
        self.system = config.SYSTEM_NAME
        self.version = config.VERSION
        self.versiondate = config.VERSION_DATE
        self.crane = armg
        self.pmn = pmn
        self.tstamp = tstamp
        self.severity = severity
        self.source = source
        self.shift = self.getShift()
        self.triggercams = []
        for cam, jpgpath in camimagelist:
            camName = cam
            with open(jpgpath, mode='rb') as file:
                imgdata = file.read()
            jpgimagestring = base64.b64encode(imgdata).decode("utf-8")
            #jpgimagestring = "JPGDATA HOLDER"
            ITfilename = self.crane + '_' + camName + '_' + self.tstamp.strftime("%Y%m%d%H%M%S%f")[:-3] + '.jpg'
            ITserverfilepath = "=HYPERLINK(\"" + "\\\\" + path.join(config.ITbasepath,
                                         self.shift, self.source,
                                         'Input_Pic', ITfilename).replace("\\","/").replace("/","\\") + "\")"
            self.triggercams.append((camName, jpgimagestring , ITserverfilepath))
        self.csvfilename = str(self.crane) + '_VA_Detected_' + self.tstamp.strftime("%Y-%m-%d") + ('.csv')
        self.block = block
        self.slot = slot
        self.row = row
        self.container = container

    def getJSON(self):
        jpgimgdatapre = "data:image/jpeg;base64,"
        triggeredCams = []

        fileContent = [
            {
                "PM": self.pmn,
                "Date": self.tstamp.strftime("%Y-%m-%d"),
                "Time": self.tstamp.strftime("%H:%M:%S"),
                "Block": self.block,
                "Slot": self.slot,
                "Row": self.row,
                "Container": self.container,
                "Crane": self.crane,
            }
        ]

        keyindex = 1
        for camName, jpgimagestring , ITserverfilepath in self.triggercams:
            fileContentKey = "ImageLink" + str(keyindex)
            fileContent[0][fileContentKey] = ITserverfilepath
            keyindex += 1

            triggeredCams.append({
                "camName": camName,
                "image": jpgimgdatapre + jpgimagestring
            })

        eventCSVDict = {
            "filename": self.csvfilename,
            "fileContent": fileContent
        }

        eventDict = {
            "timestamp": self.tstamp.strftime("%Y-%m-%d-%H:%M:%S.%f")[:-3],
            "severity": self.severity,
            "eventSource": self.source,
            "triggeredCams": triggeredCams
        }

        outputDict = {
            "system": self.system,
            "Version": self.version,
            "versionDate": self.versiondate,
            "ARMG": self.crane,
            "PMN": self.pmn,
            "event": eventDict,
            "eventCSVFile": eventCSVDict
        }

        return(json.dumps(outputDict))


    def getShift(self):        
        eventTimeStr = self.tstamp.strftime("%H:%M:$S.f")[:-3]
        if config.SHIFT1_START < eventTimeStr < config.SHIFT2_START:
            return self.tstamp.strftime("%Y%m%d_") + "shift1"
        elif config.SHIFT2_START < eventTimeStr:
            return self.tstamp.strftime("%Y%m%d_") + "shift2"
        elif eventTimeStr < config.SHIFT1_START:
            return (self.tstamp-timedelta(days=1)).strftime("%Y%m%d_") + "shift2"
