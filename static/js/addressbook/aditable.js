/**
 * Created by barzekar on 11/27/13.
 */
$(function(){

 $.fn.editable.defaults.mode = 'inline';
 $('.firstname').editable();
 $('.lastname').editable();
 $('.email').editable();
 $('.extraemail').editable();

});