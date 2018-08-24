# -*- coding: utf-8 -*-
"""
"""

import configparser

config = configparser.ConfigParser()

output = {}
output['quit instruction'] = dict(en='q: or quit to quit', de='q: oder quit zum Beenden')
output['con error'] = dict(en='Connection Error', de='Verbindungsfehler')
output['enter2cont'] = dict(en='\nPress enter to continue', de='\nEingabe zum fortfahren')
output['header'] = dict(en='I-MIEV BMU Diagnosis\n', de='Drilling BMU Diagnose\n')
output['port header'] = dict(en='Port Tool - Current Port:', de='Port Tool - Aktueller Port:')
output['port instr'] = dict(en='1=Change port   2=back', de='1=Port ändern   2=Zurück')
output['port input'] = dict(en='port name:', de='Port angeben:')
output['baud header'] = dict(en='Baud tool', de='Baud Tool')
output['baud instr'] = dict(en='1=test connection   2=try change baudrate SX   3=back', de='1=Verbindung testen   2=Baudrate SX ändern   3=Zurück')
output['con ok'] = dict(en='Connection OK', de='Verbindung in Ordnung')
output['con not ok'] = dict(en='Connection not OK', de='Verbindung nicht in Ordnung')
output['ask yn'] = dict(en='confirm y/n', de='Wirklich? y/n')
output['tried change br'] = dict(en='Tried changing Baudrate', de='Baudrate wurde versucht zu ändern')
output['diag'] = dict(en='Diagnosis', de='Diagnose')
output['main header'] = dict(en='1=Diagnosis   2=Change port   3=Test connection', de='1=Diagnose   2=Port festlegen   3=OBDLink testen')
output['read data'] = dict(en='Reading values...', de='Lese Daten...')
output['no data'] = dict(en='no data', de='Keine Daten')
output['diag header'] = dict(en='1=Get BMU values   2=Show values   3=Save result   4=back', de='1=BMU Werte einlesen   2=Werte anzeigen   3=Ergebnis speichern   4=Zurück')
# output['']=dict(en = '', de = '')


def initial_config():
    config['DEFAULT'] = {}
    config['DEFAULT']['Port'] = 'COM10'
    config['DEFAULT']['language'] = 'en'
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def output_as_str(out):
    return output[out][config['DEFAULT']['language']]


if config.read('config.ini') == []:
    initial_config()
else:
    config.read('config.ini')
