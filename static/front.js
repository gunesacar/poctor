// Send browsers that support JavaScript to the AJAX version of the
// test
$(document).ready(function(){
  $('#clicklink').attr('href',$('#clicklink').attr('href') + '&js=yes');
});
