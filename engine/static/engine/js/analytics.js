var bbgc = [
"rgba(59,199,228,0.3)",
"rgba(220,48,138,0.3)",
"rgba(174,7,202,0.3)",
"rgba(220,37,138,0.3)",
"rgba(43,144,26,0.3)",
"rgba(245,70,161,0.3)",
"rgba(69,172,158,0.3)",
"rgba(65,69,213,0.3)",
"rgba(73,50,212,0.3)",
"rgba(21,223,237,0.3)",
"rgba(43,19,43,0.3)",
"rgba(38,253,99,0.3)",
"rgba(165,18,232,0.3)",
"rgba(166,185,0,0.3)",
"rgba(46,204,13,0.3)",
"rgba(101,224,57,0.3)",
"rgba(11,85,215,0.3)",
"rgba(1,66,195,0.3)",
"rgba(61,40,89,0.3)",
"rgba(24,73,163,0.3)",
"rgba(233,1,142,0.3)",
"rgba(115,172,241,0.3)",
"rgba(162,124,173,0.3)",
"rgba(203,249,102,0.3)",
"rgba(132,130,226,0.3)",
"rgba(83,230,144,0.3)",
"rgba(221,200,57,0.3)",
"rgba(234,137,153,0.3)",
"rgba(219,252,59,0.3)",
"rgba(9,176,35,0.3)",
"rgba(249,202,102,0.3)",
"rgba(194,126,136,0.3)",
"rgba(44,43,132,0.3)",
"rgba(111,210,178,0.3)",
"rgba(100,229,27,0.3)",
"rgba(42,51,54,0.3)",
"rgba(116,146,197,0.3)",
"rgba(91,229,201,0.3)",
"rgba(169,34,166,0.3)",
"rgba(199,54,92,0.3)",
"rgba(135,187,81,0.3)",
"rgba(240,109,225,0.3)",
"rgba(233,52,154,0.3)",
"rgba(209,109,13,0.3)",
"rgba(13,82,102,0.3)",
"rgba(196,134,150,0.3)",
"rgba(112,69,160,0.3)",
"rgba(29,230,46,0.3)",
"rgba(71,115,15,0.3)",
"rgba(215,13,224,0.3)",
];

var bbc = [
'rgba(255,99,132,1)',
'rgba(54, 162, 235, 1)',
'rgba(255, 206, 86, 1)',
'rgba(75, 192, 192, 1)',
'rgba(153, 102, 255, 1)',
'rgba(255, 159, 64, 1)'
];

var lbgc = ['#e41a1c','blue', 'red', 'green', 'yellow' ,'purple','black','brown','pink'];
var lbc = ['blue', 'red', 'green', 'yellow'];

$(document).ready(function() {

    ////
    var dateObj = new Date();
    var month = (dateObj.getUTCMonth() + 1).toString(); //months from 1-12
    var day = dateObj.getUTCDate().toString();
    var year = dateObj.getUTCFullYear().toString();

    ////
    if(day.length==1){
        day = "0"+day;
    }
    if(month.length==1){
        month = "0"+month;
    }

    var d = new Date();
    d.setMonth(d.getMonth()-3);
    var new_month = (d.getUTCMonth() + 1).toString(); //months from 1-12
    var new_day = d.getUTCDate().toString();
    var new_year = d.getUTCFullYear().toString();

    if(new_day.length==1){
        new_day = "0"+new_day;
    }
    if(new_month.length==1){
        new_month = "0"+new_month;
    }

    var from_date = new_day+"/"+new_month+"/"+new_year;
    var to_date = day+"/"+month+"/"+year;

    $("#from-data").val(from_date);
    $("#to-data").val(to_date);
    $("#submit-analytics").click();
    $('.modal').modal();
});
function draw_insights(data){
    $("#insights-div").html('<div class="row"><div class="col l3"></div><div class="col l6"><canvas id="linegraph_insights_messages"></canvas></div><div class="col l3"><a id="download-report" class="waves-effect waves-light btn">Download Report</a></div></div>');

    var ctx = $("#linegraph_insights_messages");

    var labels_graph = Object.keys(data);
    var final_labels_graph = Object.keys(data[labels_graph[0]]);

    //////

    var data_set = [];
    var num = 0;
    Object.keys(data).forEach(function(key){
        num+=3;
        var obj = {};
        var current_label = key;
        var list_data = [];
        ////////
        var temp = data[key];
        for(var key_t in temp) {
            if (temp.hasOwnProperty(key_t)) {
                list_data.push(temp[key_t]);
            }
        }
        //////
        obj["data"] = list_data;
        obj["label"] = current_label;
        obj["backgroundColor"] = bbgc[num%bbgc.length];
        obj["borderColor"] = bbc[num%bbc.length];
        obj["borderWidth"] = 1;
        data_set.push(obj);
    });

    //////

    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: final_labels_graph,
            datasets: data_set,
            borderWidth: 1
        },
        options: {
            title: {
                display: true,
                fontSize: 20,

                text: 'Line Insights'
            }
        }
    });
}

