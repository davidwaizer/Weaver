import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from utils.text import slugify


class ServerType(models.Model):
    slug = models.CharField(_('slug'), max_length=110, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=100 )
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        super(ServerType, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('server-type-detail', None, {'slug': self.slug})
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('server type')
        verbose_name_plural = _('server types')
    
SERVERCONFIGURATION_ICONS = (
            ('generic', _(u'Server')),
            ('proxy', _(u'Proxy / Loadbalancer')),
            ('web', _(u'Web Server')),
            ('database', _(u'Database Server')),
            ('queue', _(u'Queue Server')),
            ('email', _(u'Email Server')),
            ('cache', _(u'Cache Server')),
        )

class ServerConfiguration(models.Model):
    slug = models.CharField(_('slug'), max_length=110, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=100)
    base_image = models.CharField(_('AMI image'), max_length=100,)
    icon_style = models.CharField(_(u'display icon'), max_length=32, choices=SERVERCONFIGURATION_ICONS, default='generic')
    type = models.ForeignKey(ServerType, verbose_name=_(u'type'), related_name='server_configurations', blank=True, null=True, editable=False)
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        super(ServerConfiguration, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('server-type-detail', None, {'slug': self.slug})
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('server configuration')
        verbose_name_plural = _('server configurations')
    



class ServerCommand(models.Model):
    slug = models.CharField(_('slug'), max_length=110, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=100, )
    code = models.TextField(_('summary'), max_length=1000)
    order = models.IntegerField(_('order'))
    configuration = models.ForeignKey('ServerConfiguration')
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        super(ServerCommand, self).save(**kwargs)

    @permalink
    def get_absolute_url(self):
        return ('server-command-detail', None, {'slug': self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('command')
        verbose_name_plural = _('commands')
    


class ServerNode(models.Model):
    types = models.ManyToManyField(ServerType, name=_('server type'), related_name='server_nodes')
    public_ip = models.CharField(_('ip'), max_length=100, unique=True)
    private_ip = models.CharField(_('ip'), max_length=100, blank=True)
    public_dns = models.CharField(_('public dns'), max_length=256, blank=True)
    private_dns = models.CharField(_('private dns'), max_length=256, blank=True)
    locked = models.BooleanField(_('locked'), default=False)
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        super(ServerCommand, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('server-command-detail', None, {'slug': self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('command')
        verbose_name_plural = _('commands')

    
