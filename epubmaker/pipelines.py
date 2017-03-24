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

config = [
	{
		'name': 'epubdir_check_task',
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

def epubdir_check_task(**kwargs):
	en_name = kwargs['en_name']
	epubdir = kwargs['epubdir']
	ok = True
	message = 'ok'
	info(en_name, 'check epubdir', 'checking...')
	if os.path.exists(epubdir):
		ok = False
		message = 'epub directory %s exists' % en_name
	info(en_name, 'check epubdir', message)
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
	info(en_name, 'check data file', 'checking...')
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
	}
	ok = True
	message = 'ok'
	info(en_name, 'epub config', 'configing...')
	try:
		epubconfig = EpubConfig(**d)
	except Exception as e:
		ok = False
		message = str(e)
	finally:
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
	info(en_name, 'load data', 'loading...')
	try:
		epubgenerator = EpubGenerator(epubconfig)
		epubgenerator.load_data()
	except Exception as e:
		ok = False
		message = str(e)
	finally:
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
	info(en_name, 'init epub', 'initing...')
	try:
		epubgenerator.init()
	except Exception as e:
		ok = False
		message = str(e)
	finally:
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
	info(en_name, 'generate epub', 'generating...')
	try:
		epubgenerator.run()
	except Exception as e:
		ok = False
		message = str(e)
	finally:
		info(en_name, 'generate epub', message)
		return {
			'ok': ok,
			'message': message
		}

def epub_archive_task(**kwargs):
	en_name = kwargs['en_name']
	epubdir = kwargs['epubdir']
	ok = True
	message = 'ok'
	try:
		# archive epub
		# mimetype must be plain text(no compressed), 
		# must be first file in archive, so other inable-unzip 
		# application can read epub's first 30 bytes
		os.chdir(epubdir) # current directory is in targetdir
		epubname = '%s.epub' % en_name
		os.system("zip -0Xq %s mimetype" % epubname)
		os.system("zip -Xr9Dq %s *" % epubname)
	except Exception as e:
		ok = False
		message = str(e)
	finally:
		info(en_name, 'archive epub', message)
		return {
			'ok': ok,
			'message': message,
			'epubname': epubname
		}

def epub_validate_task(**kwargs):
	en_name = kwargs['en_name']
	epub_check_path = kwargs['epub_check_path']
	epubname = kwargs['epubname']
	ok = True
	message = 'ok'
	info(en_name, 'validate epub', 'validating...')
	try:
		commond = "java -jar %s %s" % (epub_check_path, epubname)
		validation = subprocess.check_output(
			commond, 
			stderr=subprocess.STDOUT, 
			shell=True)
	except subprocess.CalledProcessError as e:
		validation = e.output
	message = validation.decode('utf-8')
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
	info(en_name, 'epub finish', '')
	try:
		epubgenerator.finish()
	except Exception as e:
		ok = False
		message = str(e)
	finally:
		info(en_name, 'epub finish', message)
		return {
			'ok': ok,
			'message': message
		}

def word_generate_task(**kwargs):
	en_name = kwargs['en_name']
	epubname = kwargs['epubname']
	ok = True
	message = 'ok'
	info(en_name, 'generate word', 'generating...')
	try:
		wordname = '%s.docx' % en_name
		commond = 'pandoc %s -o %s' % (epubname, wordname)
		os.system(commond)
	except Exception as e:
		ok = False
		message = str(e)
	finally:
		info(en_name, 'generate word', message)
		return {
			'ok': ok,
			'message': message,
			'wordname': wordname
		}

def product_generate_task(**kwargs):
	en_name = kwargs['en_name']
	ch_name = kwargs['ch_name']
	book_target_directory = kwargs['book_target_directory']
	epubname = kwargs['epubname']
	wordname = kwargs['wordname']
	ok = True
	message = 'ok'
	info(en_name, 'generate product', 'generating...')
	try:
		product_epubname = os.sep.join([book_target_directory, '%s.epub' % ch_name])
		product_wordname = os.sep.join([book_target_directory, '%s.docx' % ch_name])
		shutil.move(epubname, product_epubname)
		shutil.move(wordname, product_wordname)
	except Exception as e:
		ok = False
		message = str(e)
	finally:
		info(en_name, 'generate product', message)
		return {
			'ok': ok,
			'message': message
		}