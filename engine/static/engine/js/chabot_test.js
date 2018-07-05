//$('body').on('click','#test-sentences', function(){
//    var text = $("#textarea1").val();
//    if(($.trim(text) != '')){
//        var intent = $("select :selected").text();
//        var sentences = text;
//
//        
//        
//
//        //var list_sen = sentences.split("\n");
//        //
//
//        $.ajax({
//                url: "/chat/submitqueries/",
//                type: "POST",
//                data:{
//                    intent: intent,
//                    sentences: sentences
//                },
//                success: function(data){
//                    
//                    $("#intent-name").html(data["intent"]);
//                    $("#answer-table").html('<thead><tr><th>Sentence</th><th>Verdict</th></tr></thead><tbody id="answer-body"></tbody>');
//                    var list = data["answer"];
//
//                    for(var i=0;i<list.length;i++){
//                        var temp_dict = list[i];
//                        $("#answer-body").append('<tr><td>'+temp_dict["sentence"]+'</td><td>'+temp_dict["verdict"]+'</td></tr>');
//                    }
//                }
//            });
//    }
//    else{
//       Materialize.toast("Please enter some sentences", 2000);
//    }
//});


$('body').on('click','.collection-item', function(){
    //
    var id = this.id;
    var text = $(this).text();
    //
    window.location.href = "http://13.127.153.112/chat/chat_testing/"+id;
});
