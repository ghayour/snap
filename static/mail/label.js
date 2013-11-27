$(document).ready(function () {
      $("#action-bar").on("keypress", ".label-input",function (event) {
        if (event.keyCode == 13) {
            event.preventDefault();
        }
        var type = $(this).attr("id");
        autocomplete_label($(this), type);
    });

      $(".mail-tags").on("click", ".mail-tag-delete, .mail-label-delete",function(){
        var item_element = $(this);
        var item_id = item_element.attr("item_id");
        var item_type = item_element.attr("item_type");
        var label_id = item_element.attr("label_id");
        var current_label = $("#current_label").val();
        var url = arsh.dj.resolver.url('mail/delete_label');
        $.post(url,
            { item_id: item_id,item_type:item_type, label_id: label_id, current_label:current_label},
            function (data) {
                var data1 = JSON.parse(data);
                if (data1["response_text"]=="success"){
                    alert('حذف برچسب باموفقیت انجام شد.');
                    if (data1["referrer"]){
                        window.location = data["referrer"];
                    }
                    item_element.closest(".delete-label").remove();
                }
                else{
                    alert(data1["response_text"]);
                }
            });
    });
});

function autocomplete_label(item_element, item_type) {
    var current_label = $("#current_label").val();
    var a = item_element.autocomplete({
        source: function (request, response) {
            $.getJSON(arsh.dj.resolver.url('mail/label_list'),
                { name_startsWith: request.term, current_label:current_label},
                function (data1) {
                    response(data1);
                });
        },
        minLength: 2,
        focus: function (event, ui) {
            event.preventDefault();
            if (ui.item.value <= 0) {
                var add = '(برچسب جدید)';
                var parts = ui.item.label.split(add);
                item_element.val(parts[0].trim());
            }
            else
                item_element.val(ui.item.label.trim());
        },
        select: function (event, ui) {
            event.preventDefault();
            if (ui.item.value <= 0) {
                var add = '(برچسب جدید)';
                var parts = ui.item.label.split(add);
                item_element.val(parts[0].trim());
            }
            else
                item_element.val(ui.item.label.trim());

            if(item_type=="move_thread")
                mailSystem.moveToLabel(ui.item.label, ui.item.value, ui.item.label, current_label);
            else
                mailSystem.applyLabel(ui.item.value, ui.item.label);

            item_element.val("");
        }
    });
}