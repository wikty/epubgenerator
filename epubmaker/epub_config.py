import os, json
from .models import BookEntry
from .models import BookMeta
from .models import Chapter
from .models import Article
from .models import Contents

class EpubConfig(object):

	_target_epub_files = {
		'cover': 'coverpage.xhtml',
		'front': 'frontpage.xhtml',
		'contents': 'contents.xhtml',
		'nav': 'nav.xhtml',
		'package': 'package.opf',
		'ncx': 'toc.ncx',
		'maincss': 'main.css',
		'coverimg': 'cover.jpg',
		'mimetype': 'mimetype',
		'container': 'container.xml'
	}

	def __init__(self, 
		bookname, 
		bookcname, 
		booktype, 
		targetdir,  
		jsonfile, 
		metafile='', 
		chapteralone=False):
		currentdir = os.path.dirname(os.path.abspath(__file__))
		sourcedir = os.sep.join([currentdir, 'epub']) # epub source in current directory ./epub
		templatedir = os.sep.join([currentdir, 'templates']) # template directory is ./templates
		if not os.path.exists(sourcedir):
			raise Exception('epub source directory not existed: %s' % sourcedir)
		if not os.path.exists(templatedir):
			raise Exception('epub template directory not existed: %s' % templatedir)
		if not os.path.exists(jsonfile):
			raise Exception('epub json data not existed: %s' % jsonfile)

		self.jsonfile = jsonfile # data for building ebook
		self.metafile = metafile # meta data about the building data
		self.standalone = True # if True book has no chapter
		self.chapteralone = chapteralone # whether chapter has a single page for itself
		# book basic information
		self.bookname = bookname
		self.bookcname = bookcname
		self.booktype = booktype if booktype in ['tw', 'zh'] else 'tw'
		# book entry information
		self.book_entry = None
		# book metadata
		self.book_meta = None
		# book data
		self.chapters = {}
		self.articles = {}
		# source and target
		self.targetdir = targetdir.rstrip('/').rstrip('\\')
		self.sourcedir = sourcedir.rstrip('/').rstrip('\\')
		self.templatedir = templatedir.rstrip('/').rstrip('\\')
		# source epub directories and files
		self.source_epub_dirs = {
			'root': sourcedir,
			'epub': os.sep.join([sourcedir, 'EPUB']),
			'metainf': os.sep.join([sourcedir, 'META-INF']),
			'xhtml': os.sep.join([sourcedir, 'EPUB', 'xhtml']),
			'img': os.sep.join([sourcedir, 'EPUB', 'img']),
			'css': os.sep.join([sourcedir, 'EPUB', 'css']),
			'js': os.sep.join([sourcedir, 'EPUB','js'])
		}
		# source files will be copied to target same key location
		self.source_epub_files = {
			'maincss': os.sep.join([self.source_epub_dirs['css'], 'main.css']),
			'coverimg': os.sep.join([self.source_epub_dirs['img'], 'cover.jpg']),
			'mimetype': os.sep.join([self.source_epub_dirs['root'], 'mimetype']),
			'container': os.sep.join([self.source_epub_dirs['metainf'], 'container.xml'])
		}
		# target epub directories and files
		self.target_epub_dirs = {
			'root': targetdir,
			'epub': os.sep.join([targetdir, 'EPUB']),
			'metainf': os.sep.join([targetdir, 'META-INF']),
			'xhtml': os.sep.join([targetdir, 'EPUB','xhtml']),
			'img': os.sep.join([targetdir, 'EPUB','img']),
			'css': os.sep.join([targetdir, 'EPUB','css']),
			'js': os.sep.join([targetdir, 'EPUB','js'])
		}
		self.target_epub_files = {
			'maincss': os.sep.join([self.target_epub_dirs['css'], self._target_epub_files['maincss']]),
			'coverimg': os.sep.join([self.target_epub_dirs['img'], self._target_epub_files['coverimg']]),
			'mimetype': os.sep.join([self.target_epub_dirs['root'], self._target_epub_files['mimetype']]),
			'container': os.sep.join([self.target_epub_dirs['metainf'], self._target_epub_files['container']]),
			'package': os.sep.join([self.target_epub_dirs['epub'], self._target_epub_files['package']]),
			'ncx': os.sep.join([self.target_epub_dirs['epub'], self._target_epub_files['ncx']]),
			'cover': os.sep.join([self.target_epub_dirs['xhtml'], self._target_epub_files['cover']]),
			'front': os.sep.join([self.target_epub_dirs['xhtml'], self._target_epub_files['front']]),
			'contents': os.sep.join([self.target_epub_dirs['xhtml'], self._target_epub_files['contents']]),
			'nav': os.sep.join([self.target_epub_dirs['xhtml'], self._target_epub_files['nav']]),
		}
		self.setup()
		
	def setup(self):
		# load book entry information
		self.book_entry = BookEntry(self.booktype)
		
		# load book meta information
		try:
			if os.path.exists(self.metafile):
				self.book_meta = BookMeta(self.metafile)
			else:
				# meta file not exists, book is standalone and
				# meta information generate from data json file
				self.book_meta = BookMeta.create_meta_from_jsonfile(
					self.jsonfile, 
					self.bookname, 
					self.bookcname, 
					self.booktype)
			self.standalone = self.book_meta.get_standalone()
		except Exception as e:
			raise e
		
		# load book data
		self.articles = Article.create_articles_from_jsonfile(self.jsonfile, self.book_meta.get_article_meta()) # id: article
		self.chapters = Chapter.create_chapters_from_meta(self.book_meta.get_chapter_meta()) # id: chapter
		self.contents = Contents(self.articles, self.chapters, self.standalone, self.chapteralone, self.booktype)
	
	def get_book_entry(self, name):
		entry = {
			'bookname': self.bookname,
			'bookcname': self.bookcname,
			'booktype': self.booktype,
			'bookid': self.book_entry.get_book_id(),
			'bookcat': self.book_entry.get_book_category(),
			'author': self.book_entry.get_book_author(),
			'publisher': self.book_entry.get_book_publisher(),
			'covertitle': self.book_entry.get_book_cover_title(),
			'contentstitle': self.book_entry.get_book_contents_title(),
			'navtitle': self.book_entry.get_book_nav_title(),
			'fronttitle': self.book_entry.get_book_front_title(),
			'publish_year': self.book_entry.get_book_publish_year(),
			'modify_year': self.book_entry.get_book_modify_year(),
			'modify_month': self.book_entry.get_book_modify_month(),
			'modify_day': self.book_entry.get_book_modify_day(),
		}
		
		return entry.get(name, '')

	def get_target_epub_dirs(self, name=None):
		if name is None:
			return self.target_epub_dirs
		return self.target_epub_dirs.get(name, None)

	def get_target_epub_files(self, name=None, full=True):
		if full:
			files = self.target_epub_files
		else:
			files = self._target_epub_files
		return files.get(name, None) if name else files

	def get_source_epub_files(self, name=None):
		return self.source_epub_files.get(name, None) if name else self.source_epub_files

	def get_prefix_of_article_id_in_contents(self):
		return 'a'

	def get_prefix_of_chapter_id_in_contents(self):
		return 'c'

	# def get_chapter_id_list(self):
	# 	return sorted(self.chapters.keys())

	# def get_article_id_list(self):
	# 	return sorted(self.articles.keys())

	def is_standalone(self):
		return self.standalone

	def is_chapteralone(self):
		return self.chapteralone

	def get_epub_templatedir(self):
		return self.templatedir

	# def get_chapter(self, chapter_id):
	# 	chapter_id = int(chapter_id)
	# 	return self.chapters.get(chapter_id, None)

	# def get_article(self, article_id):
	# 	article_id = int(article_id)
	# 	return self.articles.get(article_id, None)

	def get_contents(self):
		'''
		[[id, title, filename, is_chapter, is_page]]
		'''
		return self.contents.serialize()