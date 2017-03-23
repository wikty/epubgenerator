# -*- coding:utf-8 -*-
import os, json, time, errno, shutil
from .epub_config import EpubConfig
from .page_generator import PageGenerator
from .template_manager import TplSimpleManager

class EpubGenerator:

    def __init__(self, **kwargs):
        config = EpubConfig(**kwargs)
        self.config = config

        self.ok = True # book generate successfully
        # book information
        self.bookname = config.get_book_entry('bookname')
        self.bookcname = config.get_book_entry('bookcname')
        self.booktype = config.get_book_entry('booktype')
        self.bookid = config.get_book_entry('bookid')
        self.bookcat = config.get_book_entry('bookcat')
        self.author = config.get_book_entry('author')
        self.publisher = config.get_book_entry('publisher')
        self.publish_year = config.get_book_entry('publish_year')
        self.modify_year = config.get_book_entry('modify_year')
        self.modify_month = config.get_book_entry('modify_month')
        self.modify_day = config.get_book_entry('modify_day')
        self.covertitle = config.get_book_entry('covertitle')
        self.contentstitle = config.get_book_entry('contentstitle')
        self.fronttitle = config.get_book_entry('fronttitle')
        self.navtitle = config.get_book_entry('navtitle')

        # chapter and article id prefix in the contents
        self.article_id_prefix = config.get_prefix_of_article_id_in_contents()
        self.chapter_id_prefix = config.get_prefix_of_chapter_id_in_contents()

        # target/source epub directories and files
        self.target_epub_dirs = config.get_target_epub_dirs()
        self.target_epub_files = config.get_target_epub_files()
        self.source_epub_files = config.get_source_epub_files()
        self.target_rootdir = self.target_epub_dirs['root']
        self.target_xhtmldir = self.target_epub_dirs['xhtml']
        self.target_epubdir = self.target_epub_dirs['epub']
        self.target_coverfile = config.get_target_epub_files('cover', False)
        self.target_frontfile = config.get_target_epub_files('front', False)
        self.target_contentsfile = config.get_target_epub_files('contents', False)
        self.target_navfile = config.get_target_epub_files('nav', False)
        self.target_packagefile = config.get_target_epub_files('package', False)
        self.target_ncxfile = config.get_target_epub_files('ncx', False)
        self.target_maincssfile = config.get_target_epub_files('maincss', False)
        self.target_coverimg = config.get_target_epub_files('coverimg', False)

        # standalone means that the book don't have chapters
        self.standalone = config.is_standalone()
        # whether has chapter page for introduce itself
        self.chapteralone = config.is_chapteralone()
        # chapters id list
        # self.chapter_id_list = config.get_chapter_id_list()
        # self.article_id_list = config.get_article_id_list()
        # table of content
        self.contents = config.get_contents()

        # template manager
        self.tplmanager = TplSimpleManager(config.get_epub_templatedir())
        # page generator
        self.generator = PageGenerator(**{
            'epubdir': self.target_epubdir,
            'xhtmldir': self.target_xhtmldir,
            'navtitle': self.navtitle,
            'covertitle': self.covertitle,
            'fronttitle': self.fronttitle,
            'contentstitle': self.contentstitle,
            'navfile': self.target_navfile,
            'coverfile': self.target_coverfile,
            'frontfile': self.target_frontfile,
            'contentsfile': self.target_contentsfile,
            'maincssfile': self.target_maincssfile,
            'coverimg': self.target_coverimg,
            'packagefile': self.target_packagefile,
            'ncxfile': self.target_ncxfile,
            'bookid': self.bookid,
            'booktype': self.booktype,
            'bookcat': self.bookcat,
            'bookcname': self.bookcname,
            'author': self.author,
            'publisher': self.publisher,
            'publish_year': self.publish_year,
            'modify_year': self.modify_year,
            'modify_month': self.modify_month,
            'modify_day': self.modify_day,
            'article_id_prefix': self.article_id_prefix,
            'chapter_id_prefix': self.chapter_id_prefix
        })

    def start(self):
        # make target epub directories and copy source to target files
        for k, dirname in self.target_epub_dirs.items():
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        for k, filename in self.source_epub_files.items():
            shutil.copy(filename, self.target_epub_files[k])

    def end(self):
        if not self.ok:
            shutil.rmtree(self.target_rootdir)

    def run(self):
        try:
            self.start()
            self.generate_pages()
            self.generate_cover()
            self.generate_front()
            self.generate_contents()
            self.generate_nav()
            self.generate_opf()
            self.generate_ncx()
        except Exception as e:
            self.ok = False
            raise e
        finally:
            self.end()

    def generate_pages(self):
        for item in self.contents:
            item_id = item.get_id()
            item_title = item.get_title()
            item_body = item.get_body()
            item_achor = item.get_achor()
            item_extra = item.get_extra()
            is_page = item.is_page()
            is_chapter = item.is_chapter()
            if is_page:
                if is_chapter:
                    self.generator.generate_chapter({
                        'id': item_id,
                        'title': item_title,
                        'filename': item_achor
                    }, self.tplmanager.get_template('chapter'))
                else:
                    if not item_extra:
                        self.generator.generate_article({
                            'id': item_id,
                            'title': item_title,
                            'body': item_body,
                            'filename': item_achor
                        }, self.tplmanager.get_template('article'))
                    else:
                        self.generator.generate_article_with_chapter_title({
                            'id': item_id,
                            'title': item_title,
                            'chapter_id': item_extra[0],
                            'chapter_title': item_extra[1],
                            'body': item_body,
                            'filename': item_achor
                        }, self.tplmanager.get_template('article_with_chapter_title'))
    
    def generate_cover(self):
        self.generator.generate_cover(self.tplmanager.get_template('cover'))

    def generate_front(self):
        self.generator.generate_front(self.tplmanager.get_template('front', self.booktype))

    def generate_nav(self):
        self.generator.generate_nav(self.contents, self.tplmanager.get_template('nav'))

    def generate_contents(self):
        self.generator.generate_contents(self.contents, self.tplmanager.get_template('contents'))

    def generate_opf(self):
        self.generator.generate_opf(self.contents, self.tplmanager.get_template('opf'))

    def generate_ncx(self):
        self.generator.generate_ncx(self.contents, self.tplmanager.get_template('ncx'))