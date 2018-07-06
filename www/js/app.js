define(function(require) {
    "use strict";

    $ = require('jquery');
    _ = require('underscore');
    var Main = require('text!views/main.html');
    var APIManager = require('APIManager');
    var Tracker = require('Tracker');
    var utils = require('Utils');

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

        $('.root').append(mainEl);
        this._input = input;
        this._button = button;
        this._resultEl = resultEl;

        this.setup();
    }

    // ------------------------------------------------------------------------
    // METHODS
    // ------------------------------------------------------------------------
    App.prototype = {
        constructor: App,
        
        setup: function() {
            var that = this;

            // handle button click
            this._button.click(function() {
                that.onSendText();
            });

            // handle key press for text area
            this._input.on("keypress", function(e) {
                if (e.keyCode == 13) {
                    e.preventDefault();
                    that.onSendText();
                }
            });
        },

        onSendText: function() {
            // start download and add tracker view (use then)
            APIManager.newDownload(this._input.val(), this).done(this.onNewSuccess).fail(this.onNewError);

            // clear input
            this._input.val('');
        },

        addTracker: function(data) {
            var info = utils.parseSafely(data) || {};
            var reqId = info['reqId'] || null;
            var url = info['url'] || '';
            var title = info['title'] || '';
            var thumbnailUrl = info['thumbnail_url'] || '';
            var duration = info['duration'] || 0;
            new Tracker(reqId, url, title, thumbnailUrl, duration, this._resultEl);
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