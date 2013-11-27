/* Globally Used Objects */
var mailToolbar;
var ajaxLoader;
var mailSystem = new arsh.mail.Client();


/* Toolbar Creation */
$(function(){
    mailToolbar = new arsh.ui.Toolbar({'div': '#action-bar'});
    mailToolbar.addButton({
        bootstrapIcon: 'chevron-up',
        title: 'بازگشت',
        show: 'mailSystem.state.viewing != "threads"',
        action: function() {
            window.location = arsh.dj.resolver.url('mail/home');
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'refresh',
        title: 'بازآوری',
        show: 'mailSystem.state.viewing == "threads"',
        action: function() {
            window.location.reload();
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'inbox',
        title: 'بایگانی',
        action: function() {
            mailSystem.setArchiveMode();
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'flag',
        title: 'هرزنامه',
        action: function() {
            mailSystem.markAsSpam();
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'trash',
        title: 'حذف',
        action: function() {
            mailSystem.moveToTrash();
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'eye-open',
        title: 'علامت گذاری به عنوان خوانده شده',
        show: 'mailSystem.state.viewing == "threads"',
        action: function() {
            var item_list = [];
            $('input:checkbox[class="thread-checkbox"]:checked').each(function () {
                item_list.push($(this).attr('value'));
            });
            $.post(arsh.dj.resolver.url('mail/mark_thread'),
                {item_id: item_list, action: 'read'},
                function (data) {
                    var data1 = JSON.parse(data);
                    if (data1["response_text"] == 'success') {
                        alert('عملیات با موفقیت انجام شد.');
                        if (mailSystem.state.onlyShowNewMail){
                            $('input:checkbox[class="thread-checkbox"]:checked').each(function () {
                                $(this).closest("tr").remove();
                            });
                            window.location = self.location;
                            window.location.reload(true);
                        }
                        //تغییر با توجه به اینکه در حالت آرشیو هست یا خیر
                        // تغییر نحوه نمایش بر اساس تفاوت خوانده شده ها با نخوانده ها
                    }
                    else {
                        alert(data1["response_text"]);
                    }
                });
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'folder-open',
        title: 'انتقال',
        popover: {
            title: 'انتقال به',
            content: '<input id="move_thread" data-type="thread" type="text" class="label-input">'
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'tag',
        title: 'برچسب گذاری',
        popover: {
            title: 'برچسب گذاری',
            content: '<input id="apply-label" item_id=-1 type="text" class="label-input">'
        }
   });
    mailToolbar.addButton({
        bootstrapIcon: 'fullscreen',
        title: 'باز کردن همه',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            //change_button_name($(this));
            showAllMails();
            expand_close_mails($(this));
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'share-alt',
        title: 'پاسخ',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            update_message_type("reply");
            forward_reply_handler("reply");
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'arrow-left',
        title: 'باز ارسال',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            update_message_type("forward");
            forward_reply_handler("forward");
        }
    });
    mailToolbar.addButton({
        bootstrapIcon: 'off',
        title: 'خروج',
        action : function(){
            window.location = arsh.dj.resolver.url('accounts/logout');
        }
    });
});

/* Loader */
$(function() {
    ajaxLoader = new arsh.ui.Loader({title: 'میل عرش'});
});

function update_message_type(message_type){
    $("#message-type").val(message_type);
    $("legend").text(_t(message_type));
}

function forward_reply_handler(action_type){
    var content_place;
    var checked_item;
    var thread_id = $('#thread-id').val();
    $("#re-or-fw").removeClass("hide-element");
    checked_item = $('input:checkbox[class="mail-checkbox"]:checked');
    if(checked_item.length == 1){
        cur_mail = checked_item.closest(".mail");
        $("#selected-mail-id").val(cur_mail.data("db"));
        content_place = cur_mail.children(".mail-content");
    }
    else{
        if(checked_item.length>1){
            alert('فقط یک مورد انتخاب کنید.');
            return;
        }
        else{
            var cur_mail = $("div.mail").last();
        }
    }

    if (action_type=="forward"){
        show_hide_info_fields(true, false);
        $("#id_title").val(get_fw_subject(cur_mail)).css('width', '300');
        tinyMCE.get('id_content').setContent(get_fw_content(cur_mail));
    }
    else{
        show_hide_info_fields(false, true);
        $("#id_title").val(get_re_subject(cur_mail)).css('width', '300');
        tinyMCE.get('id_content').setContent(get_re_content(cur_mail));
    }
    var FW_RE = $("#bottom-div");
    content_place.append(FW_RE);
}
