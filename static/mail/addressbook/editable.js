/**
 * Created by barzekar on 11/27/13.
 */
$(function(){

 $.fn.editable.defaults.mode = 'inline';
// $('.name').editable();
 $('.editable-submit').on('click' ,function(){
     $('.alert').show(1000);
     $('.alert').hide(1000);
 })
});
$(document).ready(function(){

    $('button[type=submit]').click(function(){
    var doIt=confirm('آیا مطمئنید که میخواهید این حساب را حذف کنید ؟ ');
    if(doIt){

         $.ajax({
            url : '/view/addressbook',
            type : 'POST',
            data : { pk : $(this).val()},
            success:function(response){
                ajaxLoader.show();
                window.location.reload();
            }
        })

    }

});

    });
