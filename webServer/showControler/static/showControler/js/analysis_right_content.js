
function createAResultShowNode(resultName, id, attrs){
	var headerDiv = $('<div class="customHeader"></div>');
	var headerCogDiv = $('<div class="headerImg"></div>');
	var textDiv = $('<div style="overflow:hidden;width:70%;height:35px;" class="textDiv"> </div>').text(resultName);
	var checkboxDiv = $('<div class="checkboxDiv"></div>');
	checkboxDiv.html('<input type="checkbox" value="' + id + '" name="resultshow"/>');
	headerDiv.append(headerCogDiv, textDiv, checkboxDiv);
	var bodyDiv = $('<div class="customBody"></div>');
	var bodyDivUl = $('<div class="ullist"></div>');
	for(var i=0; i<attrs.length; i++){
		var li = $('<div class="lilist"></div>');
		var name = $('<span></span>').text(attrs[i][0] + ':');
		var data = $('<span></span>').text(attrs[i][1]);
		li.append(name, data);
		bodyDivUl.append(li);
	}
	bodyDiv.append(bodyDivUl);
	var innerBox = $('<div class="innerBox"></div>').append(headerDiv, bodyDiv);
	var resultNode = $('<div class="customNode"></div>').append(innerBox);
	return resultNode;
}

function createAllResultsShowTable(results){
	var allResultsShowTable = $('<div id="resultsShowTable"></div>');
	var count = 1;
	for(var i=0; i<results.length; i++){
		var node = createAResultShowNode(results[i]['name'], results[i]['id'], results[i]['attrs']);
		allResultsShowTable.append(node);
		if( count%3 == 0 ){
			var cutline = $('<div class="cutline"></div>');
			allResultsShowTable.append(cutline);
		}
		count = count + 1;
	}
	return allResultsShowTable;
}

function createCompareTable(names, datas, tableId){
	var table = $("<table id='" + tableId + "' class='table table-striped table-hover table-bordered table-condensed'></table>");
	var thead = $("<thead></thead>");
	var tmpTr = $("<tr></tr>");
	for(var i=0; i<names.length; i++){
		tmpTr.append($("<th></th>").text(names[i]));
	}
	thead.append(tmpTr);
	table.append(thead);
	var tbody = $("<tbody></tbody>");
	for(var i=0; i<datas.length; i++){
		tmpTr = $("<tr onclick='addTrListener(this)'></tr>");
		for(var j=0; j<datas[i].length; j++){
			tmpTr.append($("<td></td>").text(datas[i][j]));
		}
		tbody.append(tmpTr);
	}
	table.append(tbody);
	return table;
}

var compareTableSize = 10;
function createAllCompareTables(results){
	var names = results['names'];
	if(!names) return
	var datas = results['datas'];
	var ids = results['ids']
	var compareContainer = $("<div id='compareContainer' style='width:100%;height:100%;overflow:hidden;'></div>");
        var modalHeader = $("<div class='modal-header' style='background-color:#1b1b1b;color:white;height:6%;'></div>");
        var closeButton = $("<button type='button' style='color:white;' class='close' data-dismiss='modal' aria-hidden='true'>×</buttton>");
        modalHeader.append(closeButton);
	var popTitle = $("<h3>Showing All Tables</h3>");
        modalHeader.append(popTitle);
	compareContainer.append(modalHeader);
	for(var i=0; i<ids.length; i++){
		tmpinput = $("<input type='hidden' value='"+ids[i]+"' name='testids'/>");
		compareContainer.append(tmpinput);
	}
        var modalBody = $("<div class='modal-body' style='max-height:88%;'></div>");
	var count = datas.length;
	for(var i=0; i<count; i++){
		var tableContainer = $("<div class='compareTableContainer' id='compareTableContainer" + i + "'></div>");
		var cuple = datas[i];
		var bodyDiv = $("<div class='compareTableBody'></div>");
		var titleDiv = $("<h4 class='pull-left' id='"+cuple[0]+"'></h4>").text(cuple[0]);
		bodyDiv.append(titleDiv)
		var showingTabel = $("<div class='showingtable pull-right text-info' style='padding-top:10px;'>showing 1 to "+compareTableSize+"</div>");
		bodyDiv.append(showingTabel);
		var theRealTable = $("<div class='realTableContainer'></div>");
		var table = createCompareTable(names, cuple[1], "compareTable"+i);
		theRealTable.append(table);
		var startTag = $("<input type='hidden' value='0' name='compareStart' />");
		theRealTable.append(startTag);
		var endTag = $("<input type='hidden' value='"+compareTableSize+"' name='compareEnd' />");
		theRealTable.append(endTag);
		bodyDiv.append(theRealTable);
		var nextButton = $("<div class='btn btn-inverse pull-right' style='margin-right:10px;' onclick='compareNext(this)'>Next</div>");
		bodyDiv.append(nextButton);
		var previousButton = $("<div class='btn btn-inverse disabled pull-right' style='margin-right:10px;' onclick='comparePrevious(this)'>Previous</div>");
		bodyDiv.append(previousButton);
		var compareButton = $("<div class='btn btn-inverse pull-right' style='margin-right:10px;' onclick='showCompareSelectedDatas(this)'>Compare</div>");
		bodyDiv.append(compareButton);
		var lastLine = $("<div class='lastline' style='clear:both;margin-bottom:10px;'></div>");
		bodyDiv.append(lastLine);
		tableContainer.append(bodyDiv);
		modalBody.append(tableContainer);
	}
        compareContainer.append(modalBody);
	$("#container").html(compareContainer);
}

