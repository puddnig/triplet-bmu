# -*- coding: utf-8 -*-
"""
"""

from datetime import datetime, timedelta
import csv

triplet_bmu_commands = ['022111',
                        '022113',
                        '022106',
                        '022101',
                        '022102',
                        '022103',
                        '022104',
                        ]

triplet_setup = ['stp33',
                 'ate0',
                 'ath1',
                 'atl0',
                 'ats0',
                 'atcaf0',
                 'stfac',
                 'atfcsh761',
                 'atfcsd300000',
                 'atfcsm1',
                 'atsh761',
                 'stffca 760,FF0'
                 ]


class triplet:
    bmu_data = {}
    cell_info = {}

    def read_bmu_data(self, connection):
        connection.reconnect()
        for i in triplet_bmu_commands:
            answer = connection.get_answer(i)
            self.message_decipher(answer, i)

    def save_bmu_data(self):
        date = datetime.today().strftime("%Y-%m-%d_%H-%M")
        filename = date + '_bmu_data.csv'
        f = open(filename, 'w')
        w = csv.writer(f)
        for key, val in self.bmu_data.items():
            w.writerow([key, val])
        for key, val in self.cell_info.items():
            w.writerow([key, val])
        f.close()

    def print_data(self, dict):
        for key, val in dict.items():
            print('{:_<30}{:_>8}'.format(key, val))

    def message_decipher(self, message, command):
        # print('decypher:',message)
        def voltage(a, b):
            return round(int(content[a:b], 16)/200.0 + 2.1, 3)

        def temp(a, b):
            return int(content[a:b], 16) - 50

        def hex2int(a, b):
            return int(content[a:b], 16)

        content = self.strip_header(message)
        content = content.decode()

        if command == '022111':
            self.bmu_data['Build Date'] = (datetime.today() - timedelta(minutes=int(content[0:8], 16))).strftime("%Y-%m-%d %H:%M")
            self.bmu_data['Ah AC'] = int(content[8:16], 16)
            self.bmu_data['Ah DC'] = int(content[16:24], 16)
            self.bmu_data['Ah Total'] = (self.bmu_data['Ah AC']
                                         + self.bmu_data['Ah DC'])
        elif command == '022101':
            self.bmu_data['SOC'] = int(content[0:2], 16)/2.0-5
            self.bmu_data['SOC Display'] = int(content[2:4], 16)/2.0-5
            self.bmu_data['Cell Voltage max'] = voltage(4, 8)
            self.bmu_data['Cell Voltage max ID'] = int(content[8:10], 16) + 1
            self.bmu_data['Cell Voltage min'] = voltage(10, 14)
            self.bmu_data['Cell Voltage min ID'] = int(content[14:16], 16) + 1
            self.bmu_data['Battery Voltage'] = int(content[16:20], 16)/10.0
            self.bmu_data['Temp max'] = temp(20, 22)
            self.bmu_data['Temp max module ID'] = int(content[22:24], 16) + 1
            self.bmu_data['Temp min'] = temp(24, 26)
            self.bmu_data['Temp min module ID'] = int(content[26:28], 16) + 1
            self.bmu_data['Battery Capacity full'] = hex2int(54, 58)/10.0
            self.bmu_data['Battery Capacity currently'] = hex2int(58, 62)/10.0
            self.bmu_data['Battery max input power'] = hex2int(62, 64)/4.0
            self.bmu_data['Battery max output power'] = hex2int(64, 66)/4.0
            self.bmu_data['Target voltage balancing'] = voltage(70, 74)
            self.bmu_data['BMU control voltage'] = hex2int(74, 76)/10.0
            self.bmu_data['EV-ECU control voltage'] = hex2int(76, 78)/10.0
            self.bmu_data['Battery fan pwm %'] = hex2int(78, 80)

        elif command == '022102':
            ID = 1
            for n in range(1, 89):
                tmp_volt = voltage(4*n-4, 4*n)
                if tmp_volt == 2.1:
                    break
                elif tmp_volt > 5:
                    pass
                else:
                    name = 'Cell Voltage ' + '{:02d}'.format(ID)
                    self.cell_info[name] = tmp_volt
                    ID += 1
        elif command == '022103':
            ID = 1
            for n in range(1, 67):
                tmp_temp = temp(2*n-2, 2*n)
                if tmp_temp > 90:
                    pass
                else:
                    name = 'Temperature ' + '{:02d}'.format(ID)
                    self.cell_info[name] = tmp_temp
                    ID += 1
        elif command == '022106':
            self.bmu_data['Odometer'] = int(content[0:6], 16)
        elif command == '022113':
            self.bmu_data['Number of Cells'] = hex2int(6, 8)

    def calculate_values(self):
        try:
            self.bmu_data['kWh Total'] = self.bmu_data['Ah Total'] * self.bmu_data['Number of Cells'] * 3.75/1000
            self.bmu_data['kWh/100km'] = round(self.bmu_data['kWh Total'] * 100/self.bmu_data['Odometer'], 2)
        except KeyError:
            return

    def strip_header(self, message):
        message = message.replace(b'76210', b'')
        message = message.replace(b'76220', b'')
        header = 0x76221
        while 1:
            message = message.replace(format(header, 'X').encode(), b'')
            header += 1
            if message.find(format(header, 'X').encode()) == -1:
                break
        message = message.replace(b'\r', b'')
        message = message.replace(b'>', b'')
        # print('stripped:', message)
        if message.decode().startswith('762') is True:
            message = message[9:]
        else:
            message = message[6:]
        return message
