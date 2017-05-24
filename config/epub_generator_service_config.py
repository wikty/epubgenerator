import os, time, copy

from .base_config import BaseConfig


class EpubGeneratorServiceConfig(BaseConfig):

	_cfg = {
		'data_books_file': 'books.jl',
		'data_json_filename': '{}.jl',
		'data_meta_filename': '{}_meta.json',
		'chapteralone': False,
		'with_indent': False,
		'product_epub_dirname': 'epub',
		'product_book_dirname': 'book',
		'product_failure_report_file': 'failure.csv',
		'product_success_report_file': 'success.csv',
	}

	def __init__(self, project_name, data_dir, product_dir, epubcheck_path, zip_path, pandoc_path):
		today = time.strftime('%Y_%m_%d')
		self.validation = ''
		self.cfg = {}
		self.cfg['epubcheck_path'] = epubcheck_path
		self.cfg['zip_path'] = zip_path
		self.cfg['pandoc_path'] = pandoc_path
		self.cfg['data_dir'] = os.sep.join([data_dir, today, project_name])
		self.cfg['image_dir'] = self.cfg['data_dir']
		self.cfg['product_dir'] = os.sep.join([product_dir, today, project_name])
		self.cfg['data_books_file'] = os.sep.join([self.cfg['data_dir'], self._cfg['data_books_file']])
		self.cfg['product_book_dir'] = os.sep.join([self.cfg['product_dir'], self._cfg['product_book_dirname']])
		self.cfg['product_epub_dir'] = os.sep.join([self.cfg['product_dir'], self._cfg['product_epub_dirname']])
		self.cfg['product_failure_report_file'] = os.sep.join([self.cfg['product_dir'], self._cfg['product_failure_report_file']])
		self.cfg['product_success_report_file'] = os.sep.join([self.cfg['product_dir'], self._cfg['product_success_report_file']])
		self.cfg['data_json_filename'] = self._cfg['data_json_filename']
		self.cfg['data_meta_filename'] = self._cfg['data_meta_filename']
		self.cfg['chapteralone'] = self._cfg['chapteralone']
		self.cfg['with_indent'] = self._cfg['with_indent']

	def get_configuration(self):
		return copy.deepcopy(self.cfg)

	def validate_configuration(self):		
		if not os.path.exists(self.cfg['epubcheck_path']):
			self.validation = 'epubcheck program path is invalid: %s' % self.cfg['epubcheck_path']
			return False
		
		if not os.path.exists(self.cfg['zip_path']):
			self.validation = 'zip program path is invalid: %s' % self.cfg['zip_path']
			return False

		if not os.path.exists(self.cfg['pandoc_path']):
			self.validation = 'pandoc program path is invalid: %s' % self.cfg['pandoc_path']
		
		if not os.path.exists(self.cfg['data_dir']):
			self.validation = 'data directory not exists: %s' % self.cfg['data_dir']
			return False
		
		if not os.path.exists(self.cfg['data_books_file']):
			self.validation = 'data directory has no books file: %s' % self.cfg['data_books_file']
			return False
		
		self.validation = 'ok'
		return True

	def get_validation(self):
		return self.validation

	def confirm_configuration(self):
		print('#'*50)
		print('\n'.join(['{0:<30} = {1}'.format(k, v) for k,v in self.cfg.items()]))
		print('#'*50)
		r = input('Would like run with above configurations?(y/n)')
		return r and 'yes'.startswith(r)