function draw_average_session_time(data){
    //
    var ctx = $("#average_session_length");

    var labels_graph = Object.keys(data);

    //

    var data_set = [];
    var temp_list = [];
    var num = 6;
    Object.keys(data).forEach(function(key){
        temp_list.push(data[key]);
    });
    var obj = {};
    obj["data"] = temp_list;
    obj["label"] = "average session length"
    obj["backgroundColor"] = bbgc[6%bbgc.length];
    obj["borderColor"] = bbc[6%bbc.length];
    obj["borderWidth"] = 1;
    data_set.push(obj);

    //
    //
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels_graph,
            datasets: data_set,
            borderWidth: 1
        },
        options: {
            title: {
                display: true,
                fontSize: 20,

                text: 'Average Session Time'
            }
        }
    });
}

function draw_total_unique_users(data){
    var ctx = $("#unique_users");

    var labels_graph = Object.keys(data);

    //////

    var data_set = [];
    var temp_list = [];
    var num = 3;
    Object.keys(data).forEach(function(key){
        num++;
        temp_list.push(data[key]);
    });
    var obj = {};
    obj["data"] = temp_list;
    obj["label"] = "Total unique users"
    obj["backgroundColor"] = bbgc[3%bbgc.length];
    obj["borderColor"] = bbc[3%bbc.length];
    obj["borderWidth"] = 1;
    data_set.push(obj);

    //////

    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels_graph,
            datasets: data_set,
            borderWidth: 1
        },
        options: {
            title: {
                display: true,
                fontSize: 20,

                text: 'Total Unique Users'
            }
        }
    });
}

