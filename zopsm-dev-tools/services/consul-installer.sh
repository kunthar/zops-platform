#!/usr/bin/env bash
#set -x

initial_info() {
  server_or_client="$1"
  bootstrap="$2"
  consul_version="$3"
  ipaddress=$(ifconfig -a eth0 | grep "inet addr:" | cut -d ':' -f 2 | cut -d ' ' -f1)
  hostname=$(hostname)
}

setup_consul() {
  # Download an unzip to /usr/local/bin
  cd "$HOME"
  echo $consul_version
        echo "Installing consul under /usr/local/bin"
        apt-get install unzip
        wget https://releases.hashicorp.com/consul/"$consul_version"/consul_"$consul_version"_linux_amd64.zip > /dev/null
        unzip -o "$PWD"/consul_"$consul_version"_linux_amd64.zip -d /usr/local/bin/ > /dev/null
        chmod +x /usr/local/bin/consul
        rm "$PWD"/consul_"$consul_version"_linux_amd64.zip
}

create_consul_user_and_set_permissions() {
  # Create consul user and group
  echo "Creating user consul and group consul"
  getent group consul > /dev/null
  if [[ "$?" -eq 0 ]]; then
    echo "Consul group already exists. PASSING!"
  else
    echo "Adding consul group."
    groupadd consul
  fi

  # Create consul user if necessary
  getent passwd consul > /dev/null
  if [[ "$?" -eq 0 ]]; then
    echo "Consul user already exists. PASSING!"
  else
    echo "Adding consul user."
    useradd consul -M -g consul
  fi

  # Create directories if necessary
  echo "Creating /etc/consul.d, /opt/consul-data, /run/consul"
  mkdir -p /etc/consul.d
  mkdir -p /opt/consul-data
  mkdir -p /run/consul

  # Change ownership of consul directories
  echo "Setting up permissions for /etc/consul.d, /opt/consul-data, /run/consul"
  chown consul:consul /etc/consul.d
  chown consul:consul /opt/consul-data
  chown consul:consul /run/consul
}


create_consul_service() {
# Setup consul.service
echo "Creating consul.service under /etc/systemd/system/"
cat > /etc/systemd/system/consul.service <<-EOM
[Unit]
Description=Consul service discovery agent
Requires=network-online.target
After=network.target

[Service]
User=consul
Group=consul
PIDFile=/run/consul/consul.pid
Restart=on-failure
Environment=GOMAXPROCS=2
ExecStart=/usr/local/bin/consul agent $OPTIONS -config-dir=/etc/consul.d -data-dir=/opt/consul-data
ExecReload=/bin/kill -s HUP $MAINPID
KillSignal=SIGINT
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOM

  chown root:root /etc/systemd/system/consul.service
  chmod 0644 /etc/systemd/system/consul.service
}

create_initial_consul_config() {
# Setup consul configuration
if [[ "$server_or_client" == "server" ]]; then
  echo "export CONSUL_HTTP_ADDR=$ipaddress:8500" >> /home/ubuntu/.bashrc
  echo  "Setting server configuration for consul"
  if [[ $bootstrap == "true" ]]; then
        boot='"bootstrap_expect": 3,'
  else
        boot='"bootstrap": false,'
  fi
  server=$(cat > /etc/consul.d/server.json <<-END
    {
      $boot
      "datacenter": "dc1",
      "data_dir": "/opt/consul-data",
      "log_level": "INFO",
      "node_name": "$hostname",
      "server": true,
      "addresses": {
        "http": "$ipaddress"
       },
       "bind_addr": "$ipaddress"
    }
END
)
else
   echo  "Setting client configuration for consul"
   client=$(cat > /etc/consul.d/client.json <<-END
    {
      "datacenter": "dc1",
      "data_dir": "/opt/consul-data",
      "log_level": "INFO",
      "node_name": "$hostname",
      "server": false,
      "bind_addr": "$ipaddress"
    }
END
)
fi
}

main() {
  initial_info "$1" "$2" "$3"
  setup_consul
  create_consul_user_and_set_permissions
  if [[ -e /etc/systemd/system/consul.service ]]; then
    create_consul_service
    echo "Reloaded consul.service"
    systemctl daemon-reload
  else
    create_consul_service
  fi

  create_initial_consul_config

  # Start consul.service
  systemctl start consul.service
  systemctl enable consul.service
}

main "$@"
