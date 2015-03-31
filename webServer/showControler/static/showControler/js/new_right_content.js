    
function hide(){
    $("#glasslevel").removeClass("glass").addClass("hidden");
    $("#poptable").removeClass("showbox").addClass("hidden");
    $("#choosedalert").removeClass("showalert").addClass("hidden");
}
function hideanother(){
        $('#selectpop').modal('hide')
}
function selectForeign(element){
	var maps = {'Project': 'projects', 'Source Code': 'source codes'};
	var name = $(element).parent().find('div[class="span3 offset1 firstheadline"] strong').text().trim();
	var item = maps[name];
    	context = {"item":item, "tps": 0, "mps":0, "rps":0,'pps':0, 'sps':0};
    	loadShowTable(context, "text", "/show/getpoptable?", new_load_headlineselect_table);
}
function confirmSelect(){
	var cTag = $("input[name='poprowchoose']:checked");
	var nextAll = cTag.parent().nextAll();
	var heads = $("#popShowTable thead");
	headNames = []
	heads.find("th").each(function(i, e){
		if(i==0) return
		headNames.push($(e).text());
	});
	nextAll.each(function(i, e){
		$("input[name='"+headNames[i]+"']").val($(e).text());
	});
        $('#selectpop').modal('hide')
}
function chooseForeign(element){
    var name_map = {'project':'projects', 'appBinary':'app binary', 'machine':'machines'};
    var m_name = $(element).find("input").val();
    var item = name_map[m_name];
    context = {"item":item, "tps": 0, "mps":0, "rps":0,"pps":0,"sps":0};
    loadShowTable(context, "text", "/show/getpoptable?", new_load_pop_table);
}
function chooseTarget(type){
    var inputType = $(type).val();
    if(inputType == 'source code'){
	$('#sourceCode').removeClass('hidden');
	$('#pid').addClass('hidden');
	$("#project").addClass("hidden");
    }else if(inputType == 'pid'){
	$('#sourceCode').addClass('hidden');
	$('#pid').removeClass('hidden');
	$("#project").removeClass("hidden");
    }else{
	$('#sourceCode').addClass('hidden');
	$('#pid').addClass('hidden');
	$("#project").removeClass("hidden");
    }
}
function show(){
    var choose_input = $("input[name='rowchoose']:checked");
    var id = $(choose_input).val();
    if(!id){
        alert("must choose a object");
        return;
    }
    var url = "/show/sampleview/";
    var dic = {"type": "results", "id": id}
    loadShowTable(context, "text", "/show/showresult", new_load_pop_table);
    initChart();
    $("#containerglasslevel").removeClass("hidden").addClass("glass");
    $("#container").removeClass("hidden").addClass("showbox");

}
function hideContainer(){
    $("#containerglasslevel").removeClass("glass").addClass("hidden");
    $("#container").removeClass("showbox").addClass("hidden");
}
function deleteItem(){
    var id = $("input[name='rowchoose']:checked").val();
    var item = $("#leftcontent li.active").text().trim();
    var str = "?id="+id+"&item="+item;
    var dic = {}
    dic["id"] = id;
    dic["item"] = item;
    submitform("/show/delete/", dic);
}
function stopTest(){
        var id = $("input[name='rowchoose']:checked").val();
        if( !id){
                alert("must choose a object");
                return;
        }
        var dic = {};
        dic['id'] = id;
        submitform("/show/stop/", dic);
}
function addOrModify(url, is_modify){
    var valid = 1;
    var dic = {};
    $("#poptable div.firstcolumn").each(function(i,n){
        var name = $(n).text();
        name = name.substring(0, name.length-1).trim();
        var tmp;
	var value = "";
	if(name=="description"){
	    tmp = "textarea";
	    value = $(tmp).val();
        }else if(name=="machine"){
            tmp = "input[name='"+name+"ForeignId']";
	    value = $(tmp).val();
        }else{
            tmp = "input[name=\""+name+"\"]";
	    value = $('input[name="'+name+'"]').val();
        }
        if(name=="version" ){
                if(isNaN(parseFloat(value)) ) {
                        alert("version must not be null")
                }
        }
        if(name=="repeat" || name=="duration" || name=="delaytime"){
            if(isNaN(parseInt(value)) || value.indexOf(".")!=-1){
                alert("Repeat, Duration and Delaytime must be Integer");
                valid = 0;
                return;
            }
        }
        dic[name] = value;
    });
    var files = []
    if(valid){
	if(is_modify){
	    var id = $("input[name='rowchoose']:checked").val();
  	    dic["id"] = id;
	}
        var item = $("#leftcontent li.active").text().trim();
        dic["item"] = item;
        submitform(url, dic, 1, files);
    }
}

