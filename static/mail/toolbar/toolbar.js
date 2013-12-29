if (typeof arsh == 'undefined') arsh = {};
if (typeof arsh.ui == 'undefined') arsh.ui = {};

arsh.ui.BaseComponent = Class.extend({

});

arsh.ui.Toolbar = arsh.ui.BaseComponent.extend({
    init: function(opts) {
        this.div = $(arsh.js.get(opts, 'div'));
        this._buttons = [];
        this._setupDiv();

        this._popoverDismissSet = false;
    },

    _setupDiv: function() {
        this.div.addClass('toolbar');
    },

    redraw: function () {
        var c;
        for (var i =0; i<this._buttons.length; i++) {
            c = this._buttons[i];
            if (! eval(c.showCond) ) {
                c.element.hide();
            }
        }
    },

    addButton: function(opts) {
        var self = this;
        var icon = arsh.js.get(opts, 'icon') || 'none';
        var align = arsh.js.get(opts, 'align', 'right');
        var css = arsh.js.get(opts, 'css');
        var title = arsh.js.get(opts, 'title', '');
        var action = arsh.js.get(opts, 'action');
        var popover = arsh.js.get(opts, 'popover');
        var showCond = arsh.js.get(opts, 'show', 'true');

        var el = $(_.template('<div class="toolbar-item"><span class="item-icon icon-{{glyph}}"></span><span class="item-title">{{title}}</span></div>')({glyph: icon, title: title}));
        var type = 'button';
        if (action) el.click(action);
        if (align == 'left') el.addClass('left-aligned');
        if (css) el.css(css);
        //if (title) el.attr('title', title);

        if (popover) {
            if (!this._popoverDismissSet) {
                $('body').on('click', function (e) {
                    for (var i=0; i<self._buttons.length; i++) {
                        var but = self._buttons[i];
                        if (but.type === 'popover' && !but.element.is(e.target) && but.element.has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                            but.element.popover('hide');
                        }
                    }
                });
                this._popoverDismissSet = true;
            }
            type = 'popover';
            $(el).popover({
                html: true,
                placement: 'bottom',
                trigger: 'click',
                title: arsh.js.get(popover, 'title'),
                content: arsh.js.get(popover, 'content')
            });
        }

        if (! eval(showCond) ) el.hide();
        el.appendTo(this.div);
        this._buttons.push({element: el, showCond: showCond, type: type});
    }
});
