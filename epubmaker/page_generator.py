# -*- coding:utf-8 -*-
import os, time

class PageGenerator():

    def __init__(
        self,
        epubdir,
        xhtmldir,
        navtitle,
        covertitle,
        fronttitle,
        contentstitle,
        navfile,
        coverfile,
        frontfile,
        contentsfile,
        maincssfile,
        coverimg,
        packagefile,
        ncxfile,
        bookid,
        booktype,
        bookcat,
        bookcname,
        author,
        publisher,
        publish_year,
        modify_year,
        modify_month,
        modify_day,
        article_id_prefix,
        chapter_id_prefix,
        images):
        xhtmldir = xhtmldir.rstrip('/').rstrip('\\')
        epubdir = epubdir.rstrip('/').rstrip('\\')

        self.xhtmldir = xhtmldir
        self.epubdir = epubdir
        self.covertitle = covertitle
        self.fronttitle = fronttitle
        self.contentstitle = contentstitle
        self.navtitle = navtitle
        self.coveranchor = ''
        self.frontanchor = 'copyright'
        self.contentsanchor = ''
        self.navanchor = ''
        self.coverfile = coverfile
        self.frontfile = frontfile
        self.contentsfile = contentsfile
        self.navfile = navfile
        self.coverimg = coverimg
        self.maincssfile = maincssfile
        self.packagefile = packagefile
        self.ncxfile = ncxfile
        self.bookid = bookid
        self.booktype = booktype
        self.bookcname = bookcname
        self.bookcat = bookcat
        self.author = author
        self.publisher = publisher
        self.publish_year = publish_year
        self.modify_year = modify_year
        self.modify_month = modify_month
        self.modify_day = modify_day
        self.article_id_prefix = article_id_prefix
        self.chapter_id_prefix = chapter_id_prefix
        self.images = images
        self.ncx_relative_dir =''
        self.xhtml_relative_dir = 'xhtml'
        self.img_relative_dir = 'img'
        self.css_relative_dir = 'css'
        self.js_relative_dir = 'js'

    def now(self, fmt='%Y-%m-%dT%H:%M:%SZ'):
        return time.strftime(fmt, time.localtime(time.time()))

    def get_navpage_li(self, filename, title):
        return '    <li><a href="{filename}">{title}</a></li>'.format(
            filename=filename, 
            title=title)

    def get_contentspage_p(self, level, filename, id_prefix, id, title):
        return '  <p class="sgc-toc-level-{level}"><a href="{filename}" id="{id_prefix}{id}">{title}</a></p>'.format(
            level=level,
            filename=filename,
            id_prefix=id_prefix,
            id=id,
            title=title)

    def get_opf_item(self, dirname, filename, id, mediatype, properties=''):
        if dirname:
            dirname = dirname+'/'
        else:
            dirname = ''
        if properties:
            return '      <item href="{dirname}{filename}" id="{id}" media-type="{mediatype}" properties="{properties}" />'.format(
                dirname=dirname,
                filename=filename, 
                id=id, 
                mediatype=mediatype, 
                properties=properties)
        else:
            return '      <item href="{dirname}{filename}" id="{id}" media-type="{mediatype}" />'.format(
                dirname=dirname,
                filename=filename, 
                id=id, 
                mediatype=mediatype)

    def get_opf_item_ncx(self, filename, id):
        return self.get_opf_item(self.ncx_relative_dir, filename, id, 'application/x-dtbncx+xml')

    def get_opf_item_nav(self, filename, id):
        return self.get_opf_item(self.xhtml_relative_dir, filename, id, 'application/xhtml+xml', 'nav')

    def get_opf_item_xhtml(self, filename, id):
        return self.get_opf_item(self.xhtml_relative_dir, filename, id, 'application/xhtml+xml')

    def get_opf_item_css(self, filename, id):
        return self.get_opf_item(self.css_relative_dir, filename, id, 'text/css')

    def get_opf_item_img(self, filename, id):
        ext = os.path.splitext(filename)[1]
        if '.png'.endswith(ext):
            mimetype = 'image/png'
        elif '.gif'.endswith(ext):
            mimetype = 'image/gif'
        elif '.svg'.endswith(ext):
            mimetype = 'image/svg+xml'
        elif '.bmp'.endswith(ext):
            mimetype = 'image/bmp'
        else:
            mimetype = 'image/jpeg'
        return self.get_opf_item(self.img_relative_dir, filename, id, mimetype)

    def get_opf_item_js(self, filename, id):
        return self.get_opf_item(self.js_relative_dir, filename, id, 'text/javascript')

    def get_opf_itemref(self, id, linear='yes'):
        linear = 'yes' if linear not in ['yes', 'no'] else linear
        return '      <itemref idref="{id}" linear="{linear}"/>'.format(id=id, linear=linear)

    def get_opf_reference(self, filename, type, title, dirname=''):
        dirname = self.xhtml_relative_dir if not dirname else dirname
        return '      <reference href="{dirname}/{filename}" type="{type}" title="{title}" />'.format(dirname=dirname, filename=filename, type=type, title=title)

    def get_ncx_navpoint(self, id, title, filename, anchor=''):
        playorder = id
        if not anchor:
            return """
    <navPoint id="navPoint-{id}" playOrder="{playorder}">
      <navLabel>
        <text>{title}</text>
      </navLabel>
      <content src="{dirname}/{filename}" />
    </navPoint>""".format(id=id, title=title, playorder=playorder, filename=filename, dirname=self.xhtml_relative_dir)
        else:
            return """
    <navPoint id="navPoint-{id}" playOrder="{playorder}">
      <navLabel>
        <text>{title}</text>
      </navLabel>
      <content src="{dirname}/{filename}#{anchor}" />
    </navPoint>""".format(id=id, title=title, playorder=playorder, filename=filename, dirname=self.xhtml_relative_dir, anchor=anchor)
    


    def generate_article(self, article, tpl):
        filename = os.sep.join([self.xhtmldir, article['filename']])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'article_id': article['id'],
                'title': article['title'],
                'content': article['body'],
                'article_id_prefix': self.article_id_prefix,
                'maincssfile': self.maincssfile,
                'contentsfile': self.contentsfile
            }))

    def generate_article_with_chapter_title(self, article, tpl):
        filename = os.sep.join([self.xhtmldir, article['filename']])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'article_id': article['id'],
                'title': article['title'],
                'content': article['body'],
                'chapter_id': article['chapter_id'],
                'chapter_title': article['chapter_title'],
                'article_id_prefix': self.article_id_prefix,
                'chapter_id_prefix': self.chapter_id_prefix,
                'maincssfile': self.maincssfile,
                'contentsfile': self.contentsfile
            }))

    def generate_chapter(self, chapter, tpl):
        filename = os.sep.join([self.xhtmldir, chapter['filename']])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'chapter_id': chapter['id'],
                'title': chapter['title'],
                'chapter_id_prefix': self.chapter_id_prefix,
                'maincssfile': self.maincssfile,
                'contentsfile': self.contentsfile
            }))

    def generate_cover(self, tpl):
        filename = os.sep.join([self.xhtmldir, self.coverfile])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'coverimg': self.coverimg,
                'title': self.covertitle
            }))

    def generate_front(self, tpl):
        filename = os.sep.join([self.xhtmldir, self.frontfile])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'maincssfile': self.maincssfile,
                'title': self.fronttitle,
                'bookid': self.bookid,
                'book_name': self.bookcname,
                'book_category': self.bookcat,
                'author': self.author,
                'publish_year': self.publish_year,
                'modify_year': self.modify_year,
                'modify_month': self.modify_month,
                'modify_day': self.modify_day,
                'frontanchor': self.frontanchor
            }))

    def generate_nav(self, contents, tpl):
        filename = os.sep.join([self.xhtmldir, self.navfile])
        with open(filename, 'w', encoding='utf-8') as f:
            l = []
            for item in contents:
                item_id = item.get_id()
                item_title = item.get_title()
                item_achor = item.get_achor()
                l.append(self.get_navpage_li(item_achor, item_title))
            content = '\n'.join(l)
            f.write(tpl.format({
                'title': self.navtitle,
                'content': content,
                'maincssfile': self.maincssfile,
                'covertitle': self.covertitle,
                'contentstitle': self.contentstitle,
                'fronttitle': self.fronttitle,
                'coverfile': self.coverfile,
                'frontfile': self.frontfile,
                'contentsfile': self.contentsfile,
                'frontanchor': self.frontanchor
            }))

    def generate_contents(self, contents, tpl):
        filename = os.sep.join([self.xhtmldir, self.contentsfile])
        with open(filename, 'w', encoding='utf-8') as f:
            l = []
            for item in contents:
                item_id = item.get_id()
                item_title = item.get_title()
                item_body = item.get_body()
                item_achor = item.get_achor()
                item_extra = item.get_extra()
                is_chapter = item.is_chapter()
                if is_chapter:
                    p = self.get_contentspage_p(1, item_achor, self.chapter_id_prefix, item_id, item_title)
                else:
                    p = self.get_contentspage_p(2, item_achor, self.article_id_prefix, item_id, item_title)
                l.append(p)
            content = '\n'.join(l)
            f.write(tpl.format({
                'title': self.contentstitle,
                'content': content,
                'maincssfile': self.maincssfile,
            }))

    def generate_opf(self, contents, tpl):
        filename  = os.sep.join([self.epubdir, self.packagefile])
        with open(filename, 'w', encoding='utf-8') as f:
            items = []
            itemrefs = []
            coverpage_id = 'coverpage'
            frontpage_id = 'frontpage'
            contentspage_id = 'contentspage'
            
            items.append(self.get_opf_item_ncx(filename=self.ncxfile, id='ncx'))
            items.append(self.get_opf_item_img(filename=self.coverimg, id='cover.jpg'))
            for image in self.images:
                items.append(self.get_opf_item_img(filename=image, id='image_'+image))
            items.append(self.get_opf_item_css(filename=self.maincssfile, id='main.css'))
            items.append(self.get_opf_item_nav(filename=self.navfile, id='nav'))
            items.append(self.get_opf_item_xhtml(filename=self.coverfile, id=coverpage_id))
            itemrefs.append(self.get_opf_itemref(id=coverpage_id))
            items.append(self.get_opf_item_xhtml(filename=self.frontfile, id=frontpage_id))
            itemrefs.append(self.get_opf_itemref(id=frontpage_id))
            items.append(self.get_opf_item_xhtml(filename=self.contentsfile, id=contentspage_id))
            itemrefs.append(self.get_opf_itemref(id=contentspage_id))

            for item in contents:
                item_id = item.get_id()
                item_title = item.get_title()
                item_body = item.get_body()
                item_achor = item.get_achor()
                item_extra = item.get_extra()
                is_page = item.is_page()
                is_chapter = item.is_chapter()
                if is_page:
                    items.append(self.get_opf_item_xhtml(filename=item_achor, id=item_achor))
                    itemrefs.append(self.get_opf_itemref(id=item_achor))

            references = []
            references.append(self.get_opf_reference(self.coverfile, 'cover', 'Cover'))
            references.append(self.get_opf_reference(self.contentsfile, 'toc', 'Table of Contents'))
            fields = {
                'bookid': self.bookid,
                'title': self.bookcname,
                'author': self.author,
                'publisher': self.publisher,
                'datetime': self.now(),
                'items': '\n'.join(items),
                'itemrefs': '\n'.join(itemrefs),
                'references': '\n'.join(references),
                'coverimg': self.coverimg
            }
            f.write(tpl.format(fields))

    def generate_ncx(self, contents, tpl):
        filename  = os.sep.join([self.epubdir, self.ncxfile])
        with open(filename, 'w', encoding='utf-8') as f:
            navpoints = []
            count = 1
            # add cover, front, contents
            np = self.get_ncx_navpoint(count, self.covertitle, self.coverfile)
            navpoints.append(np)
            count += 1
            np = self.get_ncx_navpoint(count, self.fronttitle, self.frontfile, self.frontanchor)
            navpoints.append(np)
            count += 1
            np = self.get_ncx_navpoint(count, self.contentstitle, self.contentsfile)
            navpoints.append(np)
            count += 1
            # add pages
            for item in contents:
                item_id = item.get_id()
                item_title = item.get_title()
                item_body = item.get_body()
                item_achor = item.get_achor()
                item_extra = item.get_extra()
                is_page = item.is_page()
                is_chapter = item.is_chapter()
                if is_page:
                    np = self.get_ncx_navpoint(count, item_title, item_achor)
                    navpoints.append(np)
                    count += 1
            f.write(tpl.format({
                'bookid':self.bookid,
                'title': self.bookcname,
                'navpoints': '\n'.join(navpoints)
            }))
