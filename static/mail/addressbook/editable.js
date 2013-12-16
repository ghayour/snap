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