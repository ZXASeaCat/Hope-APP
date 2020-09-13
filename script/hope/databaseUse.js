///
//需要引入SHA1算法、RESTAPI两个js文件
///

//插入
//className    数据表名
//<data>       数据
//insertRet    插入数据后执行的函数
function insert(className,data,insertRet)
{
	var client = new Resource();
    var Model = client.Factory(className);
    Model.save(data, function (ret,err) {
    	insertRet(ret);
    });
}

//往指定表插入一行数据
//className:表名称  insertFields:插入列
function insertUpdate(className,insertFields)
{
    var app = {};
    getAppConfig(app);
    api.ajax({
        url: 'https://d.apicloud.com/mcm/api/'+className,
        method: 'post',
        headers:
        {
            "X-APICloud-AppId": app.appId,
            "X-APICloud-AppKey": app.encryptAppKey
        },
        data: insertFields
    }, function(ret, err) {
        console.log(JSON.stringify(ret));
    });
}
//更新数据（根据条件）
//className 	数据表名
//where     	查询条件
//fields    	要更新的数据
//updateRet    更新数据后执行的函数
function update(className,where,fields,updateRet)
{
	var client = new Resource();
    var Model = client.Factory(className);
    Model.query({
      filter:{
        where:where,
        fields:["id"],//主键
      }
    },function (ret,err) {
	    if(ret[0])
	    {
			Model.save({"_id":ret[0]["id"]},fields,function(ret,err){
				updateRet(ret);
			});
	    }
    });
}

//更新数据（根据云数据库ID）
//className 	数据表名
//id    		进行更新的数据主键ID
//fields    	要更新的数据
//updateRet    更新数据后执行的函数
function updateAPICloud(className,id,fields,updateRet)	//审核功能check.html用到了
{
	var client = new Resource();
    var Model = client.Factory(className);
    Model.save({"_id":id},fields,function(ret,err){
				updateRet(ret);
			});
}
//如果存在就更新，不存在就插入数据
//className 数据表名
//where     查询条件，如果不存在，该条件所包含的信息会被插入,JSON
//fields    要更新的数据,JSON
//updateRet    更新数据后执行的函数
//insertRet    插入数据后执行的函数
function updateOrInsert(className,where,fields,updateRet,insertRet)
{
	var client = new Resource();
    var Model = client.Factory(className);
    Model.query({
      filter:{
        where:where,
        fields:["id"],//主键
      }
    },function (ret,err) {
	    if(ret[0])
	    {
			Model.save({"_id":ret[0]["id"]},fields,function(ret,err){
				updateRet(ret);
			});
	    }
	    else {
			//合并查询条件和更新的数据
			var data = mergeJsonObject(where, fields);
	        Model.save(data, function (ret,err) {
	        	insertRet(ret);
	        });
	    }
    });
}

//查询数据
//className 数据表名
//where     查询条件，如果不存在，该条件所包含的信息会被插入		JSON数据
//fields    要查询的数据,null返回所有列					 	  字符串数组
//classlink 查询时需要联立的表									字符串数组，对应着多个表的表名，同时也是className表的所有pointer列名
//classlinkwhere  联合查询的联立表的过滤条件						 JSON数据,每个JSON数据对应着上面每个表的过滤条件，classlink要与classlinkwhere长相同度
//success   查询成功后执行的函数
//fail      查询失败后执行的函数
function query(className,where,fields,classlink,classlinkwhere,success,fail)
{
	var client = new Resource();
	var Model = client.Factory(className);
    var filter = {};
    if(where != null)
        filter["where"] = where;
    if(fields != null)
        filter["fields"] = fields;
	//考虑到classlink数组会被修改，这里的if语句必须放在前面
	if(classlinkwhere != null)
	{
		var json = {};
		for(var i = 0;i<classlink.length;i++)
			json[classlink[i]] = classlinkwhere[i];
        filter["includefilter"] = json;
	}
	if(classlink != null)
	{
		//apicloud云数据库规范
		for(var i = 0;i<classlink.length;i++)
			classlink[i] = classlink[i] + "Pointer";
        filter["include"] = classlink;
	}
	Model.query({
	  filter:filter
	},function (ret,err) {
		if(ret[0])
		{
			success(ret);
		}
		else {
			fail(ret);
		}
	});
}

//classNameArray      查询表集合           字符串数组
//where               查询条件         JSON数据
//根据某个条件（通常是主键外键）查询多个表
function batchSelect(classNameArray,where,success,fail)
{
	let jsonArray = [];
	for(let i=0;i<classNameArray.length;i++)
		jsonArray.push({
			method: 'get',
			path : "/"+classNameArray[i]+"?filter="+JSON.stringify({where:where}) ,
		});
	let client = new Resource();
	client.batch(jsonArray,
		function(ret, err)
		{
			if(ret[0]){
				success(ret);
			}
			else {
				fail(err);
			}
		}
	);
}

///表名
//需要更新的数据对应主键ID，是数组
//该函数是对同一张表的一些数据进行相同的操作
function batchUpdate(className,idArray,body,success,fail)
{
	let jsonArray = [];
	for(let i=0;i<idArray.length;i++)
		jsonArray.push({
			method: 'put',
			path : "/"+className+"/"+idArray[i],
			body : body,
		});
	let client = new Resource();
	client.batch(jsonArray,
		function(ret, err)
		{
			if(ret[0]){
				success(ret);
			}
			else {
				fail(err);
			}
		}
	);
}
//合并两个json对象
function mergeJsonObject(jsonbject1, jsonbject2) {
	var resultJsonObject={};
	for(var attr in jsonbject1){
		resultJsonObject[attr]=jsonbject1[attr];
	}
	for(var attr in jsonbject2){
		resultJsonObject[attr]=jsonbject2[attr];
	}
	return resultJsonObject;
};
