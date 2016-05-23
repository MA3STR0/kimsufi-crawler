V_NAME="kimsufi-crawler"

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.ssh.forward_agent = true

  config.vm.network "public_network"

  config.vm.provision "shell", inline: $provision

  config.vm.hostname = V_NAME

  config.vm.provider "virtualbox" do |v|
    v.name   = V_NAME
    v.memory = 2048
  end
end

$provision = <<SCRIPT
# variables
HTML_PATH="/home/vagrant/html/"
HTML_FILE_NAME="kimsufi-crawler.html"
# install required packages
apt-get update
apt-get upgrade -y
apt-get install -y nginx git python python-pip
# nginx
mkdir -p $HTML_PATH
echo 'NOT AVAILABLE' > "$HTML_PATH/$HTML_FILE_NAME"
rm -f /etc/nginx/sites-enabled/default
cat << EOF > /etc/nginx/sites-enabled/kimsufi-crawler.conf
server {
    listen          80;
    server_name     localhost;
    root            $HTML_PATH;
}
EOF
service nginx reload
# python
cd /vagrant
pip install --pre -r requirements.txt
chown -R vagrant:vagrant /home/vagrant/*
# conf
if [ ! -f config.json ]; then
cat << EOF > /vagrant/config.json
{
    "servers": ["KS-2E"],
    "region": "europe",
    "notifier": "file",
    "file_path": "$HTML_PATH/$HTML_FILE_NAME",
    "crawler_interval": 8,
    "request_timeout": 15
}
EOF
fi
echo '*************************************************************************'
ifconfig
SCRIPT