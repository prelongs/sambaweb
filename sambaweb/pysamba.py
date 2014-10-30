# -*- encoding: utf-8 -*-
#!/usr/bin/env python
from django.conf import settings
from multiprocessing import Process, Value
import smbpasswd
import subprocess
import ldap
import pwd
import grp
import os
import re
from config import *
import smtplib
from email.mime.text import MIMEText
from random import choice
import string
import time


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class PySamba(object):
    """Main class designed for samba web access control"""



    def readUid(self, user):
        '''
	Read user uid
        '''
        try:
            return pwd.getpwnam(user).pw_uid
        except KeyError:
            return -1

    def readGid(self, groupname=defaultgroup):
        '''
	Read group gid
	'''
	try:
            groupstruct = grp.getgrnam(groupname)
            gid = groupstruct[2]
            return gid
        except Exception, e:
            return e


    def log(self, title, msg):
	'''
	Log function
	'''

        now = time.ctime()
        f = open('/var/log/samba/msg.log', 'a')
        f.write(now+'  '+title+':'+str(msg)+'\n')
        f.close

    def saveUser(self, user, password):
	'''
	modify samba user's password
	'''
        try:
            cmd = "/bin/echo -e '%s\n%s' | (/usr/bin/sudo /usr/bin/smbpasswd -s %s)" % (password, password, user)
            self.log('saveUser',cmd)
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            if not stderr_value:
                return True
            else:
                return False
            self.log('saveUser',  stdout_value + stderr_value)
        except Exception, e:
            self.log('saveUser exception', e)
            return False

    def changePasswd(self, user, oldpass, password):
	'''
	check & use self.saveUser to modify user's password
	'''
        status = False
        try:
            with open(SMB_DB) as file:
                lines = file.readlines()
            for line in lines:
                user_info = line.strip().split(':')
                if user in user_info:
                    if smbpasswd.nthash(oldpass) in user_info:
                        if self.saveUser(user, password):
                            status = True
                            msg = ("Changed successfully")
                            break
                        else:
                            msg = ("Failed change")
                            break
                    else:
                        msg = ("Wrong password")
                        break
            return status, msg
        except Exception, e:
            return status, e

    def userInSamba(self, user):
	'''
	Test is a user exists in samba user system
	'''
        try:
            with open(SMB_DB, 'r') as file:
                lines = file.readlines()
            for line in lines:
                user_info = line.strip().split(':')
                if user in user_info:
                    self.log('userInSamba', '%s exists in samba' % user)
                    return (True,'User exists in samba')
            self.log('userInSamba', '%s not exists in samba' % user)
            return (False,'User not exists in samba')
        except Exception, e:
            self.log('userInSamba exception', e)
            return (False, e)

    def listPermitUsers(self, dirname, groupname, flag):
	'''
	List user permission of a given dir
	'''
        dirname = os.path.join(rootpath, dirname) 
        #flag = 0 firstdary directory
        if flag == 0:
            if folder.has_key(dirname):
                groupname = folder[dirname]
                return self.listUsers(groupname)
            else:
                return []

        # secondary directory
        else :
            #allusers = self.listUsers(defaultgroup)
            allusers = self.listUsers(groupname)
            permission = {}
            for user in allusers:
                permit = [0, 0]
                for handle in [1,2]:
                    print handle
                    p = self.readSecondaryPermission(user, groupname, dirname, handle)
                    if p:
                        permit[handle-1] = 1

                #if permit[0] or permit[1]:
                #    permission[user] = permit
                permission[user] = permit
            return permission



    def listUsers(self, groupname=defaultgroup):
	'''
	List users of a given group name
	'''
        try:
            groupstruct = grp.getgrnam(groupname)
            users = groupstruct[3]
            return users
        
        except Exception, e:
            return e

    def readGid(self, groupname=defaultgroup):
        try:
            groupstruct = grp.getgrnam(groupname)
            gid = groupstruct[2]
            return gid
        except Exception, e:
            return e

    def addUsertogroup(self, user, groupname):
	'''
	Add user to a given group
	'''
        if user in self.listUsers(groupname):
            return False, '用户已经拥有此组权限'
        else:
            try:
                cmd = "/usr/sbin/usermod -a -G %s %s" % (groupname, user)
                self.log('addUsertogroup', cmd)
                proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                stdout_value, stderr_value = proc.communicate()
                if not stderr_value:
                    killsession_msg = self.killSession(user)
                    #msg = _("Add permission successful!")
                    return True,'赋予用户权限成功'
                else:
                    #msg = _("Add permission failed!")
                    return False, stderr_value
            except Exception, e:
                self.log('addUsertogroup', e)
                return False, e
    
    def killSession(self, user):
	'''
	Kill a user session of samba server
	'''
        try:
            cmd = "smbstatus -p"
            proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            print stdout_value
            for line in  stdout_value.split('\n'):
                if re.search('^[0-9].*',line):
                    pid =  line.split(' ')[0]
                    os.kill(int(pid), 9)
                    print '%s killed for user :%s' % (pid, user)
            return True
        except Exception, e:
            self.log('killSession', e)
            return False

    def removeUserfromgroup(self, user, groupname):
	'''
	Remove user from a given group
	'''
        try:
            cmd = "/usr/bin/gpasswd -d %s %s" % (user, groupname)
            self.log('removeUserformgroup', cmd)
            print cmd
            proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            print stderr_value
            if not stderr_value:
                killsession_msg = self.killSession(user)
                self.log('removeUserfromgroup', killsession_msg)
                try:
                    grouppath = os.path.join(rootpath, self.listPathwithgroup(groupname))
                    cmd = "/usr/bin/setfacl -R -x u:%s %s" % (user, grouppath)
                    self.log('removeUserfromgroup', cmd)
                    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    stdout_value, stderr_value = proc.communicate()
                    if not stderr_value:
                        print 'remove permission ok'
                except Exception, e:
                    self.log('removeUserfromgroup', e)
                    print e
                return 'remove user from group success'
            else:
                return stderr_value
        except Exception, e:
            self.log('removeUserfromgroup', e)
            return ''
       
    def readSecondaryPermission(self, user, groupname, dirname, handle):
        '''
        Read further permission use os.access/os.stat
        @user username
        @dirname dir/file name to be checked
        @handle operations to be checked:
        '''
        ret = {
                1:os.R_OK,
                2:os.W_OK,
                3:os.X_OK
                }
        uid = self.readUid(user)
        self.log('readSecondaryPermission', 'uid is %s' % uid)
        gid = self.readGid(groupname)
        self.log('readSecondaryPermission', 'gid is %s' % gid)
        if uid > -1:
            result = Value('d', 0)
            p = Process(target=self.readPermission, args=(dirname, uid, gid, ret, handle, result))
            p.start()
            p.join()
            return result.value


    def readPermission(self, dirname, uid, gid, ret, handle, result):
        '''
	Read user permission use os.access
	'''
	os.setgroups([gid])
        os.setgid(gid)
        os.setuid(uid)
        result.value = os.access(dirname, ret[handle])
                
    def changeSecondaryPermission(self, user, filename, groupname, permission):
        '''
        Add further permission to a secondary directory or file
        '''
        filename = os.path.join(rootpath, filename)
        print user, filename, groupname, permission
        try:
            gid = self.readGid(groupname)
        except Exception, e:
            print e
        print gid
        if groupname != defaultgroup:
            fileuid = os.stat(filename).st_gid
            if fileuid != gid:
                cmd = "chown root:%s '%s'; chmod 0000 '%s'" % (groupname, filename, filename)
                try:
                    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                    stdout_value, stderr_value = proc.communicate()
                    if not stderr_value:
                        print 'change owner ok'
                    else:
                        print stderr_value
                except Exception, e:
                    print e
        if len(permission) == 0:
            cmd = "/usr/bin/setfacl -x u:%s '%s'" % (user, filename)
        else:
            cmd = "/usr/bin/setfacl -R -d -m u:%s:%sx '%s';" % (user, permission, filename)
            cmd += "/usr/bin/setfacl -R  -m u:%s:%sx '%s';" % (user, permission, filename)
            cmd += "/usr/bin/setfacl -R -d -m m::rwx '%s'" % (filename)
        print cmd
        try:
            proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            if not stderr_value:
                return True
            else:
                return stderr_value
        except Exception, e:
            return e

    def listShare(self):
	'''
	List share from the samba share configure
	'''
        share = self.readConfig('share')
        return share 

    def listDir(self, filepath, groupname):
	'''
	List dir of a given dir
	'''
        path = os.path.join(rootpath, filepath)
        filelist = []
        if os.path.exists(path):
            if not os.path.isfile(path):
                n = 0
                tmplist = os.listdir(path)
                tmplist.sort()
                for names in [os.path.join(filepath,f) for f in tmplist if f[0] != '.']:
                    if os.path.isfile(os.path.join(rootpath, names)):
                        isfile = 1
                    else:
                        isfile = 0
                    filename = names.split('/')[-1]
                    filelist.append([n, isfile, filename, names, groupname])
                    n += 1
        return filelist
   
    def listUserDir(self, filepath, user, groupname):
	'''
	List a user's permitted dir
	'''
        path = os.path.join(rootpath, filepath)
        filelist = []
        if os.path.exists(path):
            if not os.path.isfile(path):
                n = 0
                tmplist = os.listdir(path)
                tmplist.sort()
                for names in [os.path.join(filepath,f) for f in tmplist if f[0] != '.']:
                    if os.path.isfile(os.path.join(rootpath, names)):
                        isfile = 1
                    else:
                        isfile = 0
                    filename = names.split('/')[-1]
                    status, permission = self.hasPermission(user, groupname, os.path.join(rootpath, names))
                    if status:
                        filelist.append([n, isfile, filename, names, groupname, permission[0], permission[1]])
                        n += 1
        return filelist
    
    def hasPermission(self, user, groupname, dirname):
	'''
	Test whether a user has permission to a given dir
	'''
        permit = [0, 0]
        for handle in [1,2]:
            print user, groupname, dirname
            p = self.readSecondaryPermission(user, groupname, dirname, handle)
            if p:
                permit[handle-1] = 1
        if permit[0] or permit[1]:
            print permit
            return (True, permit)
        else:
            return (False, permit)

    def listUserShare(self, user):
	'''
	List a user's share
	'''
        result = []
        share = self.readConfig('share')
        for num, sharename, groupname in share:
            if user in self.listUsers(groupname):
                result.append([sharename,  groupname])
        return result


    def listAdminGroups(self):
	'''
	List a admin's handleable groups
	TODO: change a admin's handleable groups
	'''
        groups = []
        admin = self.readConfig('admin')
        for user, group in admin.items():
            groups.extend(group)
        return {}.fromkeys(groups).keys()


    def listAvailGroups(self):
	'''
	List all groups
	'''
        adminlist = self.readConfig('group')
        print adminlist
        return adminlist
        #if adminlist.has_key(user):
        #    group = adminlist[user]
        #    return [ g for g in self.listAdminGroups() if g not in group]
    def listPathwithgroup(self, groupname):
        result = {}
        share = self.readConfig('share')
        for num , sharename, groupname in share:
            result[groupname] = sharename
        return result[groupname]

    def ldapLookup(self, user):
        try:
            ldap_conn = ldap.initialize("")
            ldap_conn.set_option(ldap.OPT_REFERRALS,0)
            ldap_conn.simple_bind_s("" , "")
            retrieveAttributes=['mail','telephoneNumber','mobile','whenCreated','initials']
            find_object = "userPrincipalName="+user+"@"
            res = ldap_conn.search_s("",ldap.SCOPE_SUBTREE,find_object,retrieveAttributes)
            print 'res is :\n', res
            if len(res) > 1:
                if len(res[0]) > 1:
                    if res[0][0] != None:
                        detail = res[0][0].replace('OU=','').split(',SINA,')[0]
                        if res[0][1].has_key('mail'):
                            detail += '<br>E-mail:'+res[0][1]['mail'][0]
                        print 'detail:%s' % detail
                        return {'status':True, 'msg':detail}
                    else :
                        return {'status':False, 'msg':'用户不存在!'}
                else:
                    return {'status':False, 'msg':'用户不存在!'}
            else:
                return {'status':False, 'msg':'用户不存在!'}
        except Exception, e:
            return {'status':False, 'msg':e}


    def ldapAuth(self, user, passwd):
        #return True, 'ldap登陆成功'
        ldap_conn = ldap.initialize("")
        ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
        try:
            ldap_conn.simple_bind_s(user, passwd)
            result = ldap_conn.search_s('', ldap.SCOPE_SUBTREE, '' )
        except ldap.INVALID_CREDENTIALS:
            return (False, '您的用户名/密码错误，请检查后重试')
        print 'True, ldap验证成功'
        return (True, 'ldap验证成功')
   
    def sambaAuth(self, user, passwd):
        status = False
        try:
            with open(SMB_DB) as file:
                lines = file.readlines()
            for line in lines:
                user_info = line.strip().split(':')
                if user in user_info:
                    if smbpasswd.nthash(passwd) in user_info:
                        return (True, '登陆成功')
                    else:
                        return (False, '您的用户名/密码错误，请检查后重试')
            return (False, '您还没有登陆过本系统，请使用您的邮箱密码登陆')
        except Exception, e:
            return (False, e)
    
    def sambaExist(self, user):
        try:
            with open( SMB_DB ) as file:
                lines = file.readlines()
            for line in lines:
                user_info = line.strip().split(':')
                if user in user_info:
                    return True
                else:
                    return False
        except Exception,e:
            return False
    def addSysUser(self, user):
        '''
        Add user to the system without a password
        '''
        is_exist = False
        addsys_ok = True
        #userlist = [x.pw_name for x in pwd.getpwall()] 
        try:
            pwd.getpwnam(user)
            is_exist = True
        except KeyError:
            is_exist = False

        if(is_exist == False):
            try:
                cmd = "/usr/sbin/useradd -M -G %s -s /sbin/nologin -c 'Samba Users' %s" % (defaultgroup, user)
                print cmd
                proc = subprocess.Popen(cmd, shell= True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_value, stderr_value = proc.communicate()
                if not stderr_value:
                    return is_exist, addsys_ok, '添加系统用户成功'
                else:
                    addsys_ok = False
                    return is_exist, addsys_ok, stderr_value
            
            except Exception, e:
                addsys_ok = False
                return is_exist, addsys_ok, stderr_value
        else :
            addsys_ok = False
            if not user in self.listUsers():
                is_exist = False
                addsys_ok = True
                status, msg = self.addUsertogroup( user, defaultgroup)
                if not status:
                    return is_exist, False, msg
            return is_exist, addsys_ok, '用户已存在' 

    def addSambaUser(self, user):
        '''
        Add sys user to samba
        '''
        addsamba_ok = 1
        try:
            cmd = "/usr/bin/smbpasswd -a -n %s" % (user)
            print cmd
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            if not stderr_value:
                return addsamba_ok, '加入用户到samba成功'
            else:
                addsamba_ok = 0
                return addsamba_ok, stderr_value
        
        except Exception, e:
            addsamba_ok = 0
            return addsamba_ok, e

    def addSambaPasswd(self, user, passwd):
        '''
        Modify samba user's passwd as defined
        '''
        sambapasswd_ok = 1
        try:
            cmd = "/bin/echo -e '%s\n%s' | (/usr/bin/smbpasswd -s %s)" % (passwd, passwd, user)
            print cmd
            proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_value , stderr_value = proc.communicate()
            if not stderr_value:
                return sambapasswd_ok, '添加samba账户密码成功'
            else:
                sambapasswd_ok = 0
                return sambapasswd_ok, stderr_value
        except Exception, e:
            sambapasswd_ok = 0
            return sambapasswd_ok, e
    
    def handleLogin(self, user, passwd):
	'''
	Handle login logit
	'''
        try:
            status, msg = self.ldapAuth(user, passwd)
            print 'ldap_status = %s,  ldap_msg = %s' % (status, msg)
            self.log('handleLogin', 'ldap_status = %s, ldap_msg = %s' % (status, msg))
            if status:
                status_insamba, msg_insamba = self.userInSamba(user)
                self.log('handleLogin', 'status_insamba = %s, msg_insamba = %s' % (status_insamba, msg_insamba))
                if status_insamba:
                    status_sambapasswd, msg_sambapasswd = self.addSambaPasswd(user, passwd)
                    self.log('handleLogin', 'sambapasswd_status = %s, sambapasswd_msg = %s' % (status_sambapasswd, msg_sambapasswd))
                    if status_sambapasswd:
                        return {'status': True, 'msg':'登陆成功'}
                    else:
                        return {'status': False, 'msg': msg_sambapasswd + '请再试一次'}
                else:
                    return {'status': False, 'msg': '您没有权限登陆本系统，请联系管理员确认'}
            else:
                return {'status': False, 'msg': msg}
        except Exception, e:
            self.log('handleLogin', e)
            return {'status': False, 'msg': '登陆失败!'}

    def addFolder(self, foldername, path, groupname):
	'''
	Add folder
	'''
        ok = True
        fail = False
        print 'foldername is :%s' % foldername
        print 'path is :%s' % path
        print 'groupname is :%s' % groupname
        fullpath = os.path.join(rootpath, path)
        folderpath = os.path.join(fullpath, foldername)
        if os.path.exists(fullpath):
            if not os.path.exists(folderpath):
                try:
                    cmd = "mkdir '%s'; chown root:%s '%s';" % (folderpath, groupname, folderpath)
                    if len(path.split('/')) == 1:
                        cmd += "chmod 000 '%s';" % folderpath
                    #cmd += "/usr/bin/setfacl -R -d -m g:superadmin:rwx '%s';" % (folderpath)
                    #cmd += "/usr/bin/setfacl -R  -m g:superadmin:rwx '%s';" % (folderpath)
                    #cmd += "/usr/bin/setfacl -R -d -m m::rwx '%s'" % (folderpath)
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout_value, stderr_value = proc.communicate()
                    print cmd, stderr_value
                    if not stderr_value:
                        if len(path.split('/')) == 1:
                            for admin in superadmin:
                                self.changeSecondaryPermission(admin, folderpath, groupname, 'rw')
                                print 'changeSecondaryPermission: %s, %s, %s' % (admin, folderpath, groupname) 
                        return {'status':ok,'msg':'新建文件夹成功'}
                    else:
                        return {'status':fail, 'msg':stderr_value}
                except Exception, e:
                    return {'status':fail,'msg':e}
            else:
                return {'status':fail, 'msg':'目标文件夹已存在'}
        else :
            return {'status':fail, 'msg':'父级目标不存在'}
    
    def readConfig(self, name):
	'''
	Read configure files
	'''
        if name == 'share':
            del groupname[:]
            del sharename[:]
            del num[:]
            with open(configfile) as f:
                for line in f.readlines():
                    if len(line.strip().split(',')) > 1:
                        n, s, g = line.strip().split(',')
                        groupname.append(g)
                        sharename.append(s)
                        num.append(n)
            share = zip(num, sharename, groupname)
            return share
        if name == 'group':
            del groupname[:]
            with open(configfile) as f:
                for line in f.readlines():
                    if len(line.strip().split(',')) > 1:
                        n, s, g = line.strip().split(',')
                        groupname.append(g)
            return groupname
        
        if name == 'admin':
            admin = {}
            with open(configadmin) as f:
                for line in f.readlines():
                    if len(line.strip().split(':')) > 1:
                        user = line.strip().split(':')[0]
                        groups = line.strip().split(':')[1].split(',')
                        admin[user] = groups
            return admin
    
    def addAdmin(self, user, group):
	'''
	Add a admin user
	'''
        admin = self.readConfig('admin')
        if admin.has_key(user) and group not in admin[user]:
            admin[user].append(group)
        elif not admin.has_key(user):
            admin[user] = [group]
        print 'adminlist is :', admin
        with open(configadmin, "w") as f:
            for user in admin.keys():
                f.write(user+":")
                f.write(",".join(admin[user]))
                f.write("\n")
    
    def delAdmin(self, user, group):
	'''
	Delete a admin user
	'''
        admin = self.readConfig('admin')
        if admin.has_key(user) and group in admin[user]:
            admin[user].remove(group)
            if len(admin[user]) == 0:
                del admin[user]
        
        print 'adminlist is :', admin
        with open(configadmin, "w") as f:
            for user in admin.keys():
                f.write(user+":")
                f.write(",".join(admin[user]))
                f.write("\n")


    def addShare(self, share):
	'''
	Add a share
	'''
        sharename = []
        groupname = []
        num = []
        sharelist = self.readConfig('share')
        for n, s, g in sharelist:
            num.append(int(n))
            sharename.append(s)
            groupname.append(g)
        if len(num) >= 1:
            maxitem = int(max(num))
        else:
            maxitem = 0
        print 'maxitem is %s' % maxitem
        sharepath = os.path.join(rootpath, share)
        group = 'sambagroup%s' % (maxitem+1)
        print 'new group:\n',group
        try:
            cmd = 'groupadd %s;' % (group)
            for admin in superadmin:
                cmd += "/usr/sbin/usermod -a -G %s %s;" % (group, admin)
            print cmd
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
        except Exception,e:
            print e
        cmd = "mkdir '%s' && chown root:%s '%s' && chmod 050 '%s';" % (sharepath, group, sharepath, sharepath)
        #cmd += "cd /data0/share/ ; /usr/bin/getfacl default |  setfacl --set-file=- '%s';" % sharepath
        #cmd += "/usr/bin/setfacl -d -m g::--- '%s'" % sharepath
        print cmd
        #cmd += "/usr/bin/setfacl -R -d -m g::--- '%s';" % (sharepath)
        #cmd += "/usr/bin/setfacl -R -d -m g:superadmin:rwx '%s';" % (sharepath)
        #cmd += "/usr/bin/setfacl -R  -m g:superadmin:rwx '%s';" % (sharepath)
        #cmd += "/usr/bin/setfacl -R -d -m m::rwx '%s';" % (sharepath)

        try:    
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            print 'Create new share directory output is:\n',stdout_value, stderr_value
            if not stderr_value:
                groupname.append(group)
                sharename.append(share)
                num.append(maxitem+1)
                print 'groupname is :',groupname
                print 'sharename is :',sharename
                print 'num is :',num
                sharelist = zip(map(str,num), sharename, groupname)
                status, msg = self.updateConfig(sharelist)
                print 'UpdateConfig output is :\n', status, msg
                if status:
                    cmd = '/usr/bin/smbcontrol smbd reload-config'
                    try:
                        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout_value, stderr_value = proc.communicate()
                        if not stderr_value:
                            print 'Reload smbd outpout is:\n', stdout_value, stderr_value
                        else:
                            return {'status':False, 'msg':stderr_value}
                    except Exception,e:
                        return {'status':False, 'msg':e}
                else:
                    return {'status':False, 'msg':msg}

                return {'status':True,'msg':"创建共享文件夹成功"}
            else:
                return {'status':False, 'msg':stderr_value}
        except Exception, e:
            return {'status':False,'msg':e}
   
    def renameShare(self, share, new):
	'''
	Rename a share
	'''
        sharename = []
        groupname = []
        num = []
        sharelist = self.readConfig('share')
        print 'oldsharelist is :\n', sharelist
        for n, s, g in sharelist:
            num.append(int(n))
            sharename.append(s)
            groupname.append(g)
        sharename[sharename.index(share)] = new
        newsharelist = zip(map(str,num), sharename, groupname)
        print 'newsharelist is :\n',newsharelist
        fullpath = os.path.join(rootpath, share)
        newfullpath = os.path.join(rootpath, new)
        try:
            cmd = "mv '%s' '%s'" % (fullpath, newfullpath)
            print cmd
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = proc.communicate()
            if not stderr_value:
                status, msg = self.updateConfig(newsharelist)
                if status:
                    try:
                        cmd = "/usr/bin/smbcontrol smbd reload-config"
                        print cmd
                        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout_value, stderr_value = proc.communicate()
                        print 'updateConfig out is :\n', stdout_value, stderr_value
                        if not stderr_value:
                            return {'status':True, 'msg': '改名成功'}
                        else:
                            return {'status': False, 'msg': stderr_vallue}
                    except Exception, e:
                        return {'status':False, 'msg':e}
                else:
                    return {'status': False, 'msg': msg}
            else:
                return {'status': False, 'msg': stderr_value}
        except Exception, e:
            return {'status': False, 'msg':e}
                
    def addUser(self, user, group):
	'''
	Add user to the /etc/passwd & sambauser configure files
	'''
        passwd = defaultpasswd
        randompass = ''.join([choice(string.ascii_letters+string.digits) for i in range(10)])
        if user not in self.listUsers():
            try:
                is_exists, status_addsys, msg_addsys = self.addSysUser(user)
                if status_addsys:
                    try:
                        addsamba_ok, addsamba_result = self.addSambaUser(user)
                    except Exception, e:
                        return {'status':False, 'msg':e}
                    if addsamba_ok:
                        try:
                            sambapasswd_ok, sambapasswd_result = self.addSambaPasswd(user, passwd)
                        except Exception, e:
                            return {'status':False, 'msg':e}
                        if sambapasswd_ok:
                            try:
                                group_ok, group_result =self.addUsertogroup(user, group)
                                if group_ok:
                                    samba_status = self.userInSamba(user)
                                    print 'userInSamba output:\n:', samba_status
                                    #if samba_status:
                                    #    self.sendMail(user)
                                    return {'status':True, 'msg':'添加用户成功赋予用户%s权限成功' % user}
                                else:
                                    return {'status':False, 'msg':group_result}
                            except Exception, e:
                                return {'status':False, 'msg':e}
                        else:
                            return {'status':False, 'msg':sambapasswd_result}
                    else:
                        return {'status':False, 'msg':addsamba_result}
                else:
                    return {'status':False, 'msg':status_addsys}
            except Exception,e:
                return {'status':False, 'msg':e }
        else:
            status, msg = self.addUsertogroup(user, group)
            return {'status':status, 'msg':msg}

    def renameFolder(self, path, filename, newname):
	'''
	Rename a folder
	'''
        fullpath = os.path.join(rootpath, path)
        print fullpath
        if os.path.exists(fullpath):
            filenamepath = os.path.join(fullpath, filename)
            print filenamepath
            newnamepath = os.path.join(fullpath, newname)
            print newnamepath
            cmd = "mv '%s' '%s'" % (filenamepath, newnamepath)
            print cmd
            try:
                proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                stdout_value, stderr_value = proc.communicate()
                if not stderr_value:
                    return {'status': True, 'msg': 'rename folder ok'}
                else:
                    return {'status': False, 'msg': stderr_value}
            except Exception, e:
                return {'status': False, 'msg':e}
        else:
            return {'status': False, 'msg': 'Folder not exists'}

    def updateConfig(self, sharelist):
	'''
	Update configure files
	'''
        try:
            f_configfile = open(configfile, 'w')
            sharename = []
            for share in sharelist:
                n, s, g = share
                sharename.append(s)
                f_configfile.write(','.join(share))
                f_configfile.write('\n')
            f_configfile.close()
            print '更新configlist成功!'
            print sharename 
            f_smb = open(sambashareconfig, 'w')
            for name in sharename:
                f_smb.write("[%s]\n" % name)
                f_smb.write("\tcomment = %s\n" % name)
                f_smb.write("\twriteable = yes\n")
                f_smb.write("\tpath = %s\n" % os.path.join(rootpath, name))
                f_smb.write("\tguest ok = no\n")
            f_smb.close()
            print '更新smb.conf成功!'
            self.killSession('test')
            return True, 'updateConfig ok'
        except Exception,e:
            print 'updateConfig error :\n',e 
            return False, e

    def sendMail(self, user):
	'''
	Simple send mail function
	'''
        to_list = ['user@dmain.com']
        to_list.append(user)
        content = '<html>Hi,' + user + '<br>&nbsp;您的账号已经创建完毕</html>'
        sender = 'sender@server.com'
        subject = "您的账号已经创建完成"
        msg = MIMEText(content, 'html', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ','.join(to_list)
        try:
            s = smtplib.SMTP('localhost')
            #s.set_debuglevel(1)
            s.sendmail(sender, to_list, msg.as_string())
            s.quit()
        except Exception,e :
            print e

    def __init__(self):
        super(PySamba, self).__init__()
