
function upload(uptag){
        $('#uploadpop').modal('show');
}

function inputchange(tag){
    var pre_input = $(tag).prevAll("input");
    $(pre_input).val($(tag).val());
}
function hidelast(){
        $('#uploadpop').modal('hide');
}
function cancelUpload(){
    $("input[name='showinput']").each(function(i,n){
	$(n).val('');
    });
    $("input[name='upload']").each(function(i,n){
	$(n).val('');
    });
    hidelast()
}

function submitUpload(){
    hidelast()
    $("#choosedalert").removeClass("hidden").addClass("showalert");
}
function addUploadRow(){
        var str = "<div class='uploadrow pull-left' style='width:55%;margin-top:10px;'>";
	str +="<input class='uploadcolumn pull-left' style='margin-left:15px;margin-top:2px;' name='showinput'/>";
	str +="<div class='uploadcolumn btn btn-inverse pull-left' style='margin-left:5px;'><i class='icon-folder-open icon-white'></i> select file</div>";
	str +="<input class='hiddeninput pull-left' style='filter: alpha(opacity=0);opacity:0;position: absolute;right: 45%;cursor: pointer;' name='upload' type='file' onchange='inputchange(this)' />";
	str +="</div>";
        $("#uploadrow").append(str);
    	count = count + 1;
}
