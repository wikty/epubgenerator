# -*- coding:utf-8 -*-
import os, json, time
from .epub_config import EpubConfig
from .page_generator import PageGenerator
from .package_generator import PackageGenerator
from .epub_source import SourceSetup
from .chapter import ChapterRaw
from .article import ArticleRaw
from .template_manager import TplSimpleManager

class EpubGenerator:

    def __init__(self, **kwargs):

        config = EpubConfig(**kwargs)
        self.config = config

        # initial: make directories and copy files
        SourceSetup.run(
            config.get_target_epub_dirs(), 
            config.get_target_epub_files(), 
            config.get_source_epub_files()
        )

        # book basic information
        self.bookname = config.get_bookname()
        self.bookcname = config.get_bookcname()
        self.booktype = config.get_booktype()
        
        # book meta information
        self.bookid = config.get_book_meta('bookid')
        self.bookcat = config.get_book_meta('bookcat')
        self.author = config.get_book_meta('author')
        self.publisher = config.get_book_meta('publisher')
        self.covertitle = config.get_book_meta('covertitle')
        self.contentstitle = config.get_book_meta('contentstitle')
        self.fronttitle = config.get_book_meta('fronttitle')
        self.navtitle = config.get_book_meta('navtitle')

        # target epub directory
        self.target_rootdir = config.get_target_epub_dirname('root')
        self.target_epubdir = config.get_target_epub_dirname('epub')
        self.target_metainfdir = config.get_target_epub_dirname('metainf')
        self.target_xhtmldir = config.get_target_epub_dirname('xhtml')
        self.target_cssdir = config.get_target_epub_dirname('css')
        self.target_jsdir = config.get_target_epub_dirname('js')
        self.target_imgdir = config.get_target_epub_dirname('img')
        
        # some target epub resource filename
        self.target_coverpage = config.get_target_epub_filename('coverpage', False)
        self.target_frontpage = config.get_target_epub_filename('frontpage', False)
        self.target_contentspage = config.get_target_epub_filename('contentspage', False)
        self.target_navpage = config.get_target_epub_filename('navpage', False)
        self.target_packagefile = config.get_target_epub_filename('packagefile', False)
        self.target_ncxfile = config.get_target_epub_filename('ncxfile', False)
        self.target_maincssfile = config.get_target_epub_filename('maincssfile', False)
        self.target_coverfile = config.get_target_epub_filename('coverfile', False)

        # chapter and article id prefix in the contents
        self.article_id_prefix = config.get_prefix_of_article_id_in_contents()
        self.chapter_id_prefix = config.get_prefix_of_chapter_id_in_contents()

        # data source
        self.jsonfile = config.get_source_data_filename()

        # standalone means that the book don't have chapters
        self.standalone = config.is_standalone_book()
        self.chapter_id_list = config.get_chapter_id_list()

        # whether has chapter page for intrduce itself
        self.has_chapter_page = config.get_has_chapter_page()

        # generated articles will be combined into epub file
        # self.articles = []
        # self.chapters = []

        # # generated articles and chapters base filename: {id: filename}
        # self.article_achor = {}
        # self.chapter_achor = {}
        self.contents = {
            'standalone': True,
            'chapters': { }, # id: {id, title, filename, articles: []}
            'articles': { } # id : {id, title, filename}
        }
        
        # template directory
        self.templatedir = config.get_epub_templatedir()
        # template manager
        self.tplmanager = TplSimpleManager(self.templatedir)

        self.generator = PageGenerator(self.target_xhtmldir, {
            'booktype': self.booktype,
            'navtitle': self.navtitle,
            'covertitle': self.covertitle,
            'fronttitle': self.fronttitle,
            'contentstitle': self.contentstitle,
            'navpage': self.target_navpage,
            'coverpage': self.target_coverpage,
            'frontpage': self.target_frontpage,
            'contentspage': self.target_contentspage,
            'maincssfile': self.target_maincssfile,
            'coverfile': self.target_coverfile,
            'article_id_prefix': self.article_id_prefix,
            'chapter_id_prefix': self.chapter_id_prefix
        })

        self.packager = PackageGenerator(self.target_epubdir, {
            'packagefile': self.target_packagefile,
            'ncxfile': self.target_ncxfile,
            'navpage': self.target_navpage,
            'coverpage': self.target_coverpage,
            'frontpage': self.target_frontpage,
            'contentspage': self.target_contentspage,
            'maincssfile': self.target_maincssfile,
            'coverfile': self.target_coverfile,
            'booktype': self.booktype,
            'bookid': self.bookid,
            'bookcname': self.bookcname,
            'author': self.author,
            'publisher': self.publisher
        })

    def run(self):
        self.generate_epub()
        self.generate_package()

    def generate_epub(self):
        self.generate_chapters_articles()
        self.generate_coverpage()
        self.generate_frontpage()
        self.generate_contentspage()
        self.generate_navpage()

    def generate_package(self):
        # self.packager.generate_opf(self.articles, self.chapters, self.tplmanager.get_template('opf'))
        # self.packager.generate_ncx(self.articles, self.chapters, self.tplmanager.get_template('ncx'))
        t = (not self.standalone) and self.has_chapter_page
        self.packager.generate_opf(self.contents, t, self.tplmanager.get_template('opf'))
        self.packager.generate_ncx(self.contents, t, self.tplmanager.get_template('ncx'))

    def resolve_contents(self):
        '''
            return [[id, title, filename, is_chapter], ...]
        '''
        l = []
        for chapter_id in sorted(self.contents['chapters'].keys()):
            chapter = self.contents['chapters'][chapter_id]
            if not self.contents['standalone']:
                l.append([chapter_id, chapter['title'], chapter['filename'], True])
            for article_id in chapter['articles']:
                article = self.contents['articles'][article_id]
                l.append([article_id, article['title'], article['filename'], False])
        return l

    def generate_chapters_articles(self):
        article_data = {}
        with open(self.jsonfile, 'r', encoding='utf-8') as f:
            for line in f:
                article = ArticleRaw(json.loads(line))
                article_data[article.get_id()] = article
                # self.articles.append([article.get_id(), article.get_title()])
        # self.articles = sorted(self.articles, key=lambda article: article[0])
        
        if self.standalone:
            # book has no chapter
            self.contents['standalone'] = True
            self.contents['chapters'][1] = {
                'id': 1,
                'title': '',
                'filename': '',
                'articles': []
            }
            for article_id in article_data.keys():
                article = article_data[article_id]
                article_title = article.get_title()
                article_body = article.get_body()
                filename = self.generator.generate_article({
                    'id': article_id,
                    'title': article_title,
                    'body': article_body
                }, self.tplmanager.get_template('article'))
                self.contents['chapters'][1]['articles'].append(article_id)
                self.contents['articles'][article_id] = {
                    'id': article_id,
                    'title': article_title,
                    'filename': filename
                }
            self.contents['chapters'][1]['articles'] = sorted(self.contents['chapters'][1]['articles'])
                # self.articles[article_id] = {
                #     'id': article_id,
                #     'title': article_title,
                #     'filename': filename
                # }
                # self.article_achor[article_id] = achor
        else:
            # book has several chapters
            self.contents['standalone'] = False
            for chapter_id in self.chapter_id_list:
                chapter = ChapterRaw(self.config.get_chapter(chapter_id))
                chapter_title = chapter.get_title()
                chapter_articles = sorted(chapter.get_articles())
                self.contents['chapters'][chapter_id] = {
                    'id': chapter_id,
                    'title': chapter_title,
                    'articles': chapter_articles,
                    'filename': ''
                }
                # self.chapters.append([chapter.get_id(), chapter.get_title(), chapter.get_articles()])
                if self.has_chapter_page:
                    filename = self.generator.generate_chapter({
                        'id': chapter_id,
                        'title': chapter_title
                    }, self.tplmanager.get_template('chapter'))
                    self.contents['chapters'][chapter_id]['filename'] = filename
                    # self.chapter_achor[chapter_id] = achor
                
                for article_id in chapter_articles:
                    article = article_data[article_id]
                    article_title = article.get_title()
                    article_body = article.get_body()
                    if not self.has_chapter_page and article_id == chapter_articles[0]:
                        filename = self.generator.generate_article_with_chapter_title({
                            'id': article_id,
                            'title': article_title,
                            'chapter_id': chapter_id,
                            'chapter_title': chapter_title,
                            'body': article_body
                        }, self.tplmanager.get_template('article_with_chapter_title'))
                        self.contents['chapters'][chapter_id]['filename'] = filename
                        # self.article_achor[article_id] = achor
                        # self.chapter_achor[chapter_id] = achor
                    else:
                        filename = self.generator.generate_article({
                            'id': article_id,
                            'title': article.get_title(),
                            'body': article.get_body()
                        }, self.tplmanager.get_template('article'))
                    self.contents['articles'][article_id] = {
                        'id': article_id,
                        'title': article_title,
                        'filename': filename
                    }
                        # self.article_achor[article_id] = achor
            # self.chapters = sorted(self.chapters, key=lambda chapter: chapter[0]) 
        self.contents = self.resolve_contents()
    
    def generate_coverpage(self):
        self.generator.generate_coverpage(self.tplmanager.get_template('cover'))

    def generate_frontpage(self):
        if self.booktype == 'tw':
            tpl = self.tplmanager.get_template('front_tw')
        else:
            tpl = self.tplmanager.get_template('front_zh')
        self.generator.generate_frontpage({
            'bookid': 'xxxxxxxx-xxxxxxxx',
            'bookcname': self.bookcname,
            'author': self.author,
            'publisher': self.publisher,
            'bookcat': self.bookcat,
            'publish_year': 'xxxx',
            'modify_year': 'xxxx',
            'modify_month': 'xx',
            'modify_day': 'xx'
        }, tpl)

    def generate_navpage(self):
        # self.generator.generate_navpage(
        #     self.articles, 
        #     self.chapters, 
        #     self.tplmanager.get_template('nav')
        # )
        self.generator.generate_navpage(
            self.contents,
            self.tplmanager.get_template('nav')
        )

    def generate_contentspage(self):
        # self.generator.generate_contentspage(
        #     self.articles, 
        #     self.chapters, 
        #     self.tplmanager.get_template('contents')
        # )
        self.generator.generate_contentspage(
            self.contents,
            self.tplmanager.get_template('contents')
        )