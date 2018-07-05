var last_asked = get_current_time_in_milliseconds();
var timeout_interval = 60000;
var help_request_shown = false;
var update_called=false;
var in_flow=true;
setInterval(function() {
  console.log("Set Interval");
  if ((get_current_time_in_milliseconds() > last_asked + timeout_interval) && !help_request_shown && update_called && !in_flow) {
    console.log("Inside?");
    //add_response(help_suggestions[Math.floor(Math.random()*help_suggestions.length)]);
    //ajaxCallToIndex("custom2","1");
    //help_request_shown = true;
  }
}, timeout_interval);

function get_current_time_in_milliseconds() {
  return (new Date()).getTime();
}

function getCookie(name) {
   var cookieValue = null;
   if (document.cookie && document.cookie !== '') {
       var cookies = document.cookie.split(';');
       for (var i = 0; i < cookies.length; i++) {
           var cookie = jQuery.trim(cookies[i]);
           // Does this cookie string begin with the name we want?
           if (cookie.substring(0, name.length + 1) === (name + '=')) {
               cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
               break;
           }
       }
   }
   return cookieValue;
}

var user_id = '';
var like_cnt = 2;
var query_cnt = 0;
var ask_3min = 1;
var mic_button_set = false;
var global_string = "";

var API_SERVER_URL = "";
//var API_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_SERVER_URL = "";
//var STATIC_SERVER_URL = "http://192.168.0.103:8000";
var STATIC_IMG_PATH = "/chat/static/engine/img";

var URL_IDENTIFIER = "chat"  // The url is built up like: API_SERVER_URL + URL_IDENTIFIER + METHOD NAME
                             // Example is: http://127.0.0.1:8000/chat/updateuser
                             //                  API_SERVER_URL        chat = URL_IDENTIFIER        updateuser = METHOD NAME

var scroll_to_bottom = function() {
  $('#style-2').scrollTop($('#style-2')[0].scrollHeight);
};

try{
   // console.log("WTF");
    var settings = {
        continuous:true, // Don't stop never because i have https connection
        onResult:function(text){
            ////
            if(text!="")
                $('#query').val(text);
            else{
                $("#submit-img").click();
                stopRecognition();
            }
        },
        onStart:function(){
            ////
        },
        onEnd:function(){
        }
    };

    var artyom = new Artyom();
    var UserDictation = artyom.newDictation(settings);
    function startRecognition(){
      UserDictation.start();
    }

    function stopRecognition(){
      UserDictation.stop();
    }
    console.log("WTF");
    stopRecognition();
    ////
    mic_button_set = true;
    console.log(mic_button_set);
}
catch(err){
    ////
    console.log(err);
}


function s4() {
return Math.floor((1 + Math.random()) * 0x10000)
  .toString(16)
  .substring(1);
}

function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

function setPcId(pcid){
    if((typeof pcid === 'undefined') || (pcid == null)){
        //pc_id = guid();
        //Cookies.set('pc_id', pc_id);
        var csrftoken = getCookie('csrftoken');
        $.ajax({
                url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/pcid",
                type: "GET",
                data : {
                    //pcid : pc_id,
                    this_cookie: csrftoken,
                },
                success: function(data){
                  pc_id = data["pc_id"];
                }
        });
    }
}

function returnTime(){
    var d = new Date();
    var hours = d.getHours().toString();
    var minutes = d.getMinutes().toString();
    var flagg = "AM";
    if(parseInt(hours) > 12){
        hours = hours - 12;
        flagg = "PM";
    }
    if(hours.length==1){
        hours = "0"+hours;
    }
    if(minutes.length==1){
        minutes = "0"+minutes;
    }

    var time = hours+":"+minutes+" "+flagg;
    return time;
}

