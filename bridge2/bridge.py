#!/usr/bin/python3

import pcb

gnd = pcb.Net('gnd')

dcdc = pcb.Part('phidias:dcdc', {'gnd': pcb.POWER_GND, 'in': pcb.POWER_IN, 'out': pcb.POWER_OUT})('dcdc')
terminal = pcb.Part('Connect:bornier2', {(1, '+'): pcb.POWER_OUT, (2, '-'): pcb.POWER_GND})('terminal')

R_ = pcb.Part('Resistors_SMD:R_1206', {1: pcb.PASSIVE, 2: pcb.PASSIVE})
R = [R_('R%d' % t) for t in range(2)]

# Pins are swapped even/odd, because this is the counter-connector.
bbb = pcb.Part('Pin_Headers:Pin_Header_Straight_2x07', {
	(1, 'gnd'): pcb.POWER_GND,
	2: pcb.POWER_GND,
	(3, '3v3'): pcb.POWER_OUT,
	4: pcb.POWER_OUT,
	(5, 'vin'): pcb.POWER_IN,
	6: pcb.POWER_IN,
	(7, '5v'): pcb.POWER_OUT,
	8: pcb.POWER_OUT,
	(10, 'pwr_but'): pcb.IN,
	(9, 'reset'): pcb.IN,
	(12, 'rxd', '30'): pcb.IN,
	(11, '60'): pcb.BI,
	(14, 'txd', '31'): pcb.OUT,
	(13, '50'): pcb.BI,
	})('bbb')
# Connect pins.
for p1, p2 in ((1, 2), (3, 4), (5, 6), (7, 8)):
	bbb[p1] = bbb[p2]
	bbb[p1].net.used = False

# Pins are swapped even/odd, because this is the counter-connector.
melzi_icsp = pcb.Part('Pin_Headers:Pin_Header_Straight_2x03', {
	(2, 'gnd'): pcb.POWER_GND,
	(1, 'reset'): pcb.IN,
	(4, 'mosi'): pcb.IN,
	(3, 'sck'): pcb.IN,
	(6, '5v'): pcb.POWER_OUT,
	(5, 'miso'): pcb.OUT,
	})('icsp')
melzi_aux = pcb.Part('Pin_Headers:Pin_Header_Straight_2x05', {
	(2, 'gnd'): pcb.POWER_GND,
	(1, 'vcc'): pcb.POWER_OUT,
	(4, 'A4'): pcb.BI,
	(3, 'rx1'): pcb.BI,
	(6, 'A3'): pcb.BI,
	(5, 'tx1'): pcb.BI,
	(8, 'A2'): pcb.BI,
	(7, 'scl'): pcb.BI,
	(10, 'A1'): pcb.BI,
	(9, 'sda'): pcb.BI,
	})('aux')
melzi = pcb.group({
	'miso': pcb.OUT,
	'mosi': pcb.IN,
	'gnd': pcb.POWER_GND,
	'sck': pcb.IN,
	'reset': pcb.IN})

# Connect pins between Melzi connectors.
for icsp, aux in (('gnd', 'gnd'), ('mosi', 'rx1'), ('miso', 'tx1')):
	melzi_aux[aux] = melzi_icsp[icsp]
	melzi_aux[aux].net.used = False

# Connect Melzi components to outside.
for i in ('miso', 'mosi', 'gnd', 'sck', 'reset'):
	melzi[i] = melzi_icsp[i]
	melzi[i].net.used = False

# Mark unconnected Melzi pins.
for p in ('A1', 'A2', 'A3', 'A4', 'scl', 'sda', 'vcc'):
	melzi_aux[p] = None
melzi_icsp['5v'] = None

# Mark unconnected bbb pins.
bbb['3v3'] = None
bbb['5v'] = None
bbb['pwr_but'] = None
bbb['reset'] = None

# Connect the parts.
bbb['gnd'] = gnd
melzi['gnd'] = gnd
bbb['txd'] = melzi['mosi'], 'mosi'
bbb['50'] = melzi['sck'], 'sck'
bbb['60'] = melzi['reset'], 'reset'
melzi['miso'] = R[0][1], 'miso_5v'
R[0][2] = bbb['rxd'], 'miso_3v3'
bbb['rxd'] = R[1][1]
R[1][2] = gnd

dcdc['gnd'] = gnd
terminal['-'] = gnd
terminal['+'] = dcdc['in'], '24V'
dcdc['out'] = bbb['vin'], '5v'

pcb.write('bridge')
