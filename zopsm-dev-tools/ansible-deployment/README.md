# Requirements
 - create ssh key under ansible-station if not exist
 - create ssh keys, adjust all servers to use same key
 - Ansible 2.5.5.
 - Before usings playbooks, you should do ```sudo apt-get install python``` on all nodes.

# Usage

- cd into /Users/cem/projects/zopsm/dev_tools/ansible-deployment .
- run ```ansible-playbook -i hosts-tmp playbooks/playbook-name.yml```

# Playbooks

- Consul
  - Uses services/consul-installer.sh script to install consul environment.
  - Joins all nodes to consul leader.
  - run consul_servers.yml
  - run consul_clients.yml
  - run consul_ssl.yml
  
- Riak
  - Installs riak on riak group.
  - Updates configuration and system settings.
  - Makes cluster.
  - Installs riak-rabbitmq-commit-hooks on all nodes' /var/lib/riak/lib.
  - Creates and activates, hook bucket-type and zopsm_logs bucket-type.
  - Registers riak service and health check to consul.
  
- RabbitMQ
  - Installs RabbitMQ on rabbitmq group.
  - Creates zopsm vhost and zopsm user.
  - Makes cluster.
  - Defines zopsm_message and zopsm_rpc policies.
  - Registers rabbitmq service and health check to consul.
  
- Redis
  - Installs Redis on redis group.
  - Makes master and slave nodes with specified groups.
  - Updates bind option in redis.conf .
  - Registers redis service and health check to consul.
  
- PostgreSQL
 - Installs postgres
 - Check backup files first. Do not run postgresql_10_logical_replication.yml before this.
 - Use postgresql_10_logical_replication.yml only in case there is no backup file
   will be used.
 - Backups located in postgresql server's /var/backups/postgresql/ path
 - Copy patroni configs(patroni01.yml, patroni02.yml) to machine, and run patroni.service
  
- Vault
 - Run vault.yml
 - Run vault_ssl.yml
 - ssh to vault nodes, follow this https://www.vaultproject.io/intro/getting-started/deploy.html
 - check vault backend consul is properly configured.
 - vault init in one node
 - vault unseal in vault nodes
 - bb.hcl, testing.hcl, tokens.hcl 
 - final test: in command line of vault node run this, `vault write` any path in policies `value`
 - put zetaopsbot into secret/bb on vault node
 - buildbot/container.yml,
  change VAULT_TOKEN(bb.hcl), VAULT_PROD_TOKEN(tokens.hcl), VAULT_TESTING_TOKEN(testing.hcl) env variables
  
- Docker
  - docker-install
    - Installs docker for Ubuntu.
    - Opens Docker API.
    - docker-install.yml
  - docker-images
    - docker-images.yml
    - Builds zopsm-base, mda, worker, auth, gateway  docker images.
  - docker-containers
    - initial-run.yml, run once. Buildbot will handle the rest of docker operations.
    - Runs mda, worker, auth, gateway containers with options.

- Buildbot
 - run buildbot/images.yml to build master and workers
 - run buildbot/containers.yml to run buildbot master
 - buildbot/docker-containers.yml will be used for production, buildbot/frontend.yml for zops.io
 
- Haproxy/Consul Template
 - run haproxy-consul-template.yml
 - change `address` in consul-template.hcl with one of consul-server's ip

- Security
- run create_user.yml 
- run firehol.yml, run ssh.yml