function appendResponseServer(sentence, flag, url1, url2){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<strong>","<b>");sentence = sentence.replace("</strong>","</b>");
    sentence = sentence.replace("<em>","<i>");sentence = sentence.replace("</em>","</i>");
    sentence = sentence.replace('background-color:#ffffff; color:#000000','');
    sentence = sentence.replace("background-color:#ffffff;","");
    //
    var html =
    '<div class="row chatmessage">\
        <div class="col s1 l1" >\
           <img src='+STATIC_SERVER_URL+STATIC_IMG_PATH+'/sbi.png  class="circle"  width=34 class="chatbot_left_image">\
        </div>\
        <div class="col s10 m10">\
           <div class="chip chip2 chip_left" >\
              <span>'+sentence+'</span>\
           </div>\
        </div>';
    like_cnt++;
    if(flag == "true"){
   // html+= '<div class="timestampl" >'+returnTime()+</div>;
    }
    else{
    html += '<div class="timestampl" >\
            '+returnTime()+'\
        </div>\
    </div>\
    ';
    }
    $("#style-2").append(html);
}

function appendButtons(list, pipe){
    ////
    var string = '';
    for(var i=0;i<list.length;i++){
        if(list[i] == "Apply Now" || list[i] == "Get Now" ){
            string += '<button class="button4 button5 chipbutton" pipe="'+pipe+'">';
            string += list[i];
            string += '</button>';
        }
        else{
            string += '<button class="button2 button3 chipbutton" pipe="'+pipe+'">';
            string += list[i];
            string += '</button>';
        }
    }
    var html = '\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s10 l10">\
           <div>'+
              string
           +'</div>\
        </div>\
    </div>\
    ';
    $("#style-2").append(html);
}
function appendResponseUser(sentence){
    sentence = sentence.replace("<p>","");sentence = sentence.replace("</p>","");
    sentence = sentence.replace("<","#");sentence = sentence.replace(">","#");
    var a_tag = '<a name="id'+query_cnt+'"/>';
    var html = a_tag +
    '<div class="row chatmessage">\
        <div class="col s3">\
        </div>\
        <div class="col s9">\
            <div class="chip chip2 right chip_right">\
                <span>'+sentence+'</span>\
            </div>\
        </div>\
        <div class="timestampr" >'+returnTime()+'</div>\
    </div>\
    ';
    $("#style-2").append(html);
    scroll_to_bottom();
}

function appendRecommendationsList(list){
    if(list.length > 0){
        var html =
        '<div class="row chatmessage">\
            <div class="col s2">\
               <img src='+STATIC_SERVER_URL+STATIC_IMG_PATH+'/sbi.png width="34"  class="circle" class="chatbot_left_image" >\
            </div>\
            <div class="col s9 l9">\
               <div class="button-group button-group2" style="margin-top:4px;">\
               ';

        for(var i=0;i<list.length;i++){
            html += '<div class="button recommendation_style chiprecommendation">'+list[i]+'</div>';
        }
        html += '</div>';

        html += '</div>\
            <div class="timestampl">'+returnTime()+'</div>\
         </div>\
        ';
        $("#style-2").append(html);
    }
}

function setUUID(uuid){
    if((typeof uuid === 'undefined') || (uuid == null)){
        //user_id = guid();
        ////
        //Cookies.set('uuid', user_id);
        var csrftoken = getCookie('csrftoken');
        $.ajax({
                url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/updateuser",
                type: "GET",
                data : {                    
                    this_cookie: csrftoken,
                },
                success: function(data){
                      ////
                      update_called = true;
                      response = data["response"];
                      user_id = data["user_id"]
                      recommended_queries = data["recommended_queries"]
                      is_typable = data["is_typable"]
              reponse = response.replace("background-color:#ffffff;","");
                      if(!((typeof response === 'undefined') || (response == null))){
                        disableOrEnableInput(is_typable, response);
                        ////
                        list = splitByDollar(response);
                        ////
                        if(!((typeof data["is_answer"] === 'undefined') || (data["is_answer"] == null))){
                            ////
                            if(data["is_answer"] == "true"){
                                global_string = "";
                            }
                            for(var i=0;i<list.length;i++){
                                if(i==list.length-1)
                                    appendResponseServer(list[i], data["is_answer"], data["upvote_link"], data["downvote_link"]);
                                else
                                    appendResponseServer(list[i], false, "", "");
                            }
                        }
                        else{
                             for(var i=0;i<list.length;i++){
                                appendResponseServer(list[i], false, "", "");
                             }

                        }
                      }
                      if(!((typeof recommended_queries === 'undefined') || (recommended_queries == null))){
                        ////
                        appendRecommendationsList(recommended_queries);
                      }
                      //global_string += "main |";
                      //ajaxCallToIndex("main","0");
                      //$("#query").focus()
                }
        });
    }
    else{
        //user_id = uuid;
        ////
    }
}

