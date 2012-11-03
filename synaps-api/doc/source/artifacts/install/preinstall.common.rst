.. _preinstall.common:

Common Pre-installation
=======================

Set up NTP
----------

Install ntpd 

.. code-block:: bash
  
   sudo apt-get install ntp

edit '/etc/ntpd.conf' as below.

.. NOTE::

   Replace "ntp host" to hostname of real NTP server. NTP uses UDP 123 port   
   
.. code-block:: bash
  
   # /etc/ntp.conf, configuration for ntpd; see ntp.conf(5) for help
   driftfile /var/lib/ntp/ntp.drift
   # Use Ubuntu's ntp server as a fallback.
   server "ntp host" 
   # Local users may interrogate the ntp server more closely.
   restrict 127.0.0.1
   

