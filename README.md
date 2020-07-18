# ZOPS CPaaS Platform


![](https://zetaops.io/static/assets/images/products/zops-cpaas/zops-m2m-main-small.jpg)



* ZOPS CPaaS Platform* is an integrated messaging platform to carry on different types of messages for web and mobile applications.
Messaging is quite necessary in modern applications, SMS message, PUSH message, real-time online messaging for communication with users.
Development companies want to maintain communication with the users over different message types according to the scenarios
required by the application. Even Firebase itself, can't answer the complex requirements of the messaging domain.
Also, it is both difficult and costly for developers to make additional development for messaging outside of their focused business area.
If you need to install and customize your own Twilio-like solution, this project is for you.
* This git repo also provides a great opportunity to study the system architecture of a SaaS microservice application, especially designed for a high number of users.
* You can adjust and integrate your very own CPaaS system for complicated/busy/overloaded systems with ZOPS.

## Base Components


![](https://zetaops.io/static/assets/images/products/zops-cpaas/zops-roc-small.jpg)


### ```zopsm```

> Backend part of the system. PUSH, Realtime Online Messaging is ready.
> SMS  design is complete.
> Machine 2 Machine implementation for MQTT and COAP is underway.



Components:

* Riak KV
* RabbitMQ
* Tornado web sockets
* Gunicorn
* Python 3
* Python Graceful REST lib
* Consul
* Vault
* REST APIS
* Fully containerized workers to scale.

* Why not Kubernetes? Well, it was not mature enough while we have started to this project to trust. I have still concerns about K8S but this is another story.

### ```zopsm-frontend```

> Decoupled Angular 5 frontend with relevant https services. You should adopt your own
> template structure and graphical elements. Please note that commercial usage of graphical
> materials are strictly prohibited!

    * Angular 5
    * Bootstrap 4
    * https services
    * Nginx

###  ```zopsm-dev-tools```

> Dev tools consist of local and production deployment and build tools.
> Please read README.md files in every sub directory of project.

    * Ansible playbooks to setup bare-metal systems.
    * Docker related files for system components.
    * Buildbot CI/CD files.
    * Both local and testing environments.

###  ```zopsm-push-test```

> Android push test application. See README.

### ```Documentation```

* Please check ```zopsm/docs``` dir. Slightly old but useful technical documents and UML diagrams reside in subdirs.
* Plantuml used for text based UML diagrams. You should have ```plantuml.jar``` and ```graphviz``` installed. 
* Also there should be PlantUML plugin installed to your IDE.
* Please read README files located in sub-project dirs to setup local development and 
as well as production setup steps.

### IDE config files

PyCharm run configs added as ```zopsm-run-configs.tar.gz```. Please check directories accordingly.

## ZOPS License

This repo is dual-licensed.
* GPL3 for personal development usage.
* ZOPS Enterprise license for corporate use. Any company using this piece of code without permission from Zetaops, will be damned with Covid-19 for sure!
* If you need other licensing options or support requests, you should contact with Zetaops info[youknow]zetaops.io email.

Brought to you by [Zetaops](https://zetaops.io) means Gokhan Boranalp aka kunthar

Whenever you need;

* Systems Architecture help
* Project management help
* Technical consultancy services

You can contact [me here](https://www.linkedin.com/in/gokhanboranalp/) and also email me to < avoid-harvesters> gokhanboranalp < /avoid-harvesters> gmail.com

![Made in URLA with Love and Enginar](https://zetaops.io/static/assets/images/enginar-small.png)
