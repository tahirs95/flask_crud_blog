var getUrl = window.location;
var baseUrl = getUrl .protocol + "//" + getUrl.host;
console.log(baseUrl);
$body = $("body");
$(document).ajaxStart(function(){
    console.log("start");
    $body.addClass("loading"); 
   
});

$(document).ajaxComplete(function()  {
  console.log("end");
  $body.removeClass("loading");
  if($('#delete').length>0){

  }
  else if($('#update').length>0){
    
  }
  else{
    window.location.href =baseUrl;
  }
  
}); 