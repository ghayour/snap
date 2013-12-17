$(document).ready(function(){
   $.fn.editable.defaults.mode = 'inline';

   $('td .glyphicon-trash').click(function(){
       var cur_tr = $(this).parents('tr');
       var doIt = confirm("آیا می خواهید این برچسب را حذف کنید ؟ ");
       if (doIt){
       $.ajax({
           url : '/manage-label/',
           type : 'POST',
           data : {
               pk : $(this).parent().parent().attr('id'),
               name : 'delete'
           },
           success:function(response){
                ajaxLoader.show();
                window.location.reload();
                cur_tr.remove();
           }
       });

       }
        });


    $('td .glyphicon-edit').click(function(){
       $(this).parents('tr').find('.name').editable('toggleDisabled');
        });
});