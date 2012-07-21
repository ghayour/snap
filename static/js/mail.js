
function reply(message, success, reload){
    if (typeof success == 'undefined') success = function(){};
    if (typeof reload == 'undefined') reload = true;
    $.post('.', {content: message}, function(){
        success();
        if (reload)
            window.location = window.location;
    });
}
