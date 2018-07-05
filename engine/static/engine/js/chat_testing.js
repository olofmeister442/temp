var API_SERVER_URL = "http://13.127.153.112";
//var API_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_SERVER_URL = "http://13.127.153.112";
//var STATIC_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_IMG_PATH = "/chat/static/engine/img";

var URL_IDENTIFIER = "chat"  // The url is built up like: API_SERVER_URL + URL_IDENTIFIER + METHOD NAME

$(document).ready(function() {
    var url = window.location.href;     // Returns full URL
    
    var id = url.split("/")
    var last = id[id.length-1];
    

    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/getsentences/",
        type: "GET",
        data: {
            intent_id: last
        },
        success: function(data){
            console.log(data);
            $("#query").html(data["name"]);
            $("#textarea1").val(data["sentences"]);
            $("#answerappend").html(data["answer"]);
            Materialize.updateTextFields();
        },
        error: function (jqXHR, exception) {
        },
    });
});



$('body').on('click','#save', function(){
    var url = window.location.href;     // Returns full URL
    
    var id = url.split("/")
    var last = id[id.length-1];
    
    var sentences = $("#textarea1").val();

    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/savesentences/",
        type: "GET",
        data: {
            intent_id: last,
            sentences: sentences
        },
        success: function(data){
//            window.location.href = "http://13.127.153.112/chat/chatbot_test/";
            Materialize.updateTextFields();
	    Materialize.toast("Saved succesfully",2000);
        },
        error: function (jqXHR, exception) {
        },
    });
});
