#!/usr/bin/python3
from huffman import HuffmanCoding 
import sys
if len(sys.argv)<3 or sys.argv[1] not in ['-c','-x']:
	if len(sys.argv)>=2 and sys.argv[1]!="-h":
		print("Invalid Switch/Usage " + sys.argv[1])
	print("Usage :\n")
	print("To compress : \npython " + sys.argv[0] + " -c filename.txt [dictfile.dict]\n")
	print("To decompress : \npython " + sys.argv[0] + " -x filename.bin [dictfile.dict]")
	print("filename.dict is optional, to be used if the dictionary was saved under a different name.")
	exit(0)

if [sys.argv[1]] == ['-c']:
	print()
	pathf=sys.argv[2]
	dictf=''
	if len(sys.argv)>3:
		dictf=sys.argv[3]
	h = HuffmanCoding(pathf)
	out = h.compress()
	h.save_codes(dictf)
elif [sys.argv[1]] == ['-x']:
	print()
	pathf=sys.argv[2]
	dictf=''
	if len(sys.argv)>3:
		dictf=sys.argv[3]
	h = HuffmanCoding(pathf,dictf)
	h.decompress()
