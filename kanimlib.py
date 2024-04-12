"""Author: Electroely

This Python library is used to manipulate animation files
from Klei Entertainment's game Don't Starve Together.

readFile(filename)
Opens an anim.bin file and reads it into a dictionary.

writeFile(data, filename)
Writes data into an anim.bin file.
"""

from struct import unpack, pack

#facings from right to left in byte
facings = {
	"RIGHT":1<<0,
	"UP":1<<1,
	"LEFT":1<<2,
	"DOWN":1<<3,
	"UPRIGHT":1<<4,
	"UPLEFT":1<<5,
	"DOWNRIGHT":1<<6,
	"DOWNLEFT":1<<7
}
def getFacingsLabel(facingsbyte):
	result = "unknown"
	if facingsbyte == facings["LEFT"]|facings["RIGHT"]|facings["UP"]|facings["DOWN"]|facings["DOWNLEFT"]|facings["DOWNRIGHT"]|facings["UPLEFT"]|facings["UPRIGHT"]:
		result = "all"
	elif facingsbyte == facings["RIGHT"]|facings["LEFT"]:
		result = "side"
	elif facingsbyte == facings["DOWNLEFT"]|facings["DOWNRIGHT"]:
		result = "downside"
	elif facingsbyte == facings["UPLEFT"]|facings["UPRIGHT"]:
		result = "upside"
	elif facingsbyte == facings["LEFT"]|facings["RIGHT"]|facings["UP"]|facings["DOWN"]:
		result = "90s"
	elif facingsbyte == facings["DOWNLEFT"]|facings["DOWNRIGHT"]|facings["UPLEFT"]|facings["UPRIGHT"]:
		result = "45s"
	elif facingsbyte == facings["RIGHT"]:
		result = "right"
	elif facingsbyte == facings["LEFT"]:
		result = "left"
	elif facingsbyte == facings["UP"]:
		result = "up"
	elif facingsbyte == facings["DOWN"]:
		result = "down"
	return result

filepos = 0
def readFile(filepath):
	fin = open(filepath, 'rb')
	fileString = fin.read()
	
	def readFile(num):
		global filepos
		filepos = filepos + num
		return fileString[filepos-num:filepos]
	def readInt():
		return unpack("i",readFile(4))[0]
	def readByte():
		return unpack("B",readFile(1))[0]
	def readFloat():
		return unpack("f",readFile(4))[0]
	def readString(length):
		return readFile(length).decode("ascii")
	
	if readFile(4).decode("ascii") != "ANIM":
		print("Not an ANIM file!")
		return
	version = readInt()
	if version != 4:
		print("Wrong file version!",version,"Should be version 4")
		return
	
	data = {}
	data['total element refs'] = readInt()
	data['num frames'] = readInt()
	data['num events'] = readInt()
	numAnims = readInt()
	data['anims'] = []
	for i in range(numAnims):
		name = readString(readInt())
		#print("name",name)
		facingsbyte = readByte()
		animfacings = {}
		for facing in facings:
			animfacings[facing] = (facingsbyte & facings[facing]) != 0
		#print(animfacings)
		rootsymbolhash = readInt()
		#print(rootsymbolhash)
		framerate = readFloat()
		#print(framerate)
		frames = []
		numFrames = readInt()
		#print(numFrames)
		for i2 in range(numFrames):
			#x,y,w,h
			pos = (readFloat(), readFloat(), readFloat(), readFloat())
			#print(pos)
			events = []
			numEvents = readInt()
			#print(numEvents)
			for i3 in range(numEvents):
				events.append(readInt())
			elements = []
			numElements = readInt()
			for i3 in range(numElements):
				symbolhash = readInt()
				frame = readInt()
				folderhash = readInt()
				elements.append({
					'symbol':None,
					'frame':frame,
					'folder':None,
					'symbolhash':symbolhash,
					'folderhash':folderhash,
					# a,b,c,d, tx, ty, tz
					'mat':{
						'a':readFloat(),'b':readFloat(),'c':readFloat(),'d':readFloat(),
						'tx':readFloat(),'ty':readFloat(),'tz':readFloat()}
				})
			frames.append({
				'events':events,
				'pos':pos,
				'elements':elements
			})
		facingslabel = getFacingsLabel(facingsbyte)
		animlabel = name
		if facingslabel != "all" and facingslabel != "unknown":
			animlabel = animlabel+"_"+facingslabel
		data['anims'].append({
			'label':animlabel,
			'name':name,
			'rootsymbol':None,
			'rootsymbolhash':rootsymbolhash,
			'framerate':framerate,
			'numframes':len(frames),
			'facingslabel':facingslabel,
			'facings':animfacings,
			'frames':frames
		})
	
	strings = {}
	numhashedstrings = readInt()
	for i in range(numhashedstrings):
		hsh = readInt()
		string = readString(readInt())
		strings[hsh] = string
	
	for anim in data['anims']:
		anim['rootsymbol'] = strings[anim['rootsymbolhash']]
		anim.pop('rootsymbolhash')
		for frame in anim['frames']:
			eventstrings = []
			for hsh in frame['events']:
				eventstrings.append(strings[hsh])
			for element in frame['elements']:
				element['symbol'] = strings[element['symbolhash']]
				element['folder'] = strings[element['folderhash']]
				element.pop('symbolhash')
				element.pop('folderhash')
				
	return data
    
