"""Author: Electroely

This Python library is used to manipulate build files
from Klei Entertainment's game Don't Starve Together.

readFile(filename)
Opens a build.bin file and reads it into a dictionary.

writeFile(data, filename)
Writes data into a build.bin file.
"""

import os
from struct import unpack, pack

enableDebug = True
def debugPrint(string):
    if enableDebug:
        print(string)

def strhash(str, hashcollection):
    hash = 0
    for c in str:
        v = ord(c.lower())
        hash = (v + (hash << 6) + (hash << 16) - hash) & 0xFFFFFFFF
    hashcollection[hash] = str
    return hash

def readFile(filename):
    print("Reading file "+filename)
    result = {}
    
    file = open(filename, mode = 'rb') #open in read binary mode
    fileContents = file.read()
    
    global fileMarker
    fileMarker = 0
    def readFile(num):
        global fileMarker
        result = fileContents[fileMarker: fileMarker + num]
        fileMarker = fileMarker + num
        return result
    
    filetype = readFile(4)
    if not filetype == b'BILD':
        print("Not a build file!")
        return
    
    #ints: version, total symbols, total frames, name len
    body1 = unpack('i'*4, readFile(4*4))
    result['VERSION'] = body1[0]
    #result['num_symbols'] = body1[1]
    result['num_frames'] = body1[2]
    
    #name (body1 had name length)
    name = readFile(body1[3]).decode()
    result['name'] = name
    
    #materials (atlas file names)
    numMaterials = unpack('i', readFile(4))[0]
    materials = []
    for i in range(numMaterials):
        matLen = unpack('i', readFile(4))[0]
        matName = readFile(matLen).decode()
        materials.append(matName)
    
    result['materials'] = materials
    
    #symbols
    symbols = []
    for i in range(body1[1]):
        symbol = {} 
        symbol_info = unpack('ii', readFile(4*2))
        symbol['hash'] = symbol_info[0]
        symbol['name'] = ""
        frames = []
        for j in range(symbol_info[1]):
            frame_info = unpack('iiffffii', readFile(4*8))
            frame = {
                'num':frame_info[0],
                'duration':frame_info[1],
                'bbox' : {
                    'x':frame_info[2],
                    'y':frame_info[3],
                    'w':frame_info[4],
                    'h':frame_info[5],
                },
                'vb_start_idx' : frame_info[6],
                'num_verts' : frame_info[7]
            }
            frames.append(frame)
        symbol['frames'] = frames
        symbols.append(symbol)
    result['symbols'] = []
    #add to result after we replace str hashes
    
    #vertices
    vertices = []
    num_vertices = unpack('i', readFile(4))[0]
    debugPrint("number of vertices: "+str(num_vertices))
    for i in range(num_vertices):
        data = unpack('ffffff', readFile(4*6))
        vertices.append({
            'x':data[0],
            'y':data[1],
            'z':data[2],
            'u':data[3],
            'v':data[4],
            'w':data[5],
        })
    result['vertices'] = vertices    
    
    #replace str hashes with actual strings
    num_hashes = unpack('i', readFile(4))[0]
    for i in range(num_hashes):
        data = unpack('ii', readFile(4*2))
        hash = data[0]
        name = readFile(data[1]).decode()
        for symbol in symbols:
            if 'hash' in symbol and symbol['hash'] == hash:
                symbol.pop('hash')
                symbol['name'] = name
    result['symbols'] = symbols
    
    unread = len(fileContents) - fileMarker
    if unread > 0:
        print("Warning! "+str(unread)+" unread bytes in file")
    
    return result

fout = None
def writeFile(data, buildpath):
	global fout
	fout = open(buildpath, "wb")
	hashes = {}
	def writeInt(num):
		global fout
		fout.write(pack("<I",num))
	def writeFloat(num):
		global fout
		fout.write(pack("<f",num))
	def writeString(string):
		global fout
		string = string.encode("ascii")
		fout.write(pack('<i'+str(len(string))+'s', len(string), string))
	def writeStringHash(string):
		hsh = strhash(string, hashes)
		writeInt(hsh)
	fout.write("BILD".encode("ascii"))
	writeInt(6)
	writeInt(len(data["symbols"]))
	framecount = 0
	for symbol in data["symbols"]:
		framecount = framecount + len(symbol["frames"])
	writeInt(framecount)
	writeString(data["name"])
	writeInt(len(data["materials"]))
	for mat in data["materials"]:
		writeString(mat)
	for symbol in data["symbols"]:
		writeStringHash(symbol["name"])
		writeInt(len(symbol["frames"]))
		for frame in symbol["frames"]:
			writeInt(frame["num"])
			writeInt(frame["duration"])
			writeFloat(frame["bbox"]["x"])
			writeFloat(frame["bbox"]["y"])
			writeFloat(frame["bbox"]["w"])
			writeFloat(frame["bbox"]["h"])
			writeInt(frame["vb_start_idx"])
			writeInt(frame["num_verts"])
	debugPrint("number of vertices: "+str(len(data["vertices"])))
	writeInt(len(data["vertices"]))
	for vertex in data["vertices"]:
		writeFloat(vertex["x"])
		writeFloat(vertex["y"])
		writeFloat(vertex["z"])
		writeFloat(vertex["u"])
		writeFloat(vertex["v"])
		writeFloat(vertex["w"])
	
	writeInt(len(hashes))
	for hashint in hashes:
		writeInt(hashint)
		writeString(hashes[hashint])
	fout.close()
	return True
    
##bdict = readFile("build.bin")
##
##import pprint
##pp = pprint.PrettyPrinter(indent = 1)
##pp.pprint(bdict)

