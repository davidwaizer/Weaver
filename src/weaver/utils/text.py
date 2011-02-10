import re
import os
import unicodedata
from BeautifulSoup import BeautifulSoup as Soup, NavigableString
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags
from feedparser import _HTMLSanitizer
from htmlentitydefs import name2codepoint
from PIL import Image


number_re = re.compile(r'^\d+$')
internal_img_re = re.compile(r'%s(.+)' % settings.MEDIA_URL)
empty_p_re = re.compile(r'<p>\s+<\/p>')


def to_text(s):
    s = strip_tags(s).strip()
    s = re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)
    s = re.sub('&#(\d+);',
            lambda m: unichr(int(m.group(1))), s)
    s = re.sub('&#x([\da-fA-F]+);',
            lambda m: unichr(int(m.group(1), 16)), s)
    return s

class HTMLSanitizer(_HTMLSanitizer):
    acceptable_elements = ('p', 'a', 'em', 'strong', 'img', 'ul', 'ol', 'li', 'br')
    acceptable_attributes = ('alt', 'rel', 'title', 'src', 'width', 'height',
      'href')

    def __init__(self, encoding, acceptable_elements=None,
          acceptable_attributes=None):
        if acceptable_elements is not None:
            self.acceptable_elements = acceptable_elements
        if acceptable_attributes is not None:
            self.acceptable_attributes = acceptable_attributes
        _HTMLSanitizer.__init__(self, encoding)

def sanitize_html(html, encoding=None, acceptable_elements=None,
      acceptable_attributes=None):
    encoding = encoding or 'utf-8'
    p = HTMLSanitizer(encoding , acceptable_elements=acceptable_elements,
      acceptable_attributes=acceptable_attributes)
    p.feed(html)
    return p.output()

def clean_html(html, max_width=None, max_height=None, *args, **kwargs):
    """
    This will objectify the html using BeautifulSoup which will do some
    cleaning in the process, then we resize the images to the specified
    size
    """
    soup = Soup(html.strip())
    images = soup.findAll('img', src=internal_img_re,
            width=number_re, height=number_re)
    for image in images:
        m = internal_img_re.match(image['src'])
        rel_path = m.group(1)
        path = os.path.join(settings.MEDIA_ROOT, *rel_path.split('/'))
        try:
            im = Image.open(path)
        except IOError:
            pass
        else:
            xr, yr = float(image['width']), float(image['height'])
            if max_width is not None and xr > max_width:
                xr = max_width
            if max_height is not None and yr > max_height:
                xy = max_height
            x, y = [float(v) for v in im.size]
            r = min(1.0, min(xr/x, yr/y))
            image['width'] = int(round(x*r))
            image['height'] = int(round(y*r))
    return empty_p_re.sub('', unicode(soup))


def slugify(s, entities=False, decimal=False, hexadecimal=False, ascii=True,
            lower=True, replace_re=None, replace_char=None, invalid=None,
            instance=None, manager=None, slug_field='slug', extra_lookup=None):
    """
    Will try to make the best url string out of any string. If the `entities`
    keyword is True it will try to translate html entities. The `decimal`
    keyword is for decimal html character reference, `hexadecimal` for
    hexadecimal.
    `invalid` should be a list or tuple of invalid slugs. You can also pass
    a Django model instance as `instance`, slugify will then make sure it is a
    unique slug for that model. The keyword `extra_lookup` should be a
    dictionary containing extra lookup. Use this to make the slug unique only
    within the the lookup. For example:
    extra_lookup = {'date': datetime.date.today()} slugify will make
    the slug unique for rows where the column 'date' is todays date. `slug_field`
    is the field in the model to match for uniqueness. You can pass a manager
    to use instead of the default one as `manager`.
    """
    s = force_unicode(s)
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint),
                lambda m: unichr(name2codepoint[m.group(1)]), s)
    if decimal:
        try:
            s = re.sub('&#(\d+);',
                    lambda m: unichr(int(m.group(1))), s)
        except ValueError:
            pass
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);',
                    lambda m: unichr(int(m.group(1), 16)), s)
        except ValueError:
            pass

    replace_re = replace_re or r'[^-a-z0-9]'
    replace_char = replace_char or '-'

    #translate to ascii
    if ascii:
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    if lower:
        s = s.lower()
    #replace unwanted characters
    s = re.sub(replace_re, replace_char, s)
    #remove redundant replace_chars
    s = re.sub('%s{2,}' % replace_char, replace_char, s).strip(replace_char)

    invalid = invalid or []
    if instance:
        lookup = extra_lookup or {}
        if not manager:
            manager = instance.__class__._default_manager

    slug, counter = s, 1
    while True:
        if slug in invalid:
            pass
        elif not instance:
            return slug
        else:
            lookup[slug_field] = slug
            qs = manager.filter(**lookup)
            if instance.pk:
                qs = qs.exclude(pk=instance.pk)
            if not qs.count():
                return slug
        slug = "%s-%s" % (s, counter)
        counter += 1

