// mailSystem.setView('compose');  // not yet!
var editor;
$(function () {
    setup_mail_form();
    editor = arsh.connectors.pen.create('#id_content', {debug: true});
});

/********************************
 * Manage bcc cc labels viewing *
 ********************************/
$(function () {
    $("#id_cc").closest('tr').hide();
    $("#id_bcc").closest('tr').hide();
    $("#id_labels").closest('tr').hide();

    var link_row = '<tr><td class="formlinks">' +
        '<a id="cc-link" href=# >افزودن رونوشت</a>' +
        '<span class="separator">|</span>' + '<a id="bcc-link" href=# >افزودن رونوشت مخفی</a>' +
        '<span class="separator">|</span>' + '<a id="labels-link" href=# > افزودن برچسب های اولیه  </a>' +
        '</td></tr>';
    $("tr").filter(function () {
        return ($(this).find("#div_id_labels").length >= 1) && ($(this).parent().find(".formlinks").length == 0);

    }).after(link_row);

    $("#cc-link").click(function () {
        $("#id_cc").closest('tr').toggle();

    });
    $("#bcc-link").click(function () {
        $("#id_bcc").closest('tr').toggle();

    });
    $("#labels-link").click(function () {
        $("#id_labels").closest('tr').toggle();

    });
});


/***********************
 * Attachment Handling *
 ***********************/
$(function () {
    Dropzone.options.uploader = {
        addRemoveLinks: true,
        dictRemoveFile: 'حذف',
        dictCancelUpload: 'لغو آپلود',
        dictCancelUploadConfirmation: 'آیا آپلود فایل لغو شود؟'
    };
});
