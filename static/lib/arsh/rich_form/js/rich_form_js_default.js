/**
 * Created with PyCharm.
 * User: hamed
 * Date: 04/07/13
 * Time: 1:48 PM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    $('form .crispy_td input,select,textarea').focus( function() {
        $(this).parents('.crispy_td').addClass('field-block-focused');
    });

    $('form .crispy_td input,select,textarea').blur( function() {
        $(this).parents('.crispy_td').removeClass('field-block-focused');
    });
});
