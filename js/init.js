var Control = {
    slice: {
        slices: {},
        update: function(id, form){
            var el = this.slices[id].element();

            try{
                el.setStyle({
                    top:    form.elements['top'].value + 'px',
                    left:   form.elements['left'].value + 'px',
                    width:  form.elements['width'].value + 'px',
                    height: form.elements['height'].value + 'px'
                });
            }
            catch(e){
                return false;
            }
            return true;
        }
    },
    ui: {
        forms: {},
        items:{},

        select: function( el ){
            var id = el.id.replace(/(\w+_)/, '');

            if( $H(this.forms).keys().indexOf(id) > -1 ){
                $('form_updater').select('form').invoke('hide');
                this.forms[id].show();
            }
            else{
                new Ajax.Request( el.href, {
                    method: 'get',
                    onComplete: function( tr ){
                        $('form_updater').select('form').invoke('hide');
                        $('form_updater').insert({top:tr.responseText});

                        var form = $('form_updater').down('form');

                        this.forms[id] = form;

                        form.observe('submit', function(evt){
                            Control.ui.submit(id,evt.findElement('form'));
                        });

                        $A(form.elements).invoke('observe', 'keyup', function(evt){
                            if( $(id).hasClassName('slice') ){
                                Control.slice.update(id,evt.findElement('form'));
                            }
                        })

                        Control.ui.update( $(id) );

                    }.bindAsEventListener(this)
                });
            }
            //return false;
        },

        submit: function( id, form ){
            form.request({
                onComplete: function(tr){
                    document.location.reload();
                }
            });
        },

        update: function( el ){
            var id   = el.id;
            var form = this.forms[id];

            if( form !== undefined ){
                var dim = el.getDimensions();
                var pos = el.positionedOffset();

                form.elements['top'].value = pos.top;
                form.elements['left'].value = pos.left;

                if( form.elements['width'] ){
                    form.elements['width'].value = dim.width;
                    form.elements['height'].value = dim.height;
                }
            }
        }
    }
}

$(document).observe('dom:loaded', function(evt){
    var slices = {};
    var active = null;

    $$('a.ahah').invoke('observe', 'click', function( evt ){
        evt.stop();
        element = evt.findElement('a');
        $$('a.ahah').invoke('show');
        $$('.ahah_content').invoke('remove');

        this.ajax = new Ajax.Request( element.href, {method: 'get',
            onComplete: function( tr ){
                var container = Element('span',{className: 'ahah_content'}).update(tr.responseText);
                element.insert({after: container});
                element.hide();
            }
        });

        return false;
    });


    $$('.slice').each(function(el){
        Control.slice.slices[el.id] = new Slice(el);
    });

    $$('.image').each(function(el){
        var img = new Movable(el)
    });

    $(document).observe('dhtml:activated', function(evt){
        active = evt.memo;
    });

    $(document).observe('dhtml:dragged', function(evt){
        Control.ui.update(evt.element());
    });

    $(document).observe('mouseup',function(){
        if( active != null ){
            active.disable();
            active = null;
        }
    })

    $('viewport').observe('mousemove', function(evt){
        if( active != null ){
            active.position(evt);
        }
    })
});

var Movable = Class.create({
    _element: null,
    _pointer: null,

    initialize: function(el, options){
        this._element = $(el);
        this._element.observe('mousedown', this.onMouseDown.bindAsEventListener(this));
    },

    onMouseDown: function( evt ){
        this.position(evt);
        this._element.fire('dhtml:activated', this)
    },

    disable: function( evt ){
        this._pointer = null;
    },

    position: function( evt ){
        if( this._pointer ){
            var delta = {
                x: this._pointer.x - evt.clientX,
                y: this._pointer.y - evt.clientY
            }

            var pos = this._element.positionedOffset();

            this._element.setStyle({
                top: pos.top - delta.y + 'px',
                left: pos.left - delta.x + 'px'
            });
        }

        this._pointer = {x:evt.clientX, y: evt.clientY}

        this._element.fire('dhtml:dragged', this);
    }
});