function compareNext(element){
	$(element).parent().find('div[class~=disabled]').removeClass("disabled");
	var tableName = $(element).parent().parent().parent().parent().find("h3").text();
	ids = [];
	$("input[name='testids']").each(function(i, e){
		ids.push($(e).val());
	});
	var realTableContainer = $(element).parent().find("div[class='realTableContainer']");
	var start = parseInt(realTableContainer.find("input[name='compareStart']").val()) + compareTableSize;
	var end = parseInt(realTableContainer.find("input[name='compareEnd']").val()) + compareTableSize;
	context = {'tableName': tableName, 'ids': ids, 'start': start, 'end': end}
	loadShowTable(context, 'json', '/show/loadcomparetable', compareNextCallback);
}

function compareNextCallback(result){
	var datas = result['datas'][0];
	var names = result['names'];
	var start = result['start'];
	var end = result['end'];
	var tablename = datas[0];
        idTableName = tablename.replace(/ /g, '');
	var oldTable = $("h3[id='"+idTableName+"']").parent().find("table");
	var tableId = oldTable.attr('id');
	var table = createCompareTable(names, datas[2], tableId);
	var tableContainer = $("h3[id='"+idTableName+"']").parent().find("div[class='realTableContainer']");
	tableContainer.html('');
	tableContainer.append(table);
	var startTag = $("<input type='hidden' value='"+start+"' name='compareStart' />");
        tableContainer.append(startTag);
        var endTag = $("<input type='hidden' value='"+end+"' name='compareEnd' />");
        tableContainer.append(endTag);
	var showingtabel = $("h3[id='"+idTableName+"']").parent().find("div[class='showingtable pull-right text-info']");
	tmpStart = parseInt(start);
	showingtabel.text("showing " + tmpStart + " to " + end);

	var rawRows = storage.getItem(tablename);
        var selectedRows = null;
        if(rawRows){
	        rawRows = rawRows.substr(0, rawRows.length-2);
	        selectedRows = rawRows.split("||");
        }
	$(table).find("tbody tr").each(function(i, e){
		var tmp = "";
		$(e).find("td").each(function(j,tde){
			tmp += $(tde).text()+"+";
		});
		tmp = tmp.substr(0,tmp.length-1);
		if(selectedRows&&selectedRows.indexOf(tmp)>=0){
			$(e).addClass("selectedRow");
		}
	});
}

function comparePrevious(element){
	var tableName = $(element).parent().parent().parent().parent().find("h3").text();
        ids = [];
        $("input[name='testids']").each(function(i, e){
                ids.push($(e).val());
        });
        var realTableContainer = $(element).parent().find("div[class='realTableContainer']");
        var start = parseInt(realTableContainer.find("input[name='compareStart']").val());
	if(start>1){
		start = start - compareTableSize;
        	var end = parseInt(realTableContainer.find("input[name='compareEnd']").val()) - compareTableSize;
	}else{
		return;
	}
	if(start<10){
		$(element).addClass("disabled");
	}
        context = {'tableName': tableName, 'ids': ids, 'start': start, 'end': end}
        loadShowTable(context, 'json', '/show/loadcomparetable', compareNextCallback);
}


storage = window.localStorage;

function addTrListener(element){
        var tableName = $(element).parent().parent().parent().parent().parent().parent().parent().find("h3").text();
        if($(element).hasClass('selectedRow')){
                $(element).removeClass("selectedRow");
                var tmpOne = ""
                $(element).find("td").each(function(i, e){
                        tmpOne = tmpOne + $(e).text() + "+";
                });
                tmpOne = tmpOne.substring(0, tmpOne.length-1);
                var value = storage.getItem(tableName);
                start = value.indexOf(tmpOne);
                value = value.substr(0, start) + value.substr(start+tmpOne.length+2);
                storage.setItem(tableName, value);

        }else{
                $(element).addClass("selectedRow");
                var tmpOne = ""
                $(element).find("td").each(function(i, e){
                        tmpOne = tmpOne + $(e).text() + "+";
                });
                tmpOne = tmpOne.substring(0, tmpOne.length-1);
                var value = storage.getItem(tableName);
                if(value == null){
                        value = "";
                }
                value = value + tmpOne + "||";
                storage.setItem(tableName, value);
        }
}
  

