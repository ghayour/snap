arsh.ui.Loader = arsh.ui.BaseUIComponent.extend({
    init: function(opts) {
        if (typeof opts === 'undefined' || !opts) opts = {};
        this.div = $(arsh.js.get(opts, 'div', '<div></div>'));
        this.parent = arsh.js.get(opts, 'parent', 'body');
        this._setupDiv(arsh.js.get(opts, 'title', 'در حال بارگزاری...'));
    },

    _setupDiv: function(title) {
        this.div.addClass('arsh-loader');
        this.div.hide().html('<span>'+title+'</span>').appendTo(this.parent);
    },

    show: function() {
        this.div.fadeIn();
    },

    hide: function() {
        this.div.fadeOut();
    },

    getComponentId: function() {
        if (typeof arsh.ui.Loader.cid === 'undefined') {
            arsh.ui.Loader.cid = 1;
        }
        arsh.ui.Loader.cid++;
        return arsh.ui.Loader.cid - 1;
    }
});