function doClone(url) {
    var valid = 1;
    var dic = {};
    $("#poptable div.firstcolumn").each(function (i, n) {
        var name = $(n).text();
        name = name.substring(0, name.length - 1).trim();
        var tmp;
        var value = "";
        if (name == "description") {
            tmp = "textarea";
            value = $(tmp).val();
        } else if (name == "machine") {
            tmp = "input[name='" + name + "ForeignId']";
            value = $(tmp).val();
        } else {
            tmp = "input[name=\"" + name + "\"]";
            value = $('input[name="' + name + '"]').val();
        }
        if (name == "version" || name == "repeat" || name == "duration" || name == "delaytime") {
            if (isNaN(parseInt(value)) || value.indexOf(".") != -1) {
                alert("Version, Repeat, Duration and Delaytime must be Integer");
                valid = 0;
                return;
            }
        }
        dic[name] = value;
    });
    var files = []
    if (valid) {
        var item = $("#leftcontent li.active").text().trim();
        dic["item"] = item;
        submitform(url, dic, 1, files);
    }
}

function addObjects(){
    addOrModify('/show/add/', false);
}
function modifyObject(){
    addOrModify('/show/modify/', true);
}
function cloneObject() {
    doClone('/show/clone/');
}

function add(){
    var item = $("#leftcontent li.active").text().trim();
    $("#poptable div.modal-header h3").text("Add "+item);
    $("#poptable div.modal-footer button").removeAttr("onclick").attr("onclick", "addObjects()");
}
function modify(){
    var choose_input = $("input[name='rowchoose']:checked");
    var id = $(choose_input).val();
    var item = $("#leftcontent li.active").text().trim();
    if( !id || !item ){
 	alert("must choose a object");
	return;	
    }
    $("#poptable div.modal-header h3").text("Modify "+item);
    $("#poptable div.modal-footer button").removeAttr("onclick").attr("onclick", "modifyObject()");
    var context = {"testId": id}
    loadShowTable(context, "json", "/show/loadtestdatas/", new_modify_pop_table);
}

function clone() {
    var choose_input = $("input[name='rowchoose']:checked");
    var id = $(choose_input).val();
    var item = $("#leftcontent li.active").text().trim();
    if (!id || !item) {
        alert("must choose a object");
        return;
    }
    $("#poptable div.modal-header h3").text("Clone " + item);
    $("#poptable div.modal-footer button").removeAttr("onclick").attr("onclick", "cloneObject()");
    var context = {"testId": id}
    loadShowTable(context, "json", "/show/loadclonedatas/", clone_pop_table);
}

