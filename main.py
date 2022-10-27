#校园网真不行+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/10/** 1*:**
# @Author  : w2c
# email    : 524339236@qq.com
# @File    : handleArt.py
# @Software: PyCharm
# @question:    1.由于本机网络不稳定，故设置了每处理一个某年某月进行写入读出，若网络稳定可修改
#               2.代码145行对于超过长度限制的行的分割做的不好，期望可以分割为hanLP.parse()能够处理的最大长度
#               3.代码48行auth处需修改为自己hanLP的API密钥，的代码167行需修改为自己hanLP的每分钟调用次数，199行目前为从“今”到”古“，可修改。
#               4.其实可以自动读取note.txt中当前待处理的文件夹路径
#               5.后期由于字典过长导致向字典操作变慢，应考虑多存几个字典，目前看来，为了效率，每1-2年应存为一个字典，可以考虑在所有字典生成完后进行合并
import os
import re
import ast
import time
import pickle
# import linecache
from collections import defaultdict
from hanlp_restful import HanLPClient
# import hanlp


def dict_slice(adict, start, end):# 用于切割字典
    keys = adict.keys()
    dict_slice = {}
    for k in list(keys)[start:end]:
        dict_slice[k] = adict[k]
    return dict_slice


def setdir(dirpath):
    if os.path.exists(dirpath):
        pass
    else:
        os.makedirs(dirpath)


def setNewDictFile(dict,filepath):
    if not os.path.exists(filepath):
        with open(filepath, "wb") as tf:
            pickle.dump(dict, tf)


def saveDictFile(dict,filepath):
    with open(filepath, "wb") as tf:
        pickle.dump(dict, tf)


count1 = 0  # 计数，每分钟最多调用 hanLP API 50次，用于记录当前调用次数

HanLP = HanLPClient('https://www.hanlp.com/api', auth='ATU2NUBiYnMuaGFubHAuY29tOkNhUUhXeW9sVFlCV1BCYmM=', language='zh') # auth不填则匿名，zh中文，mul多语种

# ！！！！！由于程序运行周期过长，注意每次运行程序前修改为当前待处理的年月
current_year = 2003 # 当前年，用于记录当前正在处理文件的发布年份
current_month = 4   # 当前月，用于记录当前正在处理文件的发布月份
current_day = 1 # 当前天，用于记录当前正在处理文件的发布天份:D

# 字典控制，使每年的记录存在一个字典中
path_dict = './dict'
path_folder_dict_word2No = path_dict + '/word2No'
path_folder_dict_No2Paragraph = path_dict + '/No2Paragraph'
setdir(path_folder_dict_word2No)
setdir(path_folder_dict_No2Paragraph)

name_dict_word2No = 'dict_word2No' + str(current_year) + '.pkl'
name_dict_No2Paragraph = 'dict_No2Paragraph' + str(current_year) + '.pkl'
folders_dict_word2No = os.listdir(path_folder_dict_word2No)
folders_dict_No2Paragraph = os.listdir(path_folder_dict_No2Paragraph)

setNewDictFile(defaultdict(list), path_folder_dict_word2No + '/' + name_dict_word2No)
# if name_dict_word2No not in folders_dict_word2No:
#     tmp_dict = defaultdict(list)
#     with open(path_folder_dict_word2No + '/' + name_dict_word2No, "wb") as tf:
#         pickle.dump(tmp_dict, tf)
if name_dict_No2Paragraph not in folders_dict_No2Paragraph:
    tmp_dict = {}
    with open(path_folder_dict_No2Paragraph + '/' + name_dict_No2Paragraph, "wb") as tf:
        pickle.dump(tmp_dict, tf)
path_file_dict_word2No = path_folder_dict_word2No + '/' + name_dict_word2No
path_file_dict_No2Paragraph = path_folder_dict_No2Paragraph + '/' + name_dict_No2Paragraph

t3 = 0  # 用于记录处理某年某月文件夹的时间

chapter_No = 1  # 篇章号，用于生成形如“年月日-版号-篇章号-段号”的编号
paragraph_No = 1    #段号，用于生成形如“年月日-版号-篇章号-段号”的编号

dict10 = {} # 字典，key:val / Num:编号(1:'20000825-01-001-001')，用于存储下面列表中的每个元素所属的编号
list_handle = []    # 列表，用于存储待处理的句子（hanLP每次可以最多可以处理一个含有200个字符串的list
dict10_overflow = {}    # 字典，为了节约API调用次数，使每次都能处理满200个字符串，每次将一个文件的内容存入list_handle和dict10后会进行长度判断，该字典用于存储dict10超出200的部分
list_handle_overflow = []   # # 列表，为了节约API调用次数，使每次都能处理满200个字符串，每次将一个文件的内容存入list_handle和dict10后会进行长度判断，该列表用于存储list_handle超出200的部分