function draw_clicked_vs_typed(clicked_vs_typed){
    $("#clicked-vs-typed-div").html('<div id="clicked-vs-typed-div"> <div class="row"> <div class="col l3"> </div> <div class="col l6"> <canvas id="clicked-vs-typed_users"> </canvas> </div> <div class="col l3"> </div> </div> </div>');
    var ctx = $("#clicked-vs-typed_users");
    var data = {};

    var list_labels = [];
    var list_data = [];
    var dict_data = {};
    var list_data_data = [];
    var list_back = [];
    var num = 14;
    Object.keys(clicked_vs_typed).forEach(function(key) {
        //////
        list_labels.push(key);
        list_data_data.push(clicked_vs_typed[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });
    dict_data["data"] = list_data_data;
    dict_data["borderWidth"] = 1;
    dict_data["backgroundColor"] = list_back;
    list_data.push(dict_data);

    data["labels"] = list_labels;
    data["datasets"] = list_data;


    var myPieChart = new Chart(ctx,{
        type: 'pie',
        data: data,
        options: {
            title: {
                display: true,
                fontSize: 20,

                text: 'Clicked vs Typed'
            }
        }
    });
}
function draw_platforms(platforms){
    $("#platforms-div").html('<div class="row"> <div class="col l3"> </div> <div class="col l6"> <canvas id="platforms"> </canvas> </div> <div class="col l3"> </div> </div>');
    var ctx = $("#platforms");
    var data = {};

    var list_labels = [];
    var list_data = [];
    var dict_data = {};
    var list_data_data = [];
    var list_back = [];
    var num = 9;
    Object.keys(platforms).forEach(function(key) {
        //////
        list_labels.push(key);
        list_data_data.push(platforms[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });
    dict_data["data"] = list_data_data;
    dict_data["borderWidth"] = 1;
    dict_data["backgroundColor"] = list_back;
    list_data.push(dict_data);

    data["labels"] = list_labels;
    data["datasets"] = list_data;


    var myPieChart = new Chart(ctx,{
        type: 'pie',
        data: data,
        options: {
            title: {
                display: true,
                fontSize: 20,

                text: 'Different Platform'
            }
        }
    });
    return;
}

function draw_top_products(products){
    $("#products-div").html(' <div class="row"> <div class="col l3"> </div> <div class="col l6"> <canvas id="products"> </canvas> </div> <div class="col l3"> </div> </div>');

    var ctx = $("#products");

    var data = {};

    var list_labels = [];
    var list_data = [];
    var dict_data = {};
    var list_data_data = [];
    var dictt = {};
    var list_back = [];
    var num = 11;
    Object.keys(products).forEach(function(key) {
        //////
        list_labels.push(key);
        list_data_data.push(products[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });
    dict_data["data"] = list_data_data;
    dict_data["borderWidth"] = 1;
    dict_data["backgroundColor"] = list_back;
    list_data.push(dict_data);
    ////
    data["labels"] = list_labels;
    data["datasets"] = list_data;
    var myPieChart = new Chart(ctx,{
        type: 'pie',
        data: data,
        options: {
            title: {
                display: true,
                fontSize: 20,

                text: 'Top Products'
            }
        }
    });
}

function draw_top_entities_in_intent(data){
    //$("#eiin").html(' <div class="row"> <div class="col l3"> </div> <div class="col l6"> <div id="entities_in_intent_chips"> </div> <div id="master_in_intent"> <canvas id="entities_in_intent"> </canvas> </div> </div> <div class="col l3"> </div> </div>');
    var ctx = $("#entities_in_intent");

    var labels_graph = Object.keys(data);

    var num = 1;
        var dic = {};
    $("#entities_in_intent_chips").html("");
    for(var i=0;i<labels_graph.length;i++){
        $("#entities_in_intent_chips").append('\
        <div class="chip in_intent">'+labels_graph[i]+'</div>\
        ');
    }

    dict = data[labels_graph[0]];
    list_back = [];
    var num = 3;
    graph_label = [];
    data_set = [];
    Object.keys(dict).forEach(function(key) {
        graph_label.push(key);
        data_set.push(dict[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });

    //////
    //////

    data_sets = [];
    temp_obj = {};
    temp_obj["label"] = labels_graph[0];
    temp_obj["data"] = data_set;
    temp_obj["borderWidth"] = 1;
    temp_obj["backgroundColor"] = list_back;
    data_sets.push(temp_obj);
    ////////
    ////////

    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: graph_label,
            datasets: data_sets,
        },
        options: {
                title: {
                    display: true,
                    fontSize: 20,

                    text: 'Top entities in Intent'
                }
            }

    });
}


function draw_top_intents_in_entities(data){
    //$("#iine").html(' <div class="row"> <div class="col l3"> </div> <div class="col l6"> <div id="intent_in_entities_chips"> </div> <div id="master_in_entities"> <canvas id="intent_in_entities"> </canvas> </div> </div> <div class="col l3"> </div> </div>');
    var ctx = $("#intent_in_entities");

    var labels_graph = Object.keys(data);
    $("#intent_in_entities_chips").html("");
    for(var i=0;i<labels_graph.length;i++){
        $("#intent_in_entities_chips").append('\
        <div class="chip in_entities">'+labels_graph[i]+'</div>\
        ');
    }

    // Initially clicking first chip.
    dict = data[labels_graph[0]];

    graph_label = [];
    data_set = [];
    var num = 16;
    var list_back = [];
    Object.keys(dict).forEach(function(key) {
        graph_label.push(key);
        data_set.push(dict[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });

    //////
    //////

    data_sets = [];
    temp_obj = {};
    temp_obj["label"] = labels_graph[0];
    temp_obj["data"] = data_set;
    temp_obj["data"] = data_set;
    temp_obj["borderWidth"] = 1;
    temp_obj["backgroundColor"] = list_back;
    data_sets.push(temp_obj);

    ////////
    ////////

    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: graph_label,
            datasets: data_sets,

        },
        options: {
                title: {
                    display: true,
                    fontSize: 20,

                    text: 'Top intent in entities'
                }
            }
    });
}

$('body').on('click','.in_entities',function(){

    var val = $(this).text();

    //$("#iine").html(' <div class="row"> <div class="col l3"> </div> <div class="col l6"> <div id="intent_in_entities_chips"> </div> <div id="master_in_entities"> <canvas id="intent_in_entities"> </canvas> </div> </div> <div class="col l3"> </div> </div>');
    $("#master_in_entities").html('<canvas id="intent_in_entities"></canvas>');

    var ctx = $("#intent_in_entities");

    dict = intent_in_entities[val];

    graph_label = [];
    data_set = [];
    var list_back = [];
    var num = parseInt(Math.floor(Math.random() * 22) + 1);
    Object.keys(dict).forEach(function(key) {
        graph_label.push(key);
        data_set.push(dict[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });

    //////
    //////

    data_sets = [];
    temp_obj = {};
    temp_obj["label"] = val;
    temp_obj["data"] = data_set;
    temp_obj["borderWidth"] = 1;
    temp_obj["backgroundColor"] = list_back;
    data_sets.push(temp_obj);
    ////////
    ////////

    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: graph_label,
            datasets: data_sets,

        },
        options: {
                title: {
                    display: true,
                    fontSize: 20,

                    text: 'Top intent in entities'
                }
            }
    });
});

$('body').on('click','.in_intent',function(){


    var val = $(this).text();
    //$("#eiin").html(' <div class="row"> <div class="col l3"> </div> <div class="col l6"> <div id="entities_in_intent_chips"> </div> <div id="master_in_intent"> <canvas id="entities_in_intent"> </canvas> </div> </div> <div class="col l3"> </div> </div>');

    $("#master_in_intent").html('<canvas id="entities_in_intent"></canvas>');

    var ctx = $("#entities_in_intent");

    dict = entities_in_intent[val];

    graph_label = [];
    data_set = [];
    list_back = [];
    var num = parseInt(Math.floor(Math.random() * 22) + 1);
    Object.keys(dict).forEach(function(key) {
        graph_label.push(key);
        data_set.push(dict[key]);
        list_back.push(bbgc[num%bbgc.length])
        num++;
    });

    data_sets = [];
    temp_obj = {};
    temp_obj["label"] = val;
    temp_obj["data"] = data_set;
    temp_obj["borderWidth"] = 1;
    temp_obj["backgroundColor"] = list_back;
    data_sets.push(temp_obj);
    ////////
    ////////

    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: graph_label,
            datasets: data_sets,

        },
        options: {
                title: {
                    display: true,
                    fontSize: 20,

                    text: 'Top Entities in Intent'
                }
            }
    });
});

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}
//
$('.datepicker').pickadate({
   selectMonths: true, // Creates a dropdown to control month
   selectYears: 15, // Creates a dropdown of 15 years to control year,
   today: 'Today',
   clear: 'Clear',
   close: 'Ok',
   format: 'dd/mm/yyyy',
   closeOnSelect: false // Close upon selecting a date,
 });

