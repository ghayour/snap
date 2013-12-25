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
            'no','yes',
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
            else{}
            })//bootbox
    }); // .confirmModal
});//document
