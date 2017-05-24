import json

def generate_article_data(article_id, title, book_name, book_type, content=[]):
	d = {
		'article_id': article_id,
		'title': title,
		'en_title': '',
		'book': book_name,
		'en_book': '',
		'book_type': book_type,
		'url': '',
		'content': content
	}
	return json.dumps(d, ensure_ascii=False)

def generate_meta_data(title_list, book_name, book_type, article_num):
	d = {
		'book': {
			'url': '',
			'type': book_type,
			'ch_name': book_name,
			'en_name': '',
			'categories': [],
			'standalone': True
		},
		'chapters': [{
			'url': '',
			'ch_name': '',
			'en_name': '',
			'id': 1,
			'articles': [i for i in range(1, article_num+1)]
		}],
		'articles': {
		}
	}

	for i in range(1, article_num+1):
		d['articles'][i] = {
			'chapter_id': 1,
			'url': '',
			'ch_name':  title_list[i-1],
			'en_name': ''
		}
	
	return json.dumps(d, ensure_ascii=False)