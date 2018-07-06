define(function (require) {
    'use strict';

    // ------------------------------------------------------------------------
    // CONSTRUCTOR
    // ------------------------------------------------------------------------
    function APIManager(frequentWrap) {
        if (!(this instanceof APIManager)) {
            throw new TypeError('APIManager constructor cannot be called as a function.');
        }
    }

    // ------------------------------------------------------------------------
    // STATIC METHODS
    // ------------------------------------------------------------------------
    APIManager.newDownload = function(videoUrl, context) {
        var url = '/videos';
        var data = {'url': videoUrl};

        return $.ajax({
            url: url,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            context: context != null ? context : null,
        });
    };

    APIManager.listDownload = function(reqId, context) {
        var url = '/videos';
        if (reqId != null) {
            url += '/' + reqId;
        }

        return $.ajax({
            url: url,
            type: 'GET',
            contentType: 'application/json',
            context: context != null ? context : null,
        });
    };

    // ------------------------------------------------------------------------
    // METHODS
    // ------------------------------------------------------------------------
    APIManager.prototype = {
        constructor: APIManager,
    };

    return APIManager;
});