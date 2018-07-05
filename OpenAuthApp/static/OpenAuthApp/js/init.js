$('#login').click(function(){

    reg_mob_no = $('#reg_mob_no').val();
    otp = $('#otp_field').val();

    console.log("SSSS", reg_mob_no, otp); 
    
    $.ajax({
        url: "/login_submit/",
        type: "POST",
        data: {
            reg_mob_no: reg_mob_no,
            otp: otp
        },
        success: function(response) {
            console.log("Success fetching data!", response);
            if(response['status']==200)
            {
                console.log("200!", window.location.href.substring(window.location.href.indexOf("next=")+5,));
                window.location.href = '/pin/?next='+window.location.href.substring(window.location.href.indexOf("next=")+5,);
            }
        },
        error: function(xhr, textstatus, errorthrown) {
            console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
        }
    });

});

$('#reg_mob_no').on('input',function(e){ 
 if($(this).val().length == 10){
    $("#get-otp").prop('disabled', false);
    $("#get-otp").css("background","#f99d27");
 }
 else{
  $("#get-otp").prop('disabled', true);  
  $("#get-otp").css("background","#808000");
 }
});

function isANumber(str){
  return !/\D/.test(str);
}
function mob_validation() {
    console.log("Wait");
    nick_1 = $("#nick_1").val();
    nick_2 = $("#nick_2").val();
    nick_3 = $("#nick_3").val();
    nick_4 = $("#nick_4").val();

    mob_1 = $("#mob_1").val();
    mob_2 = $("#mob_2").val();
    mob_3 = $("#mob_3").val();
    mob_4 = $("#mob_4").val();
    
    if(!(mob_1.length == 10 && nick_1.length>=1 && isANumber(mob_1)))
    {        
        return false;        
    }

    if(mob_2.length > 0 || nick_2.length > 0){
        if(!(mob_2.length == 10 && nick_2.length>=1 && isANumber(mob_2))){
            return false;
        }
    }

    if(mob_3.length > 0 || nick_3.length > 0){
        if(!(mob_3.length == 10 && nick_3.length>=1 && isANumber(mob_3))){            
            return false;
        }
    }

    if(mob_4.length > 0 || nick_4.length > 0){
        if(!(mob_4.length == 10 && nick_4.length>=1 && isANumber(mob_4))){            
            return false;            
        }
    }

    return true;
}

function validate(){
    pin1 = $('#enterpin').val()
    pin2 = $('#confirmpin').val()

    console.log(pin1);
    console.log(pin2);

    mpin_recharge_limit = "1"
    mpin_bill_limit = "1"
    $('#recharge').is(':checked')
    {
        mpin_recharge_limit = $('#mpin_recharge_limit').val();
    }
    $('#billpayment').is(':checked')
    {
        mpin_bill_limit = $('#mpin_bill_limit').val();
    }    
    validation = mob_validation();

    if ($("#toggle").is(':checked')) {
        agree_terms = true;        
    } else {
        agree_terms = false;        
    }
    console.log(agree_terms, "AAAAAAA");
    if(agree_terms==true && pin1==pin2 && isNaN(pin1)==false && pin1.length==4 && isNaN(mpin_recharge_limit)==false && mpin_recharge_limit.length>=1 && isNaN(mpin_bill_limit)==false && mpin_bill_limit.length>=1 && validation){        
        $("#activate").prop('disabled', false);  
    }
    else{
        $("#activate").prop('disabled', true);  
    }
}

$('#toggle').click(function () {
    validate();
});

$('#enterpin').on('input',function(e){     
    validate();
});

$('#confirmpin').on('input',function(e){     
    validate();
});

$('#mpin_recharge_limit').on('input',function(e){     
    validate();
});

$('#mpin_bill_limit').on('input',function(e){     
    validate();
});

$('#mob_1').on('input',function(e){     
    validate();
});

$('#nick_1').on('input',function(e){     
    validate();
});

$('#mob_2').on('input',function(e){     
    validate();
});

$('#nick_2').on('input',function(e){     
    validate();
});

$('#mob_3').on('input',function(e){     
    validate();
});

$('#nick_3').on('input',function(e){     
    validate();
});

$('#mob_4').on('input',function(e){     
    validate();
});

$('#nick_4').on('input',function(e){     
    validate();
});

var size_1 = false;
var size_2 = false;
var size_3 = false;

