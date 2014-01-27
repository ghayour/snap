/* Globally Used Objects */
var mailToolbar;
var ajaxLoader;
var mailSystem = new arsh.mail.Client();


/* General JS code */
$(function() {
    $('#refresh-button').click(function() {
        window.location.reload();
    });

    var $sidebar = $('#sidebar');
    function grSidebarFix() {
        $sidebar.height($( document ).height() - $sidebar.position().top - 10);
    }
    grSidebarFix();
    setTimeout(grSidebarFix, 50);
    setTimeout(grSidebarFix, 500);
    setInterval(grSidebarFix, 4000);
    $(window).resize(grSidebarFix);

    $('.box-menu-expand').click(function() {
        var $menu = $(this).closest('.box-menu');
        $menu.find('.box-menu-body').slideToggle(function() { $menu.toggleClass('active'); });
    });
});


/* Toolbar Creation */
$(function(){
    $('.mailAction').hide();
    var checklist = $('input[type=checkbox]');
    checklist.change(function(){
       if (checklist.filter(':checked').length != 0 ){
           $('.mailAction').show();
           $('.mailAction.mark-read').hide();
           $('.mailAction.mark-unread').hide();
           var row = $('input[type=checkbox]:checked').parent().parent();
           if(row.hasClass('read'))
                {$('.mailAction.mark-unread').show();}
            if(row.hasClass('unread'))
                {$('.mailAction.mark-read').show();}
            }
       else{$('.mailAction').hide();}
    });

    mailToolbar = new arsh.ui.Toolbar({'div': '#action-bar'});

    mailToolbar.addButton({
        icon: '',
        title: 'بازگشت',
        show: 'mailSystem.state.viewing != "threads"',
        action: function() {
            var url;
            var curLabel = $("#current_label").data('slug');
            if (curLabel) {
                url = arsh.dj.resolver.url('mail/see_label', {label_slug:curLabel});
            } else {
                url = arsh.dj.resolver.url('mail/home');
            }
            window.location = url;
        }
    });

    mailToolbar.addButton({
        icon: 'archive',
        title: 'بایگانی',
        class : 'mailAction',
        action: function() {
            mailSystem.setArchiveMode();
        }
    });

    mailToolbar.addButton({
        icon: 'spam',
        title: 'هرزنامه',
        class : 'mailAction',
        action: function() {
            mailSystem.markAsSpam();
        }
    });

    mailToolbar.addButton({
        icon: 'trash',
        title: 'حذف',
        class : 'mailAction',
        action: function() {
//            var doIt=confirm('آیا مطمئنید که می‌خواهید این ایمیل را حذف کنید؟');
            bootbox.confirm('آیا مطمئنید که می‌خواهید این ایمیل را حذف کنید؟',function(result){
               if(result){
                mailSystem.moveToTrash();
                }
            })

        }
    });

        mailToolbar.addButton({
        icon: '',
        title: 'خوانده شده',
        class : 'mailAction mark-read',
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
                        }
                        ajaxLoader.show();
                        window.location.reload();
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
        icon: '',
        title: 'خوانده نشده',
        class : 'mailAction mark-unread',
        show: 'mailSystem.state.viewing == "threads"',
        action: function() {
            var item_list = [];
            $('input:checkbox[class="thread-checkbox"]:checked').each(function () {
                item_list.push($(this).attr('value'));
            });
            $.post(arsh.dj.resolver.url('mail/mark_thread'),
                {item_id: item_list, action: 'unread'},
                function (data) {
                    var data1 = JSON.parse(data);
                    if (data1["response_text"] == 'success') {
                        alert('عملیات با موفقیت انجام شد.');
                        if (mailSystem.state.onlyShowNewMail){
                            $('input:checkbox[class="thread-checkbox"]:checked').each(function () {
                                $(this).closest("tr").remove();
                            });
                        }
                        ajaxLoader.show();
                        window.location.reload();
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
        icon: 'folder',
        title: 'پوشه بندی',
        class : 'mailAction',
        popover: {
            title: 'انتقال به پوشه',
            content: '<input id="move_thread" data-type="thread" type="text" class="label-input">'
        }
    });

    mailToolbar.addButton({
        icon: 'tag',
        title: 'برچسب گذاری',
        class : 'mailAction',
        popover: {
            title: 'برچسب گذاری',
            content: '<input id="apply-label" item_id=-1 type="text" class="label-input">'
        }
   });

    mailToolbar.addButton({
        icon: '',
        title: 'باز کردن همه',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            //change_button_name($(this));
            showAllMails();
            expand_close_mails($(this));
        }
    });

    mailToolbar.addButton({
        icon: '',
        title: 'نمایش همه ی میل ها ',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            //change_button_name($(this));
//            $('.main-label').removeClass('main-label');
            $(".other-mails").removeClass("other-mails");
            $('.mail-header').parent().removeClass('hide-element');


            expand_close_mails($(this));
        }
    });

    mailToolbar.addButton({
        icon: '',
        title: 'پاسخ',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            set_reply_form ();
            update_message_type("reply");
            forward_reply_handler("reply");
        }
    });
    mailToolbar.addButton({
        icon: '',
        title: 'باز ارسال',
        show: 'mailSystem.state.viewing == "mails"',
        action: function() {
            update_message_type("forward");
            forward_reply_handler("forward");
        }
    });
    mailToolbar.addButton({
        icon: '',
        title: 'خروج',
        align: 'left',
        action : function(){
            window.location = arsh.dj.resolver.url('accounts/logout');
        }
    });
    mailToolbar.addButton({
        icon: '',
        title: 'تنظیمات',
        align: 'left',
        action : function(){
            window.location = arsh.dj.resolver.url('mail/manage_label');
        }
    });
    mailToolbar.addButton({
        icon: '',
        title: 'مخاطبین',
        align: 'left',
        action : function(){
            window.location = arsh.dj.resolver.url('view/address_book');
        }
    });
    mailToolbar.addButton({
        icon: 'next',
        title: '',
        align: 'left',
        css: {width: '30px'},
        show: 'mailSystem.state.viewing == "threads"'
    });
    mailToolbar.addButton({
        icon: 'prev',
        title: '',
        align: 'left',
        css: {marginLeft: '-9px', width: '30px'},
        show: 'mailSystem.state.viewing == "threads"'
    });
    mailToolbar.addButton({
        icon: '',
        title: 'نمایش تمام نامه‌ها',
        align: 'left',
        show: 'mailSystem.state.viewing == "threads"'
    });
});

