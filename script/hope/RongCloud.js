//跟融云相关的函数


//获取融云的token
function getToken(userId,userName){
    var rong_appkey = api.loadSecureValue({
        sync: true,
        key: 'rong_appkey'
    });
    var rong_skey = api.loadSecureValue({
        sync: true,
        key: 'rong_skey'
    });
    var rong_random = Math.random();
    rong_random = rong_random.toString().substring(2,8);
    var rong_second = parseInt(new Date().getTime()/1000);
    var rong_str = rong_skey+rong_random+rong_second;
    rong_str = SHA2(rong_str);
      api.ajax({
          url:"http://api.cn.ronghub.com/user/getToken.json",//融云Http请求
          method:"POST",
          headers: {
             "App-Key":rong_appkey,			//开发者平台分配的 App Key。
             "Nonce": rong_random,			//随机数
             "Timestamp": rong_second,		//时间戳，从 1970 年 1 月 1 日 0 点 0 分 0 秒开始到现在的毫秒数。
             "Signature": rong_str,			//数据签名,使用SHA1哈希加密
             "Content-Type": "application/x-www-form-urlencoded"
      },
          data:{
             values:{
                    "userId":userId,//这里先让用户id与name相同，测试
                    "name":userName,
                    //"portraitUri":rong_headimage
            }
         }
      },function(ret,err){
            var token=ret.token;
            alert(token);
            $api.setStorage(userId+"rong_token",token);
      });
}
