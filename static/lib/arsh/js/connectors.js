arsh['connectors'] = {
    data_table: {
        _default_options:{
            oLanguage:{
                "sProcessing":"درحال پردازش...",
                "sLengthMenu":"نمایش محتویات _MENU_",
                "sZeroRecords":"موردی یافت نشد",
                "sInfo":"_START_-_END_ از _TOTAL_ فایل",
                "sInfoEmpty":"تهی",
                "sInfoFiltered":"(فیلتر شده از مجموع _MAX_ مورد)",
                "sInfoPostFix":"",
                "sSearch":"فیلتر:",
                "sUrl":"",
                "oPaginate":{
                    "sFirst":"ابتدا",
                    "sPrevious":"قبلی ",
                    "sNext":"بعدی ",
                    "sLast":"انتها"
                }
            },
            sPaginationType:"full_numbers"
        },

        create: function(selector, options){
            if (typeof selector == 'undefined' || selector == null)
                selector = '.data-table';
            if (typeof options == 'undefined' || options == null)
                options = {};
            $(selector).dataTable($.extend(options, arsh.connectors.data_table._default_options));
        }
    },

    jqgrid: {
        _default_options:{
            datatype: 'json',
            loadonce: true,
            height: 300
        },

        create: function(selector, options) {
            if (typeof options == 'undefined' || options == null)
                options = {};

            var postCalls = [];
            var selections = $(selector);

            // properties aliases
            arsh.js.rename_property(options, 'columns', 'colNames');
            arsh.js.rename_property(options, 'model', 'colModel');
            arsh.js.rename_property(options, 'title', 'caption');

            // more complicated aliases
            if (options.hasOwnProperty('selection')){
                switch (options.selection) {
                    case 'multi':
                    case 'multiple':
                    case 'multiselect':
                        options.multiselect = true;
                        break;
                    case 'single':
                        options.multiselect = true;
                        var forceSingleSelection = function(){
                            //FIXME: won't work if grouping is active
                            $(selector).jqGrid('resetSelection');
                            return true;
                        };
                        if (options.hasOwnProperty('beforeSelectRow')) {
                            var prev = options.beforeSelectRow;
                            options.beforeSelectRow = function() {
                                var allow = prev.apply(this, arguments);
                                if (allow) {
                                    return forceSingleSelection();
                                }
                                return false;
                            }
                        } else {
                            options.beforeSelectRow = forceSingleSelection;
                        }
                        postCalls.push(function(){
                            for (var i=0; i<selections.length; i++) {
                                var id = selections[i].id;
                                if (id) {
                                    $("#cb_" + id).hide();
                                } else {
                                    console.warn('Can not disable check all button for:', selections[i]);
                                }
                            }
                        });
                        break;
                    default:
                        console.warn('Invalid value for table selection:', options.selection);
                }
                delete options.selection;
            }

            if (options.hasOwnProperty('style')){
                postCalls.push(function() {
                    $(selector).closest('.ui-jqgrid').attr('style', function(i, val) {
                        if (typeof val == 'undefined')
                            return options.style;
                        return val + ';' + options.style;
                    });
                });
            }


            // dependant properties
            if (options.hasOwnProperty('data')){
                options.datatype = 'local';
            }

            // creating jqGrid
            $(selector).jqGrid($.extend({}, arsh.connectors.jqgrid._default_options, options));

            // other needed fixes (usually DOM related)
            for (var i=0; i<postCalls.length; i++) {
                postCalls[i]();
            }
        }
    },

    datepicker: {
        _default_options: {
            changeMonth: true,
            changeYear: true,
            dateFormat: "yy-mm-dd",
            onSelect: function(dateStr, inst) {
                var month;
                var day;
                if (inst.selectedDay < 10){
                    day = '0'+ inst.selectedDay;
                }else{
                    day = inst.selectedDay;
                }
                if (inst.selectedMonth < 10){
                    month = '0'+ (inst.selectedMonth+1);
                } else{
                    month = inst.selectedMonth+1;
                }
                $(this).val(inst.selectedYear+"-"+ month+"-"+ day);
            },
            onClose: function(){
                $(this).trigger('change');
            }
        },

        create: function(selector, options){
            if (typeof selector == 'undefined' || selector == null)
                selector = '.datepicker';
            if (typeof options == 'undefined' || options == null)
                options = {};
            $(selector).each(function(){
                var old_value = $(this).val();
                $(this).datepicker($.extend(options, arsh.connectors.datepicker._default_options));
                $(this).attr("autocomplete", "off");
                $(this).click(function(){
                    $(this).focus();
                });
                $(this).datepicker("option", "yearRange", "1370:1400");
                $(this).val(old_value);
            });
        }
    }
};
