(function () {
    "use strict";
    // test OS locale leak via datetime localization
    // https://trac.torproject.org/projects/tor/ticket/5926 esp. #comment:7
    var add_test = test_runner.addTest,
        epoch = new Date(Date.UTC(1970, 0, 1));
    // take a fixed reference time (epoch) and check localized version 
    add_test("locale.epoch_full_weekday", function(){
        return epoch.toLocaleFormat("%A");
    });
    add_test("locale.epoch_abbr_weekday", function(){
        return epoch.toLocaleFormat("%a");
    });
    // epoch weekday may be Wed or Thu depending on the TZ, let's store as numeric
    add_test("locale.epoch_weekday_number", function(){
        return epoch.toLocaleFormat("%u");
    });
    add_test("locale.epoch_full_month", function(){
        return epoch.toLocaleFormat("%B");
    });
    add_test("locale.epoch_abbr_month", function(){
        return epoch.toLocaleFormat("%b");
    });
    add_test("locale.epoch_24hrs", function(){
        return epoch.toLocaleFormat("%H");
    });
    add_test("locale.timezone_name", function(){
        return epoch.toLocaleFormat("%Z");
    });
    
}());
