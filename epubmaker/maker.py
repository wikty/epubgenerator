import os, json, subprocess, sys, shutil

from .epub_generator import EpubGenerator
from .models import Books

def display(target, message):
	print('[%s]' % target, message)

def get_filename(filename, en_name):
	return filename.replace('[en_name]', en_name)

def run(
	epub_data_directory,
	epub_check_path,
	book_target_directory,
	epub_target_directory,
	report_filename,
	books_filename,
	jsonfile,
	metafile,
	chapteralone):
	book_count = 0
	report = {
		'exists': [],
		'invalid': [],
		'valid': [],
		'lost': [],
		'autometa': [],
		'damaged': {}
	}
	bs = Books(books_filename)
	for en_name, ch_name, booktype in bs.get_books():
		# book epub directory
		epubdir = os.sep.join([epub_target_directory, en_name])
		# check whether book exists or not
		if os.path.exists(epubdir):
			display(en_name, 'exists!')
			report['exists'].append({
				'en_name': en_name,
				'ch_name': ch_name
			})
			continue
		display(en_name, 'generating...')
		# jsonfile
		jsonfile = get_filename(jsonfile, en_name)
		# metafile
		metafile = get_filename(metafile, en_name)
		epub_data_jsonfile = os.sep.join([epub_data_directory, jsonfile])
		epub_data_metafile = os.sep.join([epub_data_directory, metafile])
		
		if not os.path.exists(epub_data_jsonfile):
			report['lost'].append({
				'en_name': en_name,
				'ch_name': ch_name,
				'meta_exists': os.path.exists(epub_data_metafile)
			})
			display(en_name, 'lost!!!')
			continue
		if not os.path.exists(epub_data_metafile):
			# NOTICE: meta file not exists, means book is standalone
			report['autometa'].append({
				'en_name': en_name,
				'ch_name': ch_name
			})
		# generate e-book
		try:
			EpubGenerator(**{
				'bookcname': ch_name,
				'bookname': en_name,
				'booktype': booktype,
				'targetdir': epubdir,
				'jsonfile': epub_data_jsonfile,
				'metafile': epub_data_metafile,
				'chapteralone': chapteralone,
			}).run()
		except Exception as e:
			raise e
			# report['damaged'][en_name] = str(e)
			# display(en_name, 'is damaged!!!')
			# continue
		
		# archive epub
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		os.chdir(epubdir) # current directory is epubdir
		epubname = '%s.epub' % en_name
		display(epubname, 'archiving...')
		os.system("zip -0Xq %s mimetype" % epubname)
		os.system("zip -Xr9Dq %s *" % epubname)
		
		# check epub file validation
		display(epubname, 'validating...')
		try:
			commond = "java -jar %s %s" % (epub_check_path, epubname)
			validation = subprocess.check_output(
				commond, 
				stderr=subprocess.STDOUT, 
				shell=True)
		except subprocess.CalledProcessError as e:
			validation = e.output
		invalid = validation.decode('utf-8').find('No errors') < 0
		if invalid:
			display(epubname, 'has errors and %s.errors is generated' % epubname)
			report['invalid'].append({
				'en_name': en_name,
				'ch_name': ch_name,
				'message': validation.decode('utf-8')
			})
		else:
			display(epubname, 'is ok')
			report['valid'].append({
				'en_name': en_name,
				'ch_name': ch_name,
				'message': validation.decode('utf-8')
			})

			# generate .doc
			wordname = '%s.docx' % en_name
			display(wordname, 'generating...')
			commond = 'pandoc %s -o %s' % (epubname, wordname)
			os.system(commond)

			# move to product directory
			product_epubname = os.sep.join([book_target_directory, '%s.epub' % ch_name])
			product_wordname = os.sep.join([book_target_directory, '%s.docx' % ch_name])
			display(epubname, 'move to %s' % product_epubname)
			display(wordname, 'move to %s' % product_wordname)
			shutil.move(epubname, product_epubname)
			shutil.move(wordname, product_wordname)
			book_count += 1

	# generate report
	display('report', 'generate report: %s' % report_filename)
	with open(report_filename, 'w', encoding='utf8') as f:
		f.write(json.dumps(report, ensure_ascii=False, indent=4))
	
	return book_count