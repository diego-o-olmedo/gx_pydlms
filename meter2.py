# add path
import os
import sys
import requests

from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader

from gurux_common.enums import TraceLevel
from gurux_dlms.enums import ObjectType
from gurux_dlms.objects import GXDLMSObject, GXDLMSObjectCollection, GXDLMSData, GXDLMSRegister,\
    GXDLMSDemandRegister, GXDLMSProfileGeneric, GXDLMSExtendedRegister
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

    def addtask(self, v, ln, cnx):
        djson = {"Logical Name": ln, "Value": v

        }
        r = requests.post('http://194.163.161.91:8080/medidores/cnx', json=djson)
        return r

    def POST_request(self,a,b,cnx):
        response = self.addtask(a, b, cnx)
        # assert response.status_code == 200
        return response

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
            # self.reader.showValue(v, val)
        counter = 0
        for obj in self.client.objects:
            counter += 1
            if counter < 394:
                continue
            self.reader.writeTrace(f"Read {counter}. {obj.description} {obj.objectType},{obj.logicalName}", TraceLevel.VERBOSE)
            for index in range(2, len(obj.attributes)+2):
                if obj.objectType == 7 and index == 2 or \
                        obj.objectType == 15 and index == 2 or \
                        obj.objectType == 28 and index == 7:
                    continue
                self.reader.writeTrace(f"Read attribute {index}", TraceLevel.VERBOSE)
                try:
                    data = self.reader.read(obj, index)
                    self.reader.writeTrace(f"Read result: {data}", TraceLevel.VERBOSE)
                    self.POST_request(obj.logicalName, data, val)
                except:
                    self.reader.writeTrace(f"Read attribute: {index} fail", TraceLevel.ERROR)
        # self.reader.getAssociationView()
        # obj = self.client.createObject(self.client.objects[0].objectType)
        # obj.logicalName = self.client.objects[0].logicalName
        # data1 = self.reader.read(self.client.objects[0], 1)
        # data2 = self.reader.read(self.client.objects[0], 2)
        self.disconnect()
        self.POST_request(1,2, val)

    # def get_objects_from_meter(self):

    def main(self):
        self.get_objects()

if __name__ == "__main__":
    meter = MeterTest(sys.argv)
    meter.main()
