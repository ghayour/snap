if (typeof arsh == 'undefined') arsh = {};
arsh.mail = {};

arsh.e = {};
arsh.e.ValueError = function(){};

arsh.mail.Client = Class.extend({
    init: function() {
        this.state = {
            onlyShowNewMail: true,
            viewing: ''
        };
        this.objectHandler = null;
    },

    setView: function(view) {
        var VALID_VIEWS = ['threads', 'mails', ''];
        if (!_.contains(VALID_VIEWS, view))
            throw new arsh.e.ValueError();
        this.state.viewing = view;
        if (view == 'threads') {
            this.objectHandler = new arsh.mail.ThreadHandler();
        }
        if (view == 'mails') {
            this.objectHandler = new arsh.mail.MailHandler();
        }
    },

    setArchiveMode: function(mode) {
        ajaxLoader.show();
        if (typeof mode === 'undefined') {
            mode = ! this.state.onlyShowNewMail;
        }
        if (this.state.onlyShowNewMail === mode) {
            return;
        }
        if (mode) {
            window.location='';
        } else {
            window.location = 'archive';
        }
    },

    moveToLabel: function(label, label_id, label_name, current_label) {
        this.objectHandler.moveToLabel(label, label_id, label_name, current_label);
    },
    applyLabel: function (label, label_id, label_name, current_label){
        this.objectHandler.applyLabel(label, label_id, label_name, current_label);
    },
    moveToTrash: function(){
        this.objectHandler.moveToTrash();
    },
    markAsSpam: function(){
        this.objectHandler.markAsSpam();
    }
});

arsh.mail.ObjectHandler = Class.extend({
    init: function() {
        this.selection = [];
    },

    _updateSelection: function(type) {
        var self = this;
        self.selection = [];
        $('input:checkbox[class="' + type + '-checkbox"]:checked').each(function () {
            self.selection.push($(this).attr('value'));
        });
    }
});

arsh.mail.ThreadHandler = arsh.mail.ObjectHandler.extend({
    applyLabel: function (label_id, label_name) {
        // apply a label to a thread
        this._updateSelection('thread');
        var self = this;
        $.post(arsh.dj.resolver.url('mail/add_label'),
            {item_id: self.selection, item_type: 'thread',
                label_id: label_id, label_name: label_name},
            function (data) {
                if (data["response_text"] == 'success') {
                    alert('برچسب گذاري با موفقيت انجام شد.');
                }
                else {
                    alert(data["response_text"]);
                }
            });
    },

    moveToLabel: function (label, label_id, label_name, current_label) {
        this._updateSelection('thread');
        var self = this;
        if (label == label_name){
            label = '';
        }
        $.post(arsh.dj.resolver.url('mail/move_thread'),
            {item_id: self.selection, label : label, current_label:current_label,
                label_id: label_id, label_name: label_name},
                function (data) {
                    if (data["response_text"] == 'success') {
                        alert('عملیات با موفقیت انجام شد.');
                        $('input:checkbox[class="thread-checkbox"]:checked').each(function () {
                            $(this).closest("tr").remove();
                        });
                    }
                    else {
                        alert(data["response_text"]);
                    }
                });
    },

    markAsSpam: function() {
        this.moveToLabel('spam');
    },

    moveToTrash: function() {
        this.moveToLabel('trash');
    }
});

arsh.mail.MailHandler = arsh.mail.ObjectHandler.extend({
    applyLabel: function (label_id, label_name) {
        // apply a label to a mail
        var item_type = 'mail';
        this._updateSelection(item_type);
        var self = this;

        var item_id = self.selection;
        var thread_id = $('#thread-id').val();
        if (item_id.length<1){
            //hich mail ei select nashode pas thread label mikhorad
            item_id = thread_id;
            item_type = 'thread';
        }
        $.post(arsh.dj.resolver.url('mail/add_label'),
            {item_id: item_id, item_type: item_type,
                label_id: label_id, label_name: label_name},
            function (data) {
                if (data["response_text"] == 'success') {
                    alert('برچسب گذاري با موفقيت انجام شد.');
//                    $('input:checkbox[class="mail-checkbox"]:checked').each(function () {
//                        $(this).parent().nextAll("div").children("div#label-list").append(
//                            '<div class="mail-label delete-label">' +
//                                '<span class="mail-label-delete" item_type="mail" item_id=' +
//                                    item_id + ' label_id=' + data["label_id"] + '>X</span>' +
//                                '<span class="mail-label-title">' +
//                                    '<a href="' + data["label_url"] + '">' + label_name.split('(برچسب جدید)')[0] + '</a>' +
//                                '</span>' +
//                            '</div>'
//                        );
//                    });

                    $('.mail-tags').append(
                        '<div class="mail-tag delete-label">' +
                            '<span class="mail-tag-delete" item_type="thread" item_id="' +
                                thread_id + '" label_id="' + data['label_id'] + '">X</span>' +
                            '<span class="mail-tag-title">' +
                                '<a href="' + data["label_url"] + '">' + label_name.split('(برچسب جدید)')[0] + '</a>' +
                            '</span>' +
                        '</div>'
                    );
                }
                else {
                    alert(data["response_text"]);
                }
            });
    },

    moveToLabel: function (label, label_id, label_name, current_label) {
        var thread_id = $('#thread-id').val();
        if (label == label_name)
            label = '';
        $.post(arsh.dj.resolver.url('mail/move_thread'),
            {item_id: thread_id, label : label, current_label:current_label,
                label_id: label_id, label_name: label_name},
                function (data) {
                    if (data["response_text"] == 'success') {
                        alert('عملیات با موفقیت انجام شد.');
                        var current_label_slug = $("#current_label").attr('data-slug');
                        var new_url = arsh.dj.resolver.url('mail/see_label',{label_slug:current_label_slug});
                        window.location = new_url;
                    }
                    else {
                        alert(data["response_text"]);
                    }
                });
    },

        markAsSpam: function() {
        this.moveToLabel('spam');
    },

    moveToTrash: function() {
        this.moveToLabel('trash');
    }
});