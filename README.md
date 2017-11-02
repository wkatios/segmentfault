###结论

JavaScript居首位，HTML5紧随其后，Python位列第三。

*注：数据来源于569页标签页面的11,380 条记录*


![](https://i.imgur.com/RBRczi9.png)
![](https://i.imgur.com/VxvOpEY.png)
###涉及知识点

 - python爬虫
   - requests库
   - BeautifulSoup
 - elasticsearch储存
     - 批量bulk数据
 - kibana可视化
     - 做图展示
     
###实现步骤
1. 数据采集
2. 批量入库
3. 绘制图表

### 缘起
浏览segmentfault时，看到热门标签，我就是思考了一下这个热门到底有多热。于是点击到所有标签查看，发现只能肉眼一个个对比，F12看了下，中规中矩的html文本，requests+bs4可以处理，干脆我爬一下看看吧。。。额，手头正好有一套elasticsearch+kibana的环境，我导进去看吧 emmmm....

### 数据采集
使用python爬取标签信息，包括：tag名称，tag的解释说明，tag的url，tag的关注人数
嗯，够简单，我喜欢。

```
def get_tag(page_num):
    result = requests.get('http://segmentfault.com/tags/all?page=%s'%page_num)
    return result.content
```
不得不说，segmentfault对爬虫是真正的友好啊，headers什么的都不用填写，直接简单粗暴。熟悉python的同学对这种操作，恐怕就是跟 print "Hello World"差不多吧。。

```
def process_tag(content):
    soup = BeautifulSoup(content,'lxml')
    sections = soup.find_all('section')
    info = {}
    values = []
    for section in sections:
        tag = section.div.h2.a.text
        tag_instruction = section.div.p.text
        follows = section.div.div.strong.text
        url = 'https://segmentfault.com'+section.div.h2.a['href']
        info['url'] = urllib.unquote(url)
        info['tag'] = tag
        info['tag_instruction'] = tag_instruction
        info['follows'] = int(follows)
        deepcopy_info = copy.deepcopy(info)
        values.append({
            "_index": 'segmentfault',
            "_type": 'tag',
            # "_op_type": "create",
            "_source": deepcopy_info
        })
    return values
```
上面一段代码还是有些需要注意的地方。
1. BeautifulSoup的使用，tag的获取，节点属性等等，认真阅读文档我相信大家都没有问题。
2. 列表和字典copy的问题，这里面要注意python的copy并不会为此开辟新的内存，你可以想象为windows下的快捷方式，或者linux下的软链接。所以此处我们使用deepcopy,使之开辟新的内存存储这个copy.
3. bulk数据，这个我们接下来说明。

### 批量入库

因为手头有elasticsearch所以就导入了进来，关于elasticsearch的安装和使用，社区里也有资源，有空我也会整理一篇文章。

python比较友好的地方就是各种包非常的全面，elasticsearch这个库提供了一套API接口，用来增删改查。这里说一下，我有一个梦想，就是希望从业环境更加的纯粹，JD上的要求不要这么过分，当面试官问我问题的时候，我可以微笑着告诉他，没看过源码，对底层架构不熟悉，对原理的了解来自于各个博客的东拼西凑，熟练运用各种API接口，但是你不要让我说出来几个，因为我需要看文档。然后面试官微笑着说，我很满意，给你2K，如果接受明天可以来拧螺丝。

咳咳咳，言归正传。
elasticsearch的插入数据有两种方式：
1. 逐条插入
2. 批量插入

代码中实现的是批量插入。即爬取一个页面，一个页面中有20条tag信息，将这20条数据打包bulk.

数据长这个样子
![](https://i.imgur.com/yZu3DYB.png)

segmentfault站点下的569个标签页面一共采集到11380条数据
![](https://i.imgur.com/Tb0q117.png)

单线程下爬取和写入耗时269.183s
![](https://i.imgur.com/JdsLdsK.png)

### 绘制图表
通过kibana对elasticsearch的数据进行可视化，让数据变得直观，产生意义。
另外kibana 5以上新增加了词云这个功能，就是我们文章开头展示的那张图表。

kibana作图不涉及代码编写，但是各个指标跟维度需要梳理好关系，以及什么样的数据组合有意义。这个可以单独拿出来作为一篇文章，我也会抽出时间整理的。

### 扯淡
看的出来，社区以javascript的问题众多，以及Html5,Css3也分别位于第二位和第七位，看来最爱提问的是前端同学们。我想这个前端各种层出不穷的框架，以及js这个弱类型语言有很大的关系，并且通常这类问题比较具象，也较容易描述。

git这个版本控制工具的问题也不少，可是svn的身影我没有看到，看出来趋势了吧。

数据库方面问题最多的还是mysql。

在各种技术名词的标签下，还冒出一个程序员标签，排名第12位。emmmm，，，知道了你是个程序员，不用强调啦。

###GitHub
虽然程序很简单，但是当我完成下面的TODO也会继续更新下，我是个追求完美的程序员，尽管完美的事很难，当我们也要为之奋斗啊！

https://github.com/wkatios/segmentfault

### TODO
1. 爬虫对数据的抓取和写入数据库操作是一种比较耗费网络的行为，并非CPU密集型，可以改用多线程，或者协程，提高速度。
2. 多维度的数据抓取，好玩的事情通常需要更多的数据源和数据类型支持。
