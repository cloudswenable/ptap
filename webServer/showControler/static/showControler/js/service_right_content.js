
function serviceChoose(element){
        var nameMaps = {'service machine':'machines'};
        var mName = $(element).find('input').val();
        var item = nameMaps[mName];
        context = {'item':item, 'tps':0, 'mps':0, 'rps':0, 'sps':0, 'pps':0};
        loadShowTable(context, "text", "/show/getpoptable?", service_load_pop_table); 
}

function service_load_pop_table(result){
        $("#selectpop").html(result);
        $("#popconfirm").attr("onclick", "").click(serviceConfirm);
        $('#selectpop').modal('show');
}

function serviceConfirm(){
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
        column_name = 'service '+column_name;
        column_id_name = column_name + "ForeignId";
        $("#poptable  input[name='"+column_name+"']").val(name);
        $("#poptable  input[name='"+column_id_name+"']").val(id);
        hideanother();
}
function addOrModifyService(isModify){
        var valid = 1;
        var dic = {};
        var menuType = $("#leftcontent li.active a").text().trim();
        dic['menuType'] = menuType;
        $("#poptable div.firstcolumn").each(function(i,n){
                var name = $(n).text();
                name = name.substring(0, name.length-1).trim();
                var tmp;
                var value = "";
                if(name=="service description" || name=="analysis description"){
                        tmp = "textarea";
                        value = $(tmp).val();
                }else if(name=="service machine"){
                        tmp = "input[name='"+name+"ForeignId']";
                        value = $(tmp).val();
                }else if(name=="service result"){
                        tmp = "input[name='"+name+"ForeignId']";
                        value = $(tmp).val();
                }else if(name=="type"){
                        tmp = "select[name='type']";
                        value = $(tmp).val();
                }else{
                        tmp = "input[name=\""+name+"\"]";
                        value = $('input[name="'+name+'"]').val();
                }
                if(name=="version" || name=="repeat" || name=="duration" || name=="delaytime"){
                        if(isNaN(parseInt(value)) || value.indexOf(".")!=-1){
                                alert("Version, Repeat, Duration and Delaytime must be Integer");
                                valid = 0;
                                return;
                        }
                }
                dic[name] = value;
        });

        var files = []
        if(valid){
                if(isModify){
                        var id = $("input[name='rowchoose']:checked").val();
                        dic["id"] = id;
                }
                var item = $("#leftcontent li.active").text().trim();
                dic["item"] = item;
                dic["modify"] = isModify;
                var url = '/show/addormodifyservice/';
                submitform(url, dic, 0, files);
       }
}
function addService(){
        addOrModifyService(0);
}
function modifyService(){
        addOrModifyService(1);
}
function popAddService(){
        $("#poptable div.modal-header h3").text("Add Service");
        $("#poptable div.modal-footer button").removeAttr("onclick").attr("onclick", "addService()");
}
function popModifyService(){
        var choose_input = $("input[name='rowchoose']:checked");
        var id = $(choose_input).val();
        if(!id){
                alert("must choose a object");
                return;
        }
        $("#poptable div.modal-header h3").text("Modify Service");
        $("#poptable div.modal-footer button").removeAttr("onclick").attr("onclick", "modifyService()");
        var context = {'id':id}
        loadShowTable(context, "json", "/show/loadservicedatas/", serviceModifyPopTable);
}
function serviceModifyPopTable(result){
        for(var item in result){
                if(item == "service machine"){
                        $("input[name='service machine']").val(result[item][1]);
                        $("input[name='service machineForeignId']").val(result[item][0]);
                        continue;
                }
                if(item == "service description"){
                        $("textarea").text(result[item]);
                        continue;
                }
                $("input[name='"+item+"']").val(result[item]);
        }
        $('#poptable').modal('show');
}
function deleteService(){
        var choose_input = $("input[name='rowchoose']:checked");
        var id = $(choose_input).val();
        if(!id){
                alert("must choose a object");
                return;
        }
        var chooseItem = $("#leftcontent li.active a").text().trim();
        var dic = {'id':id, 'chooseItem':chooseItem}
        submitform("/show/deleteservice/", dic);
}
var service_page_size = 10;
function servicePrevious(){
        var start = parseInt($("#start").val());
        if(start<service_page_size) return;
        if(start>0) start -= service_page_size;
        var chooseItem = $("#leftcontent li.active a").text().trim();
        var context = {"start":start, "chooseItem": chooseItem};
        loadShowTable(context, "text", "/show/servicerightcontent?", serviceLoadRightContent);
}
function serviceLoadRightContent(result){
        $("div#rightcontent").html(result);
}
function serviceNext(){
        var start = parseInt($("#start").val());
        start += service_page_size;
        var chooseItem = $("#leftcontent li.active a").text().trim();
        var context = {"start":start, "chooseItem": chooseItem};
        loadShowTable(context, "text", "/show/servicerightcontent?", serviceLoadRightContent);
}
function serviceRun(){
        var choose_input = $("input[name='rowchoose']:checked");
        var id = $(choose_input).val();
        if(!id){
                alert("must choose a object");
                return;
        }
        var dic = {'id':id}
        submitform("/show/servicerun/", dic);
}
function serviceNewAnalysis(){
        var choose_input = $("input[name='rowchoose']:checked");
        var id = $(choose_input).val();
        var name = $(choose_input).parent().next().text();
        if(!id){
                alert("must choose a object");
                return;
        }
        $("input[name='service result']").val(name);
        $("input[name='service resultForeignId']").val(id);
        $('#poptable').modal('show');
}
function serviceAnalysis(){
        var choose_input = $("input[name='rowchoose']:checked");
        var id = $(choose_input).val();
        if(!id){
                alert("must choose a object");
                return;
        }
        var dic = {'id':id}
        submitform("/show/serviceanalysis/", dic);
}
function serviceShow(){
        var choose_input = $("input[name='rowchoose']:checked");
        var id = $(choose_input).val();
        if(!id){
                alert("must choose a object");
                return;
        }
        var url = "/show/serviceshow?id="+id;
        popBlankPage(url);
}
