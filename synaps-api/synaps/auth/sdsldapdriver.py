"""
SDS Auth driver for ldap.
"""
 
import functools
import sys
 
from synaps import exception
from synaps import flags
from synaps import log as logging
from synaps.openstack.common import cfg
 
sdsldap_opts = [
    cfg.IntOpt('ldap_schema_version',
               default=2,
               help='Current version of the LDAP schema'),
    cfg.StrOpt('ldap_url',
               default='ldap://localhost',
               help='Point this at your ldap server'),
    cfg.StrOpt('ldap_password',
               default='changeme',
               help='LDAP password'),
    cfg.StrOpt('ldap_user_dn',
               default='cn=Manager,dc=example,dc=com',
                help='DN of admin user'),
    cfg.StrOpt('ldap_user_id_attribute',
               default='uid',
               help='Attribute to use as id'),
    cfg.StrOpt('ldap_user_name_attribute',
               default='cn',
                help='Attribute to use as name'),
    cfg.StrOpt('ldap_user_unit', default='Users', help='OID for Users'),
    cfg.StrOpt('ldap_user_subtree',
               default='ou=Users,dc=example,dc=com',
               help='OU for Users'),
    cfg.BoolOpt('ldap_user_modify_only',
                default=False,
                help='Modify attributes for users instead of creating/deleting'),
    cfg.StrOpt('ldap_project_subtree',
               default='ou=Groups,dc=example,dc=com',
               help='OU for Projects'),
    cfg.StrOpt('role_project_subtree',
               default='ou=Groups,dc=example,dc=com',
               help='OU for Roles'),
]

FLAGS = flags.FLAGS
FLAGS.register_opts(sdsldap_opts)

LOG = logging.getLogger(__name__)
 
if FLAGS.memcached_servers:
    import memcache
else:
    from synaps.common import memorycache as memcache
    
def _clean(attr):
    """Clean attr for insertion into ldap"""
    if attr is None:
        return None
    if type(attr) is unicode:
        return str(attr)
    return attr
 
def sanitize(fn):
    """Decorator to sanitize all args"""
    @functools.wraps(fn)
    def _wrapped(self, *args, **kwargs):
        args = [_clean(x) for x in args]
        kwargs = dict((k, _clean(v)) for (k, v) in kwargs)
        return fn(self, *args, **kwargs)
    _wrapped.func_name = fn.func_name
    return _wrapped


 
class LDAPWrapper(object):
    def __init__(self, ldap, url, user, password):
        self.ldap = ldap
        self.url = url
        self.user = user
        self.password = password
        self.conn = None
 
    def connect(self):
        try:
            self.conn = self.ldap.initialize(self.url)
            self.conn.simple_bind_s(self.user, self.password)
        except self.ldap.SERVER_DOWN:
            self.conn = None
            LOG.info("LDAP SERVER DOWN")
            raise
    
    def __wrap_reconnect(f):
        def inner(self, *args, **kwargs):
            if self.conn is None:
                self.connect()
                return f(self.conn)(*args, **kwargs)
            else:
                try:
                    return f(self.conn)(*args, **kwargs)
                except self.ldap.SERVER_DOWN:
                    self.connect()
                    return f(self.conn)(*args, **kwargs)
        return inner 
    
    search_s = __wrap_reconnect(lambda conn: conn.search_s)
    add_s = __wrap_reconnect(lambda conn: conn.add_s)
    delete_s = __wrap_reconnect(lambda conn: conn.delete_s)
    modify_s = __wrap_reconnect(lambda conn: conn.modify_s)
 
