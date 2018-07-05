#!/user/bin/env python3
#-*- coding:utf-8 -*-

'''
主要待实现以下功能：
1. 每按回车，就显示一条糗百，开心一下.
2. 输入open回车，则用默认浏览器打开当前这条糗百
3. 过滤掉image/video，只显示纯text的糗事
4. 显示的形式为当前序号/内容/用户投票信息/当前糗百的Link
 
主要使用的第三方库为requests+lxml+xpath
当前code并未做异常处理，如在网络不通或不畅应该会出现异常报错退出，见谅，有兴趣的同学请自行完善。
'''

from lxml import etree
import requests
import os
import webbrowser

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

# 糗事百科页码
pagenum = 2
# 糗事内容保存在datalist中
datalist = []

# 初始化数据，获取首页的数据
def initQSData():
    # 首页的url
    url = 'https://www.qiushibaike.com'
    # 获取首页的数据
    initdatalist = getPageData(url)
    return initdatalist

# 过滤指定url页面的数据
def getPageData(url):
    # 用来保存页面的数据
    pageDataList = []
    r = requests.get(url, headers = headers).text
    html = etree.HTML(r)
    
    # 当前页面糗百的数目.
    pageTotalQiubaiNum = len(html.xpath('//div[@id="content-left"]/child::*'))
    # 当前糗百的投票信息
    voteinfo = []
    
    # 将页面数据经过滤后来后pageDataList中
    for i in range(1, pageTotalQiubaiNum):
        filterpre = '//div[@id="content-left"]/div[' + str(i) + ']'
        findfilter = filterpre + '/a/div[@class="content"]/span/text()'
        qiushibaikecontent = html.xpath(findfilter)
     
        # 当前糗百的subpage
        href = html.xpath(filterpre + '/a[@class="contentHerf"]/@href')[0]
        # 投票情况数(点赞数)
        voteinfo = html.xpath(filterpre + '//span[@class="stats-vote"]/i[@class="number"]/text()')
        # 投票情况数(评论数)
        discussNum = html.xpath(filterpre + '//span[@class="stats-comments"]//i[@class="number"]/text()')
        # 将两个list合并
        voteinfo.extend(discussNum)
        voteinfo.insert(0, '点赞: ')
        voteinfo.insert(2, '     评论: ')
        # 将list转化为字符串
        voteinfostr = ''.join(voteinfo)

        # 判断当前糗百是否显示不全(如果有查看全文字段则是显示不全)
        isExistViewFulltext = html.xpath(filterpre + '//span[@class="contentForAll"]')
        # 判断当前糗百是否存在图片
        isExistImg = html.xpath(filterpre + '//img[@class="illustration"]')
        # 判断当前糗百是否存在video
        isExistVideo = html.xpath(filterpre + '//video')
        
        # 过滤掉带image和video的糗百
        if len(isExistImg) == 1 or len(isExistVideo) == 1:
            continue
        
        # 如当前糗百显示不全(有查看全文字段)，测需要单独打开这首糗百来获取完整的糗百内容
        urlpre = 'https://www.qiushibaike.com'
        if len(isExistViewFulltext) != 1:
            qiushibaikecontent.append(voteinfostr)
            qiushibaikecontent.append(urlpre + href)
            pageDataList.append(qiushibaikecontent)
        else:
            newUrl = urlpre + href
            newr = requests.get(newUrl, headers = headers).text
            newHtml = etree.HTML(newr)
            newqiushicontent = newHtml.xpath('//div[@class="content"]/text()')
            newqiushicontent.append(voteinfostr)
            newqiushicontent.append(newUrl)
            pageDataList.append(newqiushicontent)
            
    return pageDataList   

# 加载非首页的数据,pagenum为列表的页码
def getNextpageData(pageNum):
    url = 'https://www.qiushibaike.com/8hr/page/' + str(pageNum)
    nextdatalist = getPageData(url)
    return nextdatalist

datalist = initQSData()

# 获取一个糗百数据
def getOneHappy(dataId):
    # 先大第一页开始读记录，如读完了就获取下一页的数据记录. 
    global pagenum
    datalistlen = len(datalist)-1
    
    # 如果序号要找到，就返回数据，如找不到，则再加载一个页面的数据
    if dataId <= datalistlen:
        data = datalist[dataId]
        # 获取数据后将当前item设置为空，以后占太多的内存空间
        datalist[dataId] = ''
        return data
    else:
        # 将新页面的数据直接加在之前的数据后面
        datalist.extend(getNextpageData(pagenum))
        pagenum  = pagenum + 1
        datalist[dataId] = ''
        return datalist[dataId]

# 开始嗨皮一下了        
def startHappy():
    print('是时候嗨皮一下了(数据from糗事百科)!!!')
    print('回车键可接着嗨皮, q退出, open用默认浏览器查看当前糗百@_@')
    qbId = 2
    happyId = 2
    # 直接输出第一条糗百
    happycontent = getOneHappy(1)
    print(f'\n\n第1条:\n')
    for item in range(len(happycontent)):
        if item == len(happycontent)-2:
            print('\n')
        print(happycontent[item].replace('\n', ''))
        
    while True:
        openurl = happycontent[-1].strip()
        enter = input().strip().lower()
        if enter == 'q':
            break
        elif enter == 'open':
            webbrowser.open(openurl)
        else:
            if happyId > 1:
                os.system('cls')
            print('是时候嗨皮一下了(数据from糗事百科)!!!')
            print('回车键可接着嗨皮, q退出, open用默认浏览器查看当前糗百@_@')
            
            happycontent = getOneHappy(happyId)
            # 有时happycontent会无故为空，如为空，则自动获取下一条，直到不为空为止
            while(len(happycontent) == 0):
                happyId = happyId + 1
                happycontent = getOneHappy(happyId)
                
            print('\n')
            print(f'第{qbId}条:\n')
            for item in range(len(happycontent)):
                if item == len(happycontent)-2:
                    print('\n')
                print(happycontent[item].replace('\n', ''))
            happyId = happyId + 1
            qbId = qbId + 1

if __name__ == '__main__':
    startHappy()
