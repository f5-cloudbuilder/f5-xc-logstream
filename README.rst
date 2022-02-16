LogStream for NGINX Controller App Sec
=======================================================================
.. contents:: Table of Contents

Introduction
==================================================
Use Case
###############

LogStream forwards http security event logs - received from NGINX Controller App Sec - to remote syslog servers (log collector, SIEM)

.. figure:: _picture/architecture.png

Demo
###############

.. raw:: html

    <a href="http://www.youtube.com/watch?v=3H9yDHJHSdA"><img src="http://img.youtube.com/vi/3H9yDHJHSdA/0.jpg" width="600" height="400" title="Logstream and CAS" alt="Logstream and CAS"></a>


Security consideration
#########################
No logs are stored. LogStream receives logs and then PUSH them directly to remote log collector servers.

Pre requisites
==================================================
Ansible Tower
###############
Virtualenv
***************************
- Create a virtualenv following `this guide <https://docs.ansible.com/ansible-tower/latest/html/upgrade-migration-guide/virtualenv.html>`_
- In virtualenv, as a prerequisite for Azure collection, install Azure SDK following `this guide <https://github.com/ansible-collections/azure>`_

Credential
***************************
- Create a Service Principal on Azure following `this guide <https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app>`_
- Create a Microsoft Azure Resource Manager following `this guide <https://docs.ansible.com/ansible-tower/latest/html/userguide/credentials.html#microsoft-azure-resource-manager>`_
- Create Credentials ``cred_NGINX`` to manage access to NGINX instances following `this guide <https://docs.ansible.com/ansible-tower/latest/html/userguide/credentials.html#machine>`_

=====================================================   =============================================   =============================================   =============================================   =============================================
REDENTIAL TYPE                                          USERNAME                                        SSH PRIVATE KEY                                 SIGNED SSH CERTIFICATE                          PRIVILEGE ESCALATION METHOD
=====================================================   =============================================   =============================================   =============================================   =============================================
``Machine``                                             ``my_VM_admin_user``                            ``my_VM_admin_user_key``                        ``my_VM_admin_user_CRT``                        ``sudo``
=====================================================   =============================================   =============================================   =============================================   =============================================

Role
***************************
Clone roles from `NGINX Controller collection <https://github.com/nginxinc/ansible-collection-nginx_controller>`_ in `/etc/ansible/roles/`

- nginxinc.nginx_controller_generate_token
- nginxinc.nginx_controller_integration
- nginxinc.nginx_controller_forwarder

Rename generated directory of these roles as listed above

Ansible role structure
######################
- Deployment is based on ``workflow template``. Example: ``workflow template`` = ``wf-create_create_edge_security_inbound``
- ``workflow template`` includes multiple ``job template``. Example: ``job template`` = ``poc-azure_create_hub_edge_security_inbound``
- ``job template`` have an associated ``playbook``. Example: ``playbook`` = ``playbooks/poc-azure.yaml``
- ``playbook`` launch a ``play`` in a ``role``. Example: ``role`` = ``poc-azure``

.. code:: yaml

    - hosts: localhost
      gather_facts: no
      roles:
        - role: poc-azure

- ``play`` is an ``extra variable`` named ``activity`` and set in each ``job template``. Example: ``create_hub_edge_security_inbound``
- The specified ``play`` (or ``activity``) is launched by the ``main.yaml`` task located in the role ``tasks/main.yaml``

.. code:: yaml

    - name: Run specified activity
      include_tasks: "{{ activity }}.yaml"
      when: activity is defined

- The specified ``play`` contains ``tasks`` to execute. Example: play=``create_hub_edge_security_inbound.yaml``

Installation
==================================================
Remote Syslog
#################
-  `Optimize the Network Kernel Parameters <https://docs.fluentd.org/installation/before-install#optimize-the-network-kernel-parameters>`_

.. code:: bash

    vi /etc/sysctl.conf
        net.core.somaxconn = 1024
        net.core.netdev_max_backlog = 5000
        net.core.rmem_max = 16777216
        net.core.wmem_max = 16777216
        net.ipv4.tcp_wmem = 4096 12582912 16777216
        net.ipv4.tcp_rmem = 4096 12582912 16777216
        net.ipv4.tcp_max_syn_backlog = 8096
        net.ipv4.tcp_slow_start_after_idle = 0
        net.ipv4.tcp_tw_reuse = 1
        net.ipv4.ip_local_port_range = 10240 65535
    sysctl -p

- Install `Fluentd <https://docs.fluentd.org/installation/install-by-rpm>`_

.. code:: bash

    curl -L https://toolbelt.treasuredata.com/sh/install-redhat-td-agent4.sh | sh

- Configure Fluentd with a TCP syslog INPUT

.. code:: bash

    vi /etc/td-agent/td-agent.conf

.. code:: xml

        <match debug.**>
          @type stdout
          @id output_stdout
        </match>
        <source>
          @type http
          @id input_http
          port 8888
        </source>
        <source>
          @type syslog
          tag debug.logstream
          port 5140
          bind 0.0.0.0
          <transport tcp>
            </transport>
        </source>

- Start service

.. code:: bash

    systemctl start td-agent.service


- Unit test

.. code:: bash

    tail -f -n 1 /var/log/td-agent/td-agent.log &
    curl -X POST -d 'json={"json":"message"}' http://localhost:8888/debug.test



