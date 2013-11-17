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
        this.div.addClass('toolbar-component bordered');
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
        var bootstrapIcon = arsh.js.get(opts, 'bootstrapIcon');
        // var icon = arsh.js.get(opts, 'icon'); todo
        var title = arsh.js.get(opts, 'title', '');
        var action = arsh.js.get(opts, 'action');
        var popover = arsh.js.get(opts, 'popover');
        var showCond = arsh.js.get(opts, 'show', 'true');

        var el = $(_.template('<a class="toolbar-item" href="#"><span class="glyphicon glyphicon-{{glyph}}"></span></a>')({glyph: bootstrapIcon}));
        var type = 'button';
        if (action) el.click(action);
        if (title) el.attr('title', title);

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
