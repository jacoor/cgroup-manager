# Cgroup Management
This is a simple API to manage cgroups in Cent Os. It's a sample project.
## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
### Prerequisites
* python 3.6
* virtualenv
    For the both above you may use: https://janikarhunen.fi/how-to-install-python-3-6-1-on-centos-7.html
* nginx
* supervisord

### Installing
A step by step series of examples that tell you have to get a development environment running.
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
FIXME
Add additional notes about how to deploy this on a live system
## Possible improvements
* Creating Cgroup - return an error when cgroup already exists. Right now it uses `mkdir -p` to create directory structure, so it does not complain if directory is already there.

## Contributing
Pull requests welcome.
## Authors
* **Jacek Ostanski** - *Initial work* - [github](https://github.com/jacoor)

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details