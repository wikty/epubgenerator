# -*- coding:utf-8 -*-
import os, json
from .utils import chapterid2filename, articleid2filename

class Books(object):
	def __init__(self, books_filename):
		if not os.path.exists(books_filename):
			raise Exception('books filename %s not exists' % books_filename)
		self.books = []
		with open(books_filename, 'r', encoding='utf-8') as f:
			for line in f:
				item = json.loads(line)
				self.books.append([item['en_name'], item['ch_name'], item['type']])

	def get_books(self):
		'''
		[[en_name, ch_name, type],...]
		'''
		return self.books

	def get_book_count(self):
		return len(self.books)

class Chapter(object):
	def __init__(self, chapter):
		if 'ch_name' not in chapter or not chapter['ch_name']:
			raise Exception('chapter must be have a ch_name field and not empty')
		if 'id' not in chapter or not chapter['id']:
			raise Exception('chapter must be have a id field')
		self.id = int(chapter['id'])
		self.title = chapter.get('ch_name', '')
		self.en_title = chapter.get('en_name', '')
		self.articles = chapter.get('articles', [])
	
	def get_id(self):
		return self.id

	def get_title(self):
		return self.title
	
	def get_en_title(self):
		return self.en_title
	
	def get_articles(self):
		return self.articles

	@staticmethod
	def create_chapters_from_meta(chapter_dict):
		chapters = {}
		for chapter_id in chapter_dict.keys():
			chapters[chapter_id] = Chapter(chapter_dict[chapter_id])
		return chapters

class Article(object):
	def __init__(self, article):
		if 'article_id' not in article:
			print(article)
			raise Exception('article raw lost article id')
		self.id = int(article['article_id']) # required
		self.book = article.get('book', '')
		self.en_book = article.get('en_book', '')
		self.book_type = article.get('book_type', 'tw')
		self.title = article.get('title', '')
		self.en_title = article.get('en_title', '')
		self.content = article.get('content', [])
		self.comment = article.get('comment', [])
		self._content = ''
		self._comment = ''

	def get_id(self):
		return self.id

	def get_book_type(self):
		return self.book_type

	def get_title(self):
		return self.title

	def get_en_title(self):
		return self.en_title

	def get_content_body(self):
		if not self._content:
			self._content = '\n'.join(['<p>' + l + '</p>'  for l in self.content])
		return self._content

	def get_content_head(self):
		return '\n'

	def get_content_foot(self):
		return '\n'

	def get_content(self):
		content_body = self.get_content_body()
		if not content_body:
			return ''
		
		return '\n'.join([
			self.get_content_head(),
			content_body,
			self.get_content_foot()
		])

	def get_comment_body(self):
		if not self._comment:
			self._comment = '\n'.join(['<p class="footnote">' + l + '</p>' for l in self.comment])
		return self._comment

	def get_comment_head(self):
		return '\n<hr/>\n<p class="footnote">【注释】</p>\n'

	def get_comment_foot(self):
		return '\n'

	def get_comment(self):
		comment_body = self.get_comment_body()
		if not comment_body:
			return ''
		return '\n'.join([
			self.get_comment_head(),
			comment_body,
			self.get_comment_foot()
		])

	def get_body(self):
		return '\n'.join([
			self.get_content(),
			self.get_comment()
		])

	@staticmethod
	def create_articles_from_jsonfile(jsonfile, article_dict=None):
		if not os.path.exists(jsonfile):
			raise Exception('json data file not exists')
		articles = {}
		with open(jsonfile, 'r', encoding='utf8') as f:
			for line in f:
				article = Article(json.loads(line))
				articles[article.get_id()] = article
		if article_dict:
			# check jsonfile data
			if set(article_dict.keys()) != set(articles.keys()):
				raise Exception('json file lost article')
		return articles

class BookEntry(object):
	_book_entry = {
		'tw': {
			'bookcat': '叢書名',
			'bookid': 'xxxxxxxx-xxxxxxxx',
			'author': '〔朝代〕作者名　身份',
			'publisher': '©藝雅出版社',
			'covertitle': '封面',
			'fronttitle': '版權信息',
			'contentstitle': '目錄',
			'navtitle': '目錄',
			'publish_year': 'xxxx',
			'modify_year': 'xxxx',
			'modify_month': 'xx',
			'modify_day': 'xx'
		},
		'zh': {
			'bookcat': '丛书名',
			'bookid': 'xxxxxxxx-xxxxxxxx',
			'author': '〔朝代〕作者名　身份',
			'publisher': '©艺雅出版社',
			'covertitle': '封面',
			'fronttitle': '版权信息',
			'contentstitle': '目录',
			'navtitle': '目录',
			'publish_year': 'xxxx',
			'modify_year': 'xxxx',
			'modify_month': 'xx',
			'modify_day': 'xx'
		}
	}

	def __init__(self, booktype):
		if booktype not in ['zh', 'tw']:
			raise Exception('book type not support')
		self.book_entry = self._book_entry[booktype]

	def get_book_category(self):
		return self.book_entry['bookcat']

	def get_book_id(self):
		return self.book_entry['bookid']

	def get_book_author(self):
		return self.book_entry['author']

	def get_book_publisher(self):
		return self.book_entry['publisher']

	def get_book_cover_title(self):
		return self.book_entry['covertitle']

	def get_book_front_title(self):
		return self.book_entry['fronttitle']

	def get_book_contents_title(self):
		return self.book_entry['contentstitle']

	def get_book_nav_title(self):
		return self.book_entry['navtitle']

	def get_book_publish_year(self):
		return self.book_entry['publish_year']

	def get_book_modify_year(self):
		return self.book_entry['modify_year']

	def get_book_modify_month(self):
		return self.book_entry['modify_month']

	def get_book_modify_day(self):
		return self.book_entry['modify_day']

