# 搜索文件
import pickle
import time
import os
cin = input("请输入：")
time_start = time.time()
sum = 0

path_dict = './dict'

path_dict_word2No = path_dict + '/word2No'
path_dict_No2Paragraph = path_dict + '/No2Paragraph'

folders_dict_word2No = os.listdir(path_dict_word2No)
folders_dict_No2Paragraph = os.listdir(path_dict_No2Paragraph)

for i in range(len(folders_dict_word2No)):
    file_dict_word2No_path = path_dict_word2No + '/' + folders_dict_word2No[i]    # （解决）首个文件有问题，需要重新训练
    file_dict_No2Paragraph_path = path_dict_No2Paragraph + '/' + folders_dict_No2Paragraph[i]
    print(folders_dict_word2No[i] + folders_dict_No2Paragraph[i])
    with open(file_dict_word2No_path, "rb") as tf:
        dict_word2No = pickle.load(tf)
    with open(file_dict_No2Paragraph_path, "rb") as tf:
        dict_No2paragraph = pickle.load(tf)
    sum +=len(dict_word2No[cin])
    for i in dict_word2No[cin]:
        print(f'{i}-{dict_No2paragraph[i]}')
time_end = time.time()
print(f'共查询到{sum}条记录, 耗时{time_end-time_start}秒')