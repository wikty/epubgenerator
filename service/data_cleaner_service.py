import os, json

from models import Books

def clean_article_title(title):
	return '　'.join(title.split())

def clean_article_content(content):
	l = []
	wc = 0
	for p in content:
		p = p.strip('\n')
		if not p:
			continue
		wc += len(p)
		l.append(p)
	return (l, wc)


def run(source_dir, target_dir, books_file, sitename, bookformat):
	if not os.path.exists(source_dir):
		raise Exception('source directory not exists: %s' % source_dir)
	if not os.path.exists(target_dir):
		raise Exception('target directory not exists: %s' % target_dir)
	if not os.path.exists(books_file):
		raise Exception('books file not exists: %s' % books_file)
	
	bookinfo = {}
	books = Books()
	for bk in Books.create_from_file(books_file).get_books():
		en_name = bk.get_en_name()
		if en_name in bookinfo:
			raise Exception('book ch_name duplicate: %s' % en_name)
		if not bk.get_filename():
			bk.set_filename(en_name+'.jl')
		bk.set_sitename(sitename)
		bk.set_format(bookformat)
		bookinfo[en_name] = bk

	total_count = 0
	whitelist = set(['books.jl'])
	for fname in os.listdir(source_dir):
		if fname in whitelist:
			continue
		if fname.endswith('.jl'):
			source_file = os.sep.join([source_dir, fname])
			target_file = os.sep.join([target_dir, fname])
			article_count = 0
			word_count = 0
			bookname = os.path.splitext(fname)[0]
			category = ''
			sub_category = ''
			with open(source_file, 'r', encoding='utf8') as rf, open(target_file, 'w', encoding='utf8') as wf:
				for line in rf:
					line = line.strip()
					if not line:
						continue
					article = json.loads(line)
					article['title'] = clean_article_title(article['title'])
					article['content'], count = clean_article_content(article['content'])
					wf.write(json.dumps(article, ensure_ascii=False)+'\n')
					article_count += 1
					word_count += count
					if not category:
						category = article.get('category', '')
					if not sub_category:
						sub_category = article.get('sub_category', '')
			if not bookname:
				raise Exception('data json has no book field')
			if bookname not in bookinfo:
				raise Exception('books file has no [%s]' % bookname)
			bk = bookinfo[bookname]
			bk.set_category(category)
			bk.set_sub_category(sub_category)
			bk.set_articlecount(article_count)
			bk.set_wordcount(word_count)
			books.add_book(bk)
		total_count += 1

	books.dump_to_file(os.sep.join([target_dir, 'books.jl']))
	return total_count