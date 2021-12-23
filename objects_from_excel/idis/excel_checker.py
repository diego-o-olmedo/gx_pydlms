from gurux_dlms.internal._GXCommon import _GXCommon


class Checker:
    def __init__(self, objects):
        self.objects = objects

    def check_repeat(self):
        """ object 重复检查，class,obis,ver"""
        objects_list = []
        for row in range(1, self.objects.sheet.max_row+1):
            if self.objects.sheet[f'{self.objects.title["Type"]}{row}'].value == 'o':
                value = ','.join([self.objects.sheet[f"{self.objects.title['Class']}{row}"].value,
                                  self.objects.sheet[f"{self.objects.title['Version']}{row}"].value,
                                  self.objects.sheet[f"{self.objects.title['OBIS']}{row}"].value])
                if value in objects_list:
                    raise ValueError(f"Repeat object: {value}, row: {self.objects.title['Version']}{row}")
                objects_list.append(value)

    def check_obis_format(self):
        """ OBIS 值格式检查 """
        for row in range(1, self.objects.sheet.max_row+1):
            if self.objects.sheet[f'{self.objects.title["Type"]}{row}'].value == 'o':
                value = self.objects.sheet[f"{self.objects.title['OBIS']}{row}"].value
                if ' ' in value:
                    raise ValueError(f'error obis format cell: {self.objects.title["Type"]}{row}, value: {value}')

    def check_access(self):
        """ 权限格式检查 """
        allow_value = ['--', 'Get', 'Set', 'Get, Set', 'Action']
        for key in self.objects.title['Access'].keys():
            for row in range(1, self.objects.sheet.max_row+1):
                if self.objects.sheet[f'{self.objects.title["Type"]}{row}'].value == 'a' or \
                        self.objects.sheet[f'{self.objects.title["Type"]}{row}'].value == 'm':
                    value = self.objects.sheet[f"{self.objects.title['Access'][key]}{row}"].value
                    if value not in allow_value:
                        raise ValueError(f"Error access format cell: "
                                         f"{self.objects.title['Access'][key]}{row}, value: {value}")

    def check_consistency(self):
        """ 一致性检查 """
        objects_list = {}
        tmp_attrs = None
        class_id = None
        mark_row = 0

        for row in range(1, self.objects.sheet.max_row+1):
            type_value = self.objects.sheet[f'{self.objects.title["Type"]}{row}'].value
            if type_value == 'o':
                if tmp_attrs is not None:
                    if tmp_attrs[class_id] != objects_list[class_id]:
                        raise ValueError(f"Error row: {mark_row}, "
                                         f"get: {tmp_attrs[class_id]}, "
                                         f"except: {objects_list[class_id]}")
                class_id = int(self.objects.sheet[f'{self.objects.title["Class"]}{row}'].value)
                if class_id not in objects_list.keys():
                    objects_list[class_id] = [[], []]
                    tmp_attrs = None
                else:
                    mark_row = row
                    tmp_attrs = {class_id: [[], []]}
            elif type_value in ['a', 'm']:
                type_index = 0 if type_value == 'a' else 1
                index_value = int(self.objects.sheet[f'{self.objects.title["Index"]}{row}'].value)
                if tmp_attrs is None:
                    if index_value in objects_list[class_id][type_index]:
                        raise ValueError(f"Errow index: {index_value}, has been exists, row: {row}")
                    objects_list[class_id][type_index].append(index_value)
                else:
                    tmp_attrs[class_id][type_index].append(index_value)

    def check_attr1(self):
        for row in range(1, self.objects.sheet.max_row+1):
            if self.objects.sheet[f'{self.objects.title["Type"]}{row}'].value == 'o':
                obis_str = self.objects.sheet[f'{self.objects.title["OBIS"]}{row}'].value
                obis_hex = self.objects.sheet[f'{self.objects.title["OBIS"]}{row+1}'].value
                if obis_hex.replace('"', '') != _GXCommon.logicalNameToBytes(obis_str).hex().upper():
                    raise ValueError(f"Error attr1, row: {row}, obis: {obis_str}, hex: {obis_hex}")

    @classmethod
    def check(cls, objects):
        print("Start check excel file")
        checker = cls(objects)
        checker.check_repeat()
        print("\tRepeat check.......Pass")
        checker.check_obis_format()
        print("\tOBIS format check.......Pass")
        checker.check_access()
        print("\tAccess check......Pass")
        checker.check_consistency()
        print("\tConsistency check......Pass")
        checker.check_attr1()
        print("\tAttribute 1 check......Pass")

