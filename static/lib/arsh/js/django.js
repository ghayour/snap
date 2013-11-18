_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
};

arsh.dj = {
    resolver: {
        'site_url': '/',
        _apps: {},

        initialize: function(site_url){
            this.site_url = site_url;
        },

        register_app: function(app_name, url_prefix, urls){
            this._apps[app_name] = {name: app_name, prefix: url_prefix, urls: urls};
        },

        url: function(name, kwargs){
            if (typeof kwargs == 'undefined') kwargs = {};
            for (var app in this._apps) {
                if (this._apps.hasOwnProperty(app)){
                    app = this._apps[app];
                    if (app.urls.hasOwnProperty(name))
                        return this.site_url + app.prefix + '/' + _(app.urls[name]).template()(kwargs);
                }
            }
            console.error('Can not make url for url: `' + name + '` with arguments:', kwargs);
            return '#';
        },

        direct: function(pattern, kwargs) {
            return this.site_url + _(pattern).template()(kwargs);
        }
    }
};
