import os, json, shutil
from optparse import OptionParser

class BadFileException(Exception):
	def __init__(self, *args, **kwargs):
		super(BadFileException, self).__init__(*args, **kwargs)

def check_meta(meta_file):
	if not os.path.exists(meta_file):
		raise Exception('meta file[%s] not exists' % meta_file)

	ok = True
	message = 'ok'
	# check meta file
	metainfo = None
	if ok:
		with open(meta_file, 'r', encoding='utf8') as f:
			metainfo = json.loads(f.read())
		if not metainfo:
			ok = False
			message = 'meta file[%s] is empty'

	if ok:
		book = metainfo.get('book', None)
		chapters = metainfo.get('chapters', None)
		articles = metainfo.get('articles', None)
		if ok and not book:
			ok = False
			message = 'meta file[%s] should have book field'
		if ok and not chapters:
			ok = False
			message = 'meta file[%s] should have chapters field'
		if ok and not articles:
			ok = False
			message = 'meta file[%s] should have articles field'
	
	if ok:
		bookname = book.get('ch_name', None)
		en_bookname = book.get('en_name', None)
		booktype = book.get('type', None)
		bookurl = book.get('url', None)
		if ok and not bookname:
			ok = False
			message = 'meta file[%s] book field should have ch_name'
		if ok and not en_bookname:
			ok = False
			message = 'meta file[%s] book field should have en_name'
		if ok and not booktype:
			ok = False
			message = 'meta file[%s] book field should have type'
		if ok and not bookurl:
			ok = False
			message = 'meta file[%s] book field should have url'
	
	if not ok:
		raise Exception(message % meta_file)
	
	book = {
		'ch_name': bookname,
		'en_name': en_bookname,
		'type': booktype,
		'url': bookurl
	}
	# check data file
	meta_all_article_id_list = []
	meta_article_info_dict = {}
	for chapter in chapters:
		for article_id in chapter.get('articles', []):
			meta_all_article_id_list.append(article_id)
			meta_article_info_dict[article_id] = {
				'url': articles.get(str(article_id), {}).get('url', ''),
				'title': articles.get(str(article_id), {}).get('ch_name', ''),
				'en_title': articles.get(str(article_id), {}).get('en_name', '')
			}
			if not meta_article_info_dict[article_id]['url']:
				raise Exception('meta file[%s] articles[%d] not exists or damaged' % (meta_file, article_id))

	return [book, meta_all_article_id_list, meta_article_info_dict]

def check_data(data_file, article_id_list, article_info_dict):
	if not os.path.exists(data_file):
		raise Exception('data file[%s] not exists' % data_file)
	
	data_all_article_id_list = []
	data_good_article_id_list = []
	with open(data_file, 'r', encoding='utf8') as f:
		try:
			lines = f.readlines()
		except Exception as e:
			msg = '[ERROR]', 'data file[%s] error(%s)' % (data_file, e)
			raise Exception(msg)
			# print(msg)
			# return [[], 0]
		for line, lnum in zip(lines, range(1, len(lines)+1)):
			try:
				item = json.loads(line)
			except Exception as e:
				msg = '[ERROR]', 'data file[%s] line[%d] is bad json (%s)' % (data_file, lnum, e)
				raise Exception(msg)
				# print(msg)
				# return [[], 0]
			if not item.get('article_id', None):
				raise BadFileException('data file [%s] line[%d] lost article_id' % (data_file, lnum+1))
			article_id = int(item['article_id'])
			data_all_article_id_list.append(article_id)
			if item.get('content', None):
				data_good_article_id_list.append(article_id)

	articlesinfo = []
	article_id_set = set(article_id_list)
	data_good_article_id_set = set(data_good_article_id_list)
	data_all_article_id_set = set(data_all_article_id_list)

	if data_all_article_id_set - article_id_set:
		raise BadFileException('meta file lost some article id')

	lost_article_id_set = article_id_set - data_good_article_id_set
	progress = len(lost_article_id_set) / len(article_id_set)
	for article_id in lost_article_id_set:
		url = article_info_dict[article_id]['url']
		en_title = article_info_dict[article_id]['en_title']
		title = article_info_dict[article_id]['title']
		articlesinfo.append({
			'id': article_id,
			'url': url,
			'title': title,
			'en_title': en_title,
			'content_empty': article_id in data_all_article_id_set
		})
	return [articlesinfo, progress]

