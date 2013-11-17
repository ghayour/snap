fw_template = _.template( '<p></p>' +
    '<p>----------' + _t("Forwarded message") + '----------</p>' +
    '<p>' + _t("Subject") + ': {{ subject }} </p>' +
    '<p>' + _t("Date") + ': {{ date }} </p>' +
    '<p>' + _t("To") + ': {{ to }} </p>' +
    '<p>--------------------</p>' +
    '<br><br>' +
    '<div> {{ content }} </div>'
);

function reply(message, success, reload) {
    if (typeof success == 'undefined') success = function () {
    };
    if (typeof reload == 'undefined') reload = true;
    $.post('.', {content: message}, function () {
        success();
        if (reload)
            window.location = window.location;
    });
}

function respond(id, mail_id) {
    var m_request_id = parseInt(id.replace('r_r_', ''));
    var dict = {};
    var data = $('#m_request_' + m_request_id + ' input.checkbox');
    for (var i = 0; i < data.length; i++) {
        var index = data[i]['name'].replace('request_', '');
        dict[index] = data[i]['checked'];
    }
    dict['mail_id'] = mail_id;
    url = arsh.dj.resolver.url('mail/respond', {request_id: m_request_id});
    $.post(url, dict, function (data) {
        if (data['result']) {
            $("#" + id).parent().removeClass('active_mail').addClass('inactive_mail');
            var parent_id = $("#" + id).parent().attr('id');
            $("#" + parent_id + ' input').attr('disabled', 'disabled');
            $("#" + parent_id + ' button').attr('disabled', 'disabled');

            if (data['next'] > 0) {
                var next = 'm_request_' + data['next'];
                $("#" + next).removeClass('inactive_mail').addClass('active_mail');
                $("#" + next).parent().show('blind', {}, 300);
                $("#" + next + ' input').removeAttr('disabled');
                $("#" + next + ' button').removeAttr('disabled');
            }
        }
    });
}

function show_hide_content(elem, force_hide) {
    force_hide = typeof force_hide !== 'undefined' ? force_hide : false;
    var content = elem.parent().find(".mail-content");
    show_hide(content, force_hide, false);
    show_hide(elem.find(".mail-summery"), false, force_hide);
}

function manage_read_mails() {
    var read_mails = $("div.mail-content.read");
    read_mails.addClass("hide-element");
    read_mails = read_mails.slice(1);
    read_mails.each(function () {
        var mail = $(this).parent();
//        if (mail.hasClass("request-mail"))
            mail.addClass("other-mails");
    })
}

function manage_mails_display() {
//    var last_mail = $("div.request-mail").last();
    var last_mail = $("div.mail").last();
    last_mail.removeClass("other-mails");
    last_mail.find(".mail-content").removeClass("hide-element"); //Always show last mail opened
    $("div.mail-content.hide-element").parent().find(".mail-summery").removeClass("hide-element");
    $("div.mail-header").click(function () {
        show_hide_content($(this), false);
    });
}

function showAllMails() {
    $(".other-mails").removeClass("other-mails");
    $("#other-mails").hide();
}

function respond_register(id, result) {
    url = arsh.dj.resolver.url('mail/respond_register', {member_id: id, result: result});
    $.post(url, function (data) {
        alert(data['result']);
    })
}

function change_button_name(elem) {
    var next_name = elem.text();
    elem.text(elem.data("next"));
    elem.data("next", next_name);
}

function expand_close_mails(butt) {
    var mails = [];
    var force_hide = false;
    var is_expand = true; //parseInt(butt.data("expand"), 10);
    if (is_expand) {
        mails = $("div.mail-content.hide-element");
    }
    else {
        mails = $("div.mail-content");
        force_hide = true;
    }
    //butt.data("expand", (1 - is_expand).toString());
    mails.each(function () {
        var mail_header = $(this).parent().find(".mail-header");
        show_hide_content(mail_header, force_hide);
    });
}

function show_hide_info_fields(show, hide) {
    $(".info").each(function () {
        show_hide($(this).closest('tr'),force_hide=hide, force_show=show);
        $(this).val('');
    });
}

function get_fw_content(mail) {
    var dict = {};
    dict['subject'] = mail.find('.mail-subject').text();
    dict['to'] = mail.find('.receiver').map(function(){
        return $(this).text();
    }).toArray().join(', ');
    dict['date'] = mail.find('.mail-date').text();
    dict['content'] = mail.find('.mail-content .content-p').html();
    return fw_template(dict);
}

function get_fw_subject(mail){
    return 'FW: ' + mail.find('.mail-subject').text();
}

function get_re_subject(mail){
    return 'RE: ' + mail.find('.mail-subject').text();
}

function get_re_content(last_mail){
    return '';
}

function update_message_type(){
    var message_type = $("input:checked[name=re-fw]").val();
  $("#message-type").val(message_type);
  $("legend").text(_t(message_type));
}

$(document).ready(function () {
    $("#top_menu ul").append('<img id="total-spinner" class="left-aligned hidden" src="' + arsh.dj.resolver.site_url + 'static/images/ajax-loader.gif">')
});

$(document).ajaxStart(function () {
    $("#total-spinner").show();
}).ajaxStop(function () {
        $("#total-spinner").hide();
    });

function newLabel() {
    var targetElement = document.getElementById('newLabelForm');
    targetElement.style.display = 'block';
}

function showAddLabelForm() {
    var targetElement = document.getElementById('addLabelForm');
    targetElement.style.display = 'block';
}

function cancelOperation() {
    var targetElement = document.getElementById('newLabelForm');
    targetElement.style.display = 'none';
}

function cancelAddLabel() {
    var targetElement = document.getElementById('addLabelForm');
    targetElement.style.display = 'none';
}