// taken from EFF Panopticlick project
$("#flashcontent").flash(
  {
    "src": "resources/fonts2.swf",
    "width": "1",
    "height": "1",
    "swliveconnect": "true",
    "id": "flashfontshelper",
    "name": "flashfontshelper"
  },
  { update: false }
);


var success = 0;
var retries = 2;  // max retry count for POST

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


function test_dom_storage(){
  var supported = "";
  try {
    if (localStorage.panopticlick == "yea") {
       supported += "DOM localStorage: Yes";
    } else {
       supported += "DOM localStorage: No";
    }
  } catch (ex) { supported += "DOM localStorage: No"; }

  try {
    if (sessionStorage.panopticlick == "yea") {
       supported += ", DOM sessionStorage: Yes";
    } else {
       supported += ", DOM sessionStorage: No";
    }
  } catch (ex) { supported += ", DOM sessionStorage: No"; }

  return supported;
}


function identify_plugins(){
  // fetch and serialize plugins
  var plugins = "";
  // in Mozilla and in fact most non-IE browsers, this is easy
  if (navigator.plugins) {
    var np = navigator.plugins;
    var plist = new Array();
    // sorting navigator.plugins is a right royal pain
    // but it seems to be necessary because their order
    // is non-constant in some browsers
    for (var i = 0; i < np.length; i++) {
      plist[i] = np[i].name + "; ";
      plist[i] += np[i].description + "; ";
      plist[i] += np[i].filename + ";";
      for (var n = 0; n < np[i].length; n++) {
        plist[i] += " (" + np[i][n].description +"; "+ np[i][n].type +
                   "; "+ np[i][n].suffixes + ")";
      }
      plist[i] += ". ";
    }
    plist.sort(); 
    for (i = 0; i < np.length; i++)
      plugins+= "Plugin "+i+": " + plist[i];
  }
  // in IE, things are much harder; we use PluginDetect to get less
  // information (only the plugins listed below & their version numbers)

  return plugins;
}

function get_fonts() {
  // Try flash first
  var fonts = "";
  var obj = document.getElementById("flashfontshelper");
  if (obj && typeof(obj.GetVariable) != "undefined") {
    fonts = obj.GetVariable("/:user_fonts");
    fonts = fonts.replace(/,/g,", ");
    fonts += " (via Flash)";
  } else {
    console.log("No flash placeholder flashcontent");
    // Try java fonts
    try {
      var javafontshelper = document.getElementById("javafontshelper");
      var jfonts = javafontshelper.getFontList();
      for (var n = 0; n < jfonts.length; n++) {
        fonts = fonts + jfonts[n] + ", ";
      }
    fonts += " (via Java)";
    } catch (ex) {}
  }
  if ("" == fonts)
    fonts = "No Flash or Java fonts detected";
  return fonts;
}


function fetch_client_whorls(){
  // fetch client-side vars
  var whorls = new Object();

  // this is a backup plan
  setTimeout("retry_post()",1100);


  try { 
    whorls['plugins'] = identify_plugins(); 
  } catch(ex) { 
    whorls['plugins'] = "permission denied";
  }

  // Do not catch exceptions here because the async Flash applet will raise
  // them until it is ready.  Instead, if Flash is present, the retry timeout
  // will cause us to try again until it returns something meaningful.

  whorls['fonts'] = get_fonts();
  
  try { 
    whorls['timezone'] = new Date().getTimezoneOffset();
  } catch(ex) {
    whorls['timezone'] = "permission denied";
  }

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
  whorls['supercookies'] = test_dom_storage();

  // send to server for logging / calculating
  // and fetch results

  var callback = function(results){
    success = 1;
    $('#content').html(results);
  };

  $.post("/?action=ajax_post_client_vars", whorls, callback, "html" );
  
};

function set_dom_storage(){
  try { 
    localStorage.panopticlick = "yea";
    sessionStorage.panopticlick = "yea";
  } catch (ex) { }
}

set_dom_storage();

$(document).ready(function(){
  // wait some time for the flash font detection:
  setTimeout("fetch_client_whorls()",1000);
});