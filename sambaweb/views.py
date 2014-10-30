# -*- encoding: utf-8 -*-
# Create your views here.
from django.conf import settings
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from sambaweb import forms
from sambaweb.models import User, HistPassword
from pysamba import PySamba
import smbpasswd
from django.utils.translation import ugettext_lazy as _
import os
import simplejson as json
from config import *

def changepasswd(request):
    username = request.session.get('username', None)
    if username:
        pysmb = PySamba()
        if request.method == 'POST':
            oldpasswd = request.REQUEST['oldpasswd']
            newpasswd = request.REQUEST['newpasswd']
            retpasswd = request.REQUEST['retpasswd']
            if newpasswd == retpasswd:
                if not(newpasswd == oldpasswd):
                    status, msg = pysmb.changePasswd(user, oldpasswd, newpasswd)
                    return render(request, 'sambaweb/changepasswd.html', {
                        'form': form,
                        'status': status,
                        'msg': msg,
                        })
                else:
                    status = False
                    msg = "新旧密码一样"
            else:
                status = False
                msg = "两次输入的密码不一致"
            return render(request, 'sambaweb/changepasswd.html', {
                        'form': form,
                        'status': status,
                        'msg': msg,
                        })
             
        else:
            return render(request, 'sambaweb/changepasswd.html', {
                        'form': form,
                        'status': status,
                        'msg': msg,
                        })
             
    else:
        return HttpResponseRedirect('/login')

def login(request):
    status = False
    msg = ''
    pysmb = PySamba()
    adminlist = pysmb.readConfig('admin')
    username = ''
    if request.method == 'POST':
        username = request.REQUEST['username'].split('@')[0]
        passwd = request.REQUEST['password']
            
        print username, passwd
    
        result = pysmb.handleLogin(username, passwd)
        print 'view-login:\n', result['status'], result['msg']
        if result['status']:
            request.session['username'] = username
            if username not in (adminlist.keys() or superadmin):
                return HttpResponseRedirect('/user?msg='+result['msg'])
            else:
                return HttpResponseRedirect('/share')
        else:
            form = forms.UserForm()
            print 'else here'
            return render(request, 'sambaweb/login.html', {
                'form': form,
                'err': result['msg'],
                })

   
    else:
        form = forms.UserForm()
        return render(request, 'sambaweb/login.html', {
            'form': form,
            'msg': msg,
            })

def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect('/login')

def list(request):
    pysmb = PySamba()
    adminlist = pysmb.readConfig('admin')
    #adminlist = superadmin
    page = 'list'
    username = request.session.get('username', None)
    if request.REQUEST.has_key('groupname'):
        groupname = request.REQUEST['groupname']
    else:
        groupname = ''
    #if username and (username in admin) and request.REQUEST.has_key('path') and request.REQUEST.has_key('groupname'):
    if username and (username in adminlist.keys()) and request.REQUEST.has_key('path') and request.REQUEST.has_key('groupname') and ((groupname in adminlist[username]) or (username in superadmin)):
        msg = ''
        err = ''
        if request.REQUEST.has_key('path'):
            path = request.REQUEST['path']
        if request.REQUEST.has_key('err'):
            err = request.REQUEST['err']
        if request.REQUEST.has_key('msg'):
            path = request.REQUEST['msg']
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        pathlist = path.split('/')
        pathlist = [ [a, groupname, '/'.join(pathlist[:pathlist.index(a)+1])] for a in pathlist ]
        filelist = pysmb.listDir(path, groupname)
        print filelist
        #filel = [os.path.join(sharefolder,f) for f in os.listdir(sharefolder)]
        #filelist = dict(zip([i for i in range(len(filel))], filel))
        #permitlist = dict(zip(filelist, [pysmb.listPermitUsers(f, 1) for f in filel ]))
        return render(request, 'sambaweb/list.html', {
            'filelist': filelist,
            'username': username,
            'admin': admin,
            'page':page,
            'pathlist': pathlist, 
            'path' : path,
            'groupname' : groupname,
            'err' : err,
            'msg' : msg, 
        })
    else:
        return HttpResponseRedirect('/login')


def share(request):
    pysmb = PySamba()
    adminlist = pysmb.readConfig('admin')
    admin = adminlist.keys()
    admingroups = pysmb.listAvailGroups()
    print 'admingroups:', admingroups
    username = request.session.get('username', None)
    page = 'share'
    if username and ((username in adminlist.keys() ) or username in superadmin):
        share = pysmb.listShare()
        print 'share:',share
        permitlist = adminlist[username]
        if username in superadmin:
            permitlist = admingroups
        print 'permitlist:',permitlist
        return render(request, 'sambaweb/index.html', {
            'sharelist': share,
            'username' : username,
            'admin' : admin,
            'page' : page,
            'permitlist' : permitlist,
        })
    else:
        return HttpResponseRedirect('/login')

