import os, json, shutil
from optparse import OptionParser

def is_ok(data_file, meta_file):
	if not os.path.exists(data_file):
		raise Exception('data file[%s] not exists' % data_file)
	if not os.path.exists(meta_file):
		raise Exception('meta file[%s] not exists' % meta_file)

	ok = True
	message = ''
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
		if ok and not bookname:
			ok = False
			message = 'meta file[%s] book field should have ch_name'
		if ok and not en_bookname:
			ok = False
			message = 'meta file[%s] book field should have en_name'
		if ok and not booktype:
			ok = False
			message = 'meta file[%s] book field should have type'
	
	if not ok:
		raise Exception(message % meta_file)
	
	bookinfo = {
		'ch_name': bookname,
		'en_name': en_bookname,
		'type': booktype
	}
	
	# check data file
	meta_all_article_id_list = []
	meta_lost_article_id_list = []
	meta_article_info_dict = {}
	for chapter in chapters:
		for article_id in chapter.get('articles', []):
			meta_all_article_id_list.append(article_id)
			meta_article_info_dict[article_id] = {
				'url': '',
				'title': ''
			}
			article_id_str = str(article_id)
			if not articles.get(article_id_str, None):
				meta_lost_article_id_list.append(article_id)	
				continue
			meta_article_info_dict[article_id]['url'] = articles[article_id_str].get('url', '')
			meta_article_info_dict[article_id]['title'] = articles[article_id_str].get('ch_name', '')

	data_all_article_id_list = []
	data_good_article_id_list = []
	with open(data_file, 'r', encoding='utf8') as f:
		lines = f.readlines()
		for line, lnum in zip(lines, range(len(lines))):
			item = json.loads(line)
			if not item.get('article_id', None):
				raise Exception('data file %s the %d line lost article_id' % (data_file, lnum+1))
			article_id = int(item['article_id'])
			data_all_article_id_list.append(article_id)
			if item.get('content', None):
				data_good_article_id_list.append(article_id)
			if meta_article_info_dict.get(article_id, None):
				title = item.get('title', None)
				url = item.get('url', None)
				if url and not meta_article_info_dict[article_id]['url']:
					meta_article_info_dict[article_id]['url'] = url
				if title and not meta_article_info_dict[article_id]['title']:
					meta_article_info_dict[article_id]['title'] = title

	# meta-all-articles = data-all-articles + articles-not-in-data-but-in-meta + meta-lost-articles
	meta_lost_article_id_set = set(meta_lost_article_id_list)
	data_good_article_id_set = set(data_good_article_id_list)
	data_all_article_id_set = set(data_all_article_id_list)
	articlesinfo = {}
	ok = True
	for article_id in meta_all_article_id_list:
		url = meta_article_info_dict[article_id]['url']
		title = meta_article_info_dict[article_id]['title']
		if article_id in data_good_article_id_set:
			# article ok
			pass
		else:
			ok = False
			message = ''
			if article_id in data_all_article_id_set:
				# article has no content field
				message = '[Data][Article][%d] has no [content] field'
			elif article_id in meta_lost_article_id_set:
				# article lost in meta file's articles field
				message = '[Meta][Article][%d] not in field [articles]'
			else:
				# article not in data file
				message = '[Data][Article][%d] not in data file'
			articlesinfo[article_id] = {
				'message': message % article_id,
				'url': url,
				'title': title
			}
	
	return [ok, bookinfo, articlesinfo]

def check(datadir):
	'''
		if meta file not exists
			data file will be pun into datadir/wet
		elif data file and meta file is ok
			will be copied into datadir/hot
		else
			will be copied into datadir/cold
		
		datadir/hot/_books.jl descript ok books' information
		datadir/cold/_report.jl descript not ok books' information
	'''
	if not os.path.exists(datadir):
		raise Exception('data directory not exists')
	hotdir = os.sep.join([datadir, 'hot'])
	colddir = os.sep.join([datadir, 'cold'])
	wetdir = os.sep.join([datadir, 'wet'])

	if os.path.exists(hotdir):
		shutil.rmtree(hotdir)
	if os.path.exists(colddir):
		shutil.rmtree(colddir)
	if os.path.exists(wetdir):
		shutil.rmtree(wetdir)
	os.mkdir(hotdir)
	os.mkdir(colddir)
	os.mkdir(wetdir)

	book_list_file = '_books.jl'
	report_file = '_report.jl'
	bfname = os.sep.join([hotdir, book_list_file])
	rfname = os.sep.join([colddir, report_file])

	meta_file_suffix = '_meta.json'
	data_file_suffix = '.jl'
	total_count = 0
	ok_count = 0
	with open(bfname, 'w', encoding='utf8') as bf, open(rfname, 'w', encoding='utf8') as rf:
		for fname in os.listdir(datadir):
			fnamefull = os.sep.join([datadir, fname])
			if os.path.isfile(fnamefull):
				if not fname.endswith(data_file_suffix):
					continue
				total_count += 1
				data_file = fnamefull
				meta_file = '.'.join(data_file.split('.')[:-1]) + '_meta.json'
				
				if not os.path.exists(meta_file):
					# lost meta file
					shutil.copy(data_file, wetdir)
					continue
				
				[ok, bookinfo, articles] = is_ok(data_file, meta_file)

				if ok:
					ok_count += 1
					shutil.copy(data_file, hotdir)
					shutil.copy(meta_file, hotdir)
					bf.write(json.dumps({
						'ch_name': bookinfo['ch_name'],
						'en_name': bookinfo['en_name'],
						'type': bookinfo['type']
					}, ensure_ascii=False))
					bf.write('\n')
				else:
					shutil.copy(data_file, colddir)
					shutil.copy(meta_file, colddir)
					rf.write(json.dumps({
						'ch_name': bookinfo['ch_name'],
						'en_name': bookinfo['en_name'],
						'articles': articles
					}, ensure_ascii=False, indent=4))
					rf.write('\n')

	return [total_count, ok_count]

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-d', '--dir', dest='dir', help='book data directory')
	(options, args) = parser.parse_args()
	if not os.path.exists(options.dir):
		raise Exception('book data directory not exists')
	
	check(options.dir)