//
$('body').on('click','#submit-analytics',function(){
    //////
    to_date = $("#to-data").val();
    from_date = $("#from-data").val();

    $.ajax({
        url: "/chat/getanalysis",
        type: "GET",
        data : {
            to_date: to_date,
            from_date: from_date,
        },
        success: function(data){
            ////////
            //

            list_insigths_1 = data["list_insights_1"];
            products = data["top_products"];
            platforms = data["platform_dict"];
            top_intent_in_entities = data["top_intent_in_entities"]
            top_entities_in_intent = data["top_entities_in_intent"];
            average_session_time = data["average_session_time"];
            total_unique_users = data["total_unique_users"];
            clicked_vs_typed = data["clicked_vs_typed"];

            intent_in_entities = top_intent_in_entities;
            entities_in_intent = top_entities_in_intent;

            //
            //
            //
            //
            //
            //
            //

            if(!isEmpty(platforms))
                draw_platforms(platforms);
            if(!isEmpty(products))
                draw_top_products(products);
            if(!isEmpty(list_insigths_1))
                draw_insights(list_insigths_1);
            if(!isEmpty(top_entities_in_intent))
                draw_top_intents_in_entities(top_intent_in_entities);
            if(!isEmpty(top_entities_in_intent))
                draw_top_entities_in_intent(top_entities_in_intent);
            if(!isEmpty(average_session_time))
                draw_average_session_time(average_session_time);
            if(!isEmpty(total_unique_users))
                draw_total_unique_users(total_unique_users);
            if(!isEmpty(clicked_vs_typed))
                draw_clicked_vs_typed(clicked_vs_typed);
        }
    });
});
//
function openInNewTab(url) {
  var win = window.open(url, '_blank');
  win.focus();
}

$('body').on('click',"#download-report", function(){
    var to_date = $("#to-data").val();
    var from_date = $("#from-data").val();
    var url = '/chat/report/'+from_date+'/'+to_date+'/';
    openInNewTab(url);
});
