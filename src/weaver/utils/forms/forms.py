from django.forms.forms import BoundField as DjangoBoundField
from django.forms.util import flatatt
from django import forms
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


__all__ = ('Form', 'ModelForm', 'FormMixin')


INPUT_TYPE_OVERRIDES = {
    forms.DateField: 'date',
    forms.TimeField: 'time',
    forms.URLField: 'url',
    forms.EmailField: 'email',
}


class BoundField(DjangoBoundField):

    def __init__(self, *args, **kwargs):
        uber = super(BoundField, self)
        uber.__init__(*args, **kwargs)
        widget = self.field.widget
        # overriding the input type
        input_type = INPUT_TYPE_OVERRIDES.get(self.field.__class__)
        if input_type:
            widget.input_type = input_type
        # setting the name of the class for targeting css
        widget.name = widget.__class__.__name__.lower()
        self.extended_help = self.form.extended_help_texts.get(self.name, '')

    def label_tag(self, contents=None, attrs=None):
        """
        Wraps the given contents in a <label>, if the field has an ID
        attribute. Does not HTML-escape the contents. If contents aren't
        given, uses the field's HTML-escaped label.

        If attrs are given, they're used as HTML attributes on the <label> tag.
        """
        contents = contents or conditional_escape(self.label)
        widget = self.field.widget
        id_ = widget.attrs.get('id') or self.auto_id
        if id_:
            attrs = attrs and flatatt(attrs) or ''
            html = [u'<label for="%s"%s>' % (widget.id_for_label(id_), attrs),
                    unicode(contents)]
            if self.field.required:
                html.append('<span class="required" title="%s"> *</span>'
                            % _('Required field'))
            html.append('</label>')
        return mark_safe("".join(html))



class FormMixin(object):

    template = 'forms/form.html'
    extended_help_texts = {}

    def __init__(self, *args, **kwargs):
        self.template = kwargs.pop('template', self.template)
        self.request = kwargs.get('request') # we support implicit use of request too
        uber = super(FormMixin, self)
        # hack to support request as a standard kwarg for forms
        try:
            uber.__init__(*args, **kwargs)
        except TypeError:
            kwargs.pop('request', None)
            uber.__init__(*args, **kwargs)

    def __iter__(self):
        for name, field in self.fields.items():
            yield BoundField(self, field, name)

    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return BoundField(self, field, name)

    def __unicode__(self):
        return self.render()

    def render(self, template=None):
        template = template or self.template
        return render_to_string(template, {'form': self})


class Form(FormMixin, forms.Form):
    pass


class ModelForm(FormMixin, forms.ModelForm):
    pass

