/**
 * Created by barzekar on 11/27/13.
 */

$(document).ready(function(){

    $('.confirmModal').confirmModal({
        confirmTitle     : 'هشدار',
        confirmMessage   : 'آیا مطمئنید که میخواهید این حساب را حذف کنید ؟ ',
        confirmOk        : 'بله',
        confirmCancel    : 'خیر',
        confirmDirection : 'rtl',
        confirmStyle     : 'primary',
        confirmCallback :  function(){
            $.ajax({
                 url : '/view/addressbook',
                type : 'POST',
                data : { pk : this.pk},
                success:function(){
                    ajaxLoader.show();
                    window.location.reload();
                }
                });

        }

});

});