// taken from EFF Panopticlick project
var success = 0;
var retries = 2;

function retry_post() {
  retries = retries -1;
  if (success || retries == 0)
    return 0;
  // no luck yet
  fetch_client_whorls()
}

// TODO add these to post data
function print_combined_fp(){
    var result_el = document.getElementById("json_result");
    if (result_el && test_runner && test_runner.tests){
        result_el.textContent = JSON.stringify(test_runner.tests, null,"    ");
    } else {
        result_el.textContent = "Failed. test_runner: " + test_runner + " Result element: " + result_el;
    }
}

function fetch_client_whorls(){
  // fetch client-side vars
  var whorls = new Object();

  // this is a backup plan
  setTimeout("retry_post()",1100);

  try {
    whorls['video'] = screen.width+"x"+screen.height+"x"+screen.colorDepth;
  } catch(ex) {
    whorls['video'] = "permission denied";
  }
  try {
    whorls['js_user_agent'] = navigator.userAgent;
  } catch(ex) {
    whorls['js_user_agent'] = "permission denied";
  }
  // send to server for logging / calculating
  // and fetch results

  var callback = function(results){
    success = 1;
    $('#content').html(results);
  };

  $.post("/?action=ajax_post_client_vars", whorls, callback, "html" );
  
};


$(document).ready(function(){
  // wait some time for the flash font detection:
  setTimeout("fetch_client_whorls()",1000);
});