/* 模块简介
 chatBox是一个聊天输入框模块，
 集成了表情，从相册选取图片的功能。
 开发者可自定义表情集，
 只需简单配置即可实现自定义表情和添加点击事件
*/

/* 示例简介:
 打开一个 聊天输入框;
 每次用户输入后,都会显示在屏幕;
 每次用户输入后,都会随机得到一条有关 APICloud 的回复;
 若用户输入文字,直接显示到屏幕上;
 若用户输入表情,需要将表情图片显示到屏幕上;
 用户点击 增加 按钮,出现自定义界面;
 用户点击自定义页面的 相机 图标,可以选择 "拍照" 或者 从 "相册库" 选择照片;
 用户 拍照 或者 从 相册 选取照片成功后, 图片会显示到屏幕上, 并得到一条随机回复;
 用户点击 自定义页面的 位置 图标,可以获取当前位置,并将当前位置显示到屏幕上,并得到一条随机回复;
 */

if(window.isOpenChatBox){
    die(); // 已经打开 chatBox, 那就不再继续再打开了.
}

/*引入 chatBox 模块.*/
var chatBox = api.require('chatBox');

/* 创建一个 dl 来存放聊天记录. */
var dl = document.createElement("dl");
document.getElementsByTagName("body")[0].appendChild(dl);

var dt = document.createElement("dt");
dt.innerHTML = "<h3>欢迎体验 APICloud 聊天盒子</h3>";
dl.appendChild(dt);

var dtContent = document.createElement("dt");
var ddContent = document.createElement("dd");

dtContent.id = "dtContent";
ddContent.id = "ddContent";

dl.appendChild(dtContent);
dl.appendChild(ddContent);

/* 随机回复. */
var randomReply = [
    "APICloud,很好，很强大。",
    "APICloud重新定义移动应用开发",
    "支持APICloud",
    "APICoud, 七天开发一个APP",
    "APICloud, 超级好用，超级赞",
    "开发APP哪家强，APICloud 来帮忙",
    "APICloud, 陪你到永远",
    "APICloud带你装逼，带你飞"];

var sourcePath = "widget://image/chatBox/emotion"; /* 表情源文件.*/

var emotionData; /* 存储表情信息: JSON对象,以 表情字符 为属性名, 以 表情图片URL 为值.*/

getImgsPaths(sourcePath, function(emotion){
    emotionData = emotion;
});

chatBox.open({
    "switchButton": {
        "faceNormal": "widget://image/chatBox/face1.png",
        "faceHighlight": "widget://image/chatBox/face2.png",
        "addNormal": "widget://image/chatBox/add1.png",
        "addHighlight": "widget://image/chatBox/add2.png",
        "keyboardNormal": "widget://image/chatBox/key1.png",
        "keyboardHighlight": "widget://image/chatBox/key2.png"
    },
    "sourcePath": sourcePath,
    "addButtons": [
        {
            "normal": "widget://image/chatBox/cam1.png",
            "highlight": "widget://image/chatBox/cam2.png",
            "title": "图片"
        },
        {
            "normal": "widget://image/chatBox/loc1.png",
            "highlight": "widget://image/chatBox/loc2.png",
            "title": "位置"
        }
    ]
},function(ret,err)
{
    /* 此回调会在两种情况下触发:
     * 1. 用户输入文字或表情
     * 2. 用户 点击了 添加界面 的自定义按钮.
     */

    /* 用户点击了 添加界面的 自定义按钮. */

    if(ret["click"]){
        /* 用户点击 相机 图标 */
        if(0 == ret.index){
            api.confirm({
                title: "聊天盒子",
                msg: "您想要从哪里选取图片 ?",
                buttons:["优雅自拍", "相册收藏"]
            },function(ret,err){
                var sourceType = "album";

                if(1 == ret.buttonIndex){ /* 打开相机*/
                    sourceType = "camera";
                }

                api.getPicture({
                    sourceType: sourceType,
                    encodingType: 'jpg',
                    mediaValue: 'pic'
                }, function(ret, err){
                    if (ret) {
                        var imgSrc = ret.data;

                        var sendMsg = "<img src='" + imgSrc+ "' width='" + 160 +  "' height ='" + 90 +"' />";

                        diyChat(sendMsg);
                    }
                });

            });
        }

        /* 用户点击 位置 图标.*/
        if(1 == ret.index){
            /* 先判断是否有网. */
            if("none" == api.connectionType){
                api.toast({
                    msg: "没有网络,暂时无法获取位置信息",
                    duration: 1000,
                    location: "top"
                });

                return;
            }

            api.showProgress({title: "正在定位", text: "请稍候..."});
            var baiduLocation = api.require('baiduLocation');
            baiduLocation.startLocation({
                    accuracy: '100m'
                },
                function(ret, err){
                    api.hideProgress();
                    if(ret.status){
                        var sendMsg = "我在: 经度, " +  parseInt(ret.longitude) + " ; 纬度, " + parseInt(ret.latitude);
                        diyChat(sendMsg);
                        return;
                    }

                    api.toast({
                        msg: err.msg,
                        duration: 1000,
                        location: "top"
                    });
                });
        }

        return;
    }

    /* 用户输入了表情或者文字. */

    /* 使用读文件 方法,读json文件.*/
    var sendMsg = transText(ret.msg);

    diyChat(sendMsg);

    /* -------------------------------------------------------------- */

    /* 将文字中的表情符号翻译成图片,并可自定义图片尺寸. */
    function transText(text, imgWidth, imgHeight){

        var imgWidth = imgWidth || 30;
        var imgHeight = imgHeight || 30;

        var regx= /\[(.*?)\]/gm

        var textTransed = text.replace(regx,function(match){
            var imgSrc = emotionData[match];

            if( ! imgSrc){ /* 说明不对应任何表情,直接返回即可.*/
                return match;
            }

            var img = "<img src='" + imgSrc+ "' width='" + imgWidth +  "' height ='" + imgHeight +"' />";

            return img;
        });

        return textTransed;
    }

    /* -------------------------------------------------------------- */

    /* 自定义一个简易的问答界面. */
    function diyChat(sendMsg){
        var dt = document.getElementById("dtContent");
        var dd = document.getElementById("ddContent");

        dt.innerHTML = sendMsg;
        dd.innerHTML = "<div>" +randomReply[Math.floor(Math.random() * randomReply.length)] + "</div>" + "<br />";
    }
});

/* -------------------------------------------------------------- */

/* 一个工具方法: 可以获取 所有表情图片的名称和真实url地址, 以JSON对像形式返回;
 其中以表情文本为 属性名, 以图片真实路径为属性值. */

function getImgsPaths(sourcePathOfChatBox, callback){
    var jsonPath = sourcePathOfChatBox + ".json";

    api.readFile({
        path: jsonPath
    }, function(ret, err){
        if(ret.status){
            var emotionArray = JSON.parse(ret.data);

            var emotion = {};

            for(var idx in emotionArray){
                var emotionItem = emotionArray[idx];

                var emotionText = emotionItem["text"];
                var emotionUrl = "../image/chatBox/emotion/" + emotionItem["name"] + ".png";

                emotion[emotionText] = emotionUrl;
            }

            /* 把 emotion对象 回调出去. */
            if("function" === typeof(callback)){
                callback(emotion);
            }

        }
    });
}

window.isOpenChatBox = true; // 标记 chatBox 示例已经打开.