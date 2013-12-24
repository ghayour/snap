// mailSystem.setView('compose');  // not yet!
var editor;
$(function () {
    setup_mail_form();

    editor = arsh.connectors.pen.create('#id_content', {debug: true});
});
