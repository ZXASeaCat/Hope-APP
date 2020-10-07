import csv
import json
import itertools
# 调用实例
# TransformFormat.transjson('C:/Users/Administrator/Desktop/samples_min.csv', 'C:/Users/Administrator/Desktop/samples_min.json')
class TransformFormat:
    #json to csv
    @staticmethod
    def transToCsv(jsonpath, csvpath):
        json_file = open(jsonpath, 'r', encoding='utf8')
        csv_file = open(csvpath, 'w', newline='')
        #读文件
        ls = json.load(json_file)  #将json格式的字符串转换成python的数据类型，解码过程
        data = [list(ls[0].keys())]  # 获取列名,即key
        for item in ls:
            data.append(list(item.values()))  # 获取每一行的值value
        #写入文件
        for line in data:
            csv_file.write(",".join(line) + "\n")  # 以逗号分隔一行的每个元素，最后换行 fw.close() #关闭csv文件
        #关闭文件
        json_file.close()
        csv_file.close()
    

    #csv to json
    @staticmethod
    def transToJson(csvpath, jsonpath,fieldnames=None):
        csvfile = open(csvpath,'r', encoding='utf-8')
        jsonfile = open(jsonpath, 'w',encoding='utf-8')
        #fieldnames = ("code", "name")
        if(fieldnames == None):
            reader = csv.DictReader(csvfile)
        else:
            reader = csv.DictReader(csvfile, fieldnames)
        out = json.dumps( [ row for row in reader ] ,ensure_ascii=False)
        jsonfile.write(out)
        # 关闭文件
        csvfile.close()
        jsonfile.close()


    #对MIHBIH的CSV文件进行格式化
    @staticmethod
    def toNewFormat(oldpath='C:/Users/Administrator/Desktop/samples_min.csv', newpath='C:/Users/Administrator/Desktop/new.csv',setDay = '2020-01-01'):
        # 去除引号
        filein = open(oldpath, 'rt').readlines()
        fileout = open(oldpath, 'wt')
        for line in filein:
            fileout.write(line.replace("'", ""))
        fileout.close()

        # 改写Elapsed Time的值的格式，将字符串转换成“2020-01-01T00:00:00.000Z”格式
        # MongoDB导入该CSV时，将该列的属性设置为Date
        # 打印出来的列格式为： 2020-01-01 00:00:00.000000
        with open(oldpath, 'rt') as fin:
            with open(newpath, 'wt',newline="") as fout:
                reader = csv.reader(fin)
                writer = csv.writer(fout)
                #reader添加列名行
                for row in reader:
                    writer.writerow(row)
                    break
                #reader添加列名单位行
                for row in reader:
                    writer.writerow(row)
                    break
                #reader添加大量数据行
                for row in reader:
                    #加这行判断的原因是时间格式为'0:00.000'，而不是'00:00.000'
                    #if(row[0].__len__() == 8):  
                    row[0] = setDay + 'T00:0' + row[0] +'Z'
                    writer.writerow(row)
                fout.close()
            fin.close()

    #读取片段
    @staticmethod
    def readPartDate(path='D:/Desktop/samples_min.csv'):
        i, j = 0, 20
        with open(path, 'rt') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in itertools.islice(spamreader, i, j+1):
                print(', '.join(row))


