## Getting Started with Event Driven Ansible With Cisco Model Driven Telemetry

#### Introduction 
Event-Driven Ansible enhances traditional playbook automation by enabling real-time response to IT infrastructure changes. It listens for events from external sources e.g Kafka, url_check, webhook etc using [Event Source Plugins](https://ansible.readthedocs.io/projects/rulebook/en/stable/sources.html). When an event matches using [Conditions](https://ansible.readthedocs.io/projects/rulebook/en/stable/conditions.html) with the predefined [Rule](https://ansible.readthedocs.io/projects/rulebook/en/stable/rules.html), Ansible automatically triggers the appropriate playbooks, job templates or modules to react to the situation by using the [Actions](https://ansible.readthedocs.io/projects/rulebook/en/stable/actions.html). This centralized approach streamlines automation, reduces manual intervention for handling incidents like troubleshooting tasks, even self-healing, it uses proactive approach in the sense that you don't need to wait for the incident to happen and you react to it as EDA will take of care of this which reduces reaction times to changes within your IT environment.

For further reading [Event-Driven Ansible](https://www.redhat.com/en/technologies/management/ansible/event-driven-ansible).

#### Prerequisite for Ansible Even Driven Automation

Before you deploy even driven automation using the Ansible EDA with Cisco MDT, you need to have the following in place. 

- Configure Cisco devices with MDT using the provided MDT configurations for IOSXE and XR, available in the [config-mdt-config](./config-mdt-config/) folder.

- Ensure you have Telegraf and Kafka running on your preferred operating system. They will receive those MDT logs, decode them to JSON, and send to Kafka, where Ansible EDA Kafka plugin listen. I have prepared the [docker-compose.yml](./telegraf-kafka/docker-compose.yml) file for Telegraf and Kafka as well as [telegraf.conf](./telegraf-kafka/telegraf.conf) for you which can be found in the [telegraf-kafka](./telegraf-kafka/) folder. Go to that folder and run `docker compose up -d` command to start the containers.

```
docker compose up -d
```
To verify services you need to `docker compose ps -a` and you should see the following output, if all the services are started successfully.

```shell
[root@devnetbox telegraf-kafka]# docker compose ps -a
NAME                IMAGE                             COMMAND                  SERVICE             CREATED             STATUS                PORTS
kafdrop             obsidiandynamics/kafdrop:latest   "/kafdrop.sh"            kafdrop             4 days ago          Up 4 days             0.0.0.0:9000->9000/tcp
kafka               wurstmeister/kafka                "start-kafka.sh"         kafka               4 days ago          Up 4 days             0.0.0.0:9092->9092/tcp
telegraf_1          telegraf:latest                   "/entrypoint.sh tele…"   telegraf_1          4 days ago          Up 4 days             8092/udp, 8125/udp, 8094/tcp, 0.0.0.0:57501->57501/tcp
zookeeper           wurstmeister/zookeeper            "/bin/sh -c '/usr/sb…"   zookeeper           4 days ago          Up 4 days (healthy)   22/tcp, 2888/tcp, 3888/tcp, 0.0.0.0:2181->2181/tcp
[root@devnetbox telegraf-kafka]# 
```

#### Create A Virtual Environment
`Note:` You may choose your favorites method to create your virtual environment and name the virtual environment

```shell
[root@devnetbox ~]# python3 -m venv ansible_latest
[root@devnetbox ~]# source ansible_latest/bin/activate
(ansible_latest) [root@devnetbox ~]# 
```

#### Install All Required Packages to Start with Ansible EDA
`Note:` Move on to next step if you like to install required packages separately

```shell
(ansible_latest) [root@devnetbox ~]# pip install -r requirements.txt 
Collecting aiohttp==3.9.3 (from -r requirements.txt (line 1))
  Using cached aiohttp-3.9.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (7.4 kB)
Collecting aiokafka==0.10.0 (from -r requirements.txt (line 2))
  Using cached aiokafka-0.10.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (17 kB)
Collecting aiosignal==1.3.1 (from -r requirements.txt (line 3))
  Using cached aiosignal-1.3.1-py3-none-any.whl.metadata (4.0 kB)
Collecting ansible==8.7.0 (from -r requirements.txt (line 4))
  Using cached ansible-8.7.0-py3-none-any.whl.metadata (7.9 kB)
Collecting ansible-core==2.15.10 (from -r requirements.txt (line 5))
  Using cached ansible_core-2.15.10-py3-none-any.whl.metadata (7.0 kB)
Collecting ansible-lint==5.4.0 (from -r requirements.txt (line 6))
  Using cached ansible_lint-5.4.0-py3-none-any.whl.metadata (6.1 kB)
Collecting ansible-pylibssh==1.1.0 (from -r requirements.txt (line 7))
  Using cached ansible_pylibssh-1.1.0-cp311-cp311-manylinux_2_24_x86_64.whl.metadata (5.0 kB)
Collecting ansible-runner==2.3.6 (from -r requirements.txt (line 8))
  Using cached ansible_runner-2.3.6-py3-none-any.whl.metadata (3.5 kB)
Collecting ansible_rulebook==1.0.6 (from -r requirements.txt (line 9))
  Using cached ansible_rulebook-1.0.6-py3-none-any.whl.metadata (4.3 kB)
Collecting async-timeout==4.0.3 (from -r requirements.txt (line 10))
  Using cached async_timeout-4.0.3-py3-none-any.whl.metadata (4.2 kB)
Collecting attrs==23.2.0 (from -r requirements.txt (line 11))
  Using cached attrs-23.2.0-py3-none-any.whl.metadata (9.5 kB)
Collecting bcrypt==4.1.2 (from -r requirements.txt (line 12))
  Using cached bcrypt-4.1.2-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (9.5 kB)
Collecting bracex==2.4 (from -r requirements.txt (line 13))
  Using cached bracex-2.4-py3-none-any.whl.metadata (3.6 kB)
Collecting certifi==2023.7.22 (from -r requirements.txt (line 14))
  Using cached certifi-2023.7.22-py3-none-any.whl.metadata (2.2 kB)
Collecting cffi==1.15.1 (from -r requirements.txt (line 15))
  Using cached cffi-1.15.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (1.1 kB)
Collecting charset-normalizer==3.2.0 (from -r requirements.txt (line 16))
  Using cached charset_normalizer-3.2.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (31 kB)

... Output Omitted
```

#### Install Ansible within your Virtual Environment 

```shell
(ansible_latest) [root@devnetbox ~]# pip install ansible
Collecting ansible
  Downloading ansible-9.4.0-py3-none-any.whl.metadata (8.2 kB)
Collecting ansible-core~=2.16.5 (from ansible)
  Downloading ansible_core-2.16.5-py3-none-any.whl.metadata (6.9 kB)
Collecting jinja2>=3.0.0 (from ansible-core~=2.16.5->ansible)
  Downloading Jinja2-3.1.3-py3-none-any.whl.metadata (3.3 kB)
Collecting PyYAML>=5.1 (from ansible-core~=2.16.5->ansible)
  Using cached PyYAML-6.0.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (2.1 kB)
Collecting cryptography (from ansible-core~=2.16.5->ansible)
  Downloading cryptography-42.0.5-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (5.3 kB)
Collecting packaging (from ansible-core~=2.16.5->ansible)
  Downloading packaging-24.0-py3-none-any.whl.metadata (3.2 kB)
Requirement already satisfied: resolvelib<1.1.0,>=0.5.3 in ./ansible_latest/lib64/python3.11/site-packages (from ansible-core~=2.16.5->ansible) (1.0.1)
Collecting MarkupSafe>=2.0 (from jinja2>=3.0.0->ansible-core~=2.16.5->ansible)
  Downloading MarkupSafe-2.1.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.0 kB)
Collecting cffi>=1.12 (from cryptography->ansible-core~=2.16.5->ansible)
  Using cached cffi-1.16.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (1.5 kB)
Collecting pycparser (from cffi>=1.12->cryptography->ansible-core~=2.16.5->ansible)
  Using cached pycparser-2.21-py2.py3-none-any.whl.metadata (1.1 kB)
Downloading ansible-9.4.0-py3-none-any.whl (46.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 46.4/46.4 MB 46.5 MB/s eta 0:00:00
Downloading ansible_core-2.16.5-py3-none-any.whl (2.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.3/2.3 MB 63.2 MB/s eta 0:00:00
Downloading Jinja2-3.1.3-py3-none-any.whl (133 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 133.2/133.2 kB 18.3 MB/s eta 0:00:00
Using cached PyYAML-6.0.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (757 kB)
Downloading cryptography-42.0.5-cp39-abi3-manylinux_2_28_x86_64.whl (4.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.6/4.6 MB 83.6 MB/s eta 0:00:00
Downloading packaging-24.0-py3-none-any.whl (53 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 53.5/53.5 kB 6.8 MB/s eta 0:00:00
Using cached cffi-1.16.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (464 kB)
Downloading MarkupSafe-2.1.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (28 kB)
Using cached pycparser-2.21-py2.py3-none-any.whl (118 kB)
Installing collected packages: PyYAML, pycparser, packaging, MarkupSafe, jinja2, cffi, cryptography, ansible-core, ansible
Successfully installed MarkupSafe-2.1.5 PyYAML-6.0.1 ansible-9.4.0 ansible-core-2.16.5 cffi-1.16.0 cryptography-42.0.5 jinja2-3.1.3 packaging-24.0 pycparser-2.21
(ansible_latest) [root@devnetbox ~]# ansible --version
ansible [core 2.16.5]
  config file = None
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /root/ansible_latest/lib64/python3.11/site-packages/ansible
  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
  executable location = /root/ansible_latest/bin/ansible
  python version = 3.11.2 (main, Jun 22 2023, 06:07:18) [GCC 8.5.0 20210514 (Red Hat 8.5.0-18)] (/root/ansible_latest/bin/python3)
  jinja version = 3.1.3
  libyaml = True
(ansible_latest) [root@devnetbox ~]# 
```

#### Install Paramiko for Ansible to use SSH to Network Devices

```shell
(ansible_latest) [root@devnetbox ~]# pip install paramiko
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ProtocolError('Connection aborted.', OSError(107, 'Transport endpoint is not connected'))': /simple/paramiko/
Collecting paramiko
  Using cached paramiko-3.4.0-py3-none-any.whl.metadata (4.4 kB)
Collecting bcrypt>=3.2 (from paramiko)
  Using cached bcrypt-4.1.2-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (9.5 kB)
Requirement already satisfied: cryptography>=3.3 in ./ansible_latest/lib64/python3.11/site-packages (from paramiko) (42.0.5)
Collecting pynacl>=1.5 (from paramiko)
  Using cached PyNaCl-1.5.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl.metadata (8.6 kB)
Requirement already satisfied: cffi>=1.12 in ./ansible_latest/lib64/python3.11/site-packages (from cryptography>=3.3->paramiko) (1.16.0)
Requirement already satisfied: pycparser in ./ansible_latest/lib64/python3.11/site-packages (from cffi>=1.12->cryptography>=3.3->paramiko) (2.21)
Using cached paramiko-3.4.0-py3-none-any.whl (225 kB)
Using cached bcrypt-4.1.2-cp39-abi3-manylinux_2_28_x86_64.whl (698 kB)
Using cached PyNaCl-1.5.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl (856 kB)
Installing collected packages: bcrypt, pynacl, paramiko
Successfully installed bcrypt-4.1.2 paramiko-3.4.0 pynacl-1.5.0
(ansible_latest) [root@devnetbox ~]# 
```

#### Install Ansible PyLibssh for Ansible to use SSH to Network Devices
`Note:` This is optional, you may use `paramiko` only as mentioned in the previous step.

```shell
(ansible_latest) [root@devnetbox ~]# pip install ansible-pylibssh
Collecting ansible-pylibssh
  Using cached ansible_pylibssh-1.1.0-cp311-cp311-manylinux_2_24_x86_64.whl.metadata (5.0 kB)
Using cached ansible_pylibssh-1.1.0-cp311-cp311-manylinux_2_24_x86_64.whl (2.3 MB)
Installing collected packages: ansible-pylibssh
Successfully installed ansible-pylibssh-1.1.0
(ansible_latest) [root@devnetbox ~]# 
```

#### Install IO Kafka for the Ansible Kafka Plugin
```shell
(ansible_latest) [root@devnetbox ~]# pip install aiokafka
Collecting aiokafka
  Using cached aiokafka-0.10.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (17 kB)
Requirement already satisfied: async-timeout in ./ansible_latest/lib64/python3.11/site-packages (from aiokafka) (4.0.3)
Requirement already satisfied: packaging in ./ansible_latest/lib64/python3.11/site-packages (from aiokafka) (24.0)
Using cached aiokafka-0.10.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.1 MB)
Installing collected packages: aiokafka
Successfully installed aiokafka-0.10.0
(ansible_latest) [root@devnetbox ~]# 
```

#### Install LZ4 compression library (optional)
```shell
(ansible_latest) [root@devnetbox ~]# pip install lz4
Collecting lz4
  Downloading lz4-4.3.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.7 kB)
Downloading lz4-4.3.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.3 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 41.2 MB/s eta 0:00:00
Installing collected packages: lz4
Successfully installed lz4-4.3.3
```

#### Install Ansible Rulebook Package
```shell
(ansible_latest) [root@devnetbox ~]# pip install ansible-rulebook
Collecting ansible-rulebook
  Using cached ansible_rulebook-1.0.6-py3-none-any.whl.metadata (4.3 kB)
Collecting aiohttp (from ansible-rulebook)
  Using cached aiohttp-3.9.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (7.4 kB)
Collecting pyparsing>=3.0 (from ansible-rulebook)
  Downloading pyparsing-3.1.2-py3-none-any.whl.metadata (5.1 kB)
Collecting jsonschema (from ansible-rulebook)
  Using cached jsonschema-4.21.1-py3-none-any.whl.metadata (7.8 kB)
Requirement already satisfied: jinja2 in ./ansible_latest/lib64/python3.11/site-packages (from ansible-rulebook) (3.1.3)
Collecting dpath>=2.1.4 (from ansible-rulebook)
  Using cached dpath-2.1.6-py3-none-any.whl.metadata (15 kB)
Collecting janus (from ansible-rulebook)
  Using cached janus-1.0.0-py3-none-any.whl.metadata (4.5 kB)
Collecting ansible-runner (from ansible-rulebook)
  Using cached ansible_runner-2.3.6-py3-none-any.whl.metadata (3.5 kB)
Collecting websockets (from ansible-rulebook)
  Using cached websockets-12.0-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Collecting drools-jpy==0.3.9 (from ansible-rulebook)
  Using cached drools_jpy-0.3.9-py3-none-any.whl.metadata (15 kB)
Collecting watchdog (from ansible-rulebook)
  Using cached watchdog-4.0.0-py3-none-manylinux2014_x86_64.whl.metadata (37 kB)
Collecting jpy (from drools-jpy==0.3.9->ansible-rulebook)
  Downloading jpy-0.16.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (15 kB)
Collecting aiosignal>=1.1.2 (from aiohttp->ansible-rulebook)
  Using cached aiosignal-1.3.1-py3-none-any.whl.metadata (4.0 kB)
Collecting attrs>=17.3.0 (from aiohttp->ansible-rulebook)
  Using cached attrs-23.2.0-py3-none-any.whl.metadata (9.5 kB)
Collecting frozenlist>=1.1.1 (from aiohttp->ansible-rulebook)
  Using cached frozenlist-1.4.1-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (12 kB)
Collecting multidict<7.0,>=4.5 (from aiohttp->ansible-rulebook)
  Using cached multidict-6.0.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.2 kB)
Collecting yarl<2.0,>=1.0 (from aiohttp->ansible-rulebook)
  Using cached yarl-1.9.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (31 kB)
Collecting pexpect>=4.5 (from ansible-runner->ansible-rulebook)
  Using cached pexpect-4.9.0-py2.py3-none-any.whl.metadata (2.5 kB)
Requirement already satisfied: packaging in ./ansible_latest/lib64/python3.11/site-packages (from ansible-runner->ansible-rulebook) (24.0)
Collecting python-daemon (from ansible-runner->ansible-rulebook)
  Using cached python_daemon-3.0.1-py3-none-any.whl.metadata (2.2 kB)
Requirement already satisfied: pyyaml in ./ansible_latest/lib64/python3.11/site-packages (from ansible-runner->ansible-rulebook) (6.0.1)
Collecting six (from ansible-runner->ansible-rulebook)
  Using cached six-1.16.0-py2.py3-none-any.whl.metadata (1.8 kB)
Collecting typing-extensions>=3.7.4.3 (from janus->ansible-rulebook)
  Using cached typing_extensions-4.10.0-py3-none-any.whl.metadata (3.0 kB)
Requirement already satisfied: MarkupSafe>=2.0 in ./ansible_latest/lib64/python3.11/site-packages (from jinja2->ansible-rulebook) (2.1.5)
Collecting jsonschema-specifications>=2023.03.6 (from jsonschema->ansible-rulebook)
  Using cached jsonschema_specifications-2023.12.1-py3-none-any.whl.metadata (3.0 kB)
Collecting referencing>=0.28.4 (from jsonschema->ansible-rulebook)
  Using cached referencing-0.34.0-py3-none-any.whl.metadata (2.8 kB)
Collecting rpds-py>=0.7.1 (from jsonschema->ansible-rulebook)
  Using cached rpds_py-0.18.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.1 kB)
Collecting ptyprocess>=0.5 (from pexpect>=4.5->ansible-runner->ansible-rulebook)
  Using cached ptyprocess-0.7.0-py2.py3-none-any.whl.metadata (1.3 kB)
Collecting idna>=2.0 (from yarl<2.0,>=1.0->aiohttp->ansible-rulebook)
  Using cached idna-3.6-py3-none-any.whl.metadata (9.9 kB)
Collecting docutils (from python-daemon->ansible-runner->ansible-rulebook)
  Using cached docutils-0.20.1-py3-none-any.whl.metadata (2.8 kB)
Collecting lockfile>=0.10 (from python-daemon->ansible-runner->ansible-rulebook)
  Using cached lockfile-0.12.2-py2.py3-none-any.whl.metadata (2.4 kB)
Requirement already satisfied: setuptools>=62.4.0 in ./ansible_latest/lib64/python3.11/site-packages (from python-daemon->ansible-runner->ansible-rulebook) (65.5.1)
Using cached ansible_rulebook-1.0.6-py3-none-any.whl (74 kB)
Using cached drools_jpy-0.3.9-py3-none-any.whl (6.6 MB)
Using cached dpath-2.1.6-py3-none-any.whl (17 kB)
Downloading pyparsing-3.1.2-py3-none-any.whl (103 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 103.2/103.2 kB 12.6 MB/s eta 0:00:00
Using cached aiohttp-3.9.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.3 MB)
Using cached ansible_runner-2.3.6-py3-none-any.whl (81 kB)
Using cached janus-1.0.0-py3-none-any.whl (6.9 kB)
Using cached jsonschema-4.21.1-py3-none-any.whl (85 kB)
Using cached watchdog-4.0.0-py3-none-manylinux2014_x86_64.whl (82 kB)
Using cached websockets-12.0-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (130 kB)
Using cached aiosignal-1.3.1-py3-none-any.whl (7.6 kB)
Using cached attrs-23.2.0-py3-none-any.whl (60 kB)
Using cached frozenlist-1.4.1-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (272 kB)
Using cached jsonschema_specifications-2023.12.1-py3-none-any.whl (18 kB)
Using cached multidict-6.0.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (128 kB)
Using cached pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
Using cached referencing-0.34.0-py3-none-any.whl (26 kB)
Using cached rpds_py-0.18.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.1 MB)
Using cached typing_extensions-4.10.0-py3-none-any.whl (33 kB)
Using cached yarl-1.9.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (328 kB)
Downloading jpy-0.16.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (350 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 350.6/350.6 kB 29.9 MB/s eta 0:00:00
Using cached python_daemon-3.0.1-py3-none-any.whl (31 kB)
Using cached six-1.16.0-py2.py3-none-any.whl (11 kB)
Using cached idna-3.6-py3-none-any.whl (61 kB)
Using cached lockfile-0.12.2-py2.py3-none-any.whl (13 kB)
Using cached ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
Using cached docutils-0.20.1-py3-none-any.whl (572 kB)
Installing collected packages: ptyprocess, lockfile, websockets, watchdog, typing-extensions, six, rpds-py, pyparsing, pexpect, multidict, jpy, idna, frozenlist, dpath, docutils, attrs, yarl, referencing, python-daemon, janus, drools-jpy, aiosignal, jsonschema-specifications, ansible-runner, aiohttp, jsonschema, ansible-rulebook
Successfully installed aiohttp-3.9.3 aiosignal-1.3.1 ansible-rulebook-1.0.6 ansible-runner-2.3.6 attrs-23.2.0 docutils-0.20.1 dpath-2.1.6 drools-jpy-0.3.9 frozenlist-1.4.1 idna-3.6 janus-1.0.0 jpy-0.16.0 jsonschema-4.21.1 jsonschema-specifications-2023.12.1 lockfile-0.12.2 multidict-6.0.5 pexpect-4.9.0 ptyprocess-0.7.0 pyparsing-3.1.2 python-daemon-3.0.1 referencing-0.34.0 rpds-py-0.18.0 six-1.16.0 typing-extensions-4.10.0 watchdog-4.0.0 websockets-12.0 yarl-1.9.4
```

#### Install Ansible Galaxy Collection for Ansible EDA

```shell
(ansible_latest) [root@devnetbox ~]# ansible-galaxy collection install ansible.eda
Starting galaxy collection install process
Process install dependency map
Starting collection install process
Downloading https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/artifacts/ansible-eda-1.4.5.tar.gz to /root/.ansible/tmp/ansible-local-3020711drwkdmnk/tmpcay0ta9p/ansible-eda-1.4.5-j62f2z7n
Installing 'ansible.eda:1.4.5' to '/root/.ansible/collections/ansible_collections/ansible/eda'
ansible.eda:1.4.5 was installed successfully
(ansible_latest) [root@devnetbox ~]# 
[root@devnetbox ~]# ls -la ~/.ansible/collections/ansible_collections/
total 0
drwx------. 4 root root 51 Mar 28 00:05 .
drwx------. 3 root root 33 Mar 28 00:05 ..
drwx------. 3 root root 17 Mar 28 00:05 ansible
drwx------. 2 root root 24 Mar 28 00:05 ansible.eda-1.4.5.info
[root@devnetbox ~]# 
```

#### Install Ansible Galaxy Collection for ServiceNow (Optional)
`Note:` If you like to integrate Ansible with ServiceNow, you can use this ServiceNow Ansible Galaxy collection.

```shell
(ansible_latest) [root@devnetbox ~]# ansible-galaxy collection install servicenow.itsm
Starting galaxy collection install process
Process install dependency map
Starting collection install process
Downloading https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/artifacts/servicenow-itsm-2.5.0.tar.gz to /root/.ansible/tmp/ansible-local-2950139m4v9qrg8/tmpxmrwtccw/servicenow-itsm-2.5.0-zv1r49dc
Installing 'servicenow.itsm:2.5.0' to '/root/.ansible/collections/ansible_collections/servicenow/itsm'
servicenow.itsm:2.5.0 was installed successfully
(ansible_latest) [root@devnetbox ~]# 
```

#### Generate SSH Keys (Optional)
`Note:` This is only required if you like to use SSH Keys to pull githib repo without using password. You need to add your public key to Github in the Settings.

```shell
(ansible_latest) [root@devnetbox ~]# ssh-keygen -t rsa -b 4096 -C "user@example.com" -f ~/.ssh/id_rsa -N ""
Generating public/private rsa key pair.
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:vNe46j5iiWsNvoKNUR4Z4OGZvoVfBeLIJtfm0M5l8Ps murafi@cisco.com
The key's randomart image is:
+---[RSA 4096]----+
|.o ...           |
|+ Bo.o.          |
|.Oo++ +.         |
|+.=* o.o         |
| = o+.. S        |
|. = o  . . o     |
| * o + .E o .    |
|o o + = .. .     |
|   oo+ ++o.      |
+----[SHA256]-----+
(ansible_latest) [root@devnetbox ~]# ls -l ~/.ssh
total 16
-rw-------. 1 root root  560 Dec 15 01:46 authorized_keys
-rw-------. 1 root root 3381 Mar 27 23:27 id_rsa
-rw-------. 1 root root  742 Mar 27 23:27 id_rsa.pub
-rw-r--r--. 1 root root  352 Mar  7 15:37 known_hosts
(ansible_latest) [root@devnetbox ~]# cat ~/.ssh/id_rsa.pub 
ssh-rsa AAAAB3NzaC1yc2 ..Omitted ..FS5bb1FJvzo1qTmPnm+Uvhw== user@example.com
(ansible_latest) [root@devnetbox ~]#
```

#### Install Curl and Java Oracle JDK
```shell
(ansible_latest) [root@devnetbox rulebooks]# dnf install curl -y
Last metadata expiration check: 0:01:13 ago on Wed 27 Mar 2024 11:43:05 PM GMT.
Package curl-7.61.1-30.el8_8.3.x86_64 is already installed.
Dependencies resolved.
Nothing to do.
Complete!
(ansible_latest) [root@devnetbox ~]# curl -qO https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.rpm
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  173M  100  173M    0     0  64.6M      0  0:00:02  0:00:02 --:--:-- 64.6M
(ansible_latest) [root@devnetbox]# ls -l
total 177948
-rw-------. 1 root root 182211002 Mar 27 23:45 jdk-17_linux-x64_bin.rpm
(ansible_latest) [root@devnetbox ~]#
(ansible_latest) [root@devnetbox ~]# rpm -ivh jdk-17_linux-x64_bin.rpm
warning: jdk-17_linux-x64_bin.rpm: Header V3 RSA/SHA256 Signature, key ID ad986da3: NOKEY
Verifying...                          ################################# [100%]
Preparing...                          ################################# [100%]
Updating / installing...
   1:jdk-17-2000:17.0.10-11           ################################# [100%]
(ansible_latest) [root@devnetbox ~]# java --version
java 17.0.10 2024-01-16 LTS
Java(TM) SE Runtime Environment (build 17.0.10+11-LTS-240)
Java HotSpot(TM) 64-Bit Server VM (build 17.0.10+11-LTS-240, mixed mode, sharing)
(ansible_latest) [root@devnetbox ~]# 
(ansible_latest) [root@devnetbox ~]# sudo update-alternatives --config java

There are 2 programs which provide 'java'.

  Selection    Command
-----------------------------------------------
   1           java-1.8.0-openjdk.x86_64 (/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.392.b08-4.el8.x86_64/jre/bin/java)
*+ 2           /usr/lib/jvm/jdk-17-oracle-x64/bin/java

Enter to keep the current selection[+], or type selection number: ^C
(ansible_latest) [root@devnetbox ~]#
```
`Note:` Make sure * is pointed to the required Java version, Ctrl+c to exit, otherwise select the required option, '2' in my case.

```shell
(ansible_latest) [root@devnetbox ~]# alternatives --config javac

There is 1 program that provides 'javac'.

  Selection    Command
-----------------------------------------------
*+ 1           /usr/lib/jvm/jdk-17-oracle-x64/bin/javac
(ansible_latest) [root@devnetbox ~]# javac --version
javac 17.0.10
(ansible_latest) [root@devnetbox ~]# ls -l /usr/lib/jvm/jdk-17-oracle-x64/
total 28
drwxr-xr-x.  2 root root 4096 Mar 27 23:45 bin
drwxr-xr-x.  5 root root  123 Mar 27 23:45 conf
drwxr-xr-x.  3 root root  132 Mar 27 23:45 include
drwxr-xr-x.  2 root root 4096 Mar 27 23:45 jmods
drwxr-xr-x. 72 root root 4096 Mar 27 23:45 legal
drwxr-xr-x.  6 root root 4096 Mar 27 23:45 lib
lrwxrwxrwx.  1 root root   23 Dec 19 21:50 LICENSE -> legal/java.base/LICENSE
drwxr-xr-x.  3 root root   18 Mar 27 23:45 man
-rw-r--r--.  1 root root  290 Dec 19 21:50 README
-rw-r--r--.  1 root root 1274 Dec 19 21:50 release
(ansible_latest) [root@devnetbox ~]#
(ansible_latest) [root@devnetbox ~]# alternatives --list
libnssckbi.so.x86_64    auto    /usr/lib64/pkcs11/p11-kit-trust.so
python                  auto    /usr/libexec/no-python
cifs-idmap-plugin       auto    /usr/lib64/cifs-utils/cifs_idmap_sss.so
mta                     auto    /usr/sbin/sendmail.postfix
ld                      auto    /usr/bin/ld.bfd
java                    auto    /usr/lib/jvm/jdk-17-oracle-x64/bin/java
jre_openjdk             auto    /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.392.b08-4.el8.x86_64/jre
jre_1.8.0               auto    /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.392.b08-4.el8.x86_64/jre
jre_1.8.0_openjdk       auto    /usr/lib/jvm/jre-1.8.0-openjdk-1.8.0.392.b08-4.el8.x86_64
python3                 auto    /usr/bin/python3.11
nmap                    auto    /usr/bin/ncat
javac                   auto    /usr/lib/jvm/jdk-17-oracle-x64/bin/javac
(ansible_latest) [root@devnetbox ~]#
```

#### Set Java Home Environmental Variable 
`Note:` Pickup the path for Java from last step output 

```shell
(ansible_latest) [root@devnetbox ~]#  export JAVA_HOME="/usr/lib/jvm/jdk-17-oracle-x64"
(ansible_latest) [root@devnetbox ~]# echo $JAVA_HOME
/usr/lib/jvm/jdk-17-oracle-x64
```

#### Install Latest Java OpenJDK 
`Note:` You may like to install Java Open JDK, however it was failed to installed for me, So I used Java Oracle JDK only as mentioned in my previous step. You only need one of these.

```shell
(ansible_latest) [root@devnetbox rulebooks]# dnf install java-17-openjdk java-17-openjdk-devel
runner_gitlab-runner                                                                    1.9 kB/s | 1.0 kB     00:00    
runner_gitlab-runner-source                                                             3.6 kB/s | 951  B     00:00    
Dependencies resolved.
========================================================================================================================
 Package                            Architecture     Version                         Repository                    Size
========================================================================================================================
Installing:
 java-17-openjdk                    x86_64           1:17.0.10.0.7-2.el8             systuning_alma8_64           459 k
 java-17-openjdk-devel              x86_64           1:17.0.10.0.7-2.el8             appstream                    5.1 M
Installing dependencies:
 alsa-lib                           x86_64           1.2.9-1.el8                     systuning_alma8_64           496 k
 java-17-openjdk-headless           x86_64           1:17.0.10.0.7-2.el8             systuning_alma8_64            46 M
 libXtst                            x86_64           1.2.3-7.el8                     systuning_alma8_64            21 k
 ttmkfdir                           x86_64           3.0.9-54.el8                    systuning_alma8_64            61 k
 xorg-x11-fonts-Type1               noarch           7.5-19.el8                      systuning_alma8_64           521 k

Transaction Summary
========================================================================================================================
Install  7 Packages

Total download size: 53 M
Installed size: 209 M
Is this ok [y/N]: y
Downloading Packages:
(1/7): ttmkfdir-3.0.9-54.el8.x86_64.rpm                                                 1.9 MB/s |  61 kB     00:00    
(2/7): libXtst-1.2.3-7.el8.x86_64.rpm                                                   5.5 MB/s |  21 kB     00:00    
(3/7): java-17-openjdk-17.0.10.0.7-2.el8.x86_64.rpm                                      10 MB/s | 459 kB     00:00    
(4/7): alsa-lib-1.2.9-1.el8.x86_64.rpm                                                  9.5 MB/s | 496 kB     00:00    
(5/7): xorg-x11-fonts-Type1-7.5-19.el8.noarch.rpm                                        20 MB/s | 521 kB     00:00    
(6/7): java-17-openjdk-devel-17.0.10.0.7-2.el8.x86_64.rpm                                28 MB/s | 5.1 MB     00:00    
(7/7): java-17-openjdk-headless-17.0.10.0.7-2.el8.x86_64.rpm                             72 MB/s |  46 MB     00:00    
------------------------------------------------------------------------------------------------------------------------
Total                                                                                    62 MB/s |  53 MB     00:00     
AlmaLinux 8 - AppStream                                                                 466 kB/s | 3.4 kB     00:00    
Importing GPG key 0xC21AD6EA:
 Userid     : "AlmaLinux <packager@almalinux.org>"
 Fingerprint: E53C F5EF 91CE B0AD 1812 ECB8 51D6 647E C21A D6EA
 From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux
Is this ok [y/N]: y
Key imported successfully
Import of key(s) didn't help, wrong key(s)?
Public key for java-17-openjdk-devel-17.0.10.0.7-2.el8.x86_64.rpm is not installed. Failing package is: java-17-openjdk-devel-1:17.0.10.0.7-2.el8.x86_64
 GPG Keys are configured as: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux
The downloaded packages were saved in cache until the next successful transaction.
You can remove cached packages by executing 'dnf clean packages'.
 GPG Keys are configured as: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-AlmaLinux
Error: GPG check FAILED
(ansible_latest) [root@devnetbox rulebooks]# java --version
Unrecognized option: --version
Error: Could not create the Java Virtual Machine.
Error: A fatal exception has occurred. Program will exit.
(ansible_latest) [root@devnetbox rulebooks]#
```
`Reference: https://www.howtoforge.com/how-to-install-java-openjdk-oraclejdk-on-almalinux-9/#installing-java-openjdk--2`

#### Clone Cisco Ansible Repository

```shell
(ansible_latest) [root@devnetbox ~]# git clone git@github.com:muhammad-rafi/cisco-ansible-eda.git
Cloning into 'cisco-ansible-eda'...
The authenticity of host 'github.com (140.82.113.3)' can't be established.
ECDSA key fingerprint is SHA256:p2QAMXNIC1TJYWeIOttrVc98/R1BUFWu3/LiyKgUfQM.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'github.com,140.82.113.3' (ECDSA) to the list of known hosts.
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 4 (delta 0), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (4/4), done.
(ansible_latest) [root@devnetbox ~]#
```

#### Run your first Ansible Rulebook

```shell
(ansible_latest) [root@devnetbox cisco-ansible-eda]# ansible-rulebook --rulebook rulebooks/webhook-rulebook.yml -i cml_hosts.yml --verbose
2024-03-28 00:22:52,203 - ansible_rulebook.app - INFO - Starting sources
2024-03-28 00:22:52,203 - ansible_rulebook.app - INFO - Starting rules
2024-03-28 00:22:52,203 - drools.ruleset - INFO - Using jar: /root/ansible_latest/lib/python3.11/site-packages/drools/jars/drools-ansible-rulebook-integration-runtime-1.0.6-SNAPSHOT.jar
2024-03-28 00:22:52 958 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.AbstractRulesEvaluator - Start automatic pseudo clock with a tick every 100 milliseconds
2024-03-28 00:22:52,978 - ansible_rulebook.engine - INFO - load source ansible.eda.webhook
2024-03-28 00:22:53,574 - ansible_rulebook.engine - INFO - loading source filter eda.builtin.insert_meta_info
2024-03-28 00:22:54,085 - ansible_rulebook.engine - INFO - Waiting for all ruleset tasks to end
2024-03-28 00:22:54,086 - ansible_rulebook.rule_set_runner - INFO - Waiting for actions on events from Listen for events on a webhook
2024-03-28 00:22:54,086 - ansible_rulebook.rule_set_runner - INFO - Waiting for events, ruleset: Listen for events on a webhook
2024-03-28 00:22:54 086 [drools-async-evaluator-thread] INFO org.drools.ansible.rulebook.integration.api.io.RuleExecutorChannel - Async channel connected
2024-03-28 00:23:07,280 - aiohttp.access - INFO - 10.209.208.186 [28/Mar/2024:00:23:07 +0000] "POST /endpoint HTTP/1.1" 200 159 "-" "curl/8.4.0"
2024-03-28 00:23:07 283 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.MemoryMonitorUtil - Memory occupation threshold set to 90%
2024-03-28 00:23:07 283 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.MemoryMonitorUtil - Memory check event count threshold set to 64
2024-03-28 00:23:07 283 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.MemoryMonitorUtil - Exit above memory occupation threshold set to false

PLAY [Display Messages Playbook] ***********************************************

TASK [Print all Available Facts] ***********************************************
ok: [localhost] => {
    "ansible_facts": {}
}

TASK [Check Ansible version] ***************************************************
changed: [localhost]

TASK [Print Ansible Version] ***************************************************
ok: [localhost] => {
    "msg": "Ansible Version: ansible [core 2.16.5]\n  config file = None\n  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']\n  ansible python module location = /root/ansible_latest/lib64/python3.11/site-packages/ansible\n  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections\n  executable location = /root/ansible_latest/bin/ansible\n  python version = 3.11.2 (main, Jun 22 2023, 06:07:18) [GCC 8.5.0 20210514 (Red Hat 8.5.0-18)] (/root/ansible_latest/bin/python3)\n  jinja version = 3.1.3\n  libyaml = True"
}

TASK [Print Success Message] ***************************************************
ok: [localhost] => {
    "msg": "You nailed it, you hit this playbook by \nrunning your rulebook :)\n"
}

PLAY RECAP *********************************************************************
localhost                  : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
2024-03-28 00:23:09,490 - ansible_rulebook.action.runner - INFO - Ansible runner Queue task cancelled
2024-03-28 00:23:09,492 - ansible_rulebook.action.run_playbook - INFO - Ansible runner rc: 0, status: successful
```

`Note:` Notice the output is not formatted properly, You can use `ANSIBLE_STDOUT_CALLBACK` to make the output pretty but it depends on the ansible config you have.

```shell
(ansible_latest) [root@devnetbox cisco-ansible-eda]# export ANSIBLE_STDOUT_CALLBACK=yaml
(ansible_latest) [root@devnetbox cisco-ansible-eda]#
(ansible_latest) [root@devnetbox cisco-ansible-eda]# ansible-rulebook --rulebook rulebooks/webhook-rulebook.yml -i cml_hosts.yml --verbose
2024-03-28 00:30:07,099 - ansible_rulebook.app - INFO - Starting sources
2024-03-28 00:30:07,100 - ansible_rulebook.app - INFO - Starting rules
2024-03-28 00:30:07,101 - drools.ruleset - INFO - Using jar: /root/ansible_latest/lib/python3.11/site-packages/drools/jars/drools-ansible-rulebook-integration-runtime-1.0.6-SNAPSHOT.jar
2024-03-28 00:30:07 879 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.AbstractRulesEvaluator - Start automatic pseudo clock with a tick every 100 milliseconds
2024-03-28 00:30:07,905 - ansible_rulebook.engine - INFO - load source ansible.eda.webhook
2024-03-28 00:30:08,469 - ansible_rulebook.engine - INFO - loading source filter eda.builtin.insert_meta_info
2024-03-28 00:30:08,995 - ansible_rulebook.engine - INFO - Waiting for all ruleset tasks to end
2024-03-28 00:30:08,996 - ansible_rulebook.rule_set_runner - INFO - Waiting for actions on events from Listen for events on a webhook
2024-03-28 00:30:08,996 - ansible_rulebook.rule_set_runner - INFO - Waiting for events, ruleset: Listen for events on a webhook
2024-03-28 00:30:08 996 [drools-async-evaluator-thread] INFO org.drools.ansible.rulebook.integration.api.io.RuleExecutorChannel - Async channel connected
2024-03-28 00:30:09,711 - aiohttp.access - INFO - 10.209.208.186 [28/Mar/2024:00:30:09 +0000] "POST /endpoint HTTP/1.1" 200 159 "-" "curl/8.4.0"
2024-03-28 00:30:09 714 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.MemoryMonitorUtil - Memory occupation threshold set to 90%
2024-03-28 00:30:09 714 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.MemoryMonitorUtil - Memory check event count threshold set to 64
2024-03-28 00:30:09 715 [main] INFO org.drools.ansible.rulebook.integration.api.rulesengine.MemoryMonitorUtil - Exit above memory occupation threshold set to false

PLAY [Display Messages Playbook] ***********************************************

TASK [Print all Available Facts] ***********************************************
ok: [localhost] => 
  ansible_facts: {}

TASK [Check Ansible version] ***************************************************
changed: [localhost]

TASK [Print Ansible Version] ***************************************************
ok: [localhost] => 
  msg: |-
    Ansible Version: ansible [core 2.16.5]
      config file = None
      configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
      ansible python module location = /root/ansible_latest/lib64/python3.11/site-packages/ansible
      ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
      executable location = /root/ansible_latest/bin/ansible
      python version = 3.11.2 (main, Jun 22 2023, 06:07:18) [GCC 8.5.0 20210514 (Red Hat 8.5.0-18)] (/root/ansible_latest/bin/python3)
      jinja version = 3.1.3
      libyaml = True

TASK [Print Success Message] ***************************************************
ok: [localhost] => 
  msg: |-
    You nailed it, you hit this playbook by
    running your rulebook :)

PLAY RECAP *********************************************************************
localhost                  : ok=4    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
2024-03-28 00:30:12,402 - ansible_rulebook.action.runner - INFO - Ansible runner Queue task cancelled
2024-03-28 00:30:12,404 - ansible_rulebook.action.run_playbook - INFO - Ansible runner rc: 0, status: successful
```

That's it 😊, Hope you like this and if you do, please make sure you leave the star for this repo and reach out to me via [Linkedin](https://www.linkedin.com/in/muhammad-rafi-0a37a248/) if you have any queries or issues. 

#### References

[Event-Driven Ansible](https://www.redhat.com/en/technologies/management/ansible/event-driven-ansible)

[Getting Started with Event-Driven Ansible](https://www.ansible.com/blog/getting-started-with-event-driven-ansible)

[Demo: Getting started with Event-Driven Ansible and Ansible Rulebooks](https://www.youtube.com/watch?v=aqQq5vD8-n0)

[Event Driven Ansible Github Repo](https://github.com/ansible/event-driven-ansible)

Docker Images - wurstmeister/kafka/zookeeper
https://hub.docker.com/r/wurstmeister/kafka
https://hub.docker.com/r/wurstmeister/zookeeper
https://github.com/wurstmeister/kafka-docker

#### Author
[Muhammad Rafi](https://www.linkedin.com/in/muhammad-rafi-0a37a248/)