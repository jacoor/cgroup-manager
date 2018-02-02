# Cgroup Management
This is a simple API to manage cgroups in Cent Os. It's a sample project.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

#### Development
* git

#### Development and production
* python 3.6
* virtualenv
* gcc - missing on AWS CentOs images

For the both above you may use: https://janikarhunen.fi/how-to-install-python-3-6-1-on-centos-7.html

#### Production only
* nginx
* supervisord

### Installing
A step by step series of examples that tell you have to get a development environment running.

Clone the repository to your desired directory:

```
git clone git@github.com:jacoor/cgroup-manager.git
```

Install requirements:
```
    pip install -r requirements.txt
```
Apply migrations (the project uses sqlite):
```
    ./manage.py migrate
```
Run the project:
```
    ./manage.py runserver
```
Visit local server to verify it working:
```
    http://127.0.0.1:8000/api
```
The project in the current setup will not manage real cgroups because of insuficient privileges. To allow the project to work with real cgroups it needs root user access. Please modify your 'sudoers' file with the following command:
```
    sudo visudo
```
and add the following at the end of file:
```
    [username] ALL=(ALL)       NOPASSWD: /usr/bin/bash, /usr/bin/mkdir
```
### Swagger documentation
Check url:
```
    http://[domain]/api
```
## Running the tests
There are two ways to run the tests. Both should be run in virtualenv, from the main project directory.
Django builtin mechanism:
```
    ./manage.py test .
```
or pytest:
```
    pytest
```
## Deployment
Install tools mentioned in "Prerequisites" section and activate virtualenv.

Clone the repository into your desired location using HTTPS cloning:

```
    git clone https://github.com/jacoor/cgroup-manager.git
```

Update crontab

```
    crontab [path_to_project]/config/crontab
```

Collect static files

```
    ./manage.py collectstatic
```

Migrate database (uses sqlite)

```
    /home/centos/workspace/cgroup-manager/venv/bin/python manage.py migrate
```

Because of project simplicity static files are already in the repository.

Add nginx to your user group and modify file access rights.

```
    sudo usermod -a -G centos nginx
    chmod 710 /home/centos
```

Allow nginx to run in SELinux permissive mode (https://www.getpagespeed.com/server-setup/nginx/nginx-selinux-configuration)

```
    sudo semanage permissive -a httpd_t
```

Add commands to supervisord and nginx

```
    sudo cd /etc/nginx/conf.d && ln -sf /home/centos/workspace/cgroup-manager/config/production/nginx.conf cgroup_manager.conf
    sudo cd /etc/supervisord.d/ && ln -sf /home/centos/workspace/cgroup-manager/config/production/supervisord.conf cgroup_manager.ini
    sudo service supervisord start && supervisorctl reread && supervisorctl update
```

Starting nginx requires SELinux security context change:

```
    sudo chcon -v --type=httpd_config_t /etc/nginx/conf.d/cgroup_manager.conf
    sudo systemctl start nginx
```

Allow nginx to use network:

```
    sudo setsebool -P httpd_can_network_connect 1
```

Enable nginx and supervisor to start on boot

```
    sudo systemctl enable supervisorctl
    sudo systemctl enable nginx
```

The project in the current setup will not manage real cgroups because of insuficient privileges. To allow the project to work with real cgroups it needs root user access. Please modify your 'sudoers' file with the following command:

```
    sudo visudo
```

and add the following at the end of file:

```
    centos ALL=(ALL)       NOPASSWD: /usr/bin/bash, /usr/bin/mkdir
```

Go to:

```
    http://ec2-18-196-5-59.eu-central-1.compute.amazonaws.com/api
```

to verify project working.

## Possible improvements

* Creating Cgroup - return an error when cgroup already exists. Right now it uses `mkdir -p` to create directory structure, so it does not complain if directory is already there.

## Contributing
Pull requests welcome.

## Authors
* **Jacek Ostanski** - *Initial work* - [github](https://github.com/jacoor)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details