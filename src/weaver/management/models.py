import datetime, os, linecache
from os.path import join as pjoin

from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from boto.ec2.connection import EC2Connection

from utils.text import slugify

    
class AmiManager(object):
    @staticmethod
    def get_all():
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        return conn.get_all_images()


class KeyPairManager(object):
    @staticmethod
    def get_ec2_public_keys():
        """
        Returns the public SSH keys that are on EC2.
        """
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        return conn.get_all_key_pairs()
    
    @staticmethod
    def get_local_private_keys():
        """
        Returns the local private keys used to connect to EC2 by looking at all files
        in all directories of your SSH_KEYS_DIR setting.
        """
        keys = []
        for root, dirs, files in os.walk(settings.SSH_KEYS_DIR, topdown=False):
            for file_name in files:
                
                if file_name != 'known_hosts':
                    path = pjoin(root, file_name)
                    # For lack of a better way to do this,
                    # we are going to open the file, read
                    # the first line.
                    file = open(path, 'r')
                    first_line = file.readline()
                    file.close()
                
                    if first_line and first_line.find('-----BEGIN RSA PRIVATE KEY-----') > -1:
                        keys.append({'name': file_name, 'path': path })
        return keys


SERVERCONFIGURATION_ICONS = (
            ('generic', _(u'Server')),
            ('proxy', _(u'Proxy / Loadbalancer')),
            ('web', _(u'Web Server')),
            ('database', _(u'Database Server')),
            ('queue', _(u'Queue Server')),
            ('email', _(u'Email Server')),
            ('cache', _(u'Cache Server')),
        )


SERVERCONFIGURATION_PUBLIC_KEYS = ((x.name, x.name) for x in KeyPairManager.get_ec2_public_keys())

class ServerConfiguration(models.Model):
    slug = models.CharField(_('slug'), max_length=110, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=100)
    base_image = models.CharField(_('AMI image'), max_length=100,)
    icon_style = models.CharField(_(u'display icon'), max_length=32, choices=SERVERCONFIGURATION_ICONS, default='generic')
    public_key = models.CharField(_(u'public SSH key'), max_length=32, choices=SERVERCONFIGURATION_PUBLIC_KEYS)
    base_image_architecture = models.CharField(_(u'AMI architecture'), max_length=10, blank=True, null=True)
    base_image_name = models.CharField(_(u'AMI name'), max_length=255, blank=True, null=True)
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        ami = conn.get_image(self.base_image)
        self.base_image_architecture = ami.architecture
        self.base_image_name = ami.name
        super(ServerConfiguration, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('serverconfiguration-edit', None, {'slug': self.slug})
    
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
        return ('servercommand-edit', None, {'slug': self.slug})

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('command')
        verbose_name_plural = _('commands')
    


class ServerNode(models.Model):
    configuration = models.ForeignKey(ServerConfiguration, name=_('server type'), related_name='server_nodes')
    public_ip = models.CharField(_('ip'), max_length=100, unique=True)
    private_ip = models.CharField(_('ip'), max_length=100, blank=True)
    public_dns = models.CharField(_('public dns'), max_length=255, blank=True)
    private_dns = models.CharField(_('private dns'), max_length=255, blank=True)
    locked = models.BooleanField(_('locked'), default=False)
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        super(ServerNode, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('server-command-detail', None, {'slug': self.slug})

    def __unicode__(self):
        return self.public_ip

    class Meta:
        verbose_name = _('command')
        verbose_name_plural = _('commands')


class Site(models.Model):
    slug = models.CharField(_('slug'), max_length=255, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=255)
    url = models.URLField(_('url'), max_length=255, verify_exists=False)
    configuration = models.ForeignKey(ServerConfiguration, verbose_name=_('deployment configuration'), related_name='sites')
    servers = models.ManyToManyField(ServerNode, related_name='sites', null=True, blank=True)
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.name, instance=self)
        super(Site, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('site-edit', None, {'slug': self.slug})
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('site')
        verbose_name_plural = _('sites')