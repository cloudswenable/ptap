/**
 * Created by ysun49 on 14-3-25.
 */

function getRandomColor(value){
        var negative = false;
        var tmp = value;
        if(Math.random()<0.5){
             negative = true;
        }
        if(negative){
                tmp -= Math.floor(Math.random()*30);
        }else{
                tmp += Math.floor(Math.random()*30);
        }
        if(tmp<0) tmp = 0;
        if(tmp>255) tmp = 255;
        return tmp;
}
var readyColors = [[47,126,216],[13,35,58],[164,213,58],[170,25,25],[26,173,206],[73,41,112],[255,168,92],[119,161,229],[0,76,134],[166,166,106],[232,68,114], [53, 183, 83], [67, 76, 100], [116, 16, 153]];
function createLineChart(resultDatas, container, w, h){
        var series = resultDatas['series'];
        var groupNames = [];
        var groupDatas = [];
        for(var i=0; i<series.length; i++){
                groupNames.push(series[i]['name']);
                groupDatas.push(series[i]['data']);
        }
        var labels = resultDatas['categories'];
        var chartContainer = $('#'+container).html("");
        var realChart = $("<canvas id='realChart"+container+"' width='"+w+"' height='"+h+"' style='padding:10px 10px;'></canvas>");
        chartContainer.append(realChart);
        var line = new RGraph.Line('realChart'+container, groupDatas)
                                .set('curvy', true)
                                .set('curvy.tickmarks', true)
                                .set('curvy.tickmarks.fill', null)
                                .set('curvy.tickmarks.stroke', '#aaa')
                                .set('curvy.tickmarks.stroke.linewidth', 2)
                                .set('curvy.tickmarks.size', 5)
                                .set('linewidth', 3)                
                                .set('hmargin', 5)
                                .set('linewidth', 3)
                                .set('hmargin', 5)
                                .set('labels', labels)
                                .set('tickmarks', 'circle')
                                .trace();
}
function createSimpleLine(datas, labels, groupNames, container, w, h){
        var chartContainer = $('#'+container).html("");
        var realChart = $("<canvas id='simpleLine"+container+"' width='"+w+"' height='"+h+"' style='padding:10px 10px;'></canvas>");
        chartContainer.append(realChart);
        var line = new RGraph.Line('simpleLine'+container, datas)
                        .set('labels', labels)
                        .set('key', groupNames)
                        .set('key.interactive', true)
                        .set('gutter.left', 100)                
                        .set('scale.decimals', 2)
                        .trace();
}
function createChart(resultDatas, container, w, h){
        var series = resultDatas['series'];
        var groupNames = [];
        var groupDatas = [];
        for(var i=0; i<series.length; i++){
                groupNames.push(series[i]['name']);
                groupDatas.push(series[i]['data']);
        }
        var labels = resultDatas['categories'];
        var data = [];
        var colors = [];
        var count = 0;
        var max = -9999999999;
        var min = 9999999999;
        for(var i=0; i<groupDatas.length; i++){
                var red = 0, green = 0, blue = 0;
                if(count>=readyColors.length){
                        count = count % readyColors.length;
                        red = getRandomColor(readyColors[count][0]);
                        green = getRandomColor(readyColors[count][1]);
                        blue = getRandomColor(readyColors[count][2]);
                }else{
                        red = readyColors[count][0];
                        green = readyColors[count][1];
                        blue = readyColors[count][2];
                }
                var colorStr = 'rgb('+red+','+green+','+blue+')';
                colors.push(colorStr);
                count += 1;
                for(var j=0; j<groupDatas[i].length; j++){
                        var tmpData = groupDatas[i][j];
                        if(tmpData > max) max = tmpData;
                        if(tmpData < min) min = tmpData;
                        if(i==0){
                                data.push([tmpData]);
                        }else{
                                data[j].push(tmpData);
                        }
                }
        }
        var chartContainer = $('#'+container).html("");
        var realChart = $("<canvas id='realChart"+container+"' width='"+w+"' height='"+h+"' style='padding:10px 10px;'></canvas>");
        chartContainer.append(realChart);
        var bar = new RGraph.Bar('realChart'+container, data)
                .set('colors', colors)
                .set('labels', labels)
                .set('key', groupNames)
                .set('key.background', 'rgba(255,255,255,0.2)')
                .set('key.interactive', true)
                .set('gutter.left', 55)                
                .set('gutter.bottom', 150)
                .set('text.angle', '45')
                .set('hmargin', 15) 
                .set('hmargin.grouped', 2)               
                .set('variant', '2d')
                .set('strokestyle', 'transparent');
        if(max <= 1){
                bar.set('ylabels.count', 1);
                bar.set('scale.decimals', 2);
        }else if(max < 10) bar.set('ylabels.count', 5);
        else bar.set('ylabels.count', 10);

        if(max > 1000000) bar.set('gutter.left', 120);

        if(min < 0) bar.set('xaxispos', 'center');
        bar.grow();
}

function showChart(){
	var choose_input = $("input[name='rowchoose']:checked");
    	var id = $(choose_input).val();
    	if(!id){
        	alert("must choose a object");
        	return;
    	}
	var dic = {"type": "results", "id": id}
	var resultDatas;
        $.ajax({
            type: "GET",
            async: false,
            url: "/show/showresult/",
            dataType: "json",
	    data: dic, 
            success: function(result) {
		resultDatas = result;
            }
        });
	createChart(resultDatas, 'container', 850, 550);
        $('#container').modal('show');
}
