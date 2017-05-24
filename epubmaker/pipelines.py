'''
dependencies: java, zip, pandoc
'''
import os, shutil, subprocess, sys, heapq

from .epub_generator import EpubGenerator
from .epub_config import EpubConfig

def info(target, action, message=''):
    print('[%s]' % target, '(%s)' % action, message)

class TaskItem(object):
    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __lt__(self, other):
        return self.level < other.level

    def __eq__(self, other):
        return self.level == other.level

    def __str__(self):
        return '%s - %s' % (name, level)

    def get_name(self):
        return self.name

    def get_level(self):
        return self.level

class TaskMinHeap(object):
    def __init__(self):
        self.task_list = []

    def add_task(self, task):
        if not isinstance(task, TaskItem):
            raise Exception('task object invalid')
        heapq.heappush(self.task_list, task)

    def remove_task(self):
        return heapq.heappop(self.task_list)

    def empty(self):
        return len(self.task_list) == 0

    def __len__(self):
        return len(self.task_list)

    def __getitem__(self, i):
        return self.task_list[i]

debug = True

config = [
	{
		'name': 'product_check_task',
		'level': '0100',
		'input_args': [
			'en_name',
			'epubdir'
		]
	},
	{
		'name': 'datafile_check_task',
		'level': '0200',
		'input_args': [
			'en_name',
			'jsonfile',
			'metafile'
		]
	},
	{
		'name': 'epub_config_task',
		'level': '0300',
		'input_args': [
			'ch_name',
			'en_name',
			'booktype',
			'jsonfile',
			'metafile',
			'chapteralone',
			'epubdir'
		],
		'output_args': [
			'epubconfig'
		]
	},
	{
		'name': 'data_load_task',
		'level': '0400',
		'input_args': [
			'en_name',
			'epubconfig'
		],
		'output_args': [
			'epubgenerator'
		]
	},
	{
		'name': 'epub_init_task',
		'level': '0500',
		'input_args': [
			'en_name',
			'epubgenerator'
		],
		'couple': {
			'name': 'epub_finish_task',
			'level': '0801',
			'input_args': [
				'en_name',
				'epubgenerator'
			]
		}
	},
	{
		'name': 'epub_generate_task',
		'level': '0600',
		'input_args': [
			'en_name',
			'epubgenerator'
		]
	},
	{
		'name': 'epub_archive_task',
		'level': '0700',
		'input_args': [
			'en_name',
			'epubdir'
		],
		'output_args': [
			'epubname'
		]
	},
	{
		'name': 'epub_validate_task',
		'level': '0800',
		'input_args': [
			'en_name',
			'epubname',
			'epub_check_path'
		]
	},
	{
		'name': 'word_generate_task',
		'level': '0900',
		'input_args': [
			'en_name',
			'epubname'
		],
		'output_args': [
			'wordname'
		]
	},
	{
		'name': 'product_generate_task',
		'level': '1000',
		'input_args': [
			'en_name',
			'ch_name',
			'wordname',
			'epubname',
			'book_target_directory'
		]
	}
]

def run(**kwargs):
	task_queue = TaskMinHeap()
	for item in sorted(config, key=lambda item: item['level']):
		# add task
		task = TaskItem(item['name'], item['level'])
		task_queue.add_task(task)
		if item.get('couple'):
			couple_task = TaskItem(item['couple']['name'], item['couple']['level'])
			task_queue.add_task(couple_task)
		# run the most important task
		task = task_queue.remove_task()
		task_name = task.get_name()
		result = globals()[task_name](**kwargs)
		ok = result['ok']
		message = result['message']
		
		# not ok run the remaining tasks
		if not ok:
			while not task_queue.empty():
				task = task_queue.remove_task()
				result = globals()[task.get_name()](**kwargs)
				kwargs.update(result)
			return [task_name, message]		
		kwargs.update(result)
	# run the remaining tasks
	while not task_queue.empty():
		task = task_queue.remove_task()
		result = globals()[task.get_name()](**kwargs)
		kwargs.update(result)

	return [ok, message]

def product_check_task(**kwargs):
	ch_name = kwargs['ch_name']
	en_name = kwargs['en_name']
	product_book_dir = kwargs['product_book_dir']
	ok = True
	message = 'ok'
	product_epubname = os.sep.join([product_book_dir, '%s.epub' % ch_name])
	product_wordname = os.sep.join([product_book_dir, '%s.docx' % ch_name])
	if os.path.exists(product_epubname) and os.path.exists(product_wordname):
		ok = False
		message = 'product epub and word exists'	
	# if not (os.path.exists(product_epubname) and os.path.exists(product_wordname)):
	# 	if os.path.exists(epubdir):
	# 		shutil.rmtree(epubdir)
	# else:
	# 	ok = False
	# 	message = 'product epub&word exists'
	# if os.path.exists(epubdir):
	# 	ok = False
	# 	message = 'epub directory %s exists' % en_name
	info(en_name, 'check product', message)
	return {
		'ok': ok,
		'message': message
	}

def datafile_check_task(**kwargs):
	en_name = kwargs['en_name']
	jsonfile = kwargs['jsonfile']
	metafile = kwargs['metafile']
	ok = True
	message = 'ok'
	if not os.path.exists(jsonfile):
		ok = False
		message = '%s lost!!!' % en_name
	if ok and not os.path.exists(metafile):
		# NOTICE: meta file not exists, means book is standalone
		# so pipeline is ok
		ok = True
		message = 'meta data file not exists'
	info(en_name, 'check data file', message)
	return {
		'ok': ok,
		'message': message
	}

