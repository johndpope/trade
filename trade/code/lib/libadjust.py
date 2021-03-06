import const
import os
import csv
from const import pjoin, strio
import json
from zipfile import ZipFile, ZIP_DEFLATED

def yAdjust(data):
	''' Adjust OHLC values using Y! provided Adj Close '''
	try:
		mult = float(data['Adj Close']) / float(data['Close'])
		data['Open'] = float(data['Open']) * mult 
		data['High'] = float(data['High']) * mult
		data['Low'] = float(data['Low']) * mult
		data['Close'] = float(data['Adj Close'])
		data['Volume'] = int(int(data['Volume']) / mult)
		del data['Adj Close']
	except ZeroDivisionError:
		pass


def mergeAndAdjust(symbol):
	with ZipFile(pjoin(const.RAW_DIR, '_' + symbol + '.csv.zip'), 'r', ZIP_DEFLATED) as _zip:
		files = _zip.namelist() 
		files.sort()
		files.reverse()
	
		# Adjust hist. prices in 2 steps: first adjust the Adj Close backward to the oldest data...
		merged = []
		carried_mult = 1.0
		for f in files:
			ld = list(csv.DictReader(strio(_zip.read(f))))
			if ld:
				if carried_mult != 1.0:
					for sess in ld:
						sess['Adj Close'] = float(sess['Adj Close']) * carried_mult
				carried_mult = float(ld[-1]['Adj Close']) / float(ld[-1]['Close'])
				merged += ld
	
		# ...and then use Adj Close to adjust the remaining values
		map(yAdjust, merged)
	
		name = '_' + symbol + '.json'
		zname = name + '.zip'
		with ZipFile(pjoin(const.ADJ_DIR, zname), 'w', ZIP_DEFLATED) as out:
			out.writestr(name, json.dumps(merged))
		print zname

if __name__ == '__main__':
	pass

