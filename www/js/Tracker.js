define(function(require) {
    "use strict";

    $ = require('jquery');
    _ = require('underscore');
    var APIManager = require('APIManager');
    var Card = require('text!views/card.html');
    var utils = require('Utils');

    // ------------------------------------------------------------------------
    // CONSTRUCTOR
    // ------------------------------------------------------------------------
    function Tracker(reqId, containerEl) {
        if (!(this instanceof Tracker)) {
            throw new TypeError("Tracker constructor cannot be called as a function.");
        }

        var cardEl = $(_.template(Card)());
        containerEl.prepend(cardEl);

        // hold views
        this._dlButton = cardEl.find('a.btn').first();
        this._progressBar = cardEl.find('.progress-bar').first();

        // start polling
        this._pollTimeout = this.polling();
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
            return setTimeout(function() {
                // real works here
                that.doPolling();
                
                // polling logics
                that._accPollTime += Tracker.POLL_INTERVAL;
                if (that._accPollTime <= Tracker.MAX_POLL_TIME) {
                    that._pollTimeout = that.polling();
                }
            }, Tracker.POLL_INTERVAL);
        },

        doPolling: function() {
            APIManager.listDownload(this._reqId, this).done(function(data, status) {
                console.log('List download for: ' + this._reqId);

                var info = utils.parseSafely(data)[0] || {};

                if (info.progress < 100) {
                    this.onProgress(info.progress);

                } else if (info.progress == 100) {
                    this.onComplete(info);

                    // clear setTimeout
                    clearTimeout(this._pollTimeout);
                    this._pollTimeout = null;
                }
                
            }).fail(function() {
                console.log('Failed to list download for: ' + this._reqId);
            });
        },

        onProgress: function(progress) {
            console.log('Progress: ' + progress);

            var progressText = progress + '%';
            this._progressBar.text(progressText);
            this._progressBar.css({width: progressText});
        },

        onComplete: function(info) {
            console.log('Complete: ' + info);

            // force progress to 100
            this.onProgress(100);
        }
    };

    return Tracker;
});