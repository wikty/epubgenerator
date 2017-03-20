import os, json, shutil, errno
from .models import BookEntry
from .models import BookMeta
from .models import Chapter
from .models import Article
from .utils import chapterid2filename, articleid2filename

class EpubConfig(object):

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

	def __init__(self, 
		bookname, 
		bookcname, 
		booktype, 
		targetdir, 
		sourcedir, 
		templatedir, 
		jsonfile, 
		metafile, 
		chapteralone):	
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
		# directories&files
		self.targetdir = targetdir
		self.sourcedir = sourcedir
		self.templatedir = templatedir
		self.jsonfile = jsonfile # data for building ebook
		self.metafile = metafile # meta data about the building data
		# whether chapter has a single page for introduction itself
		self.chapteralone = chapteralone
		# this book's basic information
		self.bookname = bookname
		self.bookcname = bookcname
		self.booktype = booktype if booktype in ['tw', 'zh'] else 'tw'
		# book entry information for all books
		self.book_entry = None
		# book meta information
		self.book_meta = None
		# book data holder
		self.chapters = {}
		self.articles = {}
		# source epub directory
		self.source_epub_dirs = {}
		# source epub files
		self.source_epub_files = {}
		# target epub directory
		self.target_epub_dirs = {}
		# target epub files
		self.target_epub_files = {}
		self.setup()

	def set_source_dirs_files(self, sourcedir):
		sourcedir = self.sourcedir
		self.source_epub_dirs = {
			'root': sourcedir,
			'epub': os.sep.join([sourcedir, 'EPUB']),
			'metainf': os.sep.join([sourcedir, 'META-INF']),
			'xhtml': os.sep.join([sourcedir, 'EPUB', 'xhtml']),
			'img': os.sep.join([sourcedir, 'EPUB', 'img']),
			'css': os.sep.join([sourcedir, 'EPUB', 'css']),
			'js': os.sep.join([sourcedir, 'EPUB','js'])
		}

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
				pass

	def set_target_dirs_files(self):
		targetdir = self.targetdir
		bookname = self.bookname
		self.target_epub_dirs = {
			'root': os.sep.join([targetdir, bookname]),
			'epub': os.sep.join([targetdir, bookname,'EPUB']),
			'metainf': os.sep.join([targetdir, bookname,'META-INF']),
			'xhtml': os.sep.join([targetdir, bookname,'EPUB','xhtml']),
			'img': os.sep.join([targetdir, bookname,'EPUB','img']),
			'css': os.sep.join([targetdir, bookname,'EPUB','css']),
			'js': os.sep.join([targetdir, bookname,'EPUB','js'])
		}

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
				pass

	def create_target_dirs_files(self):
		# make epub directories and copy resource epub files
		target_epub_dirs = self.get_target_epub_dirs()
		target_epub_files = self.get_target_epub_files()
		source_epub_files = self.get_source_epub_files()
		# make epub resource directories
		for dirname in target_epub_dirs.values():
			try:
				os.makedirs(dirname)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise
		for k, filename in source_epub_files.items():
			shutil.copy(filename, target_epub_files[k])

	def setup(self):
		# config target&source epub directories and files
		self.set_target_dirs_files()
		self.set_source_dirs_files()
		self.create_target_dirs_files()
		# load book entry information
		self.book_entry = BookEntry(self.booktype)
		# load book meta information
		meta = None
		if os.path.exists(self.metafile):
			with open(self.metafile, 'r', encoding='utf8') as f:
				item = json.loads(f.read())
				try:
					meta = BookMeta(item)
				except Exception as e:
					raise e
					#raise Exception('meta file [%s] has errors' % self.metafile)
		else:
			# meta file not exists, book is standalone and
			# meta information generate from data json file
			meta = BookMeta.create_meta_from_jsonfile(self.jsonfile)
		if not meta:
			raise Exception('there is some wrong with %s' % self.metafile)
		self.book_meta = meta
		
		# load book data
		for chapter_id in self.book_meta.get_chapters_id():
			chapter = Chapter(self.book_meta.get_chapter(chapter_id))
			self.chapters[chapter_id] = chapter
		
		with open(self.jsonfile, 'r', encoding='utf8') as f:
			for line in f:
				article = Article(json.loads(line))
				self.articles[article.get_id()] = article

	def get_bookname(self):
		return self.bookname

	def get_bookcname(self):
		return self.bookcname

	def get_booktype(self):
		return self.booktype

	def get_book_entry(self, name):
		result = ''
		if name == 'bookid':
			result = self.book_entry.get_book_id()
		elif name == 'bookcat':
			result = self.book_entry.get_book_category()
		elif name == 'author':
			result = self.book_entry.get_book_author()
		elif name == 'publisher':
			result = self.book_entry.get_book_publisher()
		elif name == 'covertitle':
			result = self.book_entry.get_book_cover_title()
		elif name == 'contentstitle':
			result = self.book_entry.get_book_contents_title()
		elif name == 'navtitle':
			result = self.book_entry.get_book_nav_title()
		elif name == 'fronttitle':
			result = self.book_entry.get_book_front_title()
		return result

	def get_target_epub_dirs(self, name=None):
		if name is None:
			return self.target_epub_dirs
		return self.target_epub_dirs.get(name, None)

	def get_target_epub_files(self, name, full=True):
		if full:
			files = self.target_epub_files
		else:
			files = self._target_epub_files
		return files.get(name, None)

	def get_source_epub_dirs(self, name=None):
		if name is None:
			return self.source_epub_dirs
		return self.source_epub_dirs.get(name, None)

	def get_source_epub_files(self, name, full=True):
		if full:
			files = self._source_epub_files
		else:
			files = self.source_epub_files
		return files.get(name)

	def get_prefix_of_article_id_in_contents(self):
		return 'a'

	def get_prefix_of_chapter_id_in_contents(self):
		return 'c'

	def get_chapter_id_list(self):
		return sorted(self.chapters.keys())

	def get_article_id_list(self):
		return sorted(self.articles.keys())

	def get_has_multiple_chapters(self):
		return self.book_meta.get_standalone()

	def get_has_chapter_page(self):
		return self.chapteralone

	def get_epub_targetdir(self):
		return self.targetdir

	def get_epub_sourcedir(self):
		return self.sourcedir

	def get_epub_templatedir(self):
		return self.templatedir

	def get_chapter(self, chapter_id):
		chapter_id = int(chapter_id)
		return self.chapters.get(chapter_id, None)

	def get_article(self, article_id):
		article_id = int(article_id)
		return self.articles.get(article_id, None)

	def get_contents(self):
		pass