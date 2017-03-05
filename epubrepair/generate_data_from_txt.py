import os
from .generate_data import generate_article_data, generate_meta_data

def generate(path, targetdir, book_name, book_type):
	'''
	description: generate epub data file and meta data file by txt
	arguments: 
		path -> a file path(a article content file, a line is a paragraph in the epub)
				or a directory path(contains some txt file, each txt file is a article content file)
		target -> the target directory to store the epub data file and meta data file
	'''
	if not os.path.exists(path):
		raise Exception('the path %s not exists' % path)
	if not os.path.exists(targetdir):
		raise Exception('the directory %s not exists' % targetdir)
	fname_list = []
	if os.path.isfile(path):
		fname_list = [path]
	else:
		fname_list = [os.sep.join([path, item]) for item in os.listdir(path) if os.path.isfile(os.sep.join([path, item]))]
	fname_list = [fname for fname in fname_list if fname.endswith('.txt')]

	content_list = []
	for fname in fname_list:
		title = os.path.splitext(os.path.basename(fname))[0]
		content = []
		with open(fname, 'r', encoding='utf8') as f:
			for line in f:
				content.append(line.strip())
		content_list.append([title, content])
	
	data_file = '%s.jl' % book_name
	data_file = os.sep.join([targetdir, data_file])
	meta_file = '%s_meta.json' % book_name
	meta_file = os.sep.join([targetdir, meta_file])

	with open(data_file, 'w', encoding='utf8') as df, open(meta_file, 'w', encoding='utf8') as mf:
		title_list = []
		article_count = 0
		for title, content in content_list:
			article_count += 1
			article_data = generate_article_data(
				article_count,
				title,
				book_name,
				book_type,
				content
			)
			df.write(article_data+'\n')
			title_list.append(title)
		
		meta_data = generate_meta_data(
			title_list,
			book_name,
			book_type,
			article_count
		)
		mf.write(meta_data+'\n')
	return article_count