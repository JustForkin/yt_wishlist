define(function(require) {
    "use strict";

    $ = require('jquery');
    _ = require('underscore');
    var Main = require('text!views/main.html');

    // ------------------------------------------------------------------------
    // CONSTRUCTOR
    // ------------------------------------------------------------------------
    function App() {
        if (!(this instanceof App)) {
            throw new TypeError("App constructor cannot be called as a function.");
        }

        var mainEl = $(_.template(Main)());
        var input = mainEl.find('input').first();
        var button = mainEl.find('button').first();
        
        var that = this;
        button.click(function() {
            // start download and add tracker view (use then)
            App.newDownload(input.text());
        });

        $('.root').append(mainEl);
        
    }

    // ------------------------------------------------------------------------
    // STATIC METHODS
    // ------------------------------------------------------------------------
    App.newDownload = function(url, context) {
        var url = '/new';
        var data = {'url': url};

        return $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            context: context != null ? context : null,
        });
    };
    
    // ------------------------------------------------------------------------
    // METHODS
    // ------------------------------------------------------------------------
    App.prototype = {
        constructor: App,

        addTracker: function(user) {
        },
    };

    return App;
});