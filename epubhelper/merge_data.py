import os, json, shutil
from optparse import OptionParser

def merge(data_file1, data_file2, output_file):
	data = []
	data1 = {}
	data2 = {}
	with open(data_file1, 'r', encoding='utf8') as d1, open(data_file2, 'r', encoding='utf8') as d2:
		for line in d1:
			if not line.strip():
				continue
			item = json.loads(line)
			if item['content']:
				data1[item['article_id']] = item
		for line in d2:
			if not line.strip():
				continue
			item = json.loads(line)
			if item['content']:
				data2[item['article_id']] = item
	for article_id in set(data1.keys())|set(data2.keys()):
		item = {}
		if article_id in data1 and article_id in data2:
			if len(data1[article_id]['content']) > len(data2[article_id]['content']):
				item = data1[article_id]
			else:
				item = data2[article_id]
		elif article_id in data1:
			item = data1[article_id]
		elif article_id in data2:
			item = data2[article_id]

		if not item:	
			raise Exception('there is something wrong')
		
		data.append(item)

	with open(output_file, 'w', encoding='utf8') as f:
		for item in data:
			f.write(json.dumps(item, ensure_ascii=False)+'\n')
	return len(data)

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-i', '--input', dest='input', help='two input part data files')
	parser.add_option('-o', '--output', dest='output', help='the output filename')
	(options, args) = parser.parse_args()
	file1, file2 = options.input.split(';')
	if not os.path.exists(file1):
		raise Exception('part data file not exists')
	if not os.path.exists(file2):
		raise Exception('part data file not exists')

	merge(file1, file2, options.output)