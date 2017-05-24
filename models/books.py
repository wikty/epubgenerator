import os, json

class BooksItem(object):

	def __init__(self, fields={}):
		if not isinstance(fields, dict):
			raise Exception('fields must be a dict')
		self.fields = BooksItem.get_default_fields()
		self.fields.update(fields)
		if not self.fields['ch_name']:
			raise Exception('books item must has ch_name')
		if not (self.fields['en_name'] or self.fields['filename']):
			raise Exception('books item must has either en_name or filename')

	@classmethod
	def get_default_fields(cls):
		return {
			'url': '',
			'ch_name': '',
			'en_name': '',
			'filename': '',
			'category': '',
			'sub_category': '',
			'sitename': '',
			'type': '',
			'format': '',
			'images': [],
			'wordcount': 0,
			'articlecount': 0
		}

	@classmethod
	def create_from_json(cls, s):
		if (not isinstance(s, str)) or (not s):
			return None
		item = json.loads(s)
		return BooksItem(item)

	def dump_as_dict(self):
		d = {}
		for fieldname in self.fields.keys():
			d[fieldname] = self.get_field(fieldname)
		return d

	def dump_as_json(self, with_newline=False):
		s = json.dumps(self.dump_as_dict(), ensure_ascii=False)
		if with_newline:
			s += '\n'
		return s

	def get_field(self, fieldname):
		try:
			value = getattr(self, 'get_{}'.format(fieldname))()
		except AttributeError as e:
			value = None

		return value

	def get_url(self):
		return self.fields['url']

	def set_url(self, url):
		self.fields['url'] = url

	def get_ch_name(self):
		return self.fields['ch_name']

	def set_ch_name(self, ch_name):
		self.fields['ch_name'] = ch_name

	def get_en_name(self):
		return self.fields['en_name']

	def set_en_name(self, en_name):
		self.fields['en_name'] = en_name

	def get_filename(self):
		return self.fields['filename']

	def set_filename(self, filename):
		self.fields['filename'] = filename

	def get_type(self):
		return self.fields['type']

	def set_type(self, type):
		self.fields['type'] = type

	def get_format(self):
		return self.fields['format']

	def set_format(self, format):
		self.fields['format'] = format

	def get_category(self):
		return self.fields['category']

	def set_category(self, category):
		self.fields['category'] = category

	def get_sub_category(self):
		return self.fields['sub_category']

	def set_sub_category(self, sub_category):
		self.fields['sub_category'] = sub_category

	def get_sitename(self):
		return self.fields['sitename']

	def set_sitename(self, sitename):
		self.fields['sitename'] = sitename

	def get_images(self):
		return self.fields['images']

	def set_images(self, images):
		self.fields['images'] = images

	def get_articlecount(self):
		return self.fields['articlecount']

	def set_articlecount(self, count):
		self.fields['articlecount'] = count

	def get_wordcount(self):
		return self.fields['wordcount']

	def set_wordcount(self, count):
		self.fields['wordcount'] = count
	

class Books(object):

	def __init__(self, books=[]):
		self.books = books

	@classmethod
	def create_from_file(self, filename):
		if not os.path.exists(filename):
			raise Exception('books filename [%s] not exists' % filename)
		books = []
		with open(filename, 'r', encoding='utf8') as f:
			for line in f:
				line = line.strip()
				if not line:
					continue
				books.append(BooksItem.create_from_json(line))
		return Books(books)

	def add_book(self, book):
		if not isinstance(book, BooksItem):
			raise Exception('book must be a BooksItem object')
		self.books.append(book)
	
	def get_books(self):
		return self.books

	def count(self):
		return len(self.books)

	def dump_to_file(self, filename):
		if os.path.exists(filename):
			raise Exception('file [%s] already existed' % filename)
		with open(filename, 'w', encoding='utf8') as f:
			for bk in self.books:
				f.write(bk.dump_as_json(True))