//var rootEl = $(_.template(LoadingSpinner)())[0];

requirejs.config({
    baseUrl: 'js',
    paths: {
        jquery: 'libs/jquery/1/jquery.min',
        jquery_ui: 'libs/jquery/1/jquery-ui.min',
        underscore: 'libs/underscore/1.9.0/underscore.min',
        domReady: 'libs/require/domReady',
        text: 'libs/require/text',
        i18n: 'libs/require/i18n'
    }
});

require(['js/app.js', 'domReady!'], function(App, _dom){
    new App();
});
