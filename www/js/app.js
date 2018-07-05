define(function(require) {
    "use strict";

    $ = require('jquery');
    _ = require('underscore');
    var Main = require('text!views/main.html');
    var APIManager = require('APIManager');
    var Tracker = require('Tracker');

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
        var resultEl = mainEl.find('.result').first();
        
        var that = this;
        button.click(function() {
            // start download and add tracker view (use then)
            APIManager.newDownload(input.text(), that).done(that.onNewSuccess).fail(that.onNewError);
        });

        $('.root').append(mainEl);
        this._resultEl = resultEl;
    }

    // ------------------------------------------------------------------------
    // METHODS
    // ------------------------------------------------------------------------
    App.prototype = {
        constructor: App,

        addTracker: function(reqId) {
            new Tracker(reqId, this._resultEl);
        },

        onNewSuccess: function(data, status) {
            this.addTracker(data);
        },

        onNewError: function(jqXHR, textStatus, errorThrown) {
            console.log('Failed to start download');
        }
    };

    return App;
});