class BookMeta(object):
	def __init__(self, metafile):
		if not os.path.exists(metafile):
			raise Exception('meta file not exits, you may want auto-generate it from json data file')
		metaitem = {}
		with open(metafile, 'r', encoding='utf8') as f:
			metaitem = json.loads(f.read())
		if 'book' not in metaitem:
			raise Exception('meta data must have book field')
		if 'chapters' not in metaitem:
			raise Exception('meta data must have chapters field')
		if 'articles' not in metaitem:
			raise Exception('meta data must have articles field')

		self.book = {}
		book = metaitem['book']
		self.book['url'] = book['url']
		self.book['standalone'] = book['standalone']
		self.book['type'] = book['type']
		self.book['en_name'] = book['en_name']
		self.book['ch_name'] = book['ch_name']
		self.book['categories'] = book['categories']

		self.chapter_dict = {}
		for chapter in metaitem['chapters']:
			self.chapter_dict[chapter['id']] = {
				'id': chapter['id'],
				'url': chapter['url'],
				'en_name': chapter['en_name'],
				'ch_name': chapter['ch_name'],
				'articles': chapter['articles'], # article id list
			}

		self.article_dict = {}
		for article_id, article in metaitem['articles'].items():
			article_id = int(article_id)
			self.article_dict[article_id] = {
				'id': article_id,
				'url': article['url'],
				'en_name': article['en_name'],
				'ch_name': article['ch_name'],
				'chapter_id': article['chapter_id']
			}

	def get_standalone(self):
		return self.book['standalone']

	# def get_chapters_id(self):
	# 	return sorted(self.chapter_dict.keys())

	def get_chapter_meta(self, chapter_id=None):
		'''
		{id: {id, url, en_name, ch_name, articles: []}}
		'''
		return self.chapter_dict if chapter_id is None else self.chapter_dict.get(chapter_id, None)

	# def get_articles_id(self):
	# 	return sorted(self.article_dict.keys())

	def get_article_meta(self, article_id=None):
		'''
		{id: {id, url, en_name, ch_name, chapter_id}}
		'''
		return self.article_dict if article_id is None else self.article_dict.get(article_id, None)

	@staticmethod
	def create_meta_from_jsonfile(jsonfile, en_name, ch_name, booktype, url=''):
		'''
		auto-generate metafile for standalone book
		'''
		if not os.path.exits(jsonfile):
			raise Exception('json data file not exists')
		if not en_name:
			raise Exception('you must provide en_name for auto-generating meta data')
		if not ch_name:
			raise Exception('you must provide ch_name for auto-generating meta data')
		if not booktype:
			raise Exception('you must provide booktype for auto-generating meta data')
		book = {
			'standalone': True, # create meta by data json file must be a standalone book
			'en_name': en_name,
			'ch_name': ch_name,
			'url': 'meta data auto-generate' if not url else url,
			'type': booktype,
			'categories': []
		}
		# standalone book has only one chapter
		chapters = [{
			'url': '',
			'en_name': '',
			'ch_name': '',
			'id': 1,
			'articles': []
		}]
		articles = {}
		with open(jsonfile, 'r', encoding='utf8') as f:
			for line in f:
				item = json.loads(line)
				article_id = int(item['article_id'])
				chapters[0]['articles'].append(article_id)
				articles[article_id] = {
					'chapter_id': 1,
					'url': item['url'],
					'en_name': item['en_title'],
					'ch_name': item['title']
				}
		chapters[0]['articles'] = sorted(chapters[0]['articles'])		
		return BookmetaRaw({
			'book': book,
			'chapters': chapters,
			'articles': articles
		})

class ContentsItem(object):
	def __init__(self, item_id, title, body, is_chapter, is_page, achor, extra=[]):
		self.id = item_id
		self.title = title
		self.body = body
		self.chapter = is_chapter
		self.page = is_page
		self.achor = achor
		self.extra = extra

	def get_id(self):
		return self.id

	def get_title(self):
		return self.title

	def get_body(self):
		return self.body

	def is_chapter(self):
		return self.chapter

	def is_page(self):
		return self.page

	def get_achor(self):
		return self.achor

	def get_extra(self):
		return self.extra

class Contents(object):
	def __init__(self, articles, chapters, standalone, chapteralone, booktype):
		self.articles = articles
		self.chapters = chapters
		self.standalone = standalone
		self.chapteralone = chapteralone
		self.booktype = booktype
		self.contents = []

	def serialize(self):
		if self.contents:
			return self.contents
		for chapter_id in sorted(self.chapters.keys()):
			chapter = self.chapters[chapter_id]
			chapter_title = chapter.get_title()
			article_id_list = sorted(chapter.get_articles())
			chapterinfo = []
			if (not self.standalone):
				if self.chapteralone:
					self.contents.append(ContentsItem(
						chapter_id, 
						chapter_title,
						None,
						True,
						True, 
						chapterid2filename(chapter_id, self.booktype)))
				else:
					article = self.articles[article_id_list[0]]
					self.contents.append(ContentsItem(
						chapter_id,
						chapter_title,
						None,
						True,
						False,
						articleid2filename(article.get_id(), self.booktype)))
					chapterinfo = [chapter_id, chapter_title]
			for article_id in article_id_list:
				article = self.articles[article_id]
				extra = []
				if chapterinfo and (article_id==article_id_list[0]):
					extra = chapterinfo
				self.contents.append(ContentsItem(
					article_id,
					article.get_title(),
					article.get_body(),
					False,
					True,
					articleid2filename(article_id, self.booktype),
					extra))
		return self.contents