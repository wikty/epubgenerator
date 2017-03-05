## EPUB 3 电子书制作工具

### 简介

该工具主要将JSON数据文件生成epub电子书

### JSON数据文件

要生成一本电子书必须提供一个json line数据文件，文件样例如下：

```json
{"article_id": 1, "title": "學而", "en_title": "xue-er", "book": "論語", "en_book": "analects", "book_type": "tw", "url": "http://ctext.org/analects/xue-er/zh", "content": ["子曰：「學而時習之，不亦說乎？有朋自遠方來，不亦樂乎？人不知而不慍，不亦君子乎？」 孔子說：「經常學習，不也喜悅嗎？遠方來了朋友，不也快樂嗎？得不到理解而不怨恨，不也是君子嗎？」", "有子曰：「其為人也孝弟，而好犯上者，鮮矣；不好犯上，而好作亂者，未之有也。君子務本，本立而道生。孝弟也者，其為仁之本與！」有子說：「孝敬父母、尊敬師長，卻好犯上的人，少極了；不好犯上，卻好作亂的人，絕對沒有。做人首先要從根本上做起，有了根本，就能建立正確的人生觀。孝敬父母、尊敬師長，就是仁的根本吧！」"]}
{"article_id": 17, "title": "陽貨", "en_title": "yang-huo", "book": "論語", "en_book": "analects", "book_type": "tw", "url": "http://ctext.org/analects/yang-huo/zh", "content": ["陽貨欲見孔子，孔子不見，歸孔子豚。孔子時其亡也，而往拜之，遇諸塗。謂孔子曰：「來！予與爾言。」曰：「懷其寶而迷其邦，可謂仁乎？」曰：「不可。」「好從事而亟失時，可謂知乎？」曰：「不可。」「日月逝矣，歲不我與。」孔子曰：「諾。吾將仕矣。」<br/>陽貨想見孔子，孔子不見，他便送給孔一隻熟乳豬，想讓孔子去他家緻謝。孔子乘他不在家時，去拜謝。卻在半路上碰到了，他對孔子說：「來，我有話要說。」孔子走過去，他說：「自己身懷本領卻任憑國家混亂，能叫做仁嗎？」孔子說：「不能。「想做大事卻總是不去把握機遇，能叫做明智嗎？「不能。「時光一天天過去，歲月不等人埃「好吧，我準備做官。」", "子曰：「性相近也，習相遠也。」 孔子說：「人的本性是相近的，衹是習俗使人有了差別。」"]}
{"article_id": 18, "title": "微子", "en_title": "wei-zi", "book": "論語", "en_book": "analects", "book_type": "tw", "url": "http://ctext.org/analects/wei-zi/zh", "content": ["微子去之，箕子為之奴，比干諫而死。孔子曰：「殷有三仁焉。」 紂王無道，微子離他而去，箕子淪為奴隸，比乾勸諫慘死。孔子說：「商朝有三個仁人。」", "柳下惠為士師，三黜。人曰：「子未可以去乎？」曰：「直道而事人，焉往而不三黜？枉道而事人，何必去父母之邦。」 柳下惠當司法部長，三次被罷免。有人問：「你不可以離開嗎？」他說：「堅持正直輔佐別人，到哪裏不是要屢次被罷免？如果用歪門邪道輔佐別人，何必要離開自己的國家？」"]}
```

格式约定：

* 所谓json line文件，就是多行文本文件，其中每一行内容都是json字符串

* 一个json line文件对应一本电子书的数据

* json line文件中一行内容对应电子书中一篇文章的数据

* json line文件中一行内容格式如下：

  ```json
  {"article_id": 文章id（数字）, "title": "文章标题", "en_title": "文章拼音或英文标题", "book": "电子书名", "en_book": "电子书拼音或者英文名", "book_type": "电子书文本类型：简体为zh，繁体为tw，英文为en", "url": "爬取文章的网址", "content": ["列表的每一项表示文章中一个段落", "列表的每一项表示文章中一个段落"]}
  ```

### 元数据文件

如果电子书没有任何章节结构，所有文章是直接包含在电子书中的，那么上面的json line文件足以描述电子书的数据了。但如果电子书是按照章节结构组织的，也即文章要隶属于某一章节，那就需要额外的数据来描述这种章节结构了（当然即使没有章节结构的电子书，也可以使用元数据文件来描述电子书，下面的样例就是这样的），接下来将介绍元数据文件，样例如下：

