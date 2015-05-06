# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|

  config.vm.box = "hashicorp/precise32"
  config.vm.synced_folder ".", "/vagrant_data"

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
   config.vm.provision "shell", inline: <<-SHELL
     sudo add-apt-repository -y ppa:fkrull/deadsnakes
     sudo apt-get update
     sudo apt-get install -y python2.7 python2.7-dev
     sudo apt-get install -y python-pip
     sudo pip install virtualenv
     virtualenv -p python2.7 venv27
   SHELL
end