def epub_config_task(**kwargs):
	en_name = kwargs['en_name']
	d = {
		'bookcname': kwargs['ch_name'],
		'bookname': kwargs['en_name'],
		'booktype': kwargs['booktype'],
		'targetdir': kwargs['epubdir'],
		'jsonfile': kwargs['jsonfile'],
		'metafile': kwargs['metafile'],
		'chapteralone': kwargs['chapteralone'],
		'images': kwargs['images'],
		'with_indent': kwargs['with_indent']
	}
	ok = True
	message = 'ok'
	e = None
	try:
		epubconfig = EpubConfig(**d)
	except Exception as e:
		ok = False
		message = str(e)
	finally:
		if debug and e:
			raise e
		info(en_name, 'epub config', message)
		return {
			'ok': ok,
			'message': message,
			'epubconfig': epubconfig
		}

def data_load_task(**kwargs):
	en_name = kwargs['en_name']
	epubconfig = kwargs['epubconfig']
	ok = True
	message = 'ok'
	try:
		epubgenerator = EpubGenerator(epubconfig)
		epubgenerator.load_data()
	except Exception as e:
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'load data', message)
	return {
		'ok': ok,
		'message': message,
		'epubgenerator': epubgenerator
	}

def epub_init_task(**kwargs):
	en_name = kwargs['en_name']
	epubgenerator = kwargs['epubgenerator']
	ok = True
	message = 'ok'
	try:
		epubgenerator.init()
	except Exception as e:
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'init epub', message)
	return {
		'ok': ok,
		'message': message
	}

def epub_generate_task(**kwargs):
	en_name = kwargs['en_name']
	epubgenerator = kwargs['epubgenerator']
	ok = True
	message = 'ok'
	try:
		epubgenerator.run()
	except Exception as e:
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'generate epub', message)
	return {
		'ok': ok,
		'message': message
	}

def epub_archive_task(**kwargs):
	en_name = kwargs['en_name']
	epubdir = kwargs['epubdir']
	zip_path = kwargs['zip_path']
	ok = True
	message = 'ok'
	try:
		# archive epub
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		os.chdir(epubdir) # change working directory
		epubname = '%s.epub' % en_name
		output = subprocess.check_output(
			[zip_path, '-0Xq', epubname, 'mimetype'],
			stderr=subprocess.STDOUT,
			shell=True
		)
		output = subprocess.check_output(
			[zip_path, '-Xr9Dq', epubname, '*'],
			stderr=subprocess.STDOUT,
			shell=True
		)
		# os.system("zip -0Xq %s mimetype" % epubname)
		# os.system("zip -Xr9Dq %s *" % epubname)
	except subprocess.CalledProcessError as e:
		# output = e.output.decode('utf8')
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'archive epub', message)
	return {
		'ok': ok,
		'message': message,
		'epubname': epubname
	}

def epub_validate_task(**kwargs):
	en_name = kwargs['en_name']
	epubcheck_path = kwargs['epubcheck_path']
	epubname = kwargs['epubname']
	ok = True
	message = 'ok'
	try:
		# commond = "java -jar %s %s" % (epub_check_path, epubname)
		output = subprocess.check_output(
			['java', '-jar', epubcheck_path, epubname], 
			stderr=subprocess.STDOUT, 
			shell=True)
	except subprocess.CalledProcessError as e:
		output = e.output
	try:
		message = output.decode('utf8')
	except Exception as e:
		ok = False
		message = str(e)
	else:
		if message.find('No errors') < 0:
			ok = False
			message = message
	info(en_name, 'validate epub', message)
	return {
		'ok': ok,
		'message': message
	}

def epub_finish_task(**kwargs):
	en_name = kwargs['en_name']
	epubgenerator = kwargs['epubgenerator']
	ok = True
	message = 'ok'
	try:
		epubgenerator.finish()
	except Exception as e:
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'epub finish', message)
	return {
		'ok': ok,
		'message': message
	}

def word_generate_task(**kwargs):
	en_name = kwargs['en_name']
	epubname = kwargs['epubname']
	pandoc_path = kwargs['pandoc_path']
	ok = True
	message = 'ok'
	try:
		wordname = '%s.docx' % en_name
		subprocess.check_output(
			[pandoc_path, epubname, '-o', wordname],
			stderr=subprocess.STDOUT,
			shell=True
		)
	except subprocess.CalledProcessError as e:
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'generate word', message)
	return {
		'ok': ok,
		'message': message,
		'wordname': wordname
	}

def product_generate_task(**kwargs):
	en_name = kwargs['en_name']
	ch_name = kwargs['ch_name']
	product_book_dir = kwargs['product_book_dir']
	epubname = kwargs['epubname']
	wordname = kwargs['wordname']
	ok = True
	message = 'ok'
	try:
		product_epubname = os.sep.join([product_book_dir, '%s.epub' % ch_name])
		product_wordname = os.sep.join([product_book_dir, '%s.docx' % ch_name])
		shutil.move(epubname, product_epubname)
		shutil.move(wordname, product_wordname)
	except Exception as e:
		if os.path.exists(product_epubname):
			os.remove(product_epubname)
		if os.path.exists(product_wordname):
			os.remove(product_wordname)
		if debug:
			raise e
		ok = False
		message = str(e)
	info(en_name, 'generate product', message)
	return {
		'ok': ok,
		'message': message
	}