function run(){
    var choose_input = $("input[name='rowchoose']:checked");
    var id = $(choose_input).val();
    if(!id){
	alert("must choose a object");
	return;
    }
    var url = "/show/run/";
    var dic = {"id": id};
    submitform(url, dic, 0);
}
function selectItem(){
    var cTag = $("input[name='poprowchoose']:checked");
    var id = $(cTag).val();
    var name = cTag.parent().next().text();
    var m_type = $("#selectpop div.modal-header h3").text();
    var column_name = '';
    if(m_type=="Select machines"){
	column_name = "machine";
    }else if(m_type=="Select source codes"){
	column_name="appBinary";
    }else if(m_type=="Select projects"){
	column_name="project";
    }
    column_id_name = column_name + "ForeignId";
    $("#poptable  input[name="+column_name+"]").val(name);
    $("#poptable  input[name="+column_id_name+"]").val(id);
    hideanother();
}
var page_size = 10;
function previous(){
    var type = $("#header li.active a").text().trim();
    var item = $("#leftcontent li.active").text().trim();
    var pps = $("#projectsps").val();
    var mps = 0;
    var sps = $("#sourceps").val();
    var tps = $("#testsps").val();
    var rps = $("#resultps").val();
    if (item == "projects"){
	pps = parseInt(pps);
    	if(pps > 0) pps = pps - page_size;
    }else if(item == "source codes"){
	sps = parseInt(sps);
	if(sps > 0) sps = sps - page_size;
    }else if(item == "tests"){
	tps = parseInt(tps);
	if(tps > 0) tps = tps - page_size;
    }else if(item == "results"){
	rps = parseInt(rps);
	if(rps>0) rps = rps - page_size;
    }
    var context = {"type": type, "item": item, "pps": pps, "mps": mps, "sps": sps, "tps": tps};
    loadShowTable(context, "text", "/show/showtable?", new_load_right_content);
}
function next(){
    var type = $("#header li.active a").text().trim();
    var item = $("#leftcontent li.active").text().trim();
    var pps = $("#projectsps").val();
    var mps = 0;
    var sps = $("#sourceps").val();
    var tps = $("#testsps").val();
    var rps = $("#resultps").val();
    if (item == "projects"){
        pps = parseInt(pps) + page_size;
    }else if(item == "source codes"){
        sps = parseInt(sps) + page_size;
    }else if(item == "tests"){
        tps = parseInt(tps) + page_size;
    }else if(item == "results"){
	rps = parseInt(rps) + page_size;	
    }
    var context = {"type": type, "item": item, "pps": pps, "mps": mps, "sps": sps, "tps": tps, "rps":rps};
    loadShowTable(context, "text", "/show/showtable?", new_load_right_content);
}
var pop_page_size = 5;
function popprevious(){
    var item = $("#selectpop div.modal-header h3").text();
    item = item.substr(7).trim();
    var mps = $("#popmps").val();
    var tps = $("#poptestps").val();
    var pps = $("#popprojectps").val();
    var sps = $("#popsourcecodeps").val();
    if (item == "projects"){
        pps = parseInt(pps);
   	if(pps>0) pps = pps - pop_page_size;
    }else if(item == "machines"){
	mps = parseInt(mps);
	if(mps>0) mps = mps - pop_page_size;
    }else if(item == "source codes"){
        sps = parseInt(sps);
	if(sps>0) sps = sps - pop_page_size;
    }else if(item == "tests"){
        tps = parseInt(tps);
	if(tps>0) tps = tps - pop_page_size;
    }
    context = {"item": item, "pps": pps, "mps":mps, "sps":sps, "tps": tps};
    loadShowTable(context, "text", "/show/getpoptable?", new_load_pop_table);
    $('#selectpop').modal('show');
}
function popnext(){
    var item = $("#selectpop div.modal-header h3").text();
    item = item.substr(7).trim();
    var mps = $("#popmps").val();
    var tps = $("#poptestps").val();
    var pps = $("#popprojectps").val();
    var sps = $("#popsourcecodeps").val();
    if(item == "machines"){
	mps = parseInt(mps) + pop_page_size;
    }else if(item == "tests"){
        tps = parseInt(tps) + pop_page_size;
    }else if(item == "projects"){
	pps = parseInt(pps) + pop_page_size;
    }else if(item == "source codes"){
	sps = parseInt(sps) + pop_page_size;
    }
    context = {"item": item, "mps":mps, "tps": tps, "pps": pps, "sps": sps};
    loadShowTable(context, "text", "/show/getpoptable?", new_load_pop_table);
    $('#selectpop').modal('show');
}
