/**
 * Created by barzekar on 11/27/13.
 */

$(document).ready(function(){

    $('.confirmModal').click(function(){
        var pk = $(this).data("pk");
        bootbox.confirm('آیا شما مطمئنید که می خواهید این حساب را حذف کنید  ؟',
        function(result){
            if (result){
            $.ajax({
            url : '/view/addressbook',
            type : 'POST',
            data : { pk : pk },
            success:function(){
                ajaxLoader.show();
                window.location.reload();
            }

            })
        }
            else{};

        });
    });



 });