function moveToNextGrid(a, b){
    console.log("GG", a ,b);    
    console.log(a.target.id);
    //console.log("AAAAAAAA", $(".mobnumber")[0].value);
    if(a.target.id == "TranRequestManagerFG.GRID_CARD_AUTH_VALUE_1__"){
        if(b.length == 2)
            size_1 = true;
        else
            size_1 = false;
    }
    if(a.target.id == "TranRequestManagerFG.GRID_CARD_AUTH_VALUE_2__"){
        if(b.length == 2)
            size_2 = true;
        else
            size_2 = false;
    }
    if(a.target.id == "TranRequestManagerFG.GRID_CARD_AUTH_VALUE_3__"){
        if(b.length == 2)
            size_3 = true;
        else
            size_3 = false;
    }
    if(size_1 && size_2 && size_3){
        $("#SUBMIT_TRANSACTION").prop('disabled', false);
        $("#SUBMIT_TRANSACTION").css("background","#333");
    }
    else{
        $("#SUBMIT_TRANSACTION").prop('disabled', true);
        $("#SUBMIT_TRANSACTION").css("background","#d3d3d3");
    }
}

$('#activate').click(function(){

    pin1 = $('#enterpin').val()
    pin2 = $('#confirmpin').val()
    if(pin1==pin2 && isNaN(pin1)==false && pin1.length==4)
    {    
        mpin_recharge_limit = "";
        mpin_bill_limit = "";
        $('#recharge').is(':checked')
        {
            mpin_recharge_limit = $('#mpin_recharge_limit').val();
        }
        $('#billpayment').is(':checked')
        {
            mpin_bill_limit = $('#mpin_bill_limit').val();
        }        
        mob_1 = $("#mob_1").val();
        mob_2 = $("#mob_2").val();
        mob_3 = $("#mob_3").val();
        mob_4 = $("#mob_4").val();

        nick_1 = $("#nick_1").val();
        nick_2 = $("#nick_2").val();
        nick_3 = $("#nick_3").val();
        nick_4 = $("#nick_4").val();

        mpin = $("#enterpin").val();

        user_params = {
            "mpin_recharge_limit": mpin_recharge_limit,
            "mpin_bill_limit": mpin_bill_limit,
            "mob_1": mob_1,
            "mob_2": mob_2,
            "mob_3": mob_3,
            "mob_4": mob_4,
            "nick_1": nick_1,
            "nick_2": nick_2,
            "nick_3": nick_3,
            "nick_4": nick_4,      
            "mpin": mpin      
        }

        user_params = JSON.stringify(user_params, null, 2);
        $.ajax({
            url: "/store_params/",
            type: "POST",
            data: {
                user_params: user_params,
            },
            success: function(response) {
                window.location.href = '/otp/?next='+window.location.href.substring(window.location.href.indexOf("next=")+5,);        
            },
            error: function(xhr, textstatus, errorthrown) {
                console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
            }
        });        

    }
});

$('#SUBMIT_TRANSACTION').click(function(){    
    var val1 = $(".mobnumber")[0].value;
    var val2 = $(".mobnumber")[1].value;
    var val3 = $(".mobnumber")[2].value;

    $.ajax({
           url: "/chat/VerifyGRID/",
           type: "POST",
           data: {
            val1: val1,
            val2: val2,
            val3: val3,
           },
           success: function(response) {
               if(response["success"]=="1"){
                    window.location.href = unescape(window.location.href.substring(window.location.href.indexOf("next=")+5,));
               }
               else{
                    //Show error message.
               }
           },
           error: function(xhr, textstatus, errorthrown) {
               console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
           }
       });    
});


window.onload = function() {

    console.log("Okay!");
};

if(window.location.pathname.includes('/pin/'))
   {

       $.ajax({
           url: "/chat/accountnumbersoauth/",
           type: "POST",
           data: {
           },
           success: function(response) {
               console.log("Success fetching data!", response);
               account_numbers = response['numbers'];
               html_default_account = '<br><h1 class="financial-services">DEFAULT ACCOUNT NUM</h1><select id="default_account">'
               //html_default_account += '<option value="" selected>--- Choose Default Account ---</option>'
               for(i=0;i<account_numbers.length;i++)
               {
                   html_default_account += '<option value="'+account_numbers[i]+'">'+account_numbers[i]+'</option>'
               }
               html_default_account += '</select>'

               $('#default_account_div').html(html_default_account)            
           },
           error: function(xhr, textstatus, errorthrown) {
               console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
           }
       });
   }
   $('#get-otp').click(function(){

       $.ajax({
           url: "/chat/GetOTP",
           type: "POST",
           data: {
           },
           success: function(response) {
               console.log("Success fetching data!", response);
           },
           error: function(xhr, textstatus, errorthrown) {
               console.log("Please report this error: "+errorthrown+xhr.status+xhr.responseText);
           }
       });

   }); 