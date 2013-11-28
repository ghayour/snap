/**
 * Created by barzekar on 11/27/13.
 */
$(function(){

 $.fn.editable.defaults.mode = 'inline';
//  $('.panel-collapse.in')
  $('#enable').click(function() {
       $('.myeditable').editable({
        type: "POST",
        url: '/edit/addressbook' //this url will not be used for creating new user, it is only for update,

        });

   });
$('#save-btn').click(function() {
   $('.myeditable').editable('submit', {
       url: '/edit/bookmark',
       ajaxOptions: {
           dataType: 'json' //assuming json response
       },
       success: function(data, config) {
           if(data && data.id) {  //record created, response like {"id": 2}
               //set pk
               $(this).editable('option', 'pk', data.id);
               //remove unsaved class
               $(this).removeClass('editable-unsaved');
               //show messages
               var msg = 'تغییرات با موفقیت اعمال شد';
               $('#msg').addClass('alert-success').removeClass('alert-error').html(msg).show();
               $('#save-btn').hide();
               $(this).off('save.newuser');
           } else if(data && data.errors){
               //server-side validation error, response like {"errors": {"username": "username already exist"} }
               config.error.call(this, data.errors);
           }
       },
       error: function(errors) {
           var msg = '';
           if(errors && errors.responseText) { //ajax error, errors = xhr object
               msg = errors.responseText;
           } else { //validation error (client-side or server-side)
               $.each(errors, function(k, v) { msg += k+": "+v+"<br>"; });
           }
           $('#msg').removeClass('alert-success').addClass('alert-error').html(msg).show();
       }
   });
});


});