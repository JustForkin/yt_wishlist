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
    function Tracker(info, containerEl) {
        if (!(this instanceof Tracker)) {
            throw new TypeError("Tracker constructor cannot be called as a function.");
        }
        var reqId = info['id'] || null;
        var url = info['url'] || '';
        var title = info['title'] || '';
        var thumbnailUrl = info['thumb_url'] || '';
        var duration = info['duration'] || 0;
        var status = info['status'] || '';
        var progress = info['progress'] || 0;
        var path = info['path'] || '';

        var template_info = {'title': title,
                'url': url,
                'thumbnailUrl': thumbnailUrl,
                'duration': duration};
        var cardEl = $(_.template(Card)(template_info));
        containerEl.prepend(cardEl);

        // hold views
        this._dlButton = cardEl.find('.card-button').first();
        this._progressBar = cardEl.find('.progress-bar').first();
        this._progress = cardEl.find('.progress').first();
        this._dlButtonTarget = cardEl.find('.card-button-target').first();

        this._reqId = reqId;

        // polling data
        this._pollTimeout = null;
        this._accPollTime = 0;

        this.initialize(status, progress, path);
    }

    // ------------------------------------------------------------------------
    // STATIC FIELDS
    // ------------------------------------------------------------------------
    Tracker.MAX_POLL_TIME = 60000;
    Tracker.POLL_INTERVAL = 1000;
    
    // ------------------------------------------------------------------------
    // METHODS
    // ------------------------------------------------------------------------
    Tracker.prototype = {
        constructor: Tracker,

        initialize: function(status, progress, path) {
            if (status == 'pending') {
                this.onPending();

                // start polling
                this._pollTimeout = this.polling();

            } else if (status == 'downloading') {
                this.onProgress(progress);

                // start polling
                this._pollTimeout = this.polling();

            } else if (status == 'finished') {
                this.onComplete(path);
            } else if (status == 'failed') {
                this.onFailed();
            }
        },

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

                if (info.status == 'downloading' && info.progress < 100) {
                    this.onProgress(info.progress);

                } else if (info.status == 'finished' || info.progress == 100) {
                    this.onComplete(info.path);

                    // clear setTimeout
                    clearTimeout(this._pollTimeout);
                    this._pollTimeout = null;
                }
                
            }).fail(function() {
                console.log('Failed to list download for: ' + this._reqId);
            });
        },

        onPending: function() {
            this._progress.show();
            this._dlButtonTarget.hide();
            this._progressBar.text('');
            this._progressBar.css({width: '100%'});
            this._progressBar.addClass('progress-bar-striped progress-bar-animated');
        },

        onProgress: function(progress) {
            console.log('Progress: ' + progress);

            var progressText = progress + '%';
            this._progress.show();
            this._dlButtonTarget.hide();
            this._progressBar.text(progressText);
            this._progressBar.css({width: progressText});
            this._progressBar.removeClass('progress-bar-striped progress-bar-animated');
        },

        onComplete: function(path) {
            // force progress to 100
            this.onProgress(100);

            this._progress.hide();
            this._dlButtonTarget.show();
            this._dlButtonTarget.attr("href", '/downloads/' + path);
        },

        onFailed: function() {

        },
    };

    return Tracker;
});