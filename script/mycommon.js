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
