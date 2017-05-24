# from .maker import run

__version__ = "0.1.0"

import os, csv

from .pipelines import run as pipelines_run


def run(
	data_dir,
	data_books,
	data_json_filename,
	data_meta_filename,
	product_dir,
	product_book_dir,
	product_epub_dir,
	product_failure_report_file,
	product_success_report_file,
	image_dir,
	epubcheck_path,
	zip_path,
	pandoc_path,
	chapteralone,
	with_indent):
	# check
	if not os.path.exists(data_dir):
		raise Exception('data directory [%s] not exists' % data_dir)
	if not os.path.exists(epubcheck_path):
		raise Exception('epubcheck program [%s] not exists' % epubcheck_path)
	if not os.path.exists(zip_path):
		raise Exception('zip program [%s] not exists' % zip_path)
	if not os.path.exists(pandoc_path):
		raise Exception('pandoc program [%s] not exists' % pandoc_path)
	# make dirs
	if not os.path.exists(product_epub_dir):
		os.makedirs(product_epub_dir)
	if not os.path.exists(product_book_dir):
		os.makedirs(product_book_dir)

	total_count = 0
	book_count = 0
	success_report = []
	failure_report = []
	# load books file
	for bk in data_books.get_books():
		total_count += 1
		en_name = bk.get_en_name()
		ch_name = bk.get_ch_name()
		booktype = bk.get_type()
		filename = bk.get_filename()
		images = [os.sep.join([image_dir, image]) for image in bk.get_images()]

		report = {
			'Name': ch_name,
			'Type': '繁体' if booktype == 'tw' else '简体',
			'Source': bk.get_sitename(),
			'Category': '-'.join([bk.get_category(), bk.get_sub_category()]).strip('-'),
			'Format': bk.get_format(),
			'WordCount': bk.get_wordcount(),
			'ArticleCount': bk.get_articlecount(),
			'URL': bk.get_url()
		}
		report_columns = ['Name', 'Type', 'Source', 'Category', 'Format', 'WordCount', 'ArticleCount', 'URL']
		
		if filename:
			en_name = os.path.splitext(os.path.basename(filename))[0]
		else:
			filename = en_name + '.jl'
		
		epubdir = os.sep.join([product_epub_dir, en_name])
		jsonfile = os.sep.join([data_dir, data_json_filename.format(en_name)])
		metafile = os.sep.join([data_dir, data_meta_filename.format(en_name)])

		try:
			task_name, message = pipelines_run(**{
				'ch_name': ch_name,
				'en_name': en_name,
				'booktype': booktype,
				'jsonfile': jsonfile,
				'metafile': metafile,
				'images': images,
				'chapteralone': chapteralone,
				'with_indent': with_indent,
				'epubdir': epubdir,
				'product_book_dir': product_book_dir,
				'epubcheck_path': epubcheck_path,
				'zip_path': zip_path,
				'pandoc_path': pandoc_path
			})
		except Exception as e:
			print(e)
		else:
			if message == 'ok' and task_name is True:
				success_report.append(report)
				book_count += 1

			if task_name == 'product_check_task' and message != 'ok':
				book_count += 1
			else:
				failure_report.append({
					'Name': ch_name,
					'Filename': filename,
					'Message': '%s - %s' % (task_name, message)
				})

	if not os.path.exists(product_success_report_file):
		with open(product_success_report_file, 'w', newline='') as f:
			writer = csv.DictWriter(f, report_columns)
			writer.writeheader()
	with open(product_success_report_file, 'a+', newline='') as f:
		writer = csv.DictWriter(f, report_columns)
		writer.writerows(success_report)

	with open(product_failure_report_file, 'w', newline='') as f:
		writer = csv.DictWriter(f, ['Name', 'Filename', 'Message'])
		writer.writeheader()
		writer.writerows(failure_report)

	return [total_count, book_count]