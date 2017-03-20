# -*- coding:utf-8 -*-
import os, json

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

	def __init__(self, booktype):
		if booktype not in ['zh', 'tw']:
			raise Exception('book type not support')
		self.book_entry = _book_entry[booktype]

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

class BookMeta(object):
	def __init__(self, metaitem):
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
		#self.book['categories'] = book['categories']

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

	def get_chapters_id(self):
		return list(self.chapter_dict.keys())

	def get_chapter_meta(self, chapter_id=None):
		'''
		{id: {id, url, en_name, ch_name, articles: []}}
		'''
		return self.chapter_dict if chapter_id is None else self.chapter_dict.get(chapter_id, None)

	def get_articles_id(self):
		return list(self.article_dict.keys())

	def get_article_meta(self, article_id):
		'''
		{id: {id, url, en_name, ch_name, chapter_id}}
		'''
		return self.article_dict if article_id is None else self.article_dict.get(article_id, None)

	@staticmethod
	def create_meta_from_jsonfile(jsonfile):
		chapters = [] # standalone book has just one chapter
		articles = {}
		book = {
			'standalone': True, # create meta by data json file must be a standalone
			'en_name': '',
			'ch_name': '',
			'url': 'meta data generate by programe',
			'type': '',
			'categories': []
		}
		chapterinfo = {
			'url': '',
			'en_name': '',
			'ch_name': '',
			'id': 1,
			'articles': []
		}
		chapters.append(chapterinfo)

		with open(jsonfile, 'r', encoding='utf8') as f:
			for line in f:
				item = json.loads(line)
				article_id = int(item['article_id'])
				if not book['en_name']:
					book['en_name'] = item['en_book']
				if not book['ch_name']:
					book['ch_name'] = item['book']
				if not book['type']:
					book['type'] = item['book_type']

				chapterinfo['articles'].append(article_id)
				articles[article_id] = {
					'chapter_id': 1,
					'url': item['url'],
					'en_name': item['en_title'],
					'ch_name': item['title']
				}
		chapterinfo['articles'] = sorted(chapterinfo['articles'])
		
		return BookmetaRaw({
			'book': book,
			'chapters': chapters,
			'articles': articles
		})