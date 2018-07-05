var API_SERVER_URL = "http://13.127.153.112";
//var API_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_SERVER_URL = "http://13.127.153.112";
//var STATIC_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_IMG_PATH = "/chat/static/engine/img";

var URL_IDENTIFIER = "chat"  // The url is built up like: API_SERVER_URL + URL_IDENTIFIER + METHOD NAME

$(document).ready(function() {
    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/testintent/",
        type: "GET",
        success: function(data){
            $("#countintent").html("Intent Checking (" + data["intents"].length + ")");
            var list_intent = data["intents"];
            if(list_intent.length == 0){
              str += "<tr>";
              str += '<td style="font-size:150%;font-weight:bold;color:green;">✔</td>';
              str += '<td style="font-size:150%;font-weight:bold;color:green;">✔</td>';
              str += '<td style="font-size:150%;font-weight:bold;color:green;">✔</td>';
              str += '<td style="font-size:150%;font-weight:bold;color:green;">✔</td>';
              $("#intentbody").append(str);     
              $("#aa").html('<h5>All the questions have <span class="green-text">passed succesfully</span>.</h5>');
              $("#bb").hide();
            }
            else{
            for(var i=0;i<list_intent.length;i++){
                var str = "";
                str += "<tr>";                
                str += "<td>";
                str += (parseInt(i)+1).toString();
                str += "</td>";
                str += "<td>";
                str += list_intent[i]["sentence"];
                str += "</td>";
                str += "<td>";
                str += '<a href="/chat/chat_testing/'+list_intent[i]["id1"]+'">'+list_intent[i]["intent"]+'</a>';
                str += "</td>";
                str += "<td>";
                str += '<a href="/chat/chat_testing/'+list_intent[i]["id2"]+'">'+list_intent[i]["intent_recognized"]+"</a>";
                str += "</td>";
                str += "</tr>";
                $("#intentbody").append(str);
            }
            }
	$("#loading-screen").hide();
        $("#intent-table").show();
        },
        error: function (jqXHR, exception) {
        },
    });
});
