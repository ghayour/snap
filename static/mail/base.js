// messaging
$.pnotify.defaults.styling = "jqueryui";
$.pnotify.defaults.history = false;
var pnotify_stack = {"dir1": "down", "dir2": "right"};

function notify(text, opts){
    opts = opts || {};
    var TRANS = {
        notice: 'پیام',
        info: 'اطلاعات',
        success: 'موفقیت',
        error: 'خطا'
    };
    var type = opts.type || 'notice';
    var title = opts.title || null;
    if (title === null) {
        title = TRANS[type];
    }
    $.pnotify({
        title: title,
        text: text,
        type: type,
        addclass: "stack-topleft",
        stack: pnotify_stack
    });
}




 (function($) {
    $.fn.confirmModal = function(opts)
    {
        var body = $('body');
        var defaultOptions    = {
            confirmTitle     : 'Please confirm',
            confirmMessage   : 'Are you sure you want to perform this action ?',
            confirmOk        : 'Yes',
            confirmCancel    : 'Cancel',
            confirmDirection : 'rtl',
            confirmStyle     : 'primary',
            confirmCallback  : defaultCallback
        };
        var options = $.extend(defaultOptions, opts);
        var time    = Date.now();

        var headModalTemplate =
            '<div class="modal fade" id="#modalId#" tabindex="-1" role="dialog" aria-labelledby="#AriaLabel#" aria-hidden="true">' +
             '<div class="modal-dialog">'+
                '<div class="modal-content">'+
                '<div class="modal-header">' +
                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>' +
                    '<h3>#Heading#</h3>' +
                '</div>' +
                '<div class="modal-body">' +
                    '<p>#Body#</p>' +
                '</div>' +
                '<div class="modal-footer">' +
                '#buttonTemplate#' +
                '</div>' +
                '</div>'+
                '</div>'+
            '</div>'
            ;

        return this.each(function(index)
        {
            var confirmLink = $(this);
            var targetData  = confirmLink.data();

            var currentOptions = $.extend(options, targetData);

            var modalId = "confirmModal" + parseInt(time + index);
            var modalTemplate = headModalTemplate;
            var buttonTemplate =
                '<button class="btn" data-dismiss="modal" aria-hidden="true">#Cancel#</button>' +
                '<button class="btn btn-#Style#" data-dismiss="ok" data-href="' + confirmLink.attr('href') + '">#Ok#</button>'
            ;

            if(options.confirmDirection == 'ltr')
            {
                buttonTemplate =
                    '<button class="btn btn-#Style#" data-dismiss="ok" data-href="' + confirmLink.attr('href') + '">#Ok#</button>' +
                    '<button class="btn" data-dismiss="modal" aria-hidden="true">#Cancel#</button>'
                ;
            }

            modalTemplate = modalTemplate.
                replace('#buttonTemplate#', buttonTemplate).
                replace('#modalId#', modalId).
                replace('#AriaLabel#', options.confirmTitle).
                replace('#Heading#', options.confirmTitle).
                replace('#Body#', options.confirmMessage).
                replace('#Ok#', options.confirmOk).
                replace('#Cancel#', options.confirmCancel).
                replace('#Style#', options.confirmStyle)
            ;

            body.append(modalTemplate);

            var confirmModal = $('#' + modalId);

            confirmLink.on('click', function(modalEvent)
            {
                modalEvent.preventDefault();
                confirmModal.modal('show');

                $('button[data-dismiss="ok"]', confirmModal).on('click', function(event) {
                    confirmModal.modal('hide');
                    options.confirmCallback(confirmLink);
                });
            });
        });

        function defaultCallback(target)
        {
            window.location = $(target).attr('href');
        }
    };
})(jQuery);
