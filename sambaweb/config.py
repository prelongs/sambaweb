#!/bin/env python
#-- coding:utf-8 --

#share = [
#        [1,'2014世界杯项目', '2014世界杯项目','sambagroup1'],
#        [2,'2015测试项目', '2015','sambagroup2'],
#        [3,'2016测试项目', '2016','sambagroup3'],
#        ]
global share
global groupname
global sharename
global num
share = []
groupname = []
sharename = []
num = []

rootpath = '/data0/SHARE/'

configfile = '/etc/samba/sharelist.conf'
sambashareconfig = '/etc/samba/smbshare.conf'
sambaconfig = '/etc/samba/smb.conf'
configadmin = '/etc/samba/adminlist.conf'

superadmin = ['gaoyang1', 'chenwei7']

adminlist = {
        'tanlong':['sambagroup2','sambagroup3','sambagroup4','sambagroup5','sambagroup6','sambagroup7'],
        'baoliang1':['sambagroup3'],
        'chenwei7':['sambagroup1']
        }
admin = adminlist.keys()
defaultgroup = 'sambausers'
defaultpasswd = '456123'
SMB_DB = '/etc/samba/db/smbpasswd'
