LogStream for F5 Distributed Cloud | Security Events
####################################################

.. figure:: _picture/architecture.png

.. contents:: Table of Contents

Introduction
####################################################
See repository `f5-log-converter <https://github.com/nergalex/f5-log-converter>`_

Deployment Guide
####################################################

Regional Edge | Container in F5 XC POP
*************************************************
UI
==================================================
- Deploy Logstream
    - Go to ``Distributed Apps`` > ``Virtual K8S`` > ``myVirtualCluster``
    - Create a ``workload`` by replacing emphasized line bellow

.. code:: json

    {
      "metadata": {
        "name": "logstream-xc",
        "namespace": "myNameSpace",
        "labels": {
          "project": "logstream-xc"
        },
        "annotations": {
          "ves.io/app": "logstream-xc"
        },
        "description": "https://github.com/nergalex/f5-xc-logstream",
        "disable": false
      },
      "spec": {
        "service": {
          "num_replicas": 1,
          "containers": [
            {
              "name": "logstream-xc",
              "image": {
                "name": "registry.gitlab.com/nergalex/f5-xc-logstream/logstream-xc:re",
                "public": {},
                "pull_policy": "IMAGE_PULL_POLICY_ALWAYS"
              },
              "init_container": false,
              "flavor": "CONTAINER_FLAVOR_TYPE_TINY",
              "command": [],
              "args": []
            }
          ],
          "volumes": [
            {
              "name": "unit-logstream-xc",
              "persistent_volume": {
                "storage": {
                  "access_mode": "ACCESS_MODE_READ_WRITE_ONCE",
                  "storage_size": 1,
                  "default": {}
                },
                "mount": {
                  "mode": "VOLUME_MOUNT_READ_WRITE",
                  "mount_path": "/unit",
                  "sub_path": ""
                }
              }
            }
          ],
          "configuration": {
            "parameters": [
              {
                "file": {
                  "name": "declaration.json",
                  "data": "string:///eyJmNXhjX3RlbmFudCI6eyJhcGlfa2V5IjoiWFhYWFgiLCJuYW1lIjoiWFhYWFgiLCJuYW1lc3BhY2VzIjpbeyJldmVudF9maWx0ZXIiOnsic2VjX2V2ZW50X3R5cGUiOiJ3YWZfc2VjX2V2ZW50In0sIm5hbWUiOiJhbC1kYWNvc3RhIiwiZXZlbnRfc3RhcnRfdGltZSI6eyJ5ZWFyIjoyMDIyLCJtb250aCI6NCwiZGF5IjoxNCwiaG91ciI6OCwibWludXRlIjowfX1dfSwibG9nY29sbGVjdG9yIjp7Imh0dHAiOlt7Imhvc3QiOiI1Mi4xNzcuOTQuMTUiLCJwb3J0Ijo4ODg4LCJwYXRoIjoiL2RlYnVnLnRlc3QifV0sInN5c2xvZyI6W3siaXBfYWRkcmVzcyI6IjUyLjE3Ny45NC4xNSIsInBvcnQiOjUxNDB9XX19",
                  "volume_name": "config-logstream-xc",
                  "mount": {
                    "mode": "VOLUME_MOUNT_READ_WRITE",
                    "mount_path": "/config",
                    "sub_path": ""
                  }
                }
              },
              {
                "env_var": {
                  "name": "FAAS_APP_NAME",
                  "value": "logstream-xc"
                }
              }
            ]
          },
          "deploy_options": {
            "deploy_re_sites": {
              "site": [
                {
                  "tenant": "ves-io",
                  "namespace": "system",
                  "name": "pa4-par"
                }
              ]
            }
          },
          "advertise_options": {
            "advertise_in_cluster": {
              "multi_ports": {
                "ports": [
                  {
                    "name": "http",
                    "info": {
                      "port": 8080,
                      "protocol": "PROTOCOL_HTTP",
                      "same_as_port": {}
                    }
                  },
                  {
                    "name": "https",
                    "info": {
                      "port": 8443,
                      "protocol": "PROTOCOL_TLS_WITH_SNI",
                      "same_as_port": {}
                    }
                  }
                ]
              }
            }
          }
        }
      }
    }

- Configure Logstream
    - ``Type of Workload`` > ``Service``  > ``Edit configuration``
    - ``Configuration Parameters`` > ``declaration.json`` > ``...``  > ``Edit``
    - ``File`` > ``Edit configuration``
    - ``Data``: modify in ASCII view or in JSON view
    - ``Apply`` for each screen

- Manage on which RE to deploy Logstream container
    - ``Type of Workload`` > ``Service``  > ``Edit configuration``
    - ``Deploy Options`` > ``Edit configuration``
    - List of Regional Edge Sites to Deploy: choose one RE in list
    - ``Apply`` for each screen

- ``Save and Exit``
- After a modification in Logstream configuration, start a new ``POD``:
    - ``PODs`` > ``logstream-xc`` > ``...`` > ``Delete``

Ansible
==================================================
An example of a deployment on a container hosted in a Regional Edge of F5 Distributed Cloud, using Ansible Tower.

Create and launch a workflow template ``wf-vk8s-unit-logstream`` that includes those Job templates in this order:

