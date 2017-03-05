import os, json
from .bookmeta import BookmetaRaw

class EpubConfig(object):
	_book_meta_info = {
		'tw': {
			'bookcat': '叢書名',
			'bookid': 'xxxxxxxx-xxxxxxxx',
			'author': '〔朝代〕作者名　身份',
			'publisher': '©藝雅出版社',
			'covertitle': '封面',
			'fronttitle': '版權信息',
			'contentstitle': '目錄',
			'navtitle': '目錄'
		},
		'zh': {
			'bookcat': '丛书名',
			'bookid': 'xxxxxxxx-xxxxxxxx',
			'author': '〔朝代〕作者名　身份',
			'publisher': '©艺雅出版社',
			'covertitle': '封面',
			'fronttitle': '版权信息',
			'contentstitle': '目录',
			'navtitle': '目录'
		}
	}

	_target_epub_files = {
		'coverpage': 'coverpage.xhtml',
		'frontpage': 'frontpage.xhtml',
		'contentspage': 'contents.xhtml',
		'navpage': 'nav.xhtml',
		'packagefile': 'package.opf',
		'ncxfile': 'toc.ncx',
		'maincssfile': 'main.css',
		'coverfile': 'cover.jpg',
		'mimetype': 'mimetype',
		'container': 'container.xml'
	}

	_source_epub_files = {
		'maincssfile': 'main.css',
		'coverfile': 'cover.jpg',
		'mimetype': 'mimetype',
		'container': 'container.xml'
	}

	def __init__(self, bookname, bookcname, booktype, targetdir, sourcedir, templatedir, jsonfile, metafile):		
		# check directories and files
		targetdir = targetdir.rstrip('/')
		sourcedir = sourcedir.rstrip('/')
		templatedir = templatedir.rstrip('/')
		if not os.path.exists(targetdir):
			raise Exception('epub target directory not existed: %s' % targetdir)
		if not os.path.exists(sourcedir):
			raise Exception('epub source directory not existed: %s' % sourcedir)
		if not os.path.exists(templatedir):
			raise Exception('epub template directory not existed: %s' % templatedir)
		if not os.path.exists(jsonfile):
			raise Exception('epub json data not existed: %s' % jsonfile)

		self.targetdir = targetdir
		self.sourcedir = sourcedir
		self.templatedir = templatedir
		self.jsonfile = jsonfile # data for making ebook
		self.metafile = metafile # meta data about the above data

		# this book's basic information
		self.bookname = bookname
		self.bookcname = bookcname
		self.booktype = booktype if booktype in ['tw', 'zh'] else 'tw'
		# book meta information for all books
		self.book_meta_info = self._book_meta_info['tw'] if self.booktype == 'tw' else self._book_meta_info['zh']

		# chapter and article meta information
		meta = None
		if os.path.exists(self.metafile):
			with open(self.metafile, 'r', encoding='utf8') as f:
				item = json.loads(f.read())
				try:
					meta = BookmetaRaw(item)
				except Exception as e:
					raise e
					#raise Exception('meta file [%s] has errors' % self.metafile)
		else:
			# meta file not exists, book is standalone and
			# meta information generate from data json file
			meta = BookmetaRaw.create_meta_from_jsonfile(self.jsonfile)
		if not meta:
			raise Exception('there is some wrong')
		
		self.standalone = meta.get_standalone()
		self.chapter_dict = meta.get_chapter_dict()
		self.article_dict = meta.get_article_dict()

		# source epub directory
		self.source_epub_dirs = {
			'root': sourcedir,
			'epub': os.sep.join([sourcedir, 'EPUB']),
			'metainf': os.sep.join([sourcedir, 'META-INF']),
			'xhtml': os.sep.join([sourcedir, 'EPUB', 'xhtml']),
			'img': os.sep.join([sourcedir, 'EPUB', 'img']),
			'css': os.sep.join([sourcedir, 'EPUB', 'css']),
			'js': os.sep.join([sourcedir, 'EPUB','js'])
		}

		# source epub files
		self.source_epub_files = {}
		for k,v in self._source_epub_files.items():
			if k == 'maincssfile':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['css'], v])
			elif k == 'coverfile':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['img'], v])
			elif k == 'mimetype':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['root'], v])
			elif k == 'container':
				self.source_epub_files[k] = os.sep.join([self.source_epub_dirs['metainf'], v])
			else:
				raise Exception('unknow source epub file')

		# target epub directory
		self.target_epub_dirs = {
			'root': os.sep.join([targetdir, bookname]),
			'epub': os.sep.join([targetdir, bookname,'EPUB']),
			'metainf': os.sep.join([targetdir, bookname,'META-INF']),
			'xhtml': os.sep.join([targetdir, bookname,'EPUB','xhtml']),
			'img': os.sep.join([targetdir, bookname,'EPUB','img']),
			'css': os.sep.join([targetdir, bookname,'EPUB','css']),
			'js': os.sep.join([targetdir, bookname,'EPUB','js'])
		}

		# target epub files
		self.target_epub_files = {}
		for k,v in self._target_epub_files.items():
			if v.endswith('.xhtml'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['xhtml'], v])
			elif v.endswith('.css'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['css'], v])
			elif v.endswith('.js'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['js'], v])
			elif v.endswith('.jpg') or v.endswith('.png'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['img'], v])
			elif v.endswith('.opf') or v.endswith('.ncx'):
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['epub'], v])
			elif k == 'container':
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['metainf'], v])
			elif k == 'mimetype':
				self.target_epub_files[k] = os.sep.join([self.target_epub_dirs['root'], v])
			else:
				raise Exception('unknow target epub file type')

	def get_bookname(self):
		return self.bookname

	def get_bookcname(self):
		return self.bookcname

	def get_booktype(self):
		return self.booktype

	def get_epub_targetdir(self):
		return self.targetdir

	def get_epub_sourcedir(self):
		return self.sourcedir

	def get_book_meta(self, name):
		if not name in self.book_meta_info:
			raise Exception('{} not in book meta information'.format(name))
		return self.book_meta_info[name]

	def get_epub_templatedir(self):
		return self.templatedir

	def get_target_epub_dirs(self):
		return self.target_epub_dirs

	def get_target_epub_dirname(self, name):
		if not name in self.target_epub_dirs:
			raise Exception('{} epub directory not existed'.format(name))
		return self.target_epub_dirs[name]

	def get_target_epub_files(self, full=True):
		if full:
			return self.target_epub_files
		else:
			return self._target_epub_files

	def get_target_epub_filename(self, name, full=True):
		if full:
			files = self.target_epub_files
		else:
			files = self._target_epub_files

		if not name in files:
				raise Exception('{} epub file not existed'.format(name))
		return files[name]

	def get_source_epub_files(self, full=True):
		if full:
			return self.source_epub_files
		else:
			return self._source_epub_files

	def get_source_epub_filename(self, name, full=True):
		if full:
			files = self.source_epub_files
		else:
			files = self._source_epub_files

		if not name in files:
			raise Exception('{} epub source filename not existed'.format(name))
		return files[name]

	def get_source_data_filename(self):
		return self.jsonfile

	def get_metafile_filename(self):
		return self.metafile

	def is_standalone_book(self):
		return self.standalone

	def get_chapter_id_list(self):
		return sorted(self.chapter_dict.keys())

	def get_prefix_of_article_id_in_contents(self):
		return 'a'

	def get_prefix_of_chapter_id_in_contents(self):
		return 'c'

	def get_article_id_list(self):
		return sorted(self.article_dict.keys())

	def get_chapter_id(self, article_id):
		article_id = int(article_id)
		return self.article_dict.get(article_id, {'chapter_id': None})['chapter_id']

	def get_articles_id(self, chapter_id):
		chapter_id = int(chapter_id)
		articles = self.chapter_dict.get(chapter_id, {'articles': []})['articles']
		return sorted(articles)

	def get_chapter(self, chapter_id):
		chapter_id = int(chapter_id)
		return self.chapter_dict.get(chapter_id, {})

	def get_article(self, article_id):
		article_id = int(article_id)
		return self.article_dict.get(article_id, {})