Logstream
###############
Clone this github repository and set ``declaration.json`` with your values

.. code:: json

    {
        "cas": {
            "api_key": "MySharedSecretWithNGINXController"
        },
        "logcollector": {
            "syslog": [
                {
                    "ip_address": "10.100.0.11",
                    "port": 5140
                }
            ]
        }
    }

Create and launch a workflow template ``wf-create_vm_app_nginx_unit_logstream_cas`` that includes those Job templates in this order:

=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================
Job template                                                    objective                                           playbook                                        activity                                        inventory                                       limit                                           credential
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================
``poc-azure_create-vm-nginx_unit``                              Deploy a VM                                         ``playbooks/poc-azure.yaml``                    ``create-vm-nginx_unit``                        ``my_project``                                  ``localhost``                                   ``my_azure_credential``
``poc-onboarding_nginx_unit_faas_app_logstream``                Install NGINX Unit + App                            ``playbooks/poc-nginx_vm.yaml``                 ``onboarding_nginx_unit_faas_app_logstream``    ``localhost``                                                                                   ``cred_NGINX``
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================

==============================================  =============================================
Extra variable                                  Description
==============================================  =============================================
``extra_vm``                                    Dict of VM properties
``extra_vm.ip``                                 VM IP address
``extra_vm.name``                               VM name
``extra_vm.size``                               Azure VM type
``extra_vm.availability_zone``                  Azure AZ
``extra_vm.location``                           Azure location
``extra_vm.admin_username``                     admin username
``extra_vm.key_data``                           admin user's public key
``extra_platform_name``                         platform name used for Azure resource group
``extra_platform_tags``                         Azure VM tags
``extra_subnet_mgt_on_premise``                 Cross management zone via VPN GW
``faas_app``                                    Dict of Function as a Service
``faas_app.name``                               App's name
``faas_app.repo``                               Your cloned Logstream repo
``faas_app.ca_pem``                             Intermediate CA that signed App's keys
``faas_app.cert_pem``                           App's certificate
``faas_app.key_pem``                            App's key
==============================================  =============================================

.. code:: yaml

    extra_vm:
      ip: 10.100.0.52
      name: logstream-cas
      size: Standard_B2s
      admin_username: myadmin
      availability_zone:
        - 1
      location: eastus2
      key_data: -----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----
    extra_platform_name: TotalInbound
    extra_platform_tags: environment=DMO platform=TotalInbound project=CloudBuilderf5
    extra_subnet_mgt_on_premise: 10.0.0.0/24
    faas_app:
      name: logstream-cas
      repo: https://github.com/nergalex/f5-cas-logstream.git
      ca_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
      cert_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
      key_pem: "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----"

NGINX Controller
#################

=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================
Job template                                                    objective                                           playbook                                        activity                                        inventory                                       limit                                           credential
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================
``poc-nginx_controller-create_appsec_http_forwarder``           Create/Update Forwarder                             ``playbooks/poc-nginx_controller.yaml``         ``create_appsec_http_forwarder``                ``localhost``
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================

==============================================  =============================================
Extra variable                                  Description
==============================================  =============================================
``extra_nginx_controller_ip``
``extra_nginx_controller_password``
``extra_nginx_controller_username``
``extra_log_collector.endpointUri``             Listener of remote syslog
``extra_log_collector.name``                    name of remote syslog
``extra_log_collector.api_key``                 Shared Key to authenticate Controller
==============================================  =============================================

.. code:: yaml

    extra_log_collector:
      endpointUri: 'http://10.0.0.10:3001/forward'
      name: logstream
      api_key: TESTKEY
    extra_nginx_controller:
      ip: 10.0.0.43
      password: MyPassword!
      username: admin@acme.com

Uninstallation
==================================================
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================
Job template                                                    objective                                           playbook                                        activity                                        inventory                                       limit                                           credential
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================
``poc-nginx_controller-delete_appsec_http_forwarder``           Create/Update Forwarder                             ``playbooks/poc-nginx_controller.yaml``         ``delete_appsec_http_forwarder``                ``localhost``
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================   =============================================

==============================================  =============================================
Extra variable                                  Description
==============================================  =============================================
``extra_nginx_controller_ip``
``extra_nginx_controller_password``
``extra_nginx_controller_username``
``extra_log_collector.name``                    name of remote syslog
==============================================  =============================================

.. code:: yaml

    extra_log_collector:
      name: logstream
    extra_nginx_controller:
      ip: 10.0.0.43
      password: MyPassword!
      username: admin@acme.com

Configuration
==================================================
- Install `Postman <https://www.postman.com/>`_
- Import collection LogStream_cas.postman_collection.json
- Use `declare` entry point to configure entirely LogStream. Refer to API Dev Portal for parameter and allowed values.
- Use `action` entry point to start/stop the engine.
- Use `declare` anytime you need to reconfigure LogStream and launch `restart` `action` to apply the new configuration.
- Note that the last `declaration` is saved locally

API reference
==================================================
Access to API Dev Portal with your browser ``http://<extra_vm.ip_mgt>:8080/apidocs/``

Troubleshoot
==================================================
View audit log:

:kbd:`tail -100 /var/log/unit/unit.log`

View access log:

:kbd:`tail -f /var/log/unit/access.log`

View app log:

:kbd:`tail -f /etc/faas-apps/logstream-cas/logstream.log`




