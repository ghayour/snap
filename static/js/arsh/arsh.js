/*******************
 * ARSH JS Library *
 *******************/
Function.prototype.inheritsFrom = function( parentClassOrObject ){
    if ( parentClassOrObject.constructor == Function )
    {
        //Normal Inheritance
        this.prototype = new parentClassOrObject;
        this.prototype.constructor = this;
        this.prototype.parent = parentClassOrObject.prototype;
    }
    else
    {
        //Pure Virtual Inheritance
        this.prototype = parentClassOrObject;
        this.prototype.constructor = this;
        this.prototype.parent = parentClassOrObject;
    }
    return this;
};


/**
 * @namespace کتابخانه‌ی کد عرش
 */
arsh = {
    /** نسخه‌ی جاری کتابخانه */
    version: '0.0.1',


    load_module: function(module){
        //TODO: auto dependency loading
        arsh._internals.load_file(arsh._internals.get_lib_url() + module + '.js');
    },


    /**
     * @namespace توابع برای استفاده‌ی داخلی
     * @private
     */
    _internals: {
        load_file: function (filename, filetype){
            if (typeof filetype == 'undefined' || filetype == null){
                filetype = filename.substr(filename.indexOf('.')+1);
            }

            var fileref = null;
            if (filetype=="js"){ //if filename is a external JavaScript file
                fileref=document.createElement('script');
                fileref.setAttribute("type","text/javascript");
                fileref.setAttribute("src", filename);
            }
            else if (filetype=="css"){ //if filename is an external CSS file
                fileref=document.createElement("link");
                fileref.setAttribute("rel", "stylesheet");
                fileref.setAttribute("type", "text/css");
                fileref.setAttribute("href", filename);
            } else {
                console.error('Invalid file type: ' + filetype);
            }
            document.getElementsByTagName("head")[0].appendChild(fileref);
        },

        get_lib_url: function(){
            return '/static/js/arsh/'; //TODO: implement this
        }
    },


    /**
     * @namespace توابع کمکی برای نوشتن ساده‌تر برخی اعمال
     */
    js: {
        get: function (dic, key, default_value) {
            if ((typeof dic[key] == 'undefined') || (dic[key] == null) ) {
                if (typeof default_value == 'undefined')
                    return null;
                return default_value;
            }
            return dic[key];
        },

        set_default: function (dic, key, default_value) {
            if ((typeof dic[key] == 'undefined') || (dic[key] == null) ) {
                dic[key] = default_value;
            }
        },

        is_array: function (obj) {
            return Object.prototype.toString.call(obj) === "[object Array]";
        }
    },


    /**
     * @namespace توابع مربوط به کار با DOM
     */
    dom: {
        ensure_hidden_field: function(form, name, value){
            if (typeof value == "undefined")
                value = '';
            if ($('form#'+form.id+' input[name='+name+']').length == 0)
                $('<input type="hidden" name="'+name+'" value="'+value+'" />').appendTo('form#'+form.id);
        },

        set_hidden: function(form, name, value){
            $('form#' + form.id + ' input[name=' + name + ']').val(value);
        },


        /**
         *
         * @param {String[]|Object[]} arr یک آرایه از گزینه‌ها یا یک آرایه از اشیایی به فرمت خاص
         * @param arr.value مقدار عدیی
         * @param arr.label متن برای نمایش
         * @param {Object} [default_option="null"] گزینه‌ی از ابتدا انتخاب شده
         * @return {String} کد html برای گزینه‌های یک Select Box
         * @private
         */
        _create_options: function(arr, default_option){
            if (typeof default_option == 'undefined')
                default_option = null;
            var html = '';
            if (default_option)
                html += '<option value="-1">'+default_option+'</option>';
            var is_obj = ! arsh.js.is_array(arr);
            for (var i in arr){
                //noinspection JSValidateTypes
                if (arr.hasOwnProperty(i)){
                    var value = is_obj ? arr[i].value : i;
                    var label = is_obj ? arr[i].label : arr[i];
                }
                html += '<option value="'+value+'">'+label+'</option>';
            }
            return html;
        },

        create_select: function(arr, name, default_option) {
            if (typeof default_option == 'undefined')
                default_option = null;
            var html = '<select id="'+name+'" name="'+name+'">';
            html += arsh.dom._create_options(arr, default_option);
            html += '</select>';
            return html;
        },

        update_select: function(arr, id, default_option) {
            if (typeof default_option == 'undefined')
                default_option = null;
            $('select#'+id).html(arsh.dom._create_options(arr, default_option));
        },

        load_file: function (filename, filetype){
            if (typeof filetype == 'undefined'){
                filetype = null;
            }
            return arsh._internals.load_file(filename, filetype)
        }
    },


    /**
     * @namespace کلاس‌های پایه برای ساده‌تر کردن استفاده از الگوهای طراحی معروف
     */
    patterns: {
        /**
         * @class کلاس پایه برای الگوی Observer
         * @constructor
         */
        Observable: function(){
            this._observers = [];
        }
    },


    /**
     * @namespace توابع ریاضی
     */
    math: {
        /** عدد را به توان دو می‌رساند
         *
         * @param {Number} x یک عدد
         * @return {Number} توان دوی عدد
         */
        sqr: function (x) { return x*x; }
    }
};




/****************************
 * ARSH.PATTERNS.Observable *
 ****************************/
arsh.patterns.Observable.prototype.register_observer = function(observer) {
    this._observers.push(observer);
};


arsh.patterns.Observable.prototype.remove_observer = function(observer) {
    for (var i=0; i<this._observers.length; i++){
        if (this._observers[i] == observer)
            this._observers[i] = null;
    }
};


arsh.patterns.Observable.prototype.notify_all = function() {
    for (var i=0; i<this._observers.length; i++){
        var cur = this._observers[i];
        if (cur)
            cur.notify(this);
    }
};
