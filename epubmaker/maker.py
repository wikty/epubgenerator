import os, json

from .models import Books
from .pipelines import run as pipelines_run

def get_filename(filename, en_name):
	return filename.replace('[en_name]', en_name)

def run(
	epub_data_directory,
	epub_check_path,
	book_target_directory,
	epub_target_directory,
	books_file_path,
	report_filename,
	product_filename,
	epub_data_json_filename,
	epub_data_meta_filename,
	chapteralone,
	with_indent):
	if not os.path.exists(epub_data_directory):
		raise Exception('epub data directory not exists')
	if not os.path.exists(epub_check_path):
		raise Exception('epub check path not exists')
	if not os.path.exists(book_target_directory):
		raise Exception('book target directory not exists')
	if not os.path.exists(epub_target_directory):
		raise Exception('epub target directory not exists')
	if not os.path.exists(books_file_path):
		raise Exception('books file path not exists')
	total_count = 0
	book_count = 0
	report = []
	product = []
	bs = Books(books_file_path)
	for en_name, ch_name, booktype, images, filename in bs.get_books():
		if filename:
			en_name = os.path.splitext(os.path.basename(filename))[0]
		if images:
			images = [os.sep.join([epub_data_directory, image]) for image in images]
		epubdir = os.sep.join([epub_target_directory, en_name])
		jsonfile = os.sep.join([epub_data_directory, get_filename(epub_data_json_filename, en_name)])
		metafile = os.sep.join([epub_data_directory, get_filename(epub_data_meta_filename, en_name)])
		total_count += 1

		task_name, message = pipelines_run(**{
			'ch_name': ch_name,
			'en_name': en_name,
			'booktype': booktype,
			'jsonfile': jsonfile,
			'metafile': metafile,
			'chapteralone': chapteralone,
			'epubdir': epubdir,
			'epub_check_path': epub_check_path,
			'book_target_directory': book_target_directory,
			'images': images,
			'with_indent': with_indent
		})

		if message == 'ok' and task_name == 'product_generate_task':
			product.append({
				'en_name': en_name,
				'ch_name': ch_name,
				'filename': filename,
				'type': booktype
			})

		if message == 'ok' or (task_name == 'product_check_task' and message != 'ok'):
			book_count += 1
		else:
			report.append({
				'en_name': en_name,
				'ch_name': ch_name,
				'message': '%s - %s' % (task_name, message)
			})	
		# if message == 'ok':
		# 	book_count += 1
		# else:
		# 	report.append({
		# 		'en_name': en_name,
		# 		'ch_name': ch_name,
		# 		'message': '%s - %s' % (task_name, message)
		# 	})

	with open(product_filename, 'a+', encoding='utf8') as f:
		f.write(json.dumps(product, ensure_ascii=False)+'\n')

	with open(report_filename, 'w', encoding='utf8') as f:
		f.write(json.dumps(report, indent=2, ensure_ascii=False))
	
	return [total_count, book_count]