arsh['connectors'] = {
    data_table: {
        _default_options: {oLanguage: {
            "sProcessing":   "درحال پردازش...",
            "sLengthMenu":   "نمایش محتویات _MENU_",
            "sZeroRecords":  "موردی یافت نشد",
            "sInfo":         "_START_-_END_ از _TOTAL_ پیام",
            "sInfoEmpty":    "تهی",
            "sInfoFiltered": "(فیلتر شده از مجموع _MAX_ مورد)",
            "sInfoPostFix":  "",
            "sSearch":       "فیلتر:",
            "sUrl":          "",
            "oPaginate": {
                "sFirst":    "ابتدا",
                "sPrevious": "قبلی",
                "sNext":     "بعدی",
                "sLast":     "انتها"
            }
        }},

        create: function(selector, opts){
            if (typeof opts == 'undefined') opts = {};
            $(selector).dataTable($.extend(arsh.connectors.data_table._default_options, opts));
        }
    }
};