class SDSLdapDriver(object):
    """SDS Ldap Auth driver
 
    Defines enter and exit and therefore supports the with/as syntax.
    """
 
    project_pattern = '(ou=*)'
    role_attribute = 'entitlements'
    project_attribute = 'tenant'
    conn = None
    mc = None
    cache = {}
 
    def __init__(self):
        """Imports the LDAP module"""
        self.ldap = __import__('ldap')
        if SDSLdapDriver.conn is None:
            SDSLdapDriver.conn = LDAPWrapper(self.ldap, FLAGS.ldap_url,
                                          FLAGS.ldap_user_dn,
                                          FLAGS.ldap_password)
        if SDSLdapDriver.mc is None:
            SDSLdapDriver.mc = memcache.Client(FLAGS.memcached_servers, debug=0)
    
    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_value, traceback):
        return False
    
    def __local_cache(key_fmt):  # pylint: disable=E0213
        """Wrap function to cache it's result in self.__cache.
        Works only with functions with one fixed argument.
        """
        def do_wrap(fn):
            @functools.wraps(fn)
            def inner(self, arg, **kwargs):
                cache_key = key_fmt % (arg,)
                try:
                    res = SDSLdapDriver.cache[cache_key]
                    LOG.debug('Local cache hit for %s by key %s' % 
                              (fn.__name__, cache_key))
                    return res
                except KeyError:
                    res = fn(self, arg, **kwargs)
                    SDSLdapDriver.cache[cache_key] = res
                    return res
            return inner
        return do_wrap

    @sanitize
    @__local_cache('uid_user-%s')
    def get_user(self, uid):
        """Retrieve user by id"""
        attr = self.__get_ldap_user(uid)
        return self.__to_user(attr)
 
    @sanitize
    def get_user_from_access_key(self, access):
        """Retrieve user by access key"""
        cache_key = 'uak_dn_%s' % (access,)
        user_dn = self.mc.get(cache_key)
        if user_dn:
            user = self.__to_user(
                self.__find_object(user_dn, scope=self.ldap.SCOPE_BASE))
            if user:
                if user['access'] == access:
                    return user
                else:
                    self.mc.set(cache_key, None)
        query = '(accesskey=%s)' % access
        dn = FLAGS.ldap_user_subtree
        user_obj = self.__find_object(dn, query, scope=3)
        user = self.__to_user(user_obj)
        if user:
            self.mc.set(cache_key, user_obj['dn'][0])
        return user
 
    @sanitize
    @__local_cache('pid_project-%s')
    def get_project(self, pid):
        """Retrieve project by id"""
        pattern = SDSLdapDriver.project_pattern
        attrs = []
        dn = self.__project_to_dn(pid, search=False)
        prj = self.__find_object(dn, pattern, scope=self.ldap.SCOPE_BASE)
        project_name = prj['ou'][0]
        manager = self.__find_object("ou=role," + dn, "cn=manager")
        members = self.__find_objects("ou=user," + dn, '(uid=*)')
        member_ids = [member.get('uid')[0] for member in members]
        
        LOG.debug("member_ids: %s" % str(members))
        
        if 'uniqueMember' in manager :
            manager = manager['uniqueMember'][0]
        else :
            manager = ""

        attr = {"project_name" : project_name,
                "manager" : manager,
                "member_ids" : member_ids
               }
        return self.__to_project(attr)
 
    @sanitize
    def get_users(self):
        """Retrieve list of users"""
        attrs = self.__find_objects(FLAGS.ldap_user_subtree,
                                    '(objectclass=user)')
        users = []
        for attr in attrs:
            user = self.__to_user(attr)
            if user is not None:
                users.append(user)
        return users
 
    @sanitize
    def get_projects(self, uid=None):
        """Retrieve list of projects"""
        pattern = SDSLdapDriver.project_pattern
        projects = []
        
        if uid:
            user = self.__get_ldap_user(uid)
            project_name = user[SDSLdapDriver.project_attribute][0]
            project = self.get_project(project_name)
            projects.append(project)
        else :

            prjs = self.__find_objects(FLAGS.ldap_project_subtree,
                                           scope=1)
            for prj in prjs :
                project_name = prj['ou'][0]
                project = self.get_project(project_name)
                projects.append(project)
        return projects
 
    @sanitize
    def is_in_project(self, uid, project_id):
        """Check if user is in project"""
        user = self.__get_ldap_user(uid)
        return user[SDSLdapDriver.project_attribute][0] == project_id
 
    @sanitize
    def has_role(self, uid, role, project_id=None):
        #NOTE(dan.kim) project_id is not used.
        # because user has entitlements rows.
        user = self.__get_ldap_user(uid)
        has = role in user[SDSLdapDriver.role_attribute]
        return has 

    @sanitize
    def get_user_roles(self, uid, project_id=None):
        """Retrieve list of roles for user (or user and project)"""
        #NOTE(dan.kim) project_id is not used.
        # because user has entitlements rows.
        user = self.__get_ldap_user(uid)
        return user[SDSLdapDriver.role_attribute]
    
    @__local_cache('uid_attrs-%s')
    def __get_ldap_user(self, uid):
        """Retrieve LDAP user entry by id"""
        dn = FLAGS.ldap_user_subtree
        query = ('(&(%s=%s)(objectclass=user))' % 
                 (FLAGS.ldap_user_id_attribute, uid))
        return self.__find_object(dn, query)
 
    def __find_object(self, dn, query=None, scope=None):
        """Find an object by dn and query"""
        objects = self.__find_objects(dn, query, scope)
        if len(objects) == 0:
            return None
        return objects[0]
 
    def __find_dns(self, dn, query=None, scope=None):
        """Find dns by query"""
        if scope is None:
            # One of the flags is 0!
            scope = self.ldap.SCOPE_SUBTREE
        try:
            if self.mc.get("res") != None :
                LOG.debug("The key (res) was found in memcache")
                res = self.mc.get("res")
                LOG.debug("memcache load result: %s" % str(res))
            else :            
                LOG.debug("ldap query: dn: %s / scope: %s / query: %s" % (dn,
                                                                      scope,
                                                                      query))  
                res = self.conn.search_s(dn, scope, query)
                LOG.debug("ldap query result: %s" % (res))
        except self.ldap.NO_SUCH_OBJECT:
            return []
        # Just return the DNs
        return [dn for dn, _attributes in res]
 
    def __find_objects(self, dn, query=None, scope=None):
        """Find objects by query"""
        if scope is None:
            # One of the flags is 0!
            scope = self.ldap.SCOPE_SUBTREE
        if query is None:
            query = "(objectClass=*)"
        try:
            if self.mc.get("res_objects") != None :
                LOG.debug("The key (res_objects) was found in memcache")
                res = self.mc.get("res_objects")
                LOG.debug("memcache load result: %s" % str(res))
            else :
                LOG.debug("ldap query: dn: %s / scope: %s / query: %s" % (dn,
                                                                      scope,
                                                                      query))
                res = self.conn.search_s(dn, scope, query)
                LOG.debug("ldap query result: %s" % str(res))
        except self.ldap.NO_SUCH_OBJECT:
            return []
        # Just return the attributes
        # FIXME(yorik-sar): Whole driver should be refactored to
        #                   prevent this hack
        res1 = []
        for dn, attrs in res:
            attrs['dn'] = [dn]
            res1.append(attrs)
        return res1

    @__local_cache('uid_dn-%s')
    def __uid_to_dn(self, uid):
        """Convert uid to dn"""
        userdn = ""
        query = ('%s=%s' % (FLAGS.ldap_user_id_attribute, uid))
        user = self.__find_dns(FLAGS.ldap_user_subtree, query)
        if len(user) > 0:
            userdn = user[0]
        return userdn
 
    @__local_cache('pid_dn-%s')
    def __project_to_dn(self, pid, search=True):
        """Convert pid to dn"""
        # By default return a generated DN
        projectdn = ('ou=%s,%s' % (pid, FLAGS.ldap_project_subtree))
        if search:
            query = ('(&(ou=%s)%s)' % (pid, SDSLdapDriver.project_pattern))
            project = self.__find_dns(FLAGS.ldap_project_subtree, query)
            if len(project) > 0:
                projectdn = project[0]
        return projectdn
 
    @__local_cache('dn_uid-%s')
    def __dn_to_uid(self, dn):
        """Convert user dn to uid"""
        if dn is ''  : return ''
        query = '(objectclass=person)'
        user = self.__find_object(dn, query, scope=self.ldap.SCOPE_BASE)
        return user[FLAGS.ldap_user_id_attribute][0]
    
    @staticmethod
    def __to_user(attr):
        """Convert ldap attributes to User object"""
        if attr is None:
            return None
        if ('accesskey' in attr.keys() and 'securitykey' in attr.keys() \
            and SDSLdapDriver.role_attribute in attr.keys()):
            return {
                'id': attr[FLAGS.ldap_user_id_attribute][0],
                'name': attr[FLAGS.ldap_user_id_attribute][0],
                'access': attr['accesskey'][0],
                'secret': attr['securitykey'][0],
                'admin': ('novaadmin' in \
                    attr[SDSLdapDriver.role_attribute]),
                'project': attr['tenant'][0]
                }
        else:
            return None
 
    def __to_project(self, attr):
        """Convert ldap attributes to Project object"""
        if attr is None:
            return None
        LOG.debug("project from ldap: %s" % str(attr))
        return {
            'id': attr['project_name'],
            'name': attr['project_name'],
            'project_manager_id':
                self.__dn_to_uid(attr['manager']),
            'description': "",
            'member_ids': attr['member_ids']}

    #NOTE(dan.kim) This object is read-only.
    @sanitize
    def delete_user(self, uid):
        """Delete a user"""
        pass
 
    @sanitize
    def delete_project(self, project_id):
        """Delete a project"""
        pass
 
    @sanitize
    def modify_user(self, uid, access_key=None, secret_key=None, admin=None):
        """Modify an existing user"""
        pass

    @sanitize
    def add_role(self, uid, role, project_id=None):
        """Add role for user (or user and project)"""
        pass
 
    @sanitize
    def remove_role(self, uid, role, project_id=None):
        """Remove role for user (or user and project)"""
        pass
 
    @sanitize
    def create_user(self, name, access_key, secret_key, is_admin):
        """Create a user"""
        pass
 
    @sanitize
    def create_project(self, name, manager_uid,
                       description=None, member_uids=None):
        """Create a project"""
        pass
 
    @sanitize
    def modify_project(self, project_id, manager_uid=None, description=None):
        """Modify an existing project"""
        pass
 
    @sanitize
    def add_to_project(self, uid, project_id):
        """Add user to project"""
        pass
 
    @sanitize
    def remove_from_project(self, uid, project_id):
        """Remove user from project"""
        pass
