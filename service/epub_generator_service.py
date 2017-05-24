import time, os, subprocess

from config import EpubGeneratorServiceConfig
from epubmaker import run as epub_maker_run
from models import Books


def run(project_name, data_dir, product_dir, epubcheck_path, zip_path, pandoc_path):
	# check depend java
	try:
		output = subprocess.check_output(
			'java -version',
			stderr=subprocess.STDOUT,
			shell=True
		)
	except subprocess.CalledProcessError as e:
		# print(e.returncode)
		output = e.output
		print('Project Depends on Java(TM) SE Runtime Environment, Please Install Java first!')
		r = input('Already installed Java?(y/n)')
		if not 'yes'.startswith(r):
			return '\n Bye!'

	# check configuration
	epub_cfg = EpubGeneratorServiceConfig(
		project_name, 
		data_dir, 
		product_dir, 
		epubcheck_path, 
		zip_path, 
		pandoc_path)
	
	if not epub_cfg.validate_configuration():
		return epub_cfg.get_validation()
	
	if epub_cfg.confirm_configuration():
		cfg = epub_cfg.get_configuration()
		books = Books.create_from_file(cfg['data_books_file'])

		return epub_maker_run(**{
			'epubcheck_path': cfg['epubcheck_path'],
			'zip_path': cfg['zip_path'],
			'pandoc_path': cfg['pandoc_path'],
			'data_dir': cfg['data_dir'],
			'image_dir': cfg['image_dir'],
			'data_books': books,
			'product_dir': cfg['product_dir'],
			'product_book_dir': cfg['product_book_dir'],
			'product_epub_dir': cfg['product_epub_dir'],
			'product_failure_report_file': cfg['product_failure_report_file'],
			'product_success_report_file': cfg['product_success_report_file'],
			'data_json_filename': cfg['data_json_filename'],
			'data_meta_filename': cfg['data_meta_filename'],
			'chapteralone': cfg['chapteralone'],
			'with_indent': cfg['with_indent']
		})
	else:
		return '\nOk, may be you should change your configuation first, Bye!'