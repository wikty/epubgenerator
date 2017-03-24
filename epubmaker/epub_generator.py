# -*- coding:utf-8 -*-
import os, json, errno, shutil

from .models import BookEntry
from .models import BookMeta
from .models import Chapter
from .models import Article
from .models import Contents
from .page_generator import PageGenerator
from .template_manager import TplSimpleManager


class EpubGenerator:

    def __init__(self, config):
        self.config = config

        # book generate successfully
        self.ok = True

        # book basic information
        self.bookname = config.get_bookname()
        self.bookcname = config.get_bookcname()
        self.booktype = config.get_booktype()

        # data file
        self.jsonfile = config.get_jsonfile()
        self.metafile = config.get_metafile()

        # whether has chapter page for introduce itself
        self.chapteralone = config.is_chapteralone()

        # chapter and article id prefix in the contents
        self.article_id_prefix = config.get_prefix_of_article_id_in_contents()
        self.chapter_id_prefix = config.get_prefix_of_chapter_id_in_contents()

        # template manager
        self.tplmanager = TplSimpleManager(config.get_epub_templatedir())

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
        
        # some fields will be filled later
        self.standalone = True # standalone means that the book don't have chapters
        self.book_entry = None
        self.contents = None
        self.generator = None

    def load_data(self):
        try:
            # load book entry information
            self.book_entry = BookEntry(self.booktype)
            # load book meta data
            if os.path.exists(self.metafile):
                book_meta = BookMeta(self.metafile)
            else:
                # meta file not exists, book is standalone and
                # meta information generate from data json file
                book_meta = BookMeta.create_meta_from_jsonfile(
                    self.jsonfile, 
                    self.bookname, 
                    self.bookcname, 
                    self.booktype)
            self.standalone = book_meta.get_standalone()
            self.contents = Contents(
                Article.create_articles_from_jsonfile(self.jsonfile, book_meta.get_article_meta()), 
                Chapter.create_chapters_from_meta(book_meta.get_chapter_meta()), 
                self.standalone, 
                self.chapteralone, 
                self.booktype).serialize()
        except Exception as e:
            self.ok = False
            raise e

    def init(self):
        # make target epub directories and copy source to target files
        for k, dirname in self.target_epub_dirs.items():
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        for k, filename in self.source_epub_files.items():
            shutil.copy(filename, self.target_epub_files[k])

    def finish(self):
        if not self.ok:
            shutil.rmtree(self.target_rootdir)

    def run(self):
        try:
            # page generator
            self.generator = PageGenerator(**{
                'epubdir': self.target_epubdir,
                'xhtmldir': self.target_xhtmldir,
                'navfile': self.target_navfile,
                'coverfile': self.target_coverfile,
                'frontfile': self.target_frontfile,
                'contentsfile': self.target_contentsfile,
                'maincssfile': self.target_maincssfile,
                'coverimg': self.target_coverimg,
                'packagefile': self.target_packagefile,
                'ncxfile': self.target_ncxfile,
                'booktype': self.booktype,
                'bookcname': self.bookcname,
                'article_id_prefix': self.article_id_prefix,
                'chapter_id_prefix': self.chapter_id_prefix,
                'navtitle': self.book_entry.get_book_nav_title(),
                'covertitle': self.book_entry.get_book_cover_title(),
                'fronttitle': self.book_entry.get_book_front_title(),
                'contentstitle': self.book_entry.get_book_contents_title(),
                'bookid': self.book_entry.get_book_id(),
                'bookcat': self.book_entry.get_book_category(),
                'author': self.book_entry.get_book_author(),
                'publisher': self.book_entry.get_book_publisher(),
                'publish_year': self.book_entry.get_book_publish_year(),
                'modify_year': self.book_entry.get_book_modify_year(),
                'modify_month': self.book_entry.get_book_modify_month(),
                'modify_day': self.book_entry.get_book_modify_day()
            })
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