from django.conf.urls import patterns, url, include
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
    url(r'^$', 'sambaweb.views.login'),
    url(r'^share$', 'sambaweb.views.share'),
    url(r'^user$', 'sambaweb.views.listusershare'),
    url(r'^listavailuser$', 'sambaweb.views.listavailuser'),
    url(r'^listshareuser$', 'sambaweb.views.listshareuser'),
    url(r'^addusertogroup$', 'sambaweb.views.addusertogroup'),
    url(r'^removeuserfromgroup$', 'sambaweb.views.removeuserfromgroup'),
    url(r'^list$', 'sambaweb.views.list'),
    url(r'^userfile$', 'sambaweb.views.listuserfile'),
    url(r'^login$', 'sambaweb.views.login'),
    url(r'^logout$', 'sambaweb.views.logout'),
    url(r'^changepermission$', 'sambaweb.views.changepermission'),
    url(r'^permission$', 'sambaweb.views.permission'),
    url(r'^addfolder$', 'sambaweb.views.addfolder'),
    url(r'^addshare$', 'sambaweb.views.addshare'),
    url(r'^addadmin$', 'sambaweb.views.addadmin'),
    url(r'^adduser$', 'sambaweb.views.adduser'),
    url(r'^deladmin$', 'sambaweb.views.deladmin'),
    url(r'^listadmin$', 'sambaweb.views.listadmin'),
    url(r'^listavailgroups$', 'sambaweb.views.listavailgroups'),
    url(r'^listuserinformation$', 'sambaweb.views.listuserinformation'),
    url(r'^renamefolder$', 'sambaweb.views.renamefolder'),
    url(r'^renameshare$', 'sambaweb.views.renameshare'),
)
