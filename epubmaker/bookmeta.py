import json

class BookmetaRaw(object):
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

	def get_chapter_dict(self):
		return self.chapter_dict

	def get_article_dict(self):
		return self.article_dict

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