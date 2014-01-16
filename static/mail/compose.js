// mailSystem.setView('compose');  // not yet!
var editor;
$(function () {
    setup_mail_form();

    editor = arsh.connectors.pen.create('#id_content', {debug: true});
});


// manage bcc cc labels viewing
  $(document).ready(function()
        {
             $("#id_cc").closest('tr').hide();
             $("#id_bcc").closest('tr').hide();
             $("#id_labels").closest('tr').hide();



        var link_row='<tr><td class="formlinks">'+
                '<a id="cc-link" href=# >افزودن رونوشت</a>'+
                '<span class="separator">|</span>'+'<a id="bcc-link" href=# >افزودن رونوشت مخفی</a>'+
                                '<span class="separator">|</span>'+'<a id="labels-link" href=# > افزودن برچسب های اولیه  </a>'+

                '</td></tr>';
        $("tr").filter(function(){
           if($(this).find("#div_id_labels").length>=1 && ($(this).parent().find(".formlinks").length==0))
           return true;
            return false;
        }).after(link_row);


         $("#cc-link").click(function(){
             $("#id_cc").closest('tr').toggle();

        });
         $("#bcc-link").click(function(){
             $("#id_bcc").closest('tr').toggle();

        });
            $("#labels-link").click(function(){
             $("#id_labels").closest('tr').toggle();

        });


        });