```json
{"chapters": [{"url": "", "ch_name": "", "en_name": "", "id": 1, "articles": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}], "articles": {"1": {"chapter_id": 1, "url": "http://ctext.org/analects/xue-er/zh", "en_name": "xue-er", "ch_name": "學而"}, "2": {"chapter_id": 1, "url": "http://ctext.org/analects/wei-zheng/zh", "en_name": "wei-zheng", "ch_name": "為政"}, "3": {"chapter_id": 1, "url": "http://ctext.org/analects/ba-yi/zh", "en_name": "ba-yi", "ch_name": "八佾"}, "4": {"chapter_id": 1, "url": "http://ctext.org/analects/li-ren/zh", "en_name": "li-ren", "ch_name": "里仁"}, "5": {"chapter_id": 1, "url": "http://ctext.org/analects/gong-ye-chang/zh", "en_name": "gong-ye-chang", "ch_name": "公冶長"}, "6": {"chapter_id": 1, "url": "http://ctext.org/analects/yong-ye/zh", "en_name": "yong-ye", "ch_name": "雍也"}, "7": {"chapter_id": 1, "url": "http://ctext.org/analects/shu-er/zh", "en_name": "shu-er", "ch_name": "述而"}, "8": {"chapter_id": 1, "url": "http://ctext.org/analects/tai-bo/zh", "en_name": "tai-bo", "ch_name": "泰伯"}, "9": {"chapter_id": 1, "url": "http://ctext.org/analects/zi-han/zh", "en_name": "zi-han", "ch_name": "子罕"}, "10": {"chapter_id": 1, "url": "http://ctext.org/analects/xiang-dang/zh", "en_name": "xiang-dang", "ch_name": "鄉黨"}, "11": {"chapter_id": 1, "url": "http://ctext.org/analects/xian-jin/zh", "en_name": "xian-jin", "ch_name": "先進"}, "12": {"chapter_id": 1, "url": "http://ctext.org/analects/yan-yuan/zh", "en_name": "yan-yuan", "ch_name": "顏淵"}, "13": {"chapter_id": 1, "url": "http://ctext.org/analects/zi-lu/zh", "en_name": "zi-lu", "ch_name": "子路"}, "14": {"chapter_id": 1, "url": "http://ctext.org/analects/xian-wen/zh", "en_name": "xian-wen", "ch_name": "憲問"}, "15": {"chapter_id": 1, "url": "http://ctext.org/analects/wei-ling-gong/zh", "en_name": "wei-ling-gong", "ch_name": "衛靈公"}, "16": {"chapter_id": 1, "url": "http://ctext.org/analects/ji-shi/zh", "en_name": "ji-shi", "ch_name": "季氏"}, "17": {"chapter_id": 1, "url": "http://ctext.org/analects/yang-huo/zh", "en_name": "yang-huo", "ch_name": "陽貨"}, "18": {"chapter_id": 1, "url": "http://ctext.org/analects/wei-zi/zh", "en_name": "wei-zi", "ch_name": "微子"}, "19": {"chapter_id": 1, "url": "http://ctext.org/analects/zi-zhang/zh", "en_name": "zi-zhang", "ch_name": "子張"}, "20": {"chapter_id": 1, "url": "http://ctext.org/analects/yao-yue/zh", "en_name": "yao-yue", "ch_name": "堯曰"}}, "book": {"url": "http://ctext.org/analects/zh", "type": "tw", "en_name": "analects", "ch_name": "論語", "categories": [{"en_name": "pre-qin-and-han", "ch_name": "先秦兩漢", "url": "http://ctext.org/pre-qin-and-han/zh", "id": 1}, {"en_name": "confucianism", "ch_name": "儒家", "url": "http://ctext.org/confucianism/zh", "id": 2}], "standalone": true}}
```

可以看到元数据文件整体是一个字典对象，下面将分别介绍该字典各个键值的意义以及格式

* book键

  用来描述电子书类型、书名，以及是否为简单结构（字段`standalone=true`表示是简单结构，即不含章节结构）等信息

  ```json
  "book": {"en_name": "电子书拼音或英文名", "ch_name": "电子书名", "type": "电子书文本类型：简体为zh，繁体为tw，英文为en", "url": "爬取电子书的网址", "categories": ["是一个列表，用来描述电子书丛书类别，暂时用不到"], "standalone": true或者false}
  ```

* articles键

  一个字典，记录了电子书中所有文章的元信息。字典的键是文章id，字典值是对应文章元信息，元信息格式如下：

  ```json
  {"en_name": "文章拼音或英语标题", "ch_name": "文章标题", "url": "爬取文章的网址", "chapter_id": 章节id（数字）}
  ```

* chapters键

  一个列表，记录了电子书中所有章节的元信息。每个列表项记录一个章节的元信息，元信息格式如下：

  ```json
  {"id": 章节id（数字）, "en_name": "章节拼音或英语标题", "ch_name": "章节标题", "url": "爬取章节的网址", "articles": [1, 2, 3, 4, 5]}
  ```

  注：`articles`字段是一个列表，列表项是隶属于当前章节的文章id

#### 关于文件名

此外要注意的是，元数据文件名和json line文件名的命名要符合约定，json line文件名须命名格式为`*.jl`，对应的元数据文件名格式为`*_meta.json`，两个文件名中的`*`要求一致。例如：json line文件命名为`test.jl`，则元数据文件应命名为`test_meta.json`

### 使用手册

* 将txt文本文件转化为json line数据文件（只适用于简单结构的电子书）

  ```shell
  python main.py -a generate-from-txt
  ```

* 检测修复数据文件

  ```shell
  python main.py -a check-data
  ```

* 生成epub文件

  ```shell
  python main.py -a generate-epub
  ```