/* Loader */
$(function() {
    ajaxLoader = new arsh.ui.Loader({title: 'میل عرش'});
});

function update_message_type(message_type){
    $("#message-type").val(message_type);
    var txt="پاسخ" ;
    if(message_type=='forward')
        var txt="ارجاع" ;
    $("legend").text(txt);
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
        var link_row='<tr><td class="formlinks">'+
                '<a id="replyto-link">افزودن پاسخ-به</a><span class="separator">|</span>'+
                '<a id="cc-link" >افزودن رونوشت</a>'+
                '<span class="separator">|</span>'+'<a id="bcc-link">افزودن رونوشت مخفی</a>'+
                '</td></tr>';
        $("tr").filter(function(){
           if($(this).find("#div_id_bcc").length>=1 && ($(this).parent().find(".formlinks").length==0))
           return true;
            return false;
        }).after(link_row);

        $("#replyto-link").click(function(){
            $("#id_receivers").closest('tr').toggle();

        });
         $("#cc-link").click(function(){
             $("#id_cc").closest('tr').toggle();

        });
         $("#bcc-link").click(function(){
             $("#id_bcc").closest('tr').toggle();

        });
        show_hide_info_fields(false, true);
        $("#id_title").val(get_re_subject(cur_mail)).css('width', '300');
        tinyMCE.get('id_content').setContent(get_re_content(cur_mail));
//        var url = $(location).attr('pathname');
//        var mail = cur_mail.data("db");
//         $.ajax({
//            url : url,
//            type : 'POST',
//            data : {
//                mail  : mail ,
//                action : action_type
//            }
//        });
    }
    //TODO: move fw-re form according to selected mail
//    var FW_RE = $("#bottom-div");
//    content_place.append(FW_RE);
}

function set_reply_form(){
    var selected_mail = $('.mail-checkbox:checked').val();
    var url = $(location).attr('pathname');

      $.ajax({
            url : url,
            type : 'GET',
            data : {
                mail  : selected_mail ,
                action : 'reply'
            },
          success:function(data){
              if (data.to){
                var re_to = $('#id_receivers');
                set_initial_value(data.to , re_to );
//                $("#id_receivers").closest('tr').show();

              }
              if (data.cc){
                 var re_cc = $('#id_cc');
                 set_initial_value(data.cc , re_cc );
//                 $("#id_cc").closest('tr').show()
              }


          }

        });

}

function set_initial_value( data , elem ){
                var list=  []
                  data_length = data.length
                  for(var i =0 ; i<data_length ; i++){
                      var x = {'id': i , 'text':data[i]+'@arshmail.ir'};
                      list[i]= x
                  }
                 elem.select2(
                    "data",list
                 );
                elem.closest('tr').show();

}