def countFrames(data):
	count = 0
	for anim in data['anims']:
		count = count + len(anim['frames'])
	return count
def countElements(data):
	count = 0
	for anim in data['anims']:
		for frame in anim['frames']:
			count = count + len(frame['elements'])
	return count
def countEvents(data):
	count = 0
	for anim in data['anims']:
		for frame in anim['frames']:
			count = count + len(frame['events'])
	return count

def getFacingsByte(data):
	byte = 0
	for facing in data:
		if data[facing]:
			byte = byte + facings[facing]
	return byte
def strhash(str, hashcollection):
    hash = 0
    for c in str:
        v = ord(c.lower())
        hash = (v + (hash << 6) + (hash << 16) - hash) & 0xFFFFFFFF
    hashcollection[hash] = str
    return hash
fout = None
def writeFile(data, animpath):
	global fout
	fout = open(animpath, "wb")
	hashes = {}
	def writeInt(num):
		global fout
		fout.write(pack("<I",num))
	def writeFloat(num):
		global fout
		fout.write(pack("<f",num))
	def writeString(string):
		global fout
		#writeInt(len(string))
		#fout.write(string.encode("ascii"))
		string = string.encode("ascii")
		fout.write(pack('<i'+str(len(string))+'s', len(string), string))
	def writeStringHash(string):
		hsh = strhash(string, hashes)
		writeInt(hsh)
	fout.write("ANIM".encode("ascii"))
	writeInt(4)
	writeInt(countElements(data))
	writeInt(countFrames(data))
	writeInt(countEvents(data))
	writeInt(len(data['anims']))
	for anim in data['anims']:
		writeString(anim['name'])
		fout.write(pack("<B",getFacingsByte(anim['facings'])))
		writeStringHash(anim['rootsymbol'])
		writeFloat(anim['framerate'])
		writeInt(len(anim['frames']))
		for frame in anim['frames']:
			writeFloat(frame['pos'][0])
			writeFloat(frame['pos'][1])
			writeFloat(frame['pos'][2])
			writeFloat(frame['pos'][3])
			writeInt(len(frame['events']))
			for event in frame['events']:
				writeStringHash(event)
			writeInt(len(frame['elements']))
			for element in frame['elements']:
				writeStringHash(element['symbol'])
				writeInt(element['frame'])
				writeStringHash(element['folder'])
				writeFloat(element['mat']['a'])
				writeFloat(element['mat']['b'])
				writeFloat(element['mat']['c'])
				writeFloat(element['mat']['d'])
				writeFloat(element['mat']['tx'])
				writeFloat(element['mat']['ty'])
				writeFloat(element['mat']['tz'])
	writeInt(len(hashes))
	for hsh in hashes:
		writeInt(hsh)
		writeString(hashes[hsh])
	fout.close()
	return True
