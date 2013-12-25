$(document).ready(function(){
   $.fn.editable.defaults.mode = 'inline';

//   $('td .glyphicon-trash').click(function(){
//       var cur_tr = $(this).parents('tr');
//       var doIt = confirm("آیا می خواهید این برچسب را حذف کنید ؟ ");
//       if (doIt){
//       $.ajax({
//           url : '/manage-label/',
//           type : 'POST',
//           data : {
//               pk : $(this).parent().parent().attr('id'),
//               name : 'delete'
//           },
//           success:function(){
////                ajaxLoader.show();
////                window.location.reload();
//                cur_tr.remove();
//                parent.document.getElementById("sidebar").reload();
//
//           }
//       });
//
//       }
//        });

    $('.confirmModal').confirmModal({
        confirmTitle     : 'هشدار',
        confirmMessage   : 'آیا مطمئنید که می خواهید این برچسب را حذف کنید ؟ ',
        confirmOk        : 'بله',
        confirmCancel    : 'خیر',
        confirmDirection : 'rtl',
        confirmStyle     : 'primary',
        confirmCallback  : function(){
            $.ajax({
                url : '/manage-label/',
           type : 'POST',
           data : {
               pk : this.pk,
               name : 'delete'
           },
           success:function(){
//                cur_tr.remove();
               $('tr #'+ this.pk).remove();
                ajaxLoader.show();
                window.location.reload();
           }
            })
        }
    });

    $('td .glyphicon-edit').click(function(){
       $(this).parents('tr').find('.name').editable('toggleDisabled');
        });
});