dict_word2typeOfWord = {}  # 键/值 : 词/词类标记, 看起来没什么用
dict_word2No = defaultdict(list)  # 键/值 : 词/编号, 可以将输入的词与编号关联
dict_No2Paragraph = {}  # 键/值 : 编号/段落, 可以通过编号输出段落内容

dir1_path = './data'    # 存储数据的根目录

note_txt = os.open('note.txt', os.O_RDWR | os.O_CREAT)   # 用于记录当前处理的年月，由于条件有限(笔记本会断网导致无法调用API而引起程序报错，如果发生在晚上可能无法及时发现并且windows可能会自动更新)，导致下次运行程序的起始年月未知

#处理某年某月文件夹
while current_year < 2004:  # 资料只到2003年
    t1 = time.time()    # 每个年月记录处理的起始时间
    os.write(note_txt, bytes('\n' + f'time{str(current_year)}-{str(current_month)}:' + str(t3) + '\n/' + 'current_year:' + str(current_year) + '/' + 'current_month:' + str(current_month), 'utf-8'))   # 写入当前处理的年月
    with open(path_file_dict_word2No, 'rb+') as f:   # 读取本地文件，好像是可以优化的，下次一定
        dict_word2No = pickle.load(f)
    with open(path_file_dict_No2Paragraph, 'rb+') as f:  # 读取本地文件，好像是可以优化的，下次一定
        dict_No2Paragraph = pickle.load(f)
    dir2_path = dir1_path + '/' + str(current_year) + '年' + str(current_month).rjust(2, '0') + '月'  # 某年某月的文件夹路径
    folders = os.listdir(dir2_path) # 获取某年某月文件夹中的文件
    num = 0
    for file in folders:    # 依次处理文件
        num += 1
        if num%100 == 0:
            print(f'{time.time()-t1}当前路径:{dir2_path}, 进度:{num}/{len(folders)}') # 记录程序运行状态

        file_path = dir2_path + '/' + file  # 待处理文件路径
        f = open(file_path, encoding = 'utf-8') # open待处理文件
        lines = f.readlines()   # lines[0]:题目(### xxx xxx) ///// lines[1]:作者(有时为空, 多作者时形如王泽辰康金泉) ///// lines[2]:时间(year-month-day) ///// lines[3]:版号与分类(第x版(政治·法律·社会)) ///// lines[4]:无意义, 一般为(专栏：) ///// lines[5]:一般为空行 ///// lines[6:]:正文
        topic = '_'.join(lines[0].split()[1:])  # 题目/ 题目可能有多句话，用'_'将题目连接 ///// .split[0]为'###', 舍弃
        # author = '_'.join(lines[1])    # 没啥用，作者一般在正文中都有
        author = lines[1][:-1]  # 作者/ [:-1]为去掉换行符'/n'
        times = (''.join(lines[2].split('-')))[:-1]  # 时间/ [:-1]为去掉换行符'/n'
        if current_day != times[6:]:
            chapter_No = 1
        # current_year = times[:4]  # 多余，影响程序运行
        # current_month = times[4:6]    # 多余，影响程序运行
        current_day = times[6:] # 当前天，主要用于判断当前天是否与报文发布的天相等，用于更新篇章号，因为每一天的篇章号都要从001开始
        edition_No = lines[3][1].rjust(2, '0')  # 版号/ 字符串左侧用'0'补齐
        # types = (((lines[3].split('('))[1])[:-2]).split('·')   # 文章类型/ 目前没用，后期可以增加通过分类查询文章，并根据文章名检索并输出文章，但是文章太多了
        # special_column = lines[4][3:]   # 专栏/ 目前没用，后期可以增加通过专栏查询文章，并根据专栏名检索并输出文章，但是文章太多了
        body = lines[6:]    #正文/

        # 处理正文
        for line in body:   # 正文中的每一行
            head = '-'.join([times, edition_No, str(chapter_No).rjust(3, '0'), str(paragraph_No).rjust(3, '0')])   # 编号，'19561101-02-001-001'
            line = line.replace(' ', '')    # 去掉行中的空格
            line = line.replace('　', '')
            line = line.replace('\t', '')
            if not line.isspace():
                dict_No2Paragraph.setdefault(head, line)    # 生成 '编号/段落内容' 字典
            #  由于hanLP.parse()处理的字符串内容有限制，在构造待处理list和dict时需要进行处理
            if line.isspace():  # 判断行是否为空，因为hanLP.parse()为空会报错！！！
                continue
            elif len(line) < 150:   # 因为hanLP.parse()每行不能超过150字符
                list_handle.append(line)    # 如果该行长度符合条件，将该行加入待处理list
                dict10.setdefault(len(list_handle), head)   # 如果该行长度符合条件，记录该行编号
                paragraph_No += 1   # 段号+1
            else:
                index_prev = len(list_handle)   # 当前待处理list的长度，
                tmp = re.findall(r'.{40}', line)    # 这里可能分割掉一个词语。造成损失。如果该行超过限制长度，分割 # urllib.error.HTTPError: HTTP Error 400: {"detail":"Text exceeds max-length of 15000 characters."}
                while '' in tmp:    # 去除空的元素，避免出现空的处理项（尚未触发过错误
                    tmp.remove('')
                list_handle = list_handle + tmp # 将分割后的字符串list合并入待处理list
                for i in range(index_prev+1, len(list_handle)+1):   # 因为分割了超过限制的字符串，这里需要将分割后的字符串的各个部分与同一个编号对应，所以用到了循环
                    dict10.setdefault(i, head)
                paragraph_No += 1   # 段号+1

        paragraph_No = 1    # 处理完一篇文章，段号重置为1
        chapter_No += 1 # 此为第一层循环，每循环一次文章序号+1

        # 由于hanLP每次处理字符串数目有限，如果超过200个字符串则需要进行处理
        if len(list_handle) < 200:    # 200代表了当list_handle中存储了大于200个句子时，调用一次API对该list进行分词和词性标注
            pass
        else:
            list_handle_overflow = list_handle[200:]    # 因为hanLP一次只能处理200个字符串，这里存储待处理list中超过200的部分
            list_handle = list_handle[:200] # 处理好溢出后，待处理list只保留前200个字符串

            dict10_overflow = dict_slice(dict10, 200, len(dict10))  # 因为hanLP一次只能处理200个字符串，这里存储字典中超过200的部分
            dict10 = dict_slice(dict10, 0, 200) # 处理好溢出后，字典只保留前200个键值对

            # 由于 hanLP API 调用次数有限，如果一分钟超过50次则需要进行处理
            if count1 < 44: # 计数，因为 hanLP API 每分钟只能调用50次
                if count1 == 0:
                    time_start = time.time()
                dict_win = HanLP.parse(list_handle, tasks='pos/pku').to_dict()  # 存储进行过分词和词性分析后的字典
                for i in range(len(dict_win['tok/fine'])):
                    for j in range(len(dict_win['tok/fine'][i])):
                        dict_word2typeOfWord.setdefault(dict_win['tok/fine'][i][j], dict_win['pos/pku'][i][j])  # 向字典dict_word2typeOfWord中添加键值对（词:词性
                        if not dict10[i+1] in dict_word2No[dict_win['tok/fine'][i][j]]:
                            dict_word2No[dict_win['tok/fine'][i][j]].append(dict10[i+1])    # 向字典dict_word2No中添加键值对（词:编号
                count1 += 1 # 计数+1
            else:
                time_wait = 60-(time.time()-time_start)+ 2 # 如果一分钟已经调用了50次API，记录需要等待的时间，2防止误差
                if time_wait > 0:   # 如果需要等待
                    print(f'调用次数耗尽，需等待{time_wait}秒')    # 输出提示
                    time.sleep(time_wait)   # 程序暂停
                    count1 = 0  # 重新计数
                else:   # 等待时间为负，则无需等待
                    count1 = 0  # 重新计数

            list_handle = list_handle_overflow  # 调用一次API后，将溢出写入待处理list，下次调用API时处理
            list_handle_overflow = []   # 待处理list溢出清零
            dict10 = {} # 字典清零
            for i in range(len(dict10_overflow)):   # 调用一次API后，将字典溢出谢日字典，下次调用API处理，并重新赋key值与待处理list对应
                dict10.setdefault(i + 1, dict10_overflow[i + 201])  # dict10的key从1开始
            dict10_overflow = {}  # 字典溢出清零

    saveDictFile(dict_word2No, path_file_dict_word2No)# 每处理完一个某年某月文件夹后，将字典写入，及时保存
    saveDictFile(dict_No2Paragraph, path_file_dict_No2Paragraph)# 每处理完一个某年某月文件夹后，将字典写入，及时保存

    if int(current_month) < 12: # 处理完某年某月文件后，如果月份小于12
        current_month += 1  # 月份+1
    else:   # 否则（月份为12
        current_year -= 1   # 年份+1
        current_month = 1   # 月份赋1
        # 字典控制，使每年的记录存在一个字典中
        tmp_dict = defaultdict(list)
        name_dict_word2No = 'dict_word2No' + str(current_year) + '.pkl'
        name_dict_No2Paragraph = 'dict_No2Paragraph' + str(current_year) + '.pkl'
        path_file_dict_word2No = path_folder_dict_word2No + '/' + name_dict_word2No
        path_file_dict_No2Paragraph = path_folder_dict_No2Paragraph + '/' + name_dict_No2Paragraph
        saveDictFile(tmp_dict, path_file_dict_word2No)

        tmp_dict = {}
        saveDictFile(tmp_dict, path_file_dict_No2Paragraph)

    t2 = time.time()    # 每个年月记录处理的结束时间
    t3 = t2 - t1
    print(t3)    # 输出该年月处理的时间
os.close(note_txt)  # close文件