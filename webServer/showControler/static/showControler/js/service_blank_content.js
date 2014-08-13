
function showServiceTestsChart(){
        var series = [];
        var categories = [];
        $('#testsTable').find('table thead tr th').each(function(j, ce){
                if(j==0) return;
                var tmp = {'name':$(ce).text().trim(), 'data':[]};
                series.push(tmp);
        });
        var count = 0;
        $('#testsTable').find('table tbody tr').each(function(j, ce){
                $(ce).find('td').each(function(k, cce){
                        if(k==0) categories.push($(cce).text().trim());
                        else{
                                series[k-1]['data'].push(parseFloat($(cce).text().trim()));
                        }
                });
                count += 1;
        });
        if(categories.length>0){
                alldatas = {'categories': categories, 'series': series};
                var width = count*150;
                if(width < 1200) width = 1200;
                createChart(alldatas, 'testsChartContainer', width, 600);
        }
        /**
        testFeaturesLabels = []
        testFeaturesDatas = []
        $('#testFeatures li').each(function(i, e){
                testFeaturesLabels.push($(e).find('span[class="first"]').text())
                testFeaturesDatas.push(parseFloat($(e).find('span[class="second"]').text()))
        });
        countTests = testFeaturesDatas.length
        if(countTests>0){
                //w = countTests*150
                //if(w < 1200) w = 1200;
                var w = document.body.clientWidth-100;
                var h = 150;
                createSimpleLine(testFeaturesDatas, testFeaturesLabels, 'testsFeaturesChartContainer', w, h)
        }*/
}
