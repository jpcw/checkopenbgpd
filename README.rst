

==========================================================
Check OpenBGPD Nagios|Icinga|shinken|etc plugin.
==========================================================

.. image:: https://img.shields.io/pypi/l/checkopenbgpd.svg
    :target: https://pypi.python.org/pypi/checkopenbgpd/

.. image:: https://img.shields.io/pypi/implementation/checkopenbgpd.svg
    :target: https://pypi.python.org/pypi/checkopenbgpd/

.. image:: https://img.shields.io/pypi/pyversions/checkopenbgpd.svg
    :target: https://pypi.python.org/pypi/checkopenbgpd/

.. image:: https://img.shields.io/pypi/v/checkopenbgpd.svg
      :target: https://pypi.python.org/pypi/checkopenbgpd/

.. image:: https://img.shields.io/pypi/status/checkopenbgpd.svg
    :target: https://pypi.python.org/pypi/checkopenbgpd/

.. image:: https://img.shields.io/coveralls/jpcw/checkopenbgpd.svg
      :target: https://coveralls.io/r/jpcw/checkopenbgpd

.. image:: https://api.travis-ci.org/jpcw/checkopenbgpd.svg?branch=master
      :target: http://travis-ci.org/jpcw/checkopenbgpd


+ Source: https://github.com/jpcw/checkopenbgpd

+ Bugtracker: https://github.com/jpcw/checkopenbgpd/issues

.. contents::

usage
-------

This check runs **bgpctl show** and checks that all bgp sessions are up.


sample outputs :

+ Ok

::
 
 $ check_openbgpd 
 CHECKBGPCTL OK - All bgp sessions in correct state | 'PEER-1'=529581;;;0 
    
Sometimes you have some peer sessions in ignore state, and it 's not critical. Typically a session which depends on a slave carp interface. You have an option '--ignore-list', the plugin will take care if the session is in this list, and returns an 'OK' state for this session.

::
 
  $ check_openbgpd --ignore-list PEER-2 OTHER-PEER
  CHECKBGPCTL OK - All bgp sessions in correct state | 'PEER-1'=529581;;;0 'PEER-2'=0;;;0 'OTHER-PEER'=0;;;0



+ Critical

Critical state is reached with first ignore session not escaped in the optionnal '--ignore-list' 
 
::
 
 $ check_openbgpd
 CHECKBGPCTL CRITICAL - OTHER-PEER is U (outside range 0:) | 'PEER-1'=529918;;;0 'OTHER-PEER'=U;;;0


+ Unknown

if an error occured during the check, the plugin raises a check error, which returns an UNKNOWN state.

typically UNKNOWN causes

 + OpenBGPD is not running 

 ::
   
  CHECKBGPCTL UNKNOWN - host.domain.tld bgpctl: connect: /var/run/bgpd.sock: No such file or directory

 + you're not in the wheel group, and can't read the bgpctl sosk 

 ::
   
  CHECKBGPCTL UNKNOWN - host.domain.tld bgpctl: connect: /var/run/bgpd.sock: Permission denied 

 doas is your friend to run this plugin with an unprivileged user. A sample config here 

 ::
  
  permit nopass icinga as root cmd /usr/local/bin/check_openbgpd


Install
------------

extract the tarball and :: 

    python setup.py install

Maybe you have installed setuptools with ::

    pkg_add py-setuptools

then just ::
    
    easy_install checkopenbgpd

check_openbgpd is located at /usr/local/bin/check_openbgpd


Nagios|icinga like configuration
-----------------------------------

check_openbgpd could be called localy or remotely via check_by_ssh or NRPE.

**check_by_ssh**

here a sample definition to check remotely by ssh 

Command definition ::
    
    define command{
        command_name    check_ssh_bgpctl
        command_line    $USER1$/check_by_ssh -H $HOSTADDRESS$ -i /var/spool/icinga/.ssh/id_rsa -C "sudo /usr/local/bin/check_openbgpd --ignore-list $ARG1$"
    }

the service itself ::
    
    define service{
        use                     my-service
        host_name               hostname
        service_description     bgpctl
        check_command           check_ssh_bgpctl!
    }

icinga2 command ::
    
	object CheckCommand "openbgpd" {
        import "plugin-check-command"
        import "ipv4-or-ipv6"
        command = [ PluginDir + "/check_by_ssh" ]
        arguments = {
            "-H" = "$openbgpd_address$"
            "-i" = "$ssh_id$"
            "-p" = "$ssh_port$"
            "-C" = "$ssh_command$"
    	    }
        vars.openbgpd_address = "$check_address$"
        vars.ssh_id = "/var/spool/icinga/.ssh/id_rsa"
        vars.ssh_port = "$vars.ssh_port$"
        vars.ssh_command = "sudo /usr/local/bin/check_openbgpd"
	}

icinga2 service ::
	
	apply Service "openbgpd" {
  	    check_command = "openbgpd"
  	    assign where host.name == "hostname"
	}

**NRPE**

add this line to /usr/local/etc/nrpe.cfg ::
     
    ...
    command[check_openbgpd]=/usr/local/bin/check_openbgpd
    ...

nagios command definition ::
    
    define command{
        command_name    check_nrpe_bgpctl
        command_line    $USER1$/check_nrpe -H $HOSTADDRESS$ -c check_openbgpd -a "--ignore-list $ARGS1"
    }

the service itself ::
    
    define service{
        use                     my-service
        host_name               hostname
        service_description     bgpctl
        check_command           check_nrpe_bgpctl!
    }   

testing
---------
::
     
     python bootstrap-buildout.py --setuptools-version=33.1.1 --buildout-version=2.5.2
     bin/buildout -N
     bin/test
     
