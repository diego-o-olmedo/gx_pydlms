# add path
import os
import sys
import time

import gurux_dlms.GXStructure
import requests
import json

from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader

from gurux_common.enums import TraceLevel
from datetime import datetime
from gurux_dlms import GXDateTime
from gurux_dlms.enums import ObjectType, DataType
from gurux_dlms.objects import GXDLMSObject, GXDLMSObjectCollection, GXDLMSData, GXDLMSRegister,\
    GXDLMSDemandRegister, GXDLMSProfileGeneric, GXDLMSExtendedRegister, GXDLMSClock
class MeterTest:

    def __init__(self, args):
        self.settings = GXSettings()
        # Adquisición de parámetros de línea de comando
        #self.settings.getParameters(args)
        self.settings.get_fixed_config_parameters2()
        # Reader
        self.reader = GXDLMSReader(self.settings.client,
                                   self.settings.media,
                                   self.settings.trace,
                                   self.settings.invocationCounter)
        # client
        self.client = self.reader.client

    def connect(self):
        self.settings.media.open()
        self.reader.initializeConnection()

    def disconnect(self):
        self.reader.close()
        self.settings.media.close()
    def addt(self):
        print

    def addtask(self, pid, ln, v, cnx):
        if isinstance(v, list):
            vl=list(v)
        elif isinstance(v,bytearray):
            b = bytearray(v)
            d = b.decode()
            vl = []
            vl.insert(0,d)
        else:
            vl = []
            vl.insert(0,v)
        djson = {
            "proceso":pid,
            "ip":"194.163.161.91",
            "lectura":
            [{
                "titulo" : "referencia",
                "obis" : ln,
                "atributos" : [
                    {
                        "atributo" : "ejemp1", "valor" : vl
                    }
                ]

            }]
        }
        url = 'http://194.163.161.91:8080/TOKEN/api/Consultas/medidores/' + cnx
        r = requests.put(url, json=djson)
        return r

    def PUT_request(self,a,b,c,cnx):
        response = self.addtask(a, b, c, cnx)
        # assert response.status_code == 200
        return response
    def get_sync(self):
        if self.settings.outputFile and os.path.exists(self.settings.outputFile):
            try:
                c = GXDLMSObjectCollection.load(self.settings.outputFile)
                self.settings.client.objects.extend(c)
                if self.settings.client.objects:
                    read = True
            except Exception:
                read = False
        # readObjects = []
        # readObjects.append(("0.0.42.0.0.255", int(2)))
        ts = time.time()-20000
        t = datetime.fromtimestamp(ts)
        val = GXDateTime(t)
        # print(val)
        self.connect()
        # for k, v in readObjects:
        #     obj = self.settings.client.objects.findByLN(ObjectType.NONE, k)
        #     if obj is None:
        #         raise Exception("Unknown logical name:" + k)
        #     val = self.reader.read(obj, v)
        prt = GXDLMSClock("0.0.1.0.0.255")
        # prt.setDataType(2, DataType.DATETIME)
        # prt.value = "1640777935" #("<DateTime Value=\"29/12/2021 05:45:12\" />\r\n")
        prt.setDataType(2, DataType.OCTET_STRING)
        # prt.time = bytearray(b'07E6010B0208430BFF007800')
        # prt.time = bytearray("07E6010B0208430BFF007800", encoding="utf-8")
        prt.time = val
        val = self.reader.write(prt, 2)
        self.disconnect()
    def get_objects(self):
        if self.settings.outputFile and os.path.exists(self.settings.outputFile):
            try:
                c = GXDLMSObjectCollection.load(self.settings.outputFile)
                self.settings.client.objects.extend(c)
                if self.settings.client.objects:
                    read = True
            except Exception:
                read = False
        readObjects = []
        readObjects.append(("0.0.42.0.0.255", int(2)))
        self.connect()
        for k, v in readObjects:
            obj = self.settings.client.objects.findByLN(ObjectType.NONE, k)
            if obj is None:
                raise Exception("Unknown logical name:" + k)
            val = self.reader.read(obj, v)
            b = bytearray(val)
            cnx = b.decode()
            # self.reader.showValue(v, val)
        counter = 0
        f = False
        for obj in self.client.objects:
            # counter += 1
            # if counter < 394:
            #     continue
            self.reader.writeTrace(f"Read {counter}. {obj.description} {obj.objectType},{obj.logicalName}", TraceLevel.VERBOSE)
            for index in range(2, len(obj.attributes)+2):
                # if obj.objectType == 7 and index == 2 or \
                #         obj.objectType == 15 and index == 2 or \
                #         obj.objectType == 28 and index == 7:
                #     continue
                self.reader.writeTrace(f"Read attribute {index}", TraceLevel.VERBOSE)
                try:
                    data = self.reader.read(obj, index)
                    # self.reader.writeTrace(f"Read result: {data}", TraceLevel.VERBOSE)
                    # self.reader.writeTrace(f"Read result: {self.PUT_request(obj.logicalName, data, cnx)}", TraceLevel.VERBOSE)
                    response = self.PUT_request(counter,obj.logicalName, data, cnx)
                    jn = json.loads(response.text)
                    if (jn["listaDatos"][0] ):#jn["status"] == True & response.status_code == 200:
                        # print("ok")
                        # source = response.text
                        # jn = json.loads(response.text)
                        p = int(jn["listaDatos"][0]["proceso"])
                        o = jn["listaDatos"][0]["atributos"][0]["obis"]
                        f = True
                        if(o=="0.0.1.0.0.255"):
                            offset = int(jn["listaDatos"][0]["atributos"][0]["valor"])
                            ts = time.time()+offset
                            t = datetime.fromtimestamp(ts)
                            val = GXDateTime(t)
                            prt = GXDLMSClock("0.0.1.0.0.255")
                            prt.setDataType(2, DataType.OCTET_STRING)
                            prt.time = val
                            val = self.reader.write(prt, 2)
                            # print(type(val))
                            self.reader.writeTrace(f"Read result: {self.PUT_request(p, o, 0, cnx)}",
                                                   TraceLevel.VERBOSE)
                        else:
                            val = jn["listaDatos"][0]["atributos"][0]["valor"]
                            # datacmd = self.reader.read(jn["listaDatos"][0]["atributos"]["obis"], jn["listaDatos"][0]["atributos"]["atributo"])
                            self.reader.writeTrace(f"Read result: {self.PUT_request(p, o, val, cnx)}",
                                               TraceLevel.VERBOSE)
                    # readObjects.append(("0.0.42.0.0.255", int(2)))
                    # for k, v in readObjects:
                    #     obj = self.settings.client.objects.findByLN(ObjectType.NONE, k)
                    #     if obj is None:
                    #         raise Exception("Unknown logical name:" + k)
                    #     val = self.reader.read(obj, v)
                except:
                    self.reader.writeTrace(f"Read attribute: {index} fail", TraceLevel.ERROR)
        # self.reader.getAssociationView()
        # obj = self.client.createObject(self.client.objects[0].objectType)
        # obj.logicalName = self.client.objects[0].logicalName
        # data1 = self.reader.read(self.client.objects[0], 1)
        # data2 = self.reader.read(self.client.objects[0], 2)
            if(f):
                counter += 1
        self.disconnect()
        # self.POST_request(1,2, val)

    # def get_objects_from_meter(self):

    def main(self):
        self.get_objects()
        # self.get_sync()

if __name__ == "__main__":
    meter = MeterTest(sys.argv)
    meter.main()
