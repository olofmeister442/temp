var API_SERVER_URL = "http://13.127.153.112";
//var API_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_SERVER_URL = "http://13.127.153.112";
//var STATIC_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_IMG_PATH = "/chat/static/engine/img";

var URL_IDENTIFIER = "chat"  // The url is built up like: API_SERVER_URL + URL_IDENTIFIER + METHOD NAME

$(document).ready(function() {
    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/intenttesting/",
        type: "GET",
        success: function(data){
            ////
            
            
            $("#countintent").html("Intent Checking (" + data["intents"].length + ")");
            var list_intent = data["intents"];
            for(var i=0;i<list_intent.length;i++){
                var str = "";
                str += "<tr>";
                str += "<td>";
                str += list_intent[i]["sentence"];
                str += "</td>";
                str += "<td>";
                str += list_intent[i]["intent"]+" <br>Level: "+list_intent[i]["level1"];
                str += "</td>";
                str += "<td>";
                str += list_intent[i]["intent_recognized"]+" <br>Level: "+list_intent[i]["level2"];
                str += "</td>";
                str += "</tr>";
                $("#intentbody").append(str);
            }
        },
        error: function (jqXHR, exception) {
        },
    });

    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/mappertesting/",
        type: "GET",
        success: function(data){
            ////
            
            var list_intent = data["mappers"];
            for(var i=0;i<list_intent.length;i++){
                var str = "";
                str += "<tr>";
                str += "<td>";
                str += list_intent[i]["wordmapper_keyword"];
                str += "</td>";
                str += "<td>";
                str += list_intent[i]["intent"];
                str += "</td>";
                str += "<td>";
                str += list_intent[i]["intent_keyword_remove"];
                str += "</td>";
                str += "</tr>";
                $("#wordmapperbody").append(str);
            }
        },
        error: function (jqXHR, exception) {
        },
    });
});
