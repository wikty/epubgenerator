import os, shutil, csv

from models import Books

def run(project_name, data_dir, book_dir, epub_dir, books_file, failure_books, target_dir, category='', book_format='epub3'):
	# rename success products
	if not os.path.exists(book_dir):
		raise Exception('product book directory not exists')
	if not os.path.exists(data_dir):
		raise Exception('data directory not exists')
	if not os.path.exists(epub_dir):
		raise Exception('epub directory not exists')
	if not os.path.exists(books_file):
		raise Exception('books file not exists')

	for fname in os.listdir(book_dir):
		name, ext = os.path.splitext(fname)
		if category:
			new_fname = '_'.join([name, project_name, category, book_format]) + ext
		else:
			new_fname = '_'.join([name, project_name, book_format]) + ext
		shutil.move(os.sep.join([book_dir, fname]), os.sep.join([book_dir, new_fname]))

	# move failure books
	books = Books.create_from_file(books_file)
	new_books = Books()
	target_books_file = os.sep.join([target_dir, 'books.jl'])
	for book in failure_books:
		bookname = book['bookname']
		filename = book['filename']
		dirname = os.path.splitext(filename)[0]
		source_data_file = os.sep.join([data_dir, filename])
		target_data_file = os.sep.join([target_dir, filename])
		source_epub_dir = os.sep.join([epub_dir, dirname])
		target_epub_dir = os.sep.join([target_dir, dirname])
		if not os.path.exists(target_epub_dir):
			shutil.copytree(source_epub_dir, target_epub_dir)
		if not os.path.exists(target_data_file):
			shutil.copy(source_data_file, target_data_file)
		bk = books.get_book(filename)
		if bk:
			new_books.add_book(bk, True)

	new_books.dump_to_file(target_books_file)