=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================
Job template                                                    objective                                           playbook                                        activity                                        inventory                                       credential
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================
``poc-k8s-create_nginx_unit_image``                             Build image of NGINX Unit + logstream App           ``playbooks/poc-k8s.yaml``                      ``create_nginx_unit_image``                     ``localhost``                                   ``cred_server``
``poc-volterra-create_app_logstream``                           Deploy POD in a RE                                  ``playbooks/poc-volterra.yaml``                 `create_app_logstream``                         ``localhost``
=============================================================   =============================================       =============================================   =============================================   =============================================   =============================================

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
    extra_owner_email: xxx@xxx.com
    extra_volterra:
      tenant:
        full: xxx-ccc
        short: xxx
      token: XXXXXXXXXXXXXXXXXXXX
    extra_volterra_namespace: xxx
    extra_volterra_re: xxx
    extra_volterra_site_id: 1
    faas_app:
      ca_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
      cert_pem: "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
      key_pem: "-----BEGIN RSA PRIVATE KEY-----...-----END RSA PRIVATE KEY-----"
      name: logstream-xc
      repo: 'https://github.com/nergalex/f5-xc-logstream.git'
      volume_declaration: /config
      volume_unit: /unit
    stats_acr_login_server: fqdn_of_a_container_registry
    stats_acr_password: password_credential_of_a_container_registry
    stats_acr_username: username_credential_of_a_container_registry
    stats_jumphost_ip: host_to_build_image

Customer Edge | VM/Docker
**************************************************
Github Action
==================================================
- Fork this repository
- Deploy a github runner
- Set viariable github workflow ``container-registry-ce``
    - LOCAL_DECLARATION: absolute path to your declaration file in your VM
    - runs-on: label set on your github runner

.. code:: yaml

    env:
      LOCAL_DECLARATION: /home/cyber/declaration.json
      (...)
    jobs:
      run_locally:
        runs-on: ubuntu-latest

- Commit

Ansible
==================================================
An example of a deployment on an Azure VM using Ansible Tower.

Virtualenv
--------------------------------------------------
- Create a virtualenv following `this guide <https://docs.ansible.com/ansible-tower/latest/html/upgrade-migration-guide/virtualenv.html>`_
- In virtualenv, as a prerequisite for Azure collection, install Azure SDK following `this guide <https://github.com/ansible-collections/azure>`_

Credential
--------------------------------------------------
- Create a Service Principal on Azure following `this guide <https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app>`_
- Create a Microsoft Azure Resource Manager following `this guide <https://docs.ansible.com/ansible-tower/latest/html/userguide/credentials.html#microsoft-azure-resource-manager>`_
- Create Credentials ``cred_NGINX`` to manage access to NGINX instances following `this guide <https://docs.ansible.com/ansible-tower/latest/html/userguide/credentials.html#machine>`_

=====================================================   =============================================   =============================================   =============================================   =============================================
REDENTIAL TYPE                                          USERNAME                                        SSH PRIVATE KEY                                 SIGNED SSH CERTIFICATE                          PRIVILEGE ESCALATION METHOD
=====================================================   =============================================   =============================================   =============================================   =============================================
``Machine``                                             ``my_VM_admin_user``                            ``my_VM_admin_user_key``                        ``my_VM_admin_user_CRT``                        ``sudo``
=====================================================   =============================================   =============================================   =============================================   =============================================

Ansible role structure
--------------------------------------------------
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

Workflow
--------------------------------------------------
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

    extra_logstream_declaration_b64: eyJmNXhjX3RlbmFudCI6IHsiYXBpX2tleSI6ICJYWFhYWFhYWFhYWD0iLCAibmFtZSI6ICJmNS1lbWVhLWVudCIsICJuYW1lc3BhY2VzIjogW3siZXZlbnRfZmlsdGVyIjogeyJzZWNfZXZlbnRfdHlwZSI6ICJ3YWZfc2VjX2V2ZW50In0sICJuYW1lIjogImFsLWRhY29zdGEiLCAiZXZlbnRfc3RhcnRfdGltZSI6IHsieWVhciI6IDIwMjIsICJtb250aCI6IDQsICJkYXkiOiAxMCwgImhvdXIiOiAyMCwgIm1pbnV0ZSI6IDAgfSB9IF0gfSwgImxvZ2NvbGxlY3RvciI6IHsiaHR0cCI6IFt7Imhvc3QiOiAiNTIuMTc3Ljk0LjE1IiwgInBvcnQiOiA4ODg4LCAicGF0aCI6ICIvZGVidWcudGVzdCJ9IF0sICJzeXNsb2ciOiBbeyJpcF9hZGRyZXNzIjogIjUyLjE3Ny45NC4xNSIsICJwb3J0IjogNTE0MCB9IF0gfSB9
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

Administration Guide
####################################################
Environment variable
****************************************************
Unit starts Logstream with environment variables

- Local log file
    - key: ``log_file_path``
    - value: absolute path to a log file or a relative path in wsgi folder
    - Default, if a *declaration* environment variable ``log_file_path`` is absent, LogStream will start using ``logstream.log`` present in local folder.
    - Note: If *log* file is absent, LogStream will NOT start.

- Local declaration file
    - key: ``declaration_file_path``
    - value: absolute path to a declaration file or a relative path in wsgi folder
    - Default: if a *declaration* environment variable ``declaration_file_path`` is absent, LogStream will start using ``declaration.json`` present in local folder.
    - Note: If *declaration* file is absent, LogStream will NOT start its engine but API GW is still running. In this case, use LogStream API to configure it and then to start its engine.

API
****************************************************
API allows you to:

- `declare` endpoint to configure entirely LogStream. Refer to API Dev Portal for parameter and allowed values.
- `action` endpoint to start/stop the engine.
- `declare` anytime you need to reconfigure LogStream and launch `restart` `action` to apply the new configuration.
- Note that the last `declaration` is saved locally

API Dev Portal is available at ``/apidocs/``

References
####################################################
- Understand NGINX Unit startup: `here <https://unit.nginx.org/howto/source/#startup-and-shutdown>`_



