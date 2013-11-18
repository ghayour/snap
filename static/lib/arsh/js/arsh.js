/*******************
 * ARSH JS Library *
 *******************/
(function(){
    /* Simple JavaScript Inheritance
     * By John Resig http://ejohn.org/
     * MIT Licensed.
     */
    // Inspired by base2 and Prototype

    var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

    // The base Class implementation (does nothing)
    this.Class = function(){};

    // Create a new Class that inherits from this class
    Class.extend = function(prop) {
        var _super = this.prototype;

        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        initializing = true;
        var prototype = new this();
        initializing = false;

        // Copy the properties over onto the new prototype
        for (var name in prop) {
            // Check if we're overwriting an existing function
            prototype[name] = typeof prop[name] == "function" &&
                typeof _super[name] == "function" && fnTest.test(prop[name]) ?
                (function(name, fn){
                    return function() {
                        var tmp = this._super;

                        // Add a new ._super() method that is the same method
                        // but on the super-class
                        this._super = _super[name];

                        // The method only need to be bound temporarily, so we
                        // remove it when we're done executing
                        var ret = fn.apply(this, arguments);
                        this._super = tmp;

                        return ret;
                    };
                })(name, prop[name]) :
                prop[name];
        }

        // The dummy class constructor
        function Class() {
            // All construction is actually done in the init method
            if ( !initializing && this.init )
                this.init.apply(this, arguments);
        }

        // Populate our constructed prototype object
        Class.prototype = prototype;

        // Enforce the constructor to be what we expect
        Class.prototype.constructor = Class;

        // And make this class extendable
        Class.extend = arguments.callee;

        return Class;
    };
})();

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

function _t(str) {
    if (gettext) {
        return gettext(str);
    } else {
        return str;
    }
}

function _tGuess(str) {
    var trans, s2;
    var transforms = [
        function(s) { return s },
        function(s) { return s.replace('_', ' ') },
        function(s) { return s.toLowerCase() },
        function(s) { return (s.length >= 4 && s.substr(0, 2) === '__' && s.substr(s.length - 2) === '__') ? s.substr(2, 3) : s }
    ];
    for (var i=0; i<transforms.length; i++) {
        s2 = transforms[i](str);
        trans = _t(s2);
        if (trans != s2) break;
    }
    return trans;
}


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

        rename_property: function (obj, old_name, new_name) {
            if (obj.hasOwnProperty(old_name)) {
                obj[new_name] = obj[old_name];
                delete obj[old_name];
                return true;
            }
            return false;
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
            if ($('dynamic_form#'+form.id+' input[name='+name+']').length == 0)
                $('<input type="hidden" name="'+name+'" value="'+value+'" />').appendTo('dynamic_form#'+form.id);
        },

        set_hidden: function(form, name, value){
            $('dynamic_form#' + form.id + ' input[name=' + name + ']').val(value);
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
        },

        popup_upload: function (url){
            return window.open(url, "popup_upload", "width=550,height=500,resizable=no,left=0,top=100,screenX=0,screenY=100");
        },

        goto: function(url) {
            window.location = url;
        },

        redirect: function(url) {
            return function(){arsh.dom.goto(url);}
        },

        makeNumberOnlyInput: function(selector) {
            $(selector).keydown(function (event) {
                // Allow: backspace, delete, tab, escape, and enter
                if (event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
                    // Allow: Ctrl+A
                        (event.keyCode == 65 && event.ctrlKey === true) ||
                    // Allow: home, end, left, right
                        (event.keyCode >= 35 && event.keyCode <= 39)) {
                    // let it happen, don't do anything
                } else {
                    // Ensure that it is a number and stop the keypress
                    if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105 )) {
                        event.preventDefault();
                    }
                }
            });
        },

        ensureTableHasHeader: function (table, headersTitle) {
            if (typeof headersTitle === 'undefined' || !headersTitle) {
                headersTitle = [];
            }
            var $table = $(table);
            if ($table.find('th').length == 0) {
                var row = '<tr>';
                for (var i=0; i<headersTitle.length; i++) {
                    row += '<th>' + headersTitle[i] + '</th>';
                }
                row += '<th></th>';
                row += '</tr>';
                $table.html(row); // TODO: better to prepend, or modify thead
            }
        },

        connectToPage: function () {
            $('a.http-post').click(function() {
                var action = $(this).attr('href');
                arsh.browser.postGoTo(action, {}, true);
                return false;
            });
            $('button.link.http-post').click(function() {
                var action = $(this).data('href');
                arsh.browser.postGoTo(action, {}, true);
                return false;
            });
        }
    },

    fn: {
        curry: function(f){
            return function(){f()};
        }
    },

    browser: {
        getCookie: function (name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
         },

        postGoTo: function (url, data, includeCsrf) {
            includeCsrf = typeof includeCsrf === 'boolean' && includeCsrf;
            if (typeof data === 'undefined') data = {};

            if (includeCsrf) {
                data['csrfmiddlewaretoken'] = arsh.browser.getCookie('csrftoken');
            }

            var dataStr = '';
            for (var k in data) {
                if (!data.hasOwnProperty(k)) continue;
                dataStr += '<input type="hidden" name="' + k + '" value="' + data[k] + '">';
            }

            $('<form action="' + url + '" method="POST">' + dataStr + '</form>').appendTo('body').submit();
        },

        popupWindow: function (opts) {
            if (typeof opts === 'undefined') opts = {};
            var url = arsh.js.get(opts, 'url', '#');
            var title = arsh.js.get(opts, 'title', 'popUpWindow');
            return window.open(url, title, 'height=700,width=800,left=10,top=10,resizable=0,scrollbars=1,toolbar=0,menubar=0,location=0,directories=no,status=yes');
        },

        /**
         *  A function to simulate time taking operations, just for use in testing!
         * @param millis
         */
        sleep: function (millis) {
            var startDate, currentDate;
            startDate = currentDate = new Date();
            while(currentDate - startDate < millis) {
                currentDate = new Date();
            }
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
