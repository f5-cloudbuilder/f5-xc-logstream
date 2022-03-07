LogStream for F5 Distributed Cloud | Security Events
####################################################
.. contents:: Table of Contents

Introduction
==================================================
Use Case
**************************************************

LogStream forwards http security event logs - received from `F5 XC <https://docs.cloud.f5.com/docs/api/app-security>`_ - to remote syslog servers (log collector, SIEM)

.. figure:: _picture/architecture.png

Demo
**************************************************

.. raw:: html

    <a href="http://www.youtube.com/watch?v=3H9yDHJHSdA"><img src="http://img.youtube.com/vi/3H9yDHJHSdA/0.jpg" width="600" height="400" title="Logstream and CAS" alt="Logstream and CAS"></a>

Security consideration
**************************************************
No logs are stored. LogStream receives logs and then PUSH them directly to remote log collector servers.

Specification format
=================================================
Specification of LogStream are stored as a declaration in JSON format.

Reference schema is available in the description of ``/declare`` API endpoint.

Example of a declaration:

.. code:: json

    {
        "f5xc_tenant": {
            "api_key": "XXXXXXXXXXX",
            "name": "XXXXXXXXXXX",
            "namespaces": [
                {
                    "event_filter": {
                        "sec_event_type": "waf_sec_event"
                    },
                    "name": "XXXXXXXXXXX"
                }
            ]
        },
        "logcollector": {
            "syslog": [
                {
                    "ip_address": "127.100.0.8",
                    "port": 5140
                }
            ]
        }
    }

Configure
=================================================
3 ways to apply configuration:

Environment variable
********************
If a *declaration* environment variable ``declaration`` is present, LogStream will start its engine based on it.
Value of ``declaration`` environment variable is a JSON declaration b64 encoded

Example using an `online tool <https://www.base64encode.org/>`_: ``ewogICAgImY1eGNfdGVuYW50IjogewogICAgICAgICJhcGlfa2V5IjogWCIsCiAgICAgICAgIm5hbWUiOiAiWCIsCiAgICAgICAgIm5hbWVzcGFjZXMiOiBbCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJldmVudF9maWx0ZXIiOiB7CiAgICAgICAgICAgICAgICAgICAgInNlY19ldmVudF90eXBlIjogIndhZl9zZWNfZXZlbnQiCiAgICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgICAgIm5hbWUiOiAiWCIKICAgICAgICAgICAgfQogICAgICAgIF0KICAgIH0sCiAgICAibG9nY29sbGVjdG9yIjogewogICAgICAgICJzeXNsb2ciOiBbCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpcF9hZGRyZXNzIjogIjEwLjEwMC4wLjgiLAogICAgICAgICAgICAgICAgInBvcnQiOiA1MTQwCiAgICAgICAgICAgIH0KICAgICAgICBdCiAgICB9Cn0=``

Local file
********************
If a *declaration* file named `declaration.json <https://github.com/nergalex/f5-xc-logstream/blob/master/declaration.json>`_ is present in the main folder, LogStream will start its engine based on it.

API
***************
If *declaration* is absent, LogStream will NOT start its engine. Use LogStream API to configure it and then to start its engine.

API allows you to:
- `declare` endpoint to configure entirely LogStream. Refer to API Dev Portal for parameter and allowed values.
- `action` endpoint to start/stop the engine.
- `declare` anytime you need to reconfigure LogStream and launch `restart` `action` to apply the new configuration.
- Note that the last `declaration` is saved locally

API Dev Portal is available on your LogStream instance via ``/apidocs/``

API reference can be downloaded `here <https://github.com/nergalex/f5-xc-logstream/blob/master/swagger.json>`_

A Postman collection is available `here <https://github.com/nergalex/f5-xc-logstream/blob/master/LogStream-F5_XC.postman_collection.json>`_

Deployment on a VM
==================================================
An example of a deployment on an Azure VM using Ansible Tower.

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

Ansible role structure
***************************
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

Create and launch a workflow template ``wf-create_create_vm_app_nginx_unit_logstream`` that includes those Job templates in this order:

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
``extra_subnet_mgt_on_premise``                 Cross management zone
``faas_app``                                    Dict of Function as a Service
``faas_app.name``                               App's name
``faas_app.repo``                               Logstream repo
``faas_app.ca_pem``                             Intermediate CA that signed App's keys
``faas_app.cert_pem``                           App's certificate
``faas_app.key_pem``                            App's key
==============================================  =============================================

.. code:: yaml

    extra_logstream_declaration_b64: ewogICAgImY1eGNfdGVuYW50IjogewogICAgICAgICJhcGlfa2V5IjogWCIsCiAgICAgICAgIm5hbWUiOiAiWCIsCiAgICAgICAgIm5hbWVzcGFjZXMiOiBbCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJldmVudF9maWx0ZXIiOiB7CiAgICAgICAgICAgICAgICAgICAgInNlY19ldmVudF90eXBlIjogIndhZl9zZWNfZXZlbnQiCiAgICAgICAgICAgICAgICB9LAogICAgICAgICAgICAgICAgIm5hbWUiOiAiWCIKICAgICAgICAgICAgfQogICAgICAgIF0KICAgIH0sCiAgICAibG9nY29sbGVjdG9yIjogewogICAgICAgICJzeXNsb2ciOiBbCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICJpcF9hZGRyZXNzIjogIjEwLjEwMC4wLjgiLAogICAgICAgICAgICAgICAgInBvcnQiOiA1MTQwCiAgICAgICAgICAgIH0KICAgICAgICBdCiAgICB9Cn0=
    extra_platform_name: Demo
    extra_platform_tags: environment=DMO platform=Demo project=LogStream
    extra_subnet_mgt_on_premise: 10.0.0.0/24
    extra_vm:
      admin_username: cyber
      availability_zone:
        - 1
      ip: 10.100.0.54
      key_data: -----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----
      location: eastus2
      name: logstream-xc
      size: Standard_B2s
    faas_app:
      ca_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
      cert_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
      key_pem: "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----"
      name: logstream-xc
      repo: 'https://github.com/nergalex/f5-xc-logstream.git'

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

Troubleshoot
==================================================
View audit log:

:kbd:`tail -100 /var/log/unit/unit.log`

View access log:

:kbd:`tail -f /var/log/unit/access.log`

View app log:

:kbd:`tail -f /etc/faas-apps/logstream-xc/logstream.log`



