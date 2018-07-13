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
            this.setProcessing(true);
            
            // start download and add tracker view (use then)
            APIManager.newDownload(this._input.val(), this).done(this.onNewSuccess).fail(this.onNewError);

            // clear input
            this._input.val('');
        },

        addTracker: function(data) {
            var infoList = utils.parseSafely(data) || [];
            for (var num in infoList) {
                var info = infoList[num];
                new Tracker(info, this._resultEl);
            }
            
        },

        onNewSuccess: function(data, status) {
            this.setProcessing(false);
            this.addTracker(data);
        },

        onNewError: function(jqXHR, textStatus, errorThrown) {
            this.setProcessing(false);
            console.log('Failed to start download');
        },

        setProcessing: function(flag) {
            this._button.text(flag ? 'Processing...' : 'Download');
            this._button.prop('disabled', flag);
            this._input.prop('disabled', flag);
        }
    };

    return App;
});