from heapq import heappush, heappop
import os
import pickle

class HeapNode:
	def __init__(self, char, freq):
		self.char = char
		self.freq = freq
		self.left = None
		self.right = None
                
	def __gt__(self, other):
		if(other == None):
			return -1
		if(not isinstance(other, HeapNode)):
			return -1
		return self.freq > other.freq


class HuffmanCoding:
	def __init__(self, path='', old_code_path=False):
		self.path = path
		self.heap = []
		self.old_code_path=old_code_path
		self.codes = {}
		self.rev_codes = {}
		self.freq={}

	def init(self):
		fname, fext = os.path.splitext(self.path)
		if not fext == '.bin':
			if fname:
				with open(self.path,'r') as file:
					text = file.read()
					text = text.rstrip()
				if not self.old_code_path:
					if not os.path.exists(fname + '.dict'):
						self.make_frequency_dict(text)
						self.make_heap(self.freq)
						self.merge_nodes()
						self.make_codes()
					else:
						self.old_code_path = fname + '.dict'
						print('Using dictionary found : ' + self.old_code_path)
						pickle_in = open(self.old_code_path,"rb")
						self.codes = pickle.load(pickle_in)
						self.rev_codes = dict([[v,k] for k,v in self.codes.items()])
				else:
					print('Using provided dictionary')
					pickle_in = open(self.old_code_path,"rb")
					self.codes = pickle.load(pickle_in)
					self.rev_codes = dict([[v,k] for k,v in self.codes.items()])
				return text
			if self.old_code_path:
				pickle_in = open(self.old_code_path,"rb")
				self.codes = pickle.load(pickle_in)
				self.rev_codes = dict([[v,k] for k,v in self.codes.items()])
				return
			else:
				print('No dictionary found!!')
				exit()
		if os.path.exists(fname + '.dict') or self.old_code_path:
			if self.old_code_path:
				print('Using provided dictionary')
			elif os.path.exists(fname + '.dict'):
				self.old_code_path = fname + '.dict'
				print('Using dictionary found : ' + self.old_code_path)
			pickle_in = open(self.old_code_path,"rb")
			self.codes = pickle.load(pickle_in)
			self.rev_codes = dict([[v,k] for k,v in self.codes.items()])
			return
		else:
			print('No dictionary found!!')
			exit()

	def save_codes(self, new_dict=None): 
		if not self.codes:
			self.init()
		if not new_dict:
			fname, fext = os.path.splitext(self.path)
			new_dict = fname + ".dict"
		pickle_out = open(new_dict,"wb")
		pickle.dump(self.codes, pickle_out)
		print("Code dictionary saved as " + new_dict)
		print()

	# functions for compression:

	def make_frequency_dict(self, text):
		frequency = {}
		print("Building frequency table...")
		for character in text:
			if not character in frequency:
				frequency[character] = 0
			frequency[character] += 1
		self.freq = frequency

	def make_heap(self, frequency):
		print('Generating heap...')
		for key in frequency:
			node = HeapNode(key, frequency[key])
			heappush(self.heap, node)

	def merge_nodes(self):
		print('Merging nodes...')
		while(len(self.heap)>1):
			node1 = heappop(self.heap)
			node2 = heappop(self.heap)
			merged = HeapNode(None, node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2
			heappush(self.heap, merged)

	def make_codes_helper(self, root, current_code):
		if(root == None):
			return

		if(root.char != None):
			self.codes[root.char] = current_code
			self.rev_codes[current_code] = root.char
			return

		self.make_codes_helper(root.left, current_code + "0")
		self.make_codes_helper(root.right, current_code + "1")


	def make_codes(self):
		print('Cooking code...')
		root = heappop(self.heap)
		current_code = ""
		self.make_codes_helper(root, current_code)


	def get_encoded_text(self, text):
		print('Encoding...')
		encoded_text = ""
		for character in text:
			encoded_text += self.codes[character]

		return encoded_text


	def pad_encoded_text(self, encoded_text):
		print('Padding...')
		extra_padding = 8 - len(encoded_text) % 8
		for i in range(extra_padding):
			encoded_text += "0"

		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text


	def get_byte_array(self, padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		for i in range(0, len(padded_encoded_text), 8):
			byte = padded_encoded_text[i:i+8]
			b.append(int(byte, 2))
		return b


	def compress(self):
		filename, file_extension = os.path.splitext(self.path)
		output_path = filename + ".bin"
		text = self.init()
		print("Compressing " + self.path + '...')
		with open(output_path, 'wb') as output:
			encoded_text = self.get_encoded_text(text)
			padded_encoded_text = self.pad_encoded_text(encoded_text)
			b = self.get_byte_array(padded_encoded_text)
			output.write(bytes(b))
		saved = 1 - os.path.getsize(output_path) / os.path.getsize(self.path)
		print('Done')
		print("Compressed as " + output_path + " with " + '{:.2%}'.format(saved) + " space savings.")
		print()
		return output_path


	""" functions for decompression: """

	def remove_padding(self, padded_encoded_text):
		print('Removing padding...')
		padded_info = padded_encoded_text[:8]
		extra_padding = int(padded_info, 2)

		padded_encoded_text = padded_encoded_text[8:] 
		encoded_text = padded_encoded_text[:-1*extra_padding]

		return encoded_text

	def decode_text(self, encoded_text):
		print('Decoding...')
		current_code = ""
		decoded_text = ""

		for bit in encoded_text:
			current_code += bit
			if(current_code in self.rev_codes):
				character = self.rev_codes[current_code]
				decoded_text += character
				current_code = ""

		return decoded_text


	def decompress(self, input_path=None):
		if not input_path:
			fname, fext = os.path.splitext(self.path)
			input_path = fname + ".bin"
		print("Decompressing " + input_path)
		filename, file_extension = os.path.splitext(input_path)
		output_path = filename + "-extract" + ".txt"
		if not self.codes:
			self.init()
		
		with open(input_path, 'rb') as file, open(output_path, 'w') as output:
			bit_string = ""

			byte = file.read(1)
			while(byte != b''):
				byte = ord(byte)
				bits = bin(byte)[2:].rjust(8, '0')
				bit_string += bits
				byte = file.read(1)

			encoded_text = self.remove_padding(bit_string)

			decompressed_text = self.decode_text(encoded_text)
			
			output.write(decompressed_text)
		print('Done')
		print("Decompressed as " + output_path)
		print()
		return output_path
