# -*- coding: utf-8 -*-
"""
"""

from datetime import datetime, timedelta
import csv

triplet_bmu_commands = ['022111',
                        '022101',
                        '022102',
                        '022103',
                        '022104',
                        ]

triplet_setup_odo = ['stfac',
                     'stfap 412,FFF']

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

    def read_odometer(self, connection):
        connection.do_setup(triplet_setup_odo)
        connection.write(b'stm\n\r')
        aa = connection.read_until(b'\r412')
        self.message_decipher(aa)
        connection.write(b'sti\n\r')
        connection.read_until(b'>')
        return aa

    def read_bmu_data(self, connection):
        connection.reconnect()
        for i in triplet_bmu_commands:
            self.message_decipher(connection.get_answer(i))

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

    def print_bmu_data(self):
        for key, val in self.bmu_data.items():
            print('{:_<30}{:_>8}'.format(key, val))

    def message_decipher(self, message):
        # print('decypher:',message)
        def voltage(a, b):
            return round(int(content[a:b], 16)/200.0 + 2.1, 3)

        def temp(a, b):
            return int(content[a:b], 16) - 50

        if b'762100E6111' in message:
            content = self.strip_header(message)
            content = content.decode()
            content = content.replace('0E6111', '')
            self.bmu_data['Build Date'] = (datetime.today() - timedelta(minutes=int(content[0:8], 16))).strftime("%Y-%m-%d %H:%M")
            self.bmu_data['Ah AC'] = int(content[8:16], 16)
            self.bmu_data['Ah DC'] = int(content[16:24], 16)
            self.bmu_data['Ah Total'] = self.bmu_data['Ah AC']+self.bmu_data['Ah DC']
        elif b'762102E6101'in message:
            # print('yes')
            content = self.strip_header(message)
            content = content.decode()
            content = content.replace('2E6101', '')
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
            self.bmu_data['Battery Capacity full'] = int(content[54:58], 16)/10.0
            self.bmu_data['Battery Capacity currently'] = int(content[58:62], 16)/10.0
        elif b'76210B26102' in message:
            content = self.strip_header(message)
            content = content.decode()
            content = content.replace('B26102', '')
            index = 1
            while 1:
                temp_volt = voltage(4*index-4, 4*index)
                if temp_volt == 2.1:
                    break
                else:
                    name = 'Cell Voltage ' + '{:02d}'.format(index)
                    self.cell_info[name] = temp_volt
                index += 1
            #print(content)
        elif message.startswith(b'>412') is True:
            content = message
            content = content.replace(b'>412', b'')[:16]
            content = content.decode()
            self.bmu_data['Odometer'] = int(content[5:10], 16)

        # Calculated Values:
        try:
            self.bmu_data['Number of Cells'] = len([v for k, v in self.cell_info.items() if k.startswith('Cell Voltage')])
            self.bmu_data['kWh Total'] = self.bmu_data['Ah Total'] * self.bmu_data['Number of Cells'] * 3.75/1000
            self.bmu_data['kWh/100km'] = round(self.bmu_data['kWh Total']*100/self.bmu_data['Odometer'], 2)
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
        return message
