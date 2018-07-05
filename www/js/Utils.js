define(function (require) {
    "use strict";

    $ = require('jquery');

    // ------------------------------------------------------------------------
    // CONSTRUCTOR
    // ------------------------------------------------------------------------
    function Utils() {
        if (!(this instanceof Utils)) {
            throw new TypeError("Utils constructor cannot be called as a function.");
        }
    }

    // ------------------------------------------------------------------------
    // STATIC METHODS
    // ------------------------------------------------------------------------
    Utils.parseSafely = function(jsonStr) {
        var result = {};
        try {
            result = JSON.parse(jsonStr);
        } catch (e) {
            console.log('Parse json string failed: ' + jsonStr);
        }
        return result;
    }

    Utils.setVisibility = function(elt, visible) {
        $(elt).attr('style', 'visibility: ' + (visible ? 'visible' : 'hidden'));
    }

    Utils.isVisible = function(el) {
        return $(el).is(':visible');
    }

    /**
     * Input: JS Date object
     * Output: "2018-05-08 03:39:05.566244" in UTC
     */
    Utils.makeDateStr = function(dateObj) {
        var year = dateObj.getUTCFullYear();
        var monthZeroBased = dateObj.getUTCMonth();
        var month = monthZeroBased + 1;
        var day = dateObj.getUTCDate();

        var hour = dateObj.getUTCHours();
        var minute = dateObj.getUTCMinutes();
        var second = dateObj.getUTCSeconds();
        var milliSecond = dateObj.getUTCMilliseconds();
        var microSecond = milliSecond * 1000;

        var result = Utils.formatString('{0}-{1}-{2} {3}:{4}:{5}.{6}',
                year, Utils.zeroPad(month, 2), Utils.zeroPad(day, 2),
                Utils.zeroPad(hour, 2), Utils.zeroPad(minute, 2), Utils.zeroPad(second, 2),
                Utils.zeroPad(microSecond, 6));
        return result;
    }

    /**
     * Input: "2018-05-08 03:39:05.566244" in UTC
     * Output: JS Date object
     *
     * refer to:
     * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/UTC
     */
    Utils.parseDateStr = function(dateStr) {
        var datePart = dateStr.split(' ')[0];
        var timePart = dateStr.split(' ')[1];

        var year = datePart.split('-')[0];
        var month = datePart.split('-')[1];
        month = (Number(month) - 1).toString();
        var day = datePart.split('-')[2];

        var hour = timePart.split(':')[0];
        var minute = timePart.split(':')[1];
        var secondPart = timePart.split(':')[2];

        var second = secondPart.split('.')[0];
        var microSecond = secondPart.split('.')[1];
        var milliSecond = (Number(microSecond) / 1000.0).toString();

        var timestamp = Date.UTC(year, month, day, hour, minute, second, milliSecond);
        return new Date(timestamp);
    }

    /**
     * Check if two Date objects have the same year, month, and date in local time
     */
    Utils.isMessageTheSameDate = function(m1, m2) {
        if (m1.created == null || m2.created == null) {
            return false;
        }

        return m1.created.getDate() == m2.created.getDate() &&
                m1.created.getMonth() == m2.created.getMonth() &&
                m1.created.getFullYear() == m2.created.getFullYear();
    }

    /**
     * Replace new line characters in string with <br /> tags
     *
     * refer to:
     * https://stackoverflow.com/questions/5076466/javascript-replace-n-with-br
     */
    Utils.convertNewLinesToBreaks = function(str) {
        return str.replace(new RegExp('\r?\n', 'g'), '<br />');
    }

    /**
     * Zero-pad number or strings
     *
     * refer to:
     * https://stackoverflow.com/a/2998822/1825443
     */
    Utils.zeroPad = function(num, size){
        return ('000000000' + num).substr(-size);
    }

    /**
     * String formatted output
     *
     * refer to:
     * https://stackoverflow.com/a/4673436/1825443
     */
    Utils.formatString = function(format) {
        var args = Array.prototype.slice.call(arguments, 1);
        return format.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] != 'undefined' ? args[number] : match;
        });
    }

    /**
     * refer to:
     * https://stackoverflow.com/a/3261380/1825443
     */
    Utils.isEmptyString = function(str) {
        return (!str || 0 === str.length);
    }

    /**
     * check if element is partially visible in container's client area
     *
     * refer to:
     * https://stackoverflow.com/a/488073/1825443
     * https://stackoverflow.com/a/21880020/1825443
     */
    Utils.isElementVisible = function(element, container, pageBottomIncrement) {
        pageBottomIncrement = pageBottomIncrement !== undefined ? pageBottomIncrement : 0;
        var pageTop = $(container).scrollTop();
        var pageBottom = pageTop + $(container).height() + pageBottomIncrement;
        var elementTop = $(element)[0].offsetTop;
        var elementBottom = elementTop + $(element).height();
        return ((elementTop <= pageBottom) && (elementBottom >= pageTop));
    }

    return Utils;
});