$(document).ready(function() {
    document.cookie = Math.random();
    //$("#query").focus();
    $("#navig").css("background-color","#FFF");

    var uuid = null;
    var pcid = null;

    setPcId(pcid);
    setUUID(uuid);

    if(mic_button_set){
        $("#submit").append('<img id="submit-mic" onclick="startRecognition()" src='+STATIC_SERVER_URL+STATIC_IMG_PATH+'/mic.png width=28 class="responsive-img">');
        $("#submit-img").css({'display':'none'});
    }
    else
        $("#submit-img").attr('src',STATIC_SERVER_URL+STATIC_IMG_PATH+'/send1.png');
});

function convertStrongToBold(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = sentence.replace("<strong>","<b>");
        sentence = sentence.replace("</strong>","</b>");
    }
    return sentence;
}

function removeWhiteSpaces(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = sentence.replace(" ","");
    }
    return sentence;
}

function enableInput(query){
    $("#query").removeAttr('disabled');
    if(!((typeof query === 'undefined') || (query == null))){
        query = removePTag(query);
        $("#query").attr("placeholder","Please type your query here.");
    }
}

function disableInput(){
    $('#query').val("");
    $('#query').attr('placeholder','Please select an option from the above choices');
    $("#query").attr('disabled','disabled');
}

function disableOrEnableInput(is_typable, query){
    //
    if(!((typeof is_typable === 'undefined') || (is_typable == null))){
        if(!((typeof query === 'undefined') || (query == null))){
            if(is_typable == "false"){
                disableInput();
            }
            else if(is_typable == "true"){
                enableInput(query);
            }
        }
    }
}

function removePTag(sentence){
    if(!((typeof sentence === 'undefined') || (sentence == null))){
        sentence = sentence.replace("<p>","");
        sentence = sentence.replace("</p>","");
    }
    return sentence;
}

$('#query').keypress(function (e) {
 var key = e.which;
 if(key == 13)  // the enter key code
 {
  $('#submit-img').click();
  return false;
 }
});

function splitByDollar(sentence){
    list = sentence.split("$$");
    return list;
}


function appendDataForm(data_form){
    if(!((typeof data_form === 'undefined') || (data_form == null))){
        //console.log("DATAFORM IS:", data_form)
        $("#query").val(data_form);
    }
}

$('body').on('change', '.datepicker', function(){
    $('#query').val($('#date').val());
    $("#submit").show();
    $("#mic").hide();
     if(!( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) )) {
        $('#query').focus();
     }
})

var a = new Set([]);
var check_box_cnt = 0;
$('body').on('change', '.checkkbox', function(){
    console.log("Checkbox checked", $(this).attr('text'));
    var year = $(this).attr('text');
    console.log($(this).prop('checked'));
    if($(this).prop('checked') == false){
        a.delete(year);
    }
    else{
        console.log("Bigrams");
	a.add(year);
    }
    console.log(a);
    $('#query').val(Array.from(a).join(', '));
    $("#submit").show();
    $("#mic").hide();
//     if(!( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.tes$
//        $('#query').focus();
//     }
})


