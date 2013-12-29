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

//set farsi language for confirm dialog
$(document).ready(function(){
      bootbox.setDefaults({
        locale:"fa"
      });
});

function startLoading(){
        $('#progress-bar').html(
            "<img src='{{STATIC_URL}}mail/images/loading/startloading.gif' >"
        )
    }
