# -*- coding: utf-8 -*-
"""
"""
import ev_diag
import os
from sys import exit
import serial
import configuration as cc

ev_diag.serport = cc.config['DEFAULT']['Port']


def clear():
    os.system('cls')


def print_header():
    clear()
    print(cc.output_as_str('header'))


def exit_prog(answer):
    if answer == ":q" or answer == "quit":
        exit()
        quit()


def print_menu():
    print_header()
    print(cc.output_as_str('diag'), '\n')
    print(cc.output_as_str('print header'))
    answer = input('')
    if answer == '1':
        ev_diag.ion.print_data(ev_diag.ion.bmu_data)
    elif answer == '2':
        ev_diag.ion.print_data(ev_diag.ion.cell_info)
    elif answer == '3':
        ev_diag.ion.print_data(ev_diag.ion.cell_info)


def port_tool():
    while 1:
        print_header()
        print(cc.output_as_str('port header'), ev_diag.serport, '\n')
        print(cc.output_as_str('port instr'))
        answer = input('')
        if answer == '2':
            break
        elif answer == '1':
            print(cc.output_as_str('port input'))
            nport = input('')
            try:
                nport = 'COM'+str(int(nport))
            except ValueError:
                pass
            if nport.startswith('COM') is True and nport[:3]:
                try:
                    int(nport[3:])
                    ev_diag.serport = nport
                except ValueError:
                    pass
        cc.config.set('DEFAULT', 'port', ev_diag.serport)
        cc.writeconf()
        exit_prog(answer)
    clear()


def baud_tool():
    while 1:
        print_header()
        print(cc.output_as_str('baud header'), '\n')
        print(cc.output_as_str('baud instr'))
        answer = input('')
        if answer == '1':
            try:
                result = ev_diag.is_baudrate_ok()
            except serial.SerialException:
                result = False
            if result is True:
                print('\n', cc.output_as_str('con ok'))
            else:
                print('\n', cc.output_as_str('con not ok'))
            input(cc.output_as_str('enter2cont'))
        elif answer == '2':
            print(cc.output_as_str('ask yn'))
            answer = input('')
            if answer == 'y':
                try:
                    ev_diag.switch_baudrate()
                    print(cc.output_as_str('tried change br'))
                except serial.SerialException:
                    print(cc.output_as_str('con error'))
                input(cc.output_as_str('enter2cont'))
        elif answer == '3':
            break
        exit_prog(answer)


def diagnosis_menu():
    while 1:
        print_header()
        print(cc.output_as_str('diag'), '\n')
        print(cc.output_as_str('diag header'))
        answer = input('')
        if answer == '1':
            print(cc.output_as_str('read data'))
            try:
                ev_diag.connect()
                ev_diag.serialcon.do_setup(ev_diag.triplet_setup)
                ev_diag.ion.read_bmu_data(ev_diag.serialcon)
                ev_diag.ion.calculate_values()
                ev_diag.serialcon.reset()
                ev_diag.disconnect()
            except serial.SerialException:
                print(cc.output_as_str('con error'))
                input(cc.output_as_str('enter2cont'))
        elif answer == '2':
            print_menu()
            input(cc.output_as_str('enter2cont'))
        elif answer == '3':
            if ev_diag.ion.bmu_data != {}:
                ev_diag.ion.save_bmu_data()
            else:
                print(cc.output_as_str('no data'))
                input(cc.output_as_str('enter2cont'))
        elif answer == '4':
            break
        exit_prog(answer)
    clear()


opened = False

while 1:
    print_header()
    if opened is False:
        opened = True
        print(cc.output_as_str('quit instruction'), '\n')
    else:
        print('\n')
    print(cc.output_as_str('main header'))
    answer_main = input()
    if answer_main == '3':
        baud_tool()
    elif answer_main == '2':
        port_tool()
    elif answer_main == '1':
        diagnosis_menu()
    exit_prog(answer_main)