function appendCheckBox(){
    check_box_cnt = check_box_cnt + 6;
    var html = '<div id="remove_select">\
    <div class="row chatmessage">\
        <div class="col s1 l1">\
        </div>\
        <div class="col s10 l10">\
           <div>'+
             '<ul >\
    <li style="display: inline;">\
      <input text="Nov 2017" class="checkkbox" type="checkbox" id="test'+check_box_cnt.toString()+'" />\
      <label for="test'+check_box_cnt+'">Nov 2017</label>\
    </li>\
    &nbsp;\
    <li style="display: inline;">\
      <input text="Dec 2017" class="checkkbox" type="checkbox" id="test'+(check_box_cnt+1).toString()+'"/>\
      <label for="test'+(check_box_cnt+1).toString()+'">Dec 2017</label>\
    </li>\
   &nbsp;\
  <li style="display: inline;">\
      <input text="Jan 2018" class="checkkbox" type="checkbox" id="test'+(check_box_cnt+2).toString()+'"/>\
      <label for="test'+(check_box_cnt+2).toString()+'">Jan 2018</label>\
    </li>\
    <br>\
  <li style="display: inline;">\
      <input text="Feb 2018" class="checkkbox" type="checkbox" id="test'+(check_box_cnt+3).toString()+'"/>\
      <label for="test'+(check_box_cnt+3).toString()+'">Feb 2018</label>\
    </li>\
  &nbsp;\
  <li style="display: inline;">\
      <input text="Mar 2018" class="checkkbox" type="checkbox" id="test'+(check_box_cnt+4).toString()+'"/>\
      <label for="test'+(check_box_cnt+4).toString()+'">Mar 2018</label>\
    </li>\
  &nbsp;\
  <li style="display: inline;">\
      <input text="Apr 2018" class="checkkbox" type="checkbox" id="test'+(check_box_cnt+5).toString()+'"/>\
      <label for="test'+(check_box_cnt+5).toString()+'">Apr 2018</label>\
    </li>\
</ul>'
           +'</div>\
        </div>\
    </div></div>\
    ';
    $('#style-2').append(html);
}

function appendDate(){
    var html = '<div id="remove_select">\
    <div class="row chatmessage">\
        <div class="col s2 l2">\
        </div>\
        <div class="col s6 l6 offset-l6 offset-s6">\
           <div>'+
              '<input id="date" type="text" class="datepicker" placeholder="Select DOB">'
           +'</div>\
        </div>\
    </div></div>\
    ';
    $('#style-2').append(html);
  $('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 115, // Creates a dropdown of 15 years to control year,
    today: 'Today',
    clear: 'Clear',
    close: 'Ok',
    format: 'dd/mm/yyyy',
    focus: true,
    maxDate: "0",
    closeOnSelect: false // Close upon selecting a date,
  });
   // var $input = $('.datepicker').pickadate();
   // var picker = $input.pickadate('picker');
   // picker.set('select', [1980, 1, 1]);
    $("#query").val("");
}

function appendServerChat(data){
    //
    if((!((typeof data["response"] === 'undefined') || (data["response"] == null))) && (!((typeof data["is_typable"] === 'undefined') || (data["is_typable"] == null)))){
        //
        disableOrEnableInput(data["is_typable"], data["response"]);
    }
    else{
        //
        disableOrEnableInput("false", "");
    }
    if(!((typeof data["response"] === 'undefined') || (data["response"] == null))){
                        list = splitByDollar(data["response"]);
                        if(!((typeof data["is_answer"] === 'undefined') || (data["is_answer"] == null))){
                            ////
                            if(data["is_answer"] == "true"){
                                in_flow = false;
                                global_string = "";
                            }
                            for(var i=0;i<list.length;i++){
                                if(i==list.length-1)
                                    appendResponseServer(list[i], data["is_answer"], data["upvote_link"], data["downvote_link"]);
                                else
                                    appendResponseServer(list[i], false, "", "");
                            }
                        }
                        else{
                             for(var i=0;i<list.length;i++){
                                appendResponseServer(list[i], false, "", "");
                             }

                        }
                      }
    if(!((typeof data["choices"] === 'undefined') || (data["choices"] == null)))
        if(!((typeof data["pipe"] === 'undefined') || (data["pipe"] == null)))
            appendButtons(data["choices"],data["pipe"]);
        else
            appendButtons(data["choices"],"");
    if(!((typeof data["recommended_queries"] === 'undefined') || (data["recommended_queries"] == null)))
        appendRecommendationsList(data["recommended_queries"]);
    if(data["is_date"])	{appendDate();console.log("aaaaaaaaaaaaaaaaaaaaa");}
    if(data["is_checkbox"]) {appendCheckBox();}
    if(mic_button_set){
        $("#submit-mic").show();
        $("#submit-img").hide();
    }
    else
        $("#submit-img").attr('src',STATIC_SERVER_URL+STATIC_IMG_PATH+'/send1.png');
}


