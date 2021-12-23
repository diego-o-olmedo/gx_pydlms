# add path
import os
import sys


from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader

from objects_from_excel import ObjectsIDIS
from gurux_common.enums import TraceLevel
from gurux_dlms.objects import GXDLMSObject, GXDLMSObjectCollection, GXDLMSData, GXDLMSRegister,\
    GXDLMSDemandRegister, GXDLMSProfileGeneric, GXDLMSExtendedRegister
class MeterTest:

    def __init__(self, args):
        self.settings = GXSettings()
        # 命令行参数获取
        self.settings.getParameters(args)
        # self.settings.get_fixed_config_parameters2()
        # 读取器
        self.reader = GXDLMSReader(self.settings.client,
                                   self.settings.media,
                                   self.settings.trace,
                                   self.settings.invocationCounter)
        # client
        self.client = self.reader.client

    def connect(self):
        self.settings.media.open()
        # self.reader.client.limits.maxInfoTX = 2030
        # self.reader.client.limits.maxInfoRX = 2030
        self.reader.initializeConnection()

    def disconnect(self):
        self.reader.close()
        self.settings.media.close()

    def get_objects_from_excel(self):
        # objects = ObjectsIDIS.get_objects(r"./objects_from_excel/saturn object model V1.2.xlsx",
        #                                     meter_type='DCPP-D',
        #                                     client='Management (1)')
        if self.settings.outputFile and os.path.exists(self.settings.outputFile):
            try:
                c = GXDLMSObjectCollection.load(self.settings.outputFile)
                self.settings.client.objects.extend(c)
                if self.settings.client.objects:
                    read = True
            except Exception:
                read = False
        objects = self.settings.client.objects
        self.connect()
        counter = 0
        for obj in objects:
            # counter += 1
            # if counter < 394:
            #     continue
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
                except:
                    self.reader.writeTrace(f"Read attribute: {index} fail", TraceLevel.ERROR)
        # self.reader.getAssociationView()
        # obj = self.client.createObject(self.client.objects[0].objectType)
        # obj.logicalName = self.client.objects[0].logicalName
        # data1 = self.reader.read(self.client.objects[0], 1)
        # data2 = self.reader.read(self.client.objects[0], 2)
        self.disconnect()

    # def get_objects_from_meter(self):

    def main(self):
        self.get_objects_from_excel()

if __name__ == "__main__":
    meter = MeterTest(sys.argv)
    meter.main()