var Slice = Class.create({
    _element:null,
    _hitArea:null,
    _pointer: null,

    initialize: function( el ){
        this._element = $(el);
        var body = new Element('div');
        body.setStyle('position:relative; width:100%; height:100%;\
            background-color:#cfc;opacity:0.6;border:1px solid #ff0;cursor:move;')

        var parts = {
            nResize:    {top:0,left:10,right:10,height:10,'border-top':0},
            //neResize:   {top:0,right:0,width:10,height:10},
            eResize:    {top:10,bottom:10,right:0,width:10,width:10,'border-right':0},
            //seResize:   {bottom:0,right:0,width:10,height:10},
            sResize:    {bottom:0,right:10,left:10,height:10,'border-bottom':0},
            //swResize:   {left:0,bottom:0,width:10,height:10},
            //nwResize:   {top:0,left:0,width:0,width:10,height:10} ,
            wResize:    {left:0,bottom:10,top:10,width:10,'border-left':0}
        }

        for( key in parts ){
            var value = parts[key];
            var e = new Element('div');

            var style = 'border: 1px dotted #999; position:absolute;cursor: %cursor;'
                    .replace('%cursor',key.replace('R', '-r'));

            for( val in value ){
                style += '%key: %valuepx;'.replace('%key', val);
                style = style.replace('%value', value[val]);
            }

            e.addClassName(key);
            e.setStyle(style);
            body.insert(e);
        }

        this._element.insert(body);
        this._element.observe('mousedown', this.onMouseDown.bindAsEventListener(this));
    },

    onMouseDown: function( evt ){
        evt.stop(evt);

        this._hitArea = {top:false, right:false, bottom:false, left:false};
        var className = evt.element().className;

        var config = {
            top:    ['nResize', 'neResize', 'nwResize'],
            right:  ['neResize', 'eResize', 'seResize'],
            bottom: ['seResize', 'sResize', 'swResize'],
            left:   ['swResize', 'wResize', 'nwResize']
        }

        if( config.top.indexOf(className) != -1 ){
            this._hitArea.top = true;
        }
        if( config.right.indexOf(className) != -1 ){
            this._hitArea.right = true;
        }
        if( config.bottom.indexOf(className) != -1 ){
            this._hitArea.bottom = true;
        }
        if( config.left.indexOf(className) != -1 ){
            this._hitArea.left = true;
        }

        this._element.fire('dhtml:activated', this)
    },

    disable: function(){
        this._pointer = null
    },

    position: function( evt ){
        if( this._pointer ){
            var delta = {
                x: this._pointer.x - evt.clientX,
                y: this._pointer.y - evt.clientY
            }

            var pos = this._element.positionedOffset();
            if( false == ( this._hitArea.top || this._hitArea.left
                          || this._hitArea.bottom || this._hitArea.right )){
                this._element.setStyle({
                    top: pos.top - delta.y + 'px',
                    left: pos.left - delta.x + 'px'
                })
            }
            else{
                var dim = this._element.getDimensions();
                style = '';
                if( this._hitArea.bottom ){
                    style += 'height: %hpx'.replace('%h', (dim.height - delta.y));
                }
                else if( this._hitArea.top ){
                    style += 'top: %tpx; height:%hpx'
                        .replace('%t', (pos.top-delta.y))
                        .replace('%h', (dim.height + delta.y))
                }

                if( this._hitArea.right ){
                    style += 'width: %wpx'.replace('%w', (dim.width - delta.x));
                }
                else if( this._hitArea.left ){
                    style += 'left: %lpx; width: %wpx'
                        .replace('%l', (pos.left - delta.x))
                        .replace('%w', (dim.width + delta.x))
                }

                this._element.setStyle(style);
            }

        }

        this._pointer = {x:evt.clientX, y: evt.clientY}
        this._element.fire('dhtml:dragged', this);
    }
});
