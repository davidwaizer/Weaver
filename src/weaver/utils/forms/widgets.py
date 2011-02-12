from convert import MediaFile
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import widgets
from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


__all__ = ('TinyWidget', 'TinyAdminWidget', 'RadioSelect', 'ImageWidget',
           'DeleteImageWidget', 'AdminImageWidget')


class TinyWidget(forms.Textarea):
    config = {
    }

    def __init__(self, attrs=None, config=None):
        self.config.update(config or {})
        super(TinyWidget, self).__init__(attrs)

    def render(self, name, value, attrs):
        editor_selector = 'tiny-%s' % attrs['id']
        attrs['class'] = editor_selector
        self.config['editor_selector'] = editor_selector
        s = super(TinyWidget, self).render(name, value, attrs)
        return s + render_to_string('util/tiny.html', {
            'MEDIA_URL': settings.MEDIA_URL,
            'config': simplejson.dumps(self.config),
        })

    class Media:
        js = (
            'tiny_mce/tiny_mce.js',
            'js/tiny_config.js',
        )

class TinyAdminWidget(TinyWidget):
    config = {
        # cant seem to be able to user reverse here
        # 'external_image_list_url': reverse('admin:images_image_imagelist'),
        'external_image_list_url': '/admin/images/image/imagelist/',
    }


class RadioFieldRenderer(widgets.RadioFieldRenderer):
    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        html = []
        for w in self:
            html.append('<li>%s</li>' % force_unicode(w))
        return mark_safe(u'<ul class="radiolist">\n%s\n</ul>' % u'\n'.join(html))


class RadioSelect(widgets.RadioSelect):
    renderer = RadioFieldRenderer


class ImageWidget(forms.FileInput):
    """
    An ImageField Widget that shows its current value if it has one.
    """
    def render(self, name, value, attrs=None):
        output = [super(ImageWidget, self).render(name, value, attrs)]
        if value and hasattr(value, "url"):
            im = MediaFile(value.name).thumbnail('150x150>')
            tag = '<div class="profile-image">%s</div>' % im.tag
            output.append(tag)
        return mark_safe(u''.join(output))


class AdminImageWidget(forms.FileInput):
    """
    An ImageField Widget for django.contrib.admin that shows its current
    value if it has one.
    """
    def render(self, name, value, attrs=None):
        output = [super(AdminImageWidget, self).render(name, value, attrs)]
        if value and hasattr(value, "url"):
            im = MediaFile(value.name).thumbnail('150x150>')
            tag = ('<div style="float:left"><a style="display:block;margin:0 0 10px" '
                   ' class="thumbnail" target="_blank" href="%s">%s</a>' %
                   (value.url, im.tag))
            output.insert(0, tag)
            output.append('</div>')
        return mark_safe(u''.join(output))


class DeleteImageWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None):
        uber = super(DeleteImageWidget, self).render(name, value, attrs)
        return u'<label for="%s">%s %s</label>' % (attrs['id'], uber, _('Delete image'))

