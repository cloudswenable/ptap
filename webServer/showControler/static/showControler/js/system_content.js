function doAction(url){
	var form = $('<form></form>');
	form.attr("action", url);
	form.submit();
}
function syncMachines(){
	var url = "/show/sync/";
	doAction(url);
}
function clearMachines(){
	var url = "/show/clear/";
	doAction(url);
}