def listusershare(request):
    msg = ''
    if request.REQUEST.has_key('msg'):
            msg = request.REQUEST['msg']
    username = request.session.get('username', None)
    if username:
        pysmb = PySamba()
        usershare = pysmb.listUserShare(username)
        return render(request, 'sambaweb/user.html', {
            'usershare' : usershare,
            'username' : username,
            'admin' : admin,
            'msg' : msg,
            })
    else:
        return HttpResponseRedirect('/login')

def listuserfile(request):
    username = request.session.get('username', None)
    if username and request.REQUEST.has_key('path') and request.REQUEST.has_key('groupname'):
        if request.REQUEST.has_key('path'):
            path = request.REQUEST['path']
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        pathlist = path.split('/')
        pathlist = [ [a, groupname, '/'.join(pathlist[:pathlist.index(a)+1])] for a in pathlist ]
        pysmb = PySamba()
        print username
        filelist = pysmb.listUserDir(path, username, groupname)
        return render(request, 'sambaweb/userlist.html', {
            'filelist': filelist,
            'username': username,
            'admin': admin,
            'pathlist':pathlist,
        })
    
    else:
        return HttpResponseRedirect('/login')


def addusertogroup(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()

    username = request.session.get('username', None)
    if username and (username in admin or username in superadmin):
        pysmb= PySamba()
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        
        if request.REQUEST.has_key('username'):
            username = request.REQUEST['username']
        result = pysmb.addUsertogroup(username, groupname)
        return HttpResponse(json.dumps(result), mimetype='application/json')
    else:
        return HttpResponseRedirect('/login')

def adduser(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()
    username = request.session.get('username', None)
    if username and ( username in admin or usernmae in superadmin):
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        if request.REQUEST.has_key('username'):
            user = request.REQUEST['username']
            result = pysmb.addUser(user, groupname)
            return HttpResponse(json.dumps(result), mimetype = 'application/json')
    else:
        return HttpResponseRedirect('/login')

def removeuserfromgroup(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()

    username = request.session.get('username', None)
    if username and (username in admin):
        pysmb= PySamba()
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        if request.REQUEST.has_key('username'):
            username = request.REQUEST['username']
        result = pysmb.removeUserfromgroup(username, groupname)
        return HttpResponse(json.dumps(result), mimetype='application/json')
    else:
        return HttpResponseRedirect('/login')



def listshareuser(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()

    username = request.session.get('username', None)
    if username and (username in admin):
        pysmb = PySamba()
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
            shareusers = pysmb.listUsers(groupname)
            print json.dumps(shareusers)
            return HttpResponse(json.dumps(shareusers), mimetype='application/json')
    else:
        return HttpResponseRedirect('/login')


def listavailuser(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()

    username = request.session.get('username', None)
    if username and (username in admin):
        pysmb = PySamba()
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
            shareusers = pysmb.listUsers(groupname)
            allusers = pysmb.listUsers()
            availuser = [ x for x in allusers if x not in shareusers]
            return HttpResponse(json.dumps(availuser), mimetype='applicaion/json')
    else:
        return HttpResponseRedirect('/login')



def permission(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()
    username = request.session.get('username', None)
    if username and (username in admin):
        pysmb = PySamba()
        #print request.REQUEST
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        if request.REQUEST.has_key('filename'):
            filename = request.REQUEST['filename']
            permission = pysmb.listPermitUsers(filename, groupname, 1)
            print json.dumps(permission)
            return HttpResponse(json.dumps(permission), mimetype='application/json')
        else:
            return HttpResponse('error')
    else:
        return HttpResponseRedirect('/login')


def changepermission(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()
    username = request.session.get('username', None)
    print username, admin
    if username and (username in admin):
        pysmb = PySamba()
        if request.REQUEST.has_key('filename'):
            filename = request.REQUEST['filename']
        else:
            return HttpResponse('error')
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        else:
            groupname = defaultgroup

        if request.REQUEST.has_key('user'):
            user = request.REQUEST['user']
        else:
            return HttpResponse('error')
        
        if request.REQUEST.has_key('permission'):
            permission = request.REQUEST['permission']
        else:
            return HttpResponse('error')
        try:     
            result = pysmb.changeSecondaryPermission(user, filename, groupname, permission)
            print 'view : %s' % result
            return HttpResponse(json.dumps(result), mimetype='application/json')
        except Exception,e:
            return HttpResponse(e)
    else:
        return HttpResponseRedirect('/login')

def addfolder(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()
    username = request.session.get('username', None)
    if username and (username in admin):
        foldername = ''
        path = ''
        groupname = ''
        if request.REQUEST.has_key('foldername'):
            foldername = request.REQUEST['foldername']
        if request.REQUEST.has_key('path'):
            path = request.REQUEST['path']
        if request.REQUEST.has_key('groupname'):
            groupname = request.REQUEST['groupname']
        try:
            print foldername, path, groupname
            pysmb = PySamba()
            result = pysmb.addFolder(foldername, path, groupname)
            print result
            return HttpResponse(json.dumps(result), mimetype='application/json')
        except Exception, e:
            return HttpResponse({'status':False,'msg':e})

def addshare(request):
    pysmb = PySamba()
    admin = pysmb.readConfig('admin').keys()
    username = request.session.get('username', None)
    if username and (username in admin):
        if request.REQUEST.has_key('sharename'):
            sharename = request.REQUEST['sharename']
            print 'Adding new share %s:' % (sharename) 
            pysmb = PySamba()
            result = pysmb.addShare(sharename)
        else:
            result = {'status':False, 'msg' :'not allowed'}
        print 'output from view: addshare\n', result
        return HttpResponse(json.dumps(result), mimetype='application/json')
    else:
        return HttpResponseRedirect('/login')
def addadmin(request):
    username = request.session.get('username', None)
    if username and (username in superadmin):
        if request.REQUEST.has_key('user'):
            user = request.REQUEST['user']
        if request.REQUEST.has_key('group'):
            group = request.REQUEST['group']
        pysmb = PySamba()
        result = pysmb.addAdmin(user, group)
        return HttpResponse(json.dumps(result), mimetype='application/json')

def deladmin(request):
    username = request.session.get('username', None)
    if username and (username in superadmin):
        if request.REQUEST.has_key('user'):
            user = request.REQUEST['user']
        if request.REQUEST.has_key('group'):
            group = request.REQUEST['group']
        pysmb = PySamba()
        result = pysmb.addAdmin(user, group)
        return HttpResponse(json.dumps(result), mimetype='application/json')

def listadmin(request):
    username = request.session.get('username',None)
    if username and (username in superadmin):
        pysmb = PySamba()
        adminlist = pysmb.readConfig('admin')
        admin = adminlist.keys()
        return render(request, 'sambaweb/adminlist.html', {
            'username': username,
            'adminlist':adminlist,
            'admin':admin,
        })
    
    else:
        return HttpResponseRedirect('/login')
def listavailgroups(request):
    username = request.session.get('username', None)
    if username and (username in superadmin):
        if request.REQUEST.has_key('user'):
            user = request.REQUEST['user']
        pysmb = PySamba()
        groups = pysmb.listAvailGroups(user)
        print groups
        return HttpResponse(json.dumps(groups), mimetype='application/json')

def listuserinformation(request):
    username = request.session.get('username', None)
    if username and ((username in superadmin) or (username in adminlist.keys())):
        if request.REQUEST.has_key('user'):
            user = request.REQUEST['user']
            pysmb = PySamba()
            result = pysmb.ldapLookup(user)
            print result
        else:
            result = {'status':False,'msg':'not allowed'}
        return HttpResponse(json.dumps(result), mimetype='application/json')
    else:
        return HttpResponseRedirect('/login')

def renamefolder(request):
    username = request.session.get('username', None)
    if username and ((username in superadmin) or (username in adminlist.keys())):
        path = ''
        filename = ''
        newname = ''
        if request.REQUEST.has_key('path') and request.REQUEST.has_key('filename') and request.REQUEST.has_key('newname'):
            path = request.REQUEST['path']
            filename = request.REQUEST['filename']
            newname = request.REQUEST['newname']
            pysmb = PySamba()
            result = pysmb.renameFolder(path, filename, newname)
        else:
            result = {'status': False, 'msg':'not allowed'}
        return HttpResponse(json.dumps(result), mimetype='application/json')

    else:
        return HttpResponseRedirect('login')
def renameshare(request):
    username = request.session.get('username', None)
    if username and ((username in superadmin) or (username in adminlist.keys())):
        if request.REQUEST.has_key('sharename') and request.REQUEST.has_key('newname'):
            sharename = request.REQUEST['sharename']
            newname = request.REQUEST['newname']
            pysmb = PySamba()
            result = pysmb.renameShare(sharename, newname)
        else:
            result = {'status': False, 'msg':'not allowed'}
        return HttpResponse(json.dumps(result), mimetype='application/json')

    else:
        return HttpResponseRedirect('login')
 