function showCompareSelectedDatas(element){
        var names = [];
        var categories = [];
        var values = [];
        var tableName = $(element).parent().parent().parent().parent().find("h3").text();
        var tmpValues = storage.getItem(tableName);
        tmpValues = tmpValues.substr(0, tmpValues.length-2);
        var rows = tmpValues.split("||");
        for(var i=0; i<rows.length; i++){
                var row = rows[i];
                items = row.split('+');
                categories.push(items[0]);
                tmp = [];
                for(var j=1; j<items.length; j++){
                        tmp.push(items[j]);
                }
                values.push(tmp);
        }
        var table = $(element).parent().find("table");
        $(table).find("thead tr th").each(function(i, e){
                if(i==0) return;
                names.push($(e).text());
        });
        var series = [];
        for(var i=0; i<names.length; i++){
                var data = [];
                for(var j=0; j<values.length; j++){
                        data.push(parseFloat(values[j][i]));
                }
                series.push({'name': names[i], 'data': data});
        }
        alldatas = {'categories': categories, 'series': series}
        createChart(alldatas, 'rightChart'+tableName.replace(/ /g, ''), 1200, 570);
        $('#chartContainer').modal('show');
}

function showOverviewDatas(){
        $('div.row-fluid').each(function(i,e){
                var series = [];
                var categories = [];
                var tableName = $(e).attr('id');
                $(e).find('table thead tr th').each(function(j, ce){
                        if(j==0) return;
                        var tmp = {'name':$(ce).text().trim(), 'data':[]};
                        series.push(tmp);
                });
                $(e).find('table tbody tr').each(function(j, ce){
                        $(ce).find('td').each(function(k, cce){
                                if(k==0) categories.push($(cce).text().trim());
                                else{
                                        series[k-1]['data'].push(parseFloat($(cce).text().trim()));
                                }
                        });
                });
                if(categories.length>0){
                        alldatas = {'categories': categories, 'series': series};
                        createChart(alldatas, 'chart'+tableName, 1200, 570);
                }
        });
}
function showModelsAnalysisDatas(){
        $('div#datasBlock table').each(function(i, e){
                var tableId = $(e).attr('id');
                var isFirstTime = true;
                var allDatas = [];
                var firstTime = true;
                var tmpLabels = [];
                var groupNames = [];
                $(e).find('tr').each(function(j, ce){
                        var tmpDatas = [];
                        $(ce).find('td').each(function(k, cce){
                                tmpDatas.push(parseFloat($(cce).text()));
                                if(firstTime){
                                        tmpLabels.push(k+' s');
                                }
                        });
                        firstTime = false;
                        allDatas.push(tmpDatas);
                        groupNames.push($(ce).attr('id'));
                });
                createSimpleLine(allDatas, tmpLabels, groupNames, tableId+'Charts', 1300, 400);
        });
}

function compare(){
        var url = "/show/analysiscompare?";
        var chooseItem = false;
        $('input[name="resultshow"]:checked').each(function(i, e){
                chooseItem = true;
                url = url + "ids=" + $(e).val() + "&";
        });
        if(!chooseItem){
                alert('PLEASE CHOOSE A TEST');
                return;
        }
        popBlankPage(url);
}
function overview(){
        var url = "/show/analysisoverview?";
        var chooseItem = false;
        $('input[name="resultshow"]:checked').each(function(i, e){
                chooseItem = true;
                url = url + "ids=" + $(e).val() + "&";
        });
        if(!chooseItem){
                alert('PLEASE CHOOSE A TEST');
                return;
        }
        popBlankPage(url);
}
function analysis(){
        var url = "/show/analysisanalysis?";
        var chooseItem = false;
        $('input[name="resultshow"]:checked').each(function(i, e){
                chooseItem = true;
                url = url + "ids=" + $(e).val() + "&";
        });
        if(!chooseItem){
                alert('PLEASE CHOOSE A TEST');
                return;
        }
        popBlankPage(url);
}
function modelsAnalysis(){
        var url = "/show/analysismodelsanalysis?";
        var chooseItem = false;
        $('input[name="resultshow"]:checked').each(function(i, e){
                chooseItem = true;
                url = url + "ids=" + $(e).val() + "&";
        });
        if(!chooseItem){
                alert('PLEASE CHOOSE A TEST');
                return;
        }
        popBlankPage(url);
}
