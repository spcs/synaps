..
      Copyright 2014 Samsung SDS.
      All Rights Reserved.

Configure Identification Backend Guide
======================================

Synaps includes three types of filters for authentication in the WSGI 
application pipeline.

* no_auth: No authentication. With this filter, the access key of a request is
  tenant ID. 
* ec2keystoneauth: Use Openstack Keystone for authentication. This is default
  authentication filter.
* authenticate: Use `synaps.auth.manager.AuthManager` for authentication.
  Synaps includes LdapDriver for AuthManager backend. Or, you can build your
  own custom driver for your identification system.  

You can configure your api-paste.ini file to select filter.

no_auth filter
--------------

api-paste.ini

.. code-block:: bash

  [pipeline:cloudwatch_api_v1]
  pipeline = fault_wrap log_request no_auth monitor_request authorizer cloudwatch_executor


ec2keystoneauth filter
----------------------

To use ec2keystoneauth filter, you need to configure api-paste.ini and 
synaps.conf also. This filter is default.

api-paste.ini

.. code-block:: bash

  [pipeline:cloudwatch_api_v1]
  pipeline = fault_wrap log_request ec2keystoneauth monitor_request authorizer cloudwatch_executor

synaps.conf

.. code-block:: bash

  keystone_ec2_url=http://keystone.endpointurl:5000/v2.0/ec2tokens


authenticate filter
-------------------

While Synaps is OpenStack related project, it is designed with loosely coupled
architecture with other OpenStack projects. If you want to use Synaps as a 
standalone service without any OpenStack component, use this filter. This 
filter supports LDAP backend.  

To use authenticate filter, you need to configure api-paste.ini and synaps.conf 
also.

api-paste.ini

.. code-block:: bash

  [pipeline:cloudwatch_api_v1]
  pipeline = fault_wrap log_request authenticate monitor_request authorizer cloudwatch_executor

synaps.conf
  
.. code-block:: bash

  auth_driver=synaps.auth.ldapdriver.LdapDriver
  ldap_url=ldap://ldapurl:port
  ldap_password=changeme
  ldap_user_dn=cn=Manager,dc=example,dc=com
  
Synaps provides working LDAP schema and initial installation script for 
openldap. You can start with this example script to connect your own LDAP.
To install ldap for Synaps, use the script. (It works for Ubuntu)

.. Note::

  Be careful running this script. It will scrub all users.

.. code-block:: bash

  $ git clone https://github.com/spcs/synaps
  $ cd synaps/synaps/etc/auth_setup
  $ sudo ./slap.sh

And then, user management is not scope of Synaps. You can create user and 
project with LDAP management tools. And, there is an example script for create 
user and project. Following script will create an user, create project and set 
the user as a manager of "prjname" project.

.. code-block:: python

	import os
	import sys
	
	possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
	                                                os.pardir, os.pardir))
	if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
	    sys.path.insert(0, possible_topdir)
	
	from synaps import flags
	from synaps import log as logging
	from synaps import utils
	from synaps.auth.manager import AuthManager
	
	if __name__ == "__main__":
	    flags.FLAGS(sys.argv)
	    utils.default_flagfile()
	    logging.setup()
	    LOG = logging.getLogger()
	
	    auth = AuthManager()
	    try:
	         auth.create_user("username", "access", "secret", False)
	         auth.create_project("prjname", "username")
	    except:
	        LOG.exception()

.. Note::

	When your Synaps instance is using this filter, users should use composite
	string as an access key in form of accesskey:projectid so that Synaps can
	distinguish the project of user. Without projectid, Synaps will assume the 
	user name and project id is identical.
	