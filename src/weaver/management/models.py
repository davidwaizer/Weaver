import datetime, os, linecache
from os.path import join as pjoin

from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from boto.ec2.connection import EC2Connection

from utils.text import slugify


class EC2Helper(object):
    @staticmethod
    def get_owner_id():
        """ 
        We have to get this information from the security group object,
        since the user will always have a security group.
        """
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        groups = conn.get_all_security_groups()
        if groups and len(groups) > 0:
            return groups[0].owner_id
        return None
    
    @staticmethod
    def get_all_instances():
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        reservations = conn.get_all_instances()
        instances = []
        for res in reservations:
            for instance in res.instances:
                instance.reservation = res
                instances.append(instance)
        return instances
    
    @staticmethod
    def get_images(image_ids):
        """ Gets the AMI images that match the image_ids supplied """
        if not image_ids:
            return []
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        return conn.get_all_images(image_ids=image_ids)
    
    @staticmethod
    def get_my_images():
        """ Returns the AMI images that I have created """
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        owner_id = EC2Helper.get_owner_id()
        
        if owner_id:
            return conn.get_all_images(owners=[owner_id,])
        else:
            return []
    
    @staticmethod
    def get_my_instance_images():
        """ Gets the AMI images that I have running (regardless of who they belong to) """
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        image_ids = set([x.image_id for x in EC2Helper.get_all_instances()])
        return EC2Helper.get_images(image_ids)
    
    @staticmethod
    def get_image(ami_name):
        """ Gets an arbitrary AMI image """
        conn = EC2Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        return conn.get_image(ami_name)
    

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


class ServerImageManager(models.Manager):
    
    def get_all(self):
        server_images = self.all()
        
        
        instances = EC2Helper.get_all_instances()
        
        # First get the amis that you created
        ami_images = EC2Helper.get_my_images()
        
        # Get all distinct amis.
        my_ami_ids = [x.id for x in ami_images]
        saved_ami_ids = [x.ami_id for x in server_images]
        instance_ami_ids = [x.image_id for x in instances]
        
        # Next, we need to fetch the AMI data from AWS
        # for the AMIs that we don't already have.
        all_ami_ids = set(my_ami_ids + saved_ami_ids + instance_ami_ids)
        needed_ami_ids = all_ami_ids - set(my_ami_ids)
        
        # Add the amis that we dont have
        ami_images = ami_images + EC2Helper.get_images(list(needed_ami_ids))
        
        all_server_images = []
        
        for ami in ami_images:
            
            matches = [x for x in server_images if x.ami_id == ami.id]
            server_image = matches[0] if matches else None
            
            if not server_image:
                server_image = ServerImage(ami=ami)
            else:
                server_image.ami = ami
            
            if not server_image.name:
                server_image.name = ami.name if ami.name else ""
            
            instance_count = len([x for x in instances if x.image_id == ami.id])
            server_image.instance_count = instance_count
            all_server_images.append(server_image)
        
        return all_server_images
        
        
        

class ServerImage(models.Model):
    _cached_ami = None
    instance_count = 0
    name = models.CharField(_('name'), max_length=100, blank=True, null=True)
    ami_id = models.CharField(_('AMI'), max_length=100, unique=True)
    icon_style = models.CharField(_(u'display icon'), max_length=32, choices=SERVERCONFIGURATION_ICONS, default='generic')
    
    objects = ServerImageManager()
    
    def __init__(self, *args, **kwargs):
        self._cached_ami = kwargs.pop('ami', None)
        if self._cached_ami:
            self.ami_id = self._cached_ami.id
        
        self.instance_count = kwargs.pop('instance_count', 0)
        super(ServerImage, self).__init__(*args, **kwargs)
    
    def _get_ami(self):
        """ Gets the underlying ami """
        if not self._cached_ami and ami_id:
            self._cached_ami = EC2Helper.get_image(self.ami_id)
        return self._cached_ami
        
    def _set_ami(self, ami):
        """ Sets the underlying ami """
        self._cached_ami = ami
    
    ami = property(_get_ami, _set_ami)
    
    #def save(self, **kwargs):
    #    if not self.ami_id:
    #        raise Exception('The AMI id needs to be specified in order to save.')
    #    super(ServerImage, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('serverconfiguration-edit', None, {'ami_id': self.ami_id})
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('server image')
        verbose_name_plural = _('server images')
    



class ServerCommand(models.Model):
    slug = models.CharField(_('slug'), max_length=110, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=100, )
    code = models.TextField(_('summary'), max_length=1000)
    order = models.IntegerField(_('order'))
    configuration = models.ForeignKey('ServerImage')
    
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
    

class Server(models.Model):
    slug = models.CharField(_('slug'), max_length=110, editable=False, unique=True)
    configuration = models.ForeignKey(ServerImage, name=_('server type'), related_name='server_nodes')
    instance_id = models.CharField(_('instance_id'), max_length=100, unique=True)
    public_dns = models.CharField(_('public dns'), max_length=255, unique=True, editable=False)
    private_dns = models.CharField(_('private dns'), max_length=255, unique=True, editable=False)
    
    def save(self, **kwargs):
        if not self.id:
            self.slug = slugify(self.public_dns, instance=self)
        super(ServerNode, self).save(**kwargs)
    
    @permalink
    def get_absolute_url(self):
        return ('server-edit', None, {'slug': self.slug})
        
    def __unicode__(self):
        return self.public_dns

    class Meta:
        verbose_name = _('server instance')
        verbose_name_plural = _('server instance')


class Site(models.Model):
    slug = models.CharField(_('slug'), max_length=255, editable=False, unique=True)
    name = models.CharField(_('name'), max_length=255)
    url = models.URLField(_('url'), max_length=255, verify_exists=False)
    configuration = models.ForeignKey(ServerImage, verbose_name=_('deployment configuration'), related_name='sites')
    servers = models.ManyToManyField(Server, related_name='sites', null=True, blank=True)
    
    
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

