import pymongo 

class MongodbHelper:
    #########  静态属性，client配置  #########
    client = pymongo.MongoClient(host='127.0.0.1') 
    @classmethod
    def initClient(cls):
        return cls.client

    #########  显示所有数据库名字  #########
    @staticmethod
    def showDataBase():
        client = MongodbHelper.initClient()
        db_list = client.list_database_names()
        print(db_list)


    ##########  插入数据，可重复插入  #########
    ##   参数  ## 
    #  dbname       数据库
    #  classname    数据表
    #  fields       需要插入的数据

    ##  返回值 ##
    #  ret          插入成功，返回ObjectId;插入失败,返回None
    @staticmethod
    def insert(dbname,classname,fields):
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        ret = collection.insert_one(fields)
        try:
            return ret
        except:
            return None

    #########  插入数据，若存在数据则不插入  #########
    #  参数
    #  dbname       数据库
    #  classname    数据表
    #  where        查重字段；where的字段必须包含于data的字段
    #  fields       需要插入的数据

    #  返回值
    #  ret          插入成功，返回ObjectId;插入失败,数据已存在,返回None插入失败
    
    @staticmethod
    def insertCheck(dbname,classname,where,fields):
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        ret = collection.update(
            where,
            {'$setOnInsert': fields},
            upsert=True
        )
        if(ret['updatedExisting'] == True):
            return None
        else:
            return ret['upserted']


    #########  更新数据，存在就更新，否则就不管  #########
    #  参数
    #  dbname       数据库
    #  classname    数据表
    #  where        查重字段；where的字段必须包含于data的字段
    #  fields       需要插入的数据

    #  返回值
    #  ret          更新成功，返回True;更新失败,返回False
    @staticmethod
    def update(dbname,classname,where,fields):
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        ret = collection.update(
            where,
            {'$set': fields}
        )
        if(ret['updatedExisting'] == True):
            return True
        else:
            return False


    #########  更新数据，存在就更新，否则就插入  或者  插入数据，存在就覆盖  #########
    #  参数
    #  dbname       数据库
    #  classname    数据表
    #  where        查重字段；where的字段必须包含于data的字段
    #  fields       需要插入的数据

    #  返回值
    #  ret          更新成功，返回True;不存在数据，则插入数据,返回ObjectId
    @staticmethod
    def updateOrInsert(dbname,classname,where,fields):
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        ret = collection.update(
            where,
            {'$set': fields},
            upsert=True
        )
        if(ret['updatedExisting'] == True):
            return True
        else:
            return ret['upserted']

    #########  根据查询条件，查询数据  #########
    #  参数
    #  dbname       数据库
    #  classname    数据表
    #  where        查重字段；where的字段必须包含于data的字段
    #  fields       需要插入的数据

    #  返回值
    #  ret          返回的数据是JSON数组
    @staticmethod
    def query(dbname,classname,where={},fields=None):
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        if(fields==None):
            results = collection.find(where)
        else:
            results = collection.find(where, fields)
        ret = []
        for r in results:
            ret.append(r)
        return ret



    #########  查询指定数量数据  #########
    #  dbname           数据库
    #  classname        数据表
    #  limitCount       此次查询数据数量
    #  skipCount        跳过前几行数据
    #  cursorMoveSteps  游标每次移动步数，设置后查询的数据数量 ret.__len()__ = limitCount / (cursorMoveSteps + 1)
    #  fields           该返回哪些列，默认不返回标识列_id
    #  ret              返回的数据是JSON数组
    @staticmethod
    def queryCount(dbname,classname,limitCount=0,skipCount=0,cursorMoveSteps=0,fields={"_id":0}):
        ret = []
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        if(limitCount ==0 and cursorMoveSteps==0):
            results = collection.find({},fields).skip(skipCount)
            for r in results:
                ret.append(r)
        elif(limitCount != 0 and cursorMoveSteps ==0):
            results = collection.find({},fields).limit(limitCount).skip(skipCount)
            for r in results:
                ret.append(r)
        elif(limitCount == 0 and cursorMoveSteps !=0):
            results = collection.find({},fields).skip(skipCount)
            for r in results:
                ret.append(r)
                try:
                    for i in range(cursorMoveSteps-1):
                        results.next()
                except:
                    return ret 
        else:
            results = collection.find({},fields).limit(limitCount * cursorMoveSteps).skip(skipCount)
            # for语句每次循环都会调用一次results.next()
            for r in results:
                ret.append(r)
                #游标每次一次性移动多步
                #注意！假如一次移动5步，即从第1步移动到第6步；那么在下一次循环前移动到第5步，即next4次
                try:
                    for i in range(cursorMoveSteps-1):
                        results.next()
                #可能会超出下标,但此时只需直接返回数据
                except:
                    return ret 
        return ret


    #########  查询心电图指定数量数据  #########
    # queryCount改良，主要是为了将Elapsed time字段的数据格式化，方便客户端的Echart使用
    @staticmethod
    def queryECGCount(dbname,classname,limitCount=0,skipCount=0,cursorMoveSteps=0,fields={"_id":0}):
        ret = []
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        if(limitCount ==0 and cursorMoveSteps==0):
            results = collection.find({},fields).skip(skipCount)
            for r in results:
                #读取出来的time是datetime.datetime对象，需要转换成时间戳
                #当然，如果为了提高效率，可以让MongoDB的["Elapsed time"]列属性改为timestamp，然后删除下面这句代码
                r["Elapsed time"] = r["Elapsed time"].timestamp()*1000
                ret.append(r)
        elif(limitCount != 0 and cursorMoveSteps ==0):
            results = collection.find({},fields).limit(limitCount).skip(skipCount)
            for r in results:
                r["Elapsed time"] = r["Elapsed time"].timestamp()*1000
                ret.append(r)
        elif(limitCount == 0 and cursorMoveSteps !=0):
            results = collection.find({},fields).skip(skipCount)
            for r in results:
                r["Elapsed time"] = r["Elapsed time"].timestamp()*1000
                ret.append(r)
                try:
                    for i in range(cursorMoveSteps-1):
                        results.next()
                except:
                    return ret 
        else:
            results = collection.find({},fields).limit(limitCount*cursorMoveSteps).skip(skipCount)
            for r in results:
                r["Elapsed time"] = r["Elapsed time"].timestamp()*1000
                ret.append(r)
                try:
                    for i in range(cursorMoveSteps-1):
                        results.next()
                except:
                    return ret 
        return ret


    ######################  
    #  根据查询条件，关联查询数据（1条数据对应1条数据）
    #  这里实现的是一对多的表，[a1→[b1,b2,b3]];
    #  反过来可实现[b1→a1,b2→a1,b3→a1]  
    ######################
    @staticmethod
    def queryInclude(dbname,localClass,foreignClass,foreignField,where={},fields={'users.age':1,'name':1}):
        client = MongodbHelper.initClient()
        db = client[dbname]
        collection = db[classname]
        where={foreignClass+".age":"25"}
        #当前表A
        results = collection.aggregate(
            [
                {
                    '$lookup':
                        {
                            "from": foreignClass , #需要联合查询的另一张表B
                            "localField": foreignField,   #表A的字段
                            "foreignField": foreignField, #表B的字段
                            "as": foreignClass   #根据A、B联合生成的新字段名，即关联字段，这里用表B代表
                        },
                },
                {
                    '$project':fields                        #联合查询后需要显示哪些字段，1：显示
                },
                {
                    '$match': where                          #根据哪些条件进行查询,只能查询A表的字段
                }
            ]
        )
        ret = []
        for r in results:
            ret.append(r)
        return ret