def check(datadir):
	'''
		if meta file not exists
			data file will be pun into datadir/wet
		elif data file and meta file is ok
			will be copied into datadir/hot
		elif data file lost some articles data
			will be copied into datadir/cold
		else
			data file is damaged, copied into datadir/trash
		
		datadir/hot/_books.jl descript ok books' information
		datadir/cold/_report.jl descript lost articles information
		datadir/cold/_booklist.jl
		datadir/trash/_booklist.jl
	'''
	if not os.path.exists(datadir):
		raise Exception('data directory not exists')
	hotdir = os.sep.join([datadir, 'hot'])
	colddir = os.sep.join([datadir, 'cold'])
	wetdir = os.sep.join([datadir, 'wet'])
	trashdir = os.sep.join([datadir, 'trash'])

	if os.path.exists(hotdir):
		shutil.rmtree(hotdir)
	if os.path.exists(colddir):
		shutil.rmtree(colddir)
	if os.path.exists(wetdir):
		shutil.rmtree(wetdir)
	if os.path.exists(trashdir):
		shutil.rmtree(trashdir)
	os.mkdir(hotdir)
	os.mkdir(colddir)
	os.mkdir(wetdir)
	os.mkdir(trashdir)

	books_file = '_books.jl'
	report_file = '_report.jl'
	booklist_file = '_booklist.jl'
	bfname = os.sep.join([hotdir, books_file])
	rfname = os.sep.join([colddir, report_file])
	lfname = os.sep.join([colddir, booklist_file])
	tfname = os.sep.join([trashdir, booklist_file])

	meta_file_suffix = '_meta.json'
	data_file_suffix = '.jl'
	total_count = 0
	ok_count = 0
	max_progress = 0.7
	with open(bfname, 'w', encoding='utf8') as bf, open(rfname, 'w', encoding='utf8') as rf, open(lfname, 'w', encoding='utf8') as lf, open(tfname, 'w', encoding='utf8') as tf:
		for fname in os.listdir(datadir):
			fnamefull = os.sep.join([datadir, fname])
			if os.path.isfile(fnamefull):
				if not fname.endswith(data_file_suffix):
					continue
				total_count += 1
				data_file = fnamefull
				meta_file = '.'.join(data_file.split('.')[:-1]) + meta_file_suffix
				
				# if meta file not exists, data file will be copied into wetdir
				if (not os.path.exists(meta_file)):
					shutil.copy(data_file, wetdir)
					continue
				bookinfo, article_id_list, article_info_dict = check_meta(meta_file)
				try:
					[articlesinfo, progress] = check_data(data_file, article_id_list, article_info_dict)
				except BadFileException as e:
					# data file has errors, will be copied into trashdir
					shutil.copy(data_file, trashdir)
					shutil.copy(meta_file, trashdir)
					tf.write(json.dumps({
						'url': bookinfo['url'],
						'name': bookinfo['ch_name'],
						'category_url': '',
						'category_name': '',
						'message': str(e)
					}, ensure_ascii=False))
					tf.write('\n')
					print(e)
					continue
				except Exception as e:
					raise e

				if not articlesinfo:
					# data file is ok
					ok_count += 1
					shutil.copy(data_file, hotdir)
					shutil.copy(meta_file, hotdir)
					bf.write(json.dumps({
						'ch_name': bookinfo['ch_name'],
						'en_name': bookinfo['en_name'],
						'type': bookinfo['type'],
						'url': bookinfo['url']
					}, ensure_ascii=False))
					bf.write('\n')
				else:
					# data file lost some articles
					shutil.copy(data_file, colddir)
					shutil.copy(meta_file, colddir)
					# if progress > max_progress:
						# rf.write(json.dumps({
						# 	'url': bookinfo['url'],
						# 	'ch_name': bookinfo['ch_name'],
						# 	'en_name': bookinfo['en_name'],
						# 	'type': bookinfo['type'],
						# 	'articles': articlesinfo
						# }, ensure_ascii=False, indent=4))
					rf.write(json.dumps({
						'url': bookinfo['url'],
						'ch_name': bookinfo['ch_name'],
						'en_name': bookinfo['en_name'],
						'type': bookinfo['type'],
						'articles': articlesinfo
					}, ensure_ascii=False, indent=4))
					rf.write('\n')
					# else:
					lf.write(json.dumps({
						'url': bookinfo['url'],
						'name': bookinfo['ch_name'],
						'category_url': '',
						'category_name': ''
					}, ensure_ascii=False))
					lf.write('\n')

	return [total_count, ok_count]

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-d', '--dir', dest='dir', help='book data directory')
	(options, args) = parser.parse_args()
	if not os.path.exists(options.dir):
		raise Exception('book data directory not exists')
	
	check(options.dir)