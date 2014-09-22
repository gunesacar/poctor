// based on EFF's Panopticlick
(function () {
    "use strict";
    var plugins = "";
    if (navigator.plugins) {
        var np = navigator.plugins;
          var plist = new Array();
          // pde: sorting navigator.plugins is a right royal pain
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
    test_runner.add_test("navigator.plugins", plugins);

}());
