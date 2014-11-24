function init(){
    $("#leftcontent ul li").click(selectProjectItem);
    var h_type = $("#header li.active a").text().trim();
    if(h_type == "analysis"){
 	var id = $("#leftcontent li.active input").val();
	if(id){
            var context = {'id': id}
            loadShowTable(context, "json", "/show/analysiscontent", analysis_load_right_content);
	}
    }
}
function popBlankPage(url){
        var a = $("<a href='"+url+"' target='_blank'>blank</a>").get(0);
        var e = document.createEvent('MouseEvents');
        e.initEvent( 'click', true, true );
        a.dispatchEvent(e);
}
function selectProjectItem()
{
    $("#leftcontent ul li").removeClass("active");
    $(this).addClass("active");
    var h_type = $("#header li.active a").text().trim();
    if(h_type == "new"){
        var d_item = $("#leftcontent li.active a").text().trim();
        context = {"type":h_type, "item": d_item}
        loadShowTable(context, "text", "/show/showtable", new_load_right_content);
    }else if(h_type == "analysis"){
        var id = $("#leftcontent li.active input").val();
        context = {'id': id}
	loadShowTable(context, "json", "/show/analysiscontent", analysis_load_right_content);
    }else if(h_type == "service"){
        var d_item = $("#leftcontent li.active a").text().trim();
        var context = {'start': 0, 'chooseItem':d_item};
        var url = "/show/servicerightcontent?";
        loadShowTable(context, "text", url, serviceLoadRightContent);
    }
}
function analysis_load_right_content(result){
    var table = createAllResultsShowTable(result);
    $('#resultsContainer').html(table);
}
function analysis_compare_right_content(result){
	createAllCompareTables(result);
        $('#container').modal('show');
}
function hideCompareTable(){
	$("#compareDataTableGlass").removeClass("glass").addClass("hidden");
        $("#container").removeClass("showbox").addClass("hidden");
	oTables = [];
	storage.clear();
}
function new_load_pop_table(result){
    $("#selectpop").html(result);
    $("#selectpop").modal('show');
}
function new_load_headlineselect_table(result){
    $("#selectpop").html(result);
    $("#popconfirm").attr("onclick", "").click(confirmSelect);
    $('#selectpop').modal('show');
}
function new_load_right_content(result){
    $("div#rightcontent").html(result);
}
function new_modify_pop_table(result){
	for(var item in result){
		if(item == "machine"){
			$("input[name='machine']").val(result[item][1]);
			$("input[name='machineForeignId']").val(result[item][0]);
			continue;
		}
		if(item == "description"){
			$("textarea").text(result[item]);
			continue;
		}
		$("input[name='"+item+"']").val(result[item]);
	}
        $('#poptable').modal('show');
}

function clone_pop_table(result){
	for(var item in result){
		if(item == "machine"){
			$("input[name='machine']").val(result[item][1]);
			$("input[name='machineForeignId']").val(result[item][0]);
			continue;
		}
		if(item == "description"){
			$("textarea").text(result[item]);
			continue;
		}
        if(item == "version"){
			$("input[name='version']").val(result[item] + 1);
			continue;
		}
		$("input[name='"+item+"']").val(result[item]);
	}
        $('#poptable').modal('show');
}


function loadShowTable(data, datatype, url, callback){
    $.ajax({
	type: "GET",
	traditional: true,
	async: false,
	url: url,
	dataType: datatype,
	data: data,
	success: callback
    });
	
}
function submitform(url, dic, post, files){
    if(post){
        var Myform = $('#postform');
        Myform.attr("action", url);
        $("#uploadrow input[name='upload']").each(function(i, n){
            Myform.append(n);
        });
    }else{
        var Myform = $('#getform');
        Myform.attr("action", url);
    }
    for(var name in dic){
        var my_input = $('<input type="text" name="'+name+'" value="'+dic[name]+'" />');
        Myform.append(my_input);
    }
    Myform.submit();
}
var storage;
$(document).ready(function(){
    init();
    if(storage){
        storage.clear();
    }
    $('#container').on('hidden', function () {
        if(storage){
                storage.clear();
        }
    })
});
