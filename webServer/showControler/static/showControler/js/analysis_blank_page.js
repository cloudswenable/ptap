
function showAnalysisMetrics(element){
        var metricName = $(element).find('a').text();
        var ids = [];
        $('input[name="ids"]').each(function(i, e){
                ids.push($(e).val());
        });
        context = {'metricName': metricName, 'ids':ids};
        loadShowTable(context, "text", "/show/analysisanalysisrightpage", analysis_analysis_right_content);
}

function analysis_analysis_right_content(results){
        $('#rightcontent').html(results);
        showAnalysisChart();
}

function showAnalysisChart(){
        var series = [];
        var categories = [];
        $('#showTableContainer').find('table thead tr th').each(function(j, e){
                if(j==1){
                        categories.push($(e).text().trim());
                }
        });
        $('#showTableContainer').find('table tbody tr').each(function(i, e){
                var tmp = {};
                $(e).find('td').each(function(j, ce){
                        if(j==0) tmp['name'] = $(ce).text().trim();
                        else if(j==1){
                                var tmptmp = [];
                                tmptmp.push(parseFloat($(ce).text().trim()));
                                tmp['data'] = tmptmp;
                        }
                });
                series.push(tmp);
        });
        if(categories.length>0){
                alldatas = {'categories': categories, 'series': series};
                createChart(alldatas, 'showChartContainer', 900, 300);
        }
}