function ajaxCallToIndex(sentence, clicked){
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/query/",
        type: "GET",
        data: {
            message: sentence,
            user_id: user_id,
            channel: "android",
            language: "eng",
            clicked: clicked,
            pipe: global_string,
            this_cookie: csrftoken,
        },
        success: function(data){
            setTimeout(function(){
                appendServerChat(data);
                //$("#query").focus();
                ////
                scroll_to_bottom();
                query_cnt++;
            }, 500);
            ////
            ////

        },
        error: function (jqXHR, exception) {
             appendResponseServer("HIA is under maintenance, Please try again after some time. Sorry for your inconvenience.", false, "", "");
             disableOrEnableInput("true","");
             scroll_to_bottom();
        },
    });
}

$("#submit-img").click(function(){
    if(($.trim($('#query').val()) != '') && ($("#query").val()).length<300){
        var sentence = $("#query").val();
        sentence = $($.parseHTML(sentence)).text();
        if (sentence.length == 0) {      // error!
          $("#query").val("");
          return;
        }
        $("#query").val("");
        appendResponseUser(sentence);
        global_string +=  sentence + " | ";
        ajaxCallToIndex(sentence,"0");
    }
    else{
        //.toast("Please enter a valid query", 2000);
    }
});

$('body').on('click','.like-query', function(){
    var clicked = $(this).attr('clicked');
    if(!((typeof clicked === 'undefined') || (clicked == null))){
        if(clicked != "true"){
            var id = this.id;
            var id = id.substring(4);
            $("#like"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+'/thumbs-down-filled.png');
            $("#disl"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+'/thumbs-down1.png');
            $("#disl"+id).removeAttr("clicked");
            var url = $(this).attr('url_t');
            var final_url = API_SERVER_URL+"/"+URL_IDENTIFIER+url;
            //$(this).removeAttr('url_t');
            if(!((typeof url === 'undefined') || (url == null))){
                $(this).attr('clicked','true');
                var csrftoken = getCookie('csrftoken');
                $.ajax({
                    url: final_url,
                    type: "GET",
                    data: {
                        this_cookie: csrftoken,
                    },
                    success: function(data){
                    }
                });
            }
        }
    }
    else{
        var id = this.id;
        var id = id.substring(4);
        $("#like"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+"/thumbs-down-filled.png");
        $("#disl"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+"/thumbs-down1.png");
        $("#disl"+id).removeAttr("clicked");
        var url = $(this).attr('url_t');
        //$(this).removeAttr('url_t');
        var final_url = API_SERVER_URL+"/"+URL_IDENTIFIER+url;
        if(!((typeof url === 'undefined') || (url == null))){
            $(this).attr("clicked","true");
            var csrftoken = getCookie('csrftoken');
            $.ajax({
                url: final_url,
                type: "GET",
                data: {
                    this_cookie: csrftoken,
                },
                success: function(data){
                }
            });
        }
    }
});

$('body').on('click','.dislike-query', function(){
    var clicked = $(this).attr('clicked');
    if(!((typeof clicked === 'undefined') || (clicked == null))){
        if(clicked != "true"){
            var id = this.id;
            var id = id.substring(4);
           // $("#disl"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+"/thumbs-up-filled.png");
           // $("#like"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+"/thumbs-up1.png");
            $("#like"+id).removeAttr("clicked");
            var url = $(this).attr('url_t');
            //$(this).removeAttr('url_t');
            var final_url = API_SERVER_URL+"/"+URL_IDENTIFIER+url;
            if(!((typeof url === 'undefined') || (url == null))){
                $(this).attr("clicked","true");
                var csrftoken = getCookie('csrftoken');
                $.ajax({
                    url: final_url,
                    type: "GET",
                    data: {
                        this_cookie: csrftoken,
                    },
                    success: function(data){
                    }
                });
            }
        }
    }
    else{
        var id = this.id;
        var id = id.substring(4);
        $("#disl"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+"/thumbs-up-filled.png");
        $("#like"+id).attr("src",STATIC_SERVER_URL+STATIC_IMG_PATH+"/thumbs-up1.png");
        $("#like"+id).removeAttr("clicked");
        var url = $(this).attr('url_t');
        //$(this).removeAttr('url_t');
        var final_url = API_SERVER_URL+"/"+URL_IDENTIFIER+url;
        if(!((typeof url === 'undefined') || (url == null))){
            $(this).attr('clicked','true');
            var csrftoken = getCookie('csrftoken');
            $.ajax({
                url: final_url,
                type: "GET",
                data: {
                    this_cookie: csrftoken,
                },
                success: function(data){
                }
            });
        }
    }
});

