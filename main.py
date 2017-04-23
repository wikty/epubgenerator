#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, time
from optparse import OptionParser
from epubrepair import generate_data, check_data, merge_data
from epubmaker import run as epub_maker_run

def generate_epub(rootdir):
	'''
	epub data directory 	: 	rootdir/data/today/
	book list file 			: 	rootdir/data/today/books.jl
	epub target directory 	: 	rootdir/products/today/epub/
	book target directory 	: 	rootdir/products/today/book/
	report file 			: 	rootdir/products/today/report.json
	epub check path         :   define your epubchecker path
	'''
	today = time.strftime('%Y_%m_%d')
	epub_data_directory = os.sep.join([rootdir, 'data', today])
	books_file_path = os.sep.join([epub_data_directory, 'books.jl'])
	epub_check_path = os.sep.join([rootdir, 'epubcheck-4.0.1/epubcheck.jar'])
	book_target_directory = os.sep.join([rootdir, 'products', today, 'book'])
	epub_target_directory = os.sep.join([rootdir, 'products', today, 'epub'])
	report_filename = os.sep.join([rootdir, 'products', today, 'report.json'])

	source_items = [
		epub_data_directory,
		epub_check_path,
		books_file_path
	]

	target_dirs = [
		book_target_directory,
		epub_target_directory
	]

	for source_item in source_items:
		if not os.path.exists(source_item):
			raise Exception('[%s] not exists' % source_item)

	for target_dir in target_dirs:
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)

	return epub_maker_run(**{
		'epub_data_directory': epub_data_directory,
		'epub_check_path': epub_check_path,
		'book_target_directory': book_target_directory,
		'epub_target_directory': epub_target_directory,
		'books_file_path': books_file_path,
		'report_filename': report_filename,
		'epub_data_json_filename': '[en_name].jl', # [en_name] is placeholder for book en_name
		'epub_data_meta_filename': '[en_name]_meta.json', # [en_name] is placeholder for book en_name
		'chapteralone': False
	})

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-a', '--action', dest='action', help='action')
	parser.add_option('-d', '--data', dest='data', help='extra data about action')
	(options, args) = parser.parse_args()
	if options.action == 'generate-from-txt':
		print(generate_data('tmp', 'tmp', '生僻字目录', 'zh'))
	elif options.action == 'check-data':
		today = time.strftime('%Y_%m_%d')
		print(check_data('data/%s' % today))
	elif options.action == 'generate-epub':
		print(generate_epub(os.path.abspath(os.getcwd())))
	elif options.action == 'merge-data':
		input1, input2, output = options.data.split(';')
		print(merge_data(input1, input2, output))