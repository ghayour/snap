$(function(){

            $(".receiver , .sender").popover({ placement: 'bottom', trigger: 'manual', html: true,
                content: '<a class="add-contact">' + "اضافه شدن به لیست تماس" + '<a>' }).mouseenter(function () {
                        var $taraget=$(this);
                        var user_id = $('.thread').data('user-id');
                        var contact_user_id = $(this).data('contact-user-id');
                            $.post(arsh.dj.resolver.url('mail/contact/add'),{user_id: user_id, contact_user_id: contact_user_id, action:'validate'}
                    ).success(function (data) {

                        if (data.result==true) {
                            $taraget.popover('show');
                        } else {
                            return;
                        }
                    });

                });


                $(".add-contact").on('click', function () {
                    var user_id = $('.thread').data('user-id');
                    var contact_user_id = $(this).parents().find('.contact').data('contact-user-id');
                    $.post(arsh.dj.resolver.url('mail/contact/add'),
                           {user_id: user_id, contact_user_id: contact_user_id}
                    ).success(function (contact) {
                        if (contact.errors) {
                            notify(contact.errors, {type: 'error'});
                        } else {
                            notify(contact.display_name + 'آدرس مورد نظر با موفق?ت به ل?ست تماس اضافه شد.');
                        }
                    });
                });


            $("html").on('click', function () {
                $('.contact').popover('hide');
                $('.select2-dropdown-open').removeClass("select2-dropdown-open");
            });
});