$('body').on('click','#restart-button', function(){
    $(".chatmessage").remove();
    enableInput("");
    var csrftoken = getCookie('csrftoken');
    $.ajax({
        url: API_SERVER_URL+"/"+URL_IDENTIFIER+"/cancelbutton/",
        type: "GET",
        data: {
            user_id: user_id,
        },
        success: function(data){
            response = data["response"]
            recommended_queries = data["recommended_queries"]
            is_typable = data["is_typable"]

            if(!((typeof response === 'undefined') || (response == null))){
              disableOrEnableInput(is_typable, response);
              list = splitByDollar(data["response"]);
              for(var i=0;i<list.length;i++){
                 appendResponseServer(list[i], false, "", "");
              }
            }
            if(!((typeof recommended_queries === 'undefined') || (recommended_queries == null))){
              appendRecommendationsList(recommended_queries);
            }
        }
    });
    $("#query").val("");
    global_string = "";
    if(mic_button_set){
        $("#submit-mic").show();
        $("#submit-img").hide();
    }
    else
        $("#submit-img").attr('src',STATIC_SERVER_URL+STATIC_IMG_PATH+'/send1.png');
    //ajaxCallToIndex("main","1");
});

$('body').on('click','.chiprecommendation', function(){
    var isDisabled = $('#query').prop('disabled');
    if(!isDisabled){
        //removeClickablePropertyRec($(this));
        $(this).removeClass("chiprecommendation");
        $(this).css({'background-color':'#eeeeee'});
        $(this).css({'cursor' :"default"});
        var sentence = $(this).text();
        sentence = $($.parseHTML(sentence)).text();
        if (sentence.length == 0) {      // error!
          return;
        }
        global_string +=  sentence + " | ";
        appendResponseUser($(this).text());
        ajaxCallToIndex($(this).text(),"1");
    }
});

$('body').on('click','#close-chatbot', function(){

   //$('#allincall-chat-box', window.parent.document).slideUp("slow");
   $('#allincall-chat-box', window.parent.document).hide();
   $('#allincall-popup', window.parent.document).show();
});

$('body').on('click','.chipbutton', function(){
    $(this).css({'background-color':'#1e88e5'});
    $(this).css({'color':'white'});
    $(this).parent().children().css({'cursor' :"default"});
    $(this).parent().children().removeClass("chipbutton");
    $(this).parent().children().removeClass("button3");

    //removeClickablePropertyBut($(this));
    var sentence = $(this).text();
    sentence = $($.parseHTML(sentence)).text();
    if (sentence.length == 0) {      // error!
      return;
    }
    appendResponseUser($(this).text());
    global_string =  $(this).attr('pipe') + $(this).text() +"|";
    ////
    ajaxCallToIndex($(this).text(),"1");
});

function removeClickablePropertyRec(ctx){
   $(ctx).parent().children().removeClass("chiprecommendation");
   $(ctx).parent().removeClass("button-group2");
   $(ctx).parent().children().css({'cursor' :"default"});
}

function removeClickablePropertyBut(ctx){
   $(ctx).parent().children().removeClass("chipbutton");
   $(ctx).parent().children().removeClass("button3");
   $(ctx).parent().children().css({'cursor' :"default"});
}

$('body').on('click','#logo-container', function(){
     $("#query").focus();
});

$('#query').on('input',function(e){
    var value = $("#query").val();
    if($.trim($('#query').val()) == ''){
        if(mic_button_set){
            $("#submit-mic").show();
            $("#submit-img").hide();
        }
        else
            $("#submit-img").attr('src',STATIC_SERVER_URL+STATIC_IMG_PATH+'/send1.png');
    }
    else{
        $("#submit-mic").hide();
        $("#submit-img").show();
        $("#submit-img").attr('src',STATIC_SERVER_URL+STATIC_IMG_PATH+'/send2.png');
    }
});
