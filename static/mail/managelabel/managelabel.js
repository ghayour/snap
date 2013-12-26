$(document).ready(function(){
   $.fn.editable.defaults.mode = 'inline';


    $('td .glyphicon-edit').click(function(){
       $(this).parents('tr').find('.name').editable('toggleDisabled');
        });
});

$(document).ready(function(){
    $('.confirmModal').click(function(){
        var cur_tr = $(this).parents('tr');
        var pk = $(this).parent().parent().attr('id');
        bootbox.confirm('آیا مطمئنید که می خواهید برچسب را حذف کنید؟',

            function(result){

            if (result){
                $.ajax({
                url  : '/manage-label/',
                type : 'POST',
                data : {
                    pk   : pk ,
                    name : 'delete'},
                success:function(){
                    cur_tr.remove();
                    ajaxLoader.show();
                    window.location.reload()
                }


            })//ajax

    }
            else{
            }
            })//bootbox
    }); // .confirmModal
});//document

bootbox.setDefaults({
  /**
   * @optional String
   * @default: en
   * which locale settings to use to translate the three
   * standard button labels: OK, CONFIRM, CANCEL
   */
  locale: "fa",

  /**
   * @optional Boolean
   * @default: true
   * whether the dialog should be shown immediately
   */
  show: true,

  /**
   * @optional Boolean
   * @default: true
   * whether the dialog should be have a backdrop or not
   */
  backdrop: true,

  /**
   * @optional Boolean
   * @default: true
   * show a close button
   */
  closeButton: true,

  /**
   * @optional Boolean
   * @default: true
   * animate the dialog in and out (not supported in < IE 10)
   */
  animate: true,

  /**
   * @optional String
   * @default: null
   * an additional class to apply to the dialog wrapper
   */
  className: "my-modal"

});