define(function(require) {
    "use strict";

    $ = require('jquery');
    _ = require('underscore');
    var APIManager = require('APIManager');
    var Card = require('text!views/card.html');

    // ------------------------------------------------------------------------
    // CONSTRUCTOR
    // ------------------------------------------------------------------------
    function Tracker(reqId, containerEl) {
        if (!(this instanceof Tracker)) {
            throw new TypeError("Tracker constructor cannot be called as a function.");
        }

        var cardEl = $(_.template(Card)());
        containerEl.append(cardEl);

        // hold views
        var dlButton = cardEl.find('a.btn').first();
        this._dlButton = dlButton;

        // start polling
        this.polling();
        this._accPollTime = 0;

        this._reqId = reqId;
    }

    // ------------------------------------------------------------------------
    // STATIC FIELDS
    // ------------------------------------------------------------------------
    Tracker.MAX_POLL_TIME = 10000;
    Tracker.POLL_INTERVAL = 500;
    
    // ------------------------------------------------------------------------
    // METHODS
    // ------------------------------------------------------------------------
    Tracker.prototype = {
        constructor: Tracker,

        polling: function() {
            console.log('Polling, accumulated time: ' + this._accPollTime);
            var that = this;
            setTimeout(function() {
                // real works here
                that.doPolling();
                
                // polling logics
                that._accPollTime += Tracker.POLL_INTERVAL;
                if (that._accPollTime <= Tracker.MAX_POLL_TIME) {
                    that.polling();
                }
            }, Tracker.POLL_INTERVAL);
        },

        doPolling: function() {
            APIManager.listDownload(this._reqId).done(function(data, status) {
                console.log('List download for: ' + this._reqId);
                console.log(data);
            }).fail(function() {
                console.log('Failed to list download for: ' + this._reqId);
            });
        },
    };

    return Tracker;
});