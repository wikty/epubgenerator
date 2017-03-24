import os

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
		self.chapteralone = chapteralone # whether chapter has a single page for itself
		# book basic information
		self.bookname = bookname
		self.bookcname = bookcname
		self.booktype = booktype if booktype in ['tw', 'zh'] else 'tw'
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

	def get_bookname(self):
		return self.bookname

	def get_bookcname(self):
		return self.bookcname

	def get_booktype(self):
		return self.booktype

	def get_jsonfile(self):
		return self.jsonfile

	def get_metafile(self):
		return self.metafile

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

	def is_chapteralone(self):
		return self.chapteralone

	def get_epub_templatedir(self):
		return self.templatedir