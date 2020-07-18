# Setting Up Development Environment

* development_containers/riak/riak-rabbitmq-commit-hooks.tar.gz must be extracted to the same folder.

* Build images by running the 'script.sh' in dev folder. It must be run from dev folder.

> dev/ $ ./script.sh

### For Riak Development Environment Init

* Firstly riak must be configured so that dependent containers do not conomplains about absence of riak.

> dev/ $ docker-compose up -d riak_single

> dev/ $ docker exec -it dev_riak_single_1 /bin/sh

> \# riak-admin bucket-type create zopsm_rabbit_hook '{"props":{"postcommit":[{"mod":"riak_rabbitmq","fun":"postcommit_send_amqp"}]}}'

> \# riak-admin bucket-type activate zopsm_rabbit_hook

> \# riak-admin bucket-type create zopsm_logs '{"props":{"backend":"leveldb"}}'

> \# riak-admin bucket-type activate zopsm_logs

> \# riak-admin bucket-type create develop_logs '{"props":{"backend":"leveldb"}}'

> \# riak-admin bucket-type activate develop_logs

> \# riak-admin bucket-type create zopsm '{"props":{"backend":"leveldb"}}'

> \# riak-admin bucket-type activate zopsm

* Secondly set riak backend storage.

> \# vi /etc/riak/riak.conf

> storage_backend = leveldb

Then


Then it is time to make system up.

> dev/ $ export ZOPSM=/your/zopsm/repo/path

> dev/ $ docker-compose up

### For Saas Development Environment Database Init
> docker exec -it dev_saas_1 /bin/sh

> cd /usr/local/lib/python3.6/site-packages/zopsm/saas

> python manage.py init && python manage.py migrate && python manage.py upgrade

### Test User Init
> docker exec -it dev_db_1 /bin/sh

> psql -U zopsm

>insert into tenants(id,email,is_deleted,is_active,organization_name,address)
  values (1,'zopsm_tenant_manager@example.com',false,true,'zetaops','zetaland');

>insert into users(id,email,tenant_id,first_name,last_name,password,role) 
  values(1,'zopsm_tenant_manager@example.com',1,'zeta','ops','ce83a5931b8f85e15b2254dc551f8ec00abcb562638cc69afd657a7d3820b445a35c53772dac9d46c1d81d7b40d14893ecc1c087994ea5675b6e3ecc7e33b8e7','manager');


### Configuration of PyCharm for Run Tests Without Docker Container

> export PYCURL_SSL_LIBRARY=openssl

> export LDFLAGS=-L/usr/local/opt/openssl/lib

> export CPPFLAGS=-I/usr/local/opt/openssl/include

> pip install pycurl --compile --no-cache-dir

> cd Workspace

> Workspace/ $ mkdir resttest

> Workspace/ $ cd resttest

> Workspace/resttest $ virtualenv venv (python version 3.6)

> Workspace/ $ venv/bin/active

> (venv) Workspace/resttest $ pip install git+https://github.com/zetaops/pyresttest

> (venv) Workspace/resttest $ deactivate 

Then open PyCharm

* Add Python Interpreter
>Preferences

>Project:zopsm

>Project Interpreter

>Add Project Interpreter

>New Environment

>Location -> Workspace/resttest/venv/bin/python (python version 3.6) 

* Add Python Configuration

> Select Edit Configuration

* For Saas
> Add Python 

> Name -> pyresttest-saas

> Script path -> Workspace/resttest/venv/bin/pyresttest

> Parameters: -> ""
test_saas.yaml
--absolute-urls
--print-bodies=True
--vars
"{\"saas_host\":\"localhost:8000\", \"tenant_manager_email\":\"zopsm_tenant_manager@example.com\", \"manager_password\":\"9703262a38954448ad6ftr419b571500\"}"

> Python interpreter -> Python 3.6 (venv) (Select from resttest directory)

> Working directory -> Workspace/zopsm/tests

* For Push
> Add Python 

> Name -> pyresttest-push

> Script path -> Workspace/resttest/venv/bin/pyresttest

> Parameters: -> ""
test_saas.yaml
--absolute-urls
--print-bodies=True
--vars
"{\"saas_host\":\"localhost:8000\", \"tenant_manager_email\":\"zopsm_tenant_manager@example.com\", \"manager_password\":\"9703262a38954448ad6ftr419b571500\"}"

> Python interpreter -> Python 3.6 (venv) (Select from resttest directory)

> Working directory -> Workspace/zopsm/tests

* For Roc
> Add Python 

> Name -> pyresttest-roc

> Script path -> Workspace/resttest/venv/bin/pyresttest

> Parameters: -> ""
test_roc.yaml
--absolute-urls
--vars
"{\"saas_host\":\"localhost:8000\",\"roc_host\":\"localhost:8888\",\"auth_host_uri_prefix\":\"localhost:12345/v1/auth/token\",\"tenant_manager_email\":\"zopsm_tenant_manager@example.com\",\"manager_password\":\"9703262a38954448ad6ftr419b571500\"}"

> Python interpreter -> Python 3.6 (venv) (Select from resttest directory)

> Working directory -> Workspace/zopsm/tests

### Run Tests with Docker
> docker run --name resttest --rm --net host -v /your/zopsm/path:/usr/local/lib/python3.6/site-packages/zopsm zetaops/pyresttest pyresttest http://localhost:8000 /usr/local/lib/python3.6/site-packages/zopsm/tests/test_saas.yaml


### For Vault Settings ( unnecessary )
> docker exec -it dev_vault_1 /bin/sh

> First you should do vault auth and paste below token to work with vault.

> vault auth
  b258f5f2-fc67-24fe-3750-0055f625aa74

> vault mount -path=tokens kv


### Remote Debugging 
To debug the remote script, it must be added the following code snippet to top of the script. 
PyCharm remote debugger configuration must be configured respectively(host, port).

```python
import pydevd
pydevd.settrace('localhost', port=1234, stdoutToServer=True, stderrToServer=True)
```
