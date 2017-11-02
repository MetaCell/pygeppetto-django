<p align="center">
  <img src="https://github.com/tarelli/bucket/blob/master/geppetto%20logo.png?raw=true" alt="Geppetto logo"/>
</p>

# Python Geppetto Core
Python Geppetto Core Server developed in Django. This module provides the basic functionality to start a Python Geppetto Instance:
- Basic socket communication (Just enough to start main Geppetto page.
- Redirection for Geppetto Frontend static content.
- Implement main view (Geppetto Canvas).

This is a work in progress and therefore, you will not find all the API (sockets and WS end points) available in [the Java version](https://github.com/openworm/org.geppetto.frontend/tree/master/src/main/java/org/geppetto/frontend).

This django module is thought to be used as part of a larger Django application which will contain any specific (non Geppetto) functionality. You can start developing your own project clonning Geppetto Django templated provided in [this repo](https://github.com/MetaCell/geppetto-django-template). Just follow the detailed explanation provided in the [readme](https://github.com/MetaCell/geppetto-django-template).


## Installation

**Stable version:**
```
pip install pygeppetto-django
```

**Development version:**
```
git clone https://github.com/MetaCell/pygeppetto-django.git
cd pygeppetto-django
git checkout development
pip install -e .
```

## Developers

**Socket communication**

Socket handling happens in consumers.py. Three methods are implemented so far:
- ws_connect
- ws_receive
- ws_disconnect

Currently, three request are sort of handle:
- client_id (on connection)
- user_privileges (on connection)
- geppetto_version (on message)

This is enought to load a basic geppetto canvas (geppetto.vm template).

Mapping (Controller) between url and python method is defined in routing.py. This file will be referenced from the main application. See https://github.com/MetaCell/pygeppetto-django/readme.


**Load main view**

Views.py implements the views in the application. Currently, just index is implemented and it only renders geppetto.vm.

Controller can be found at urls.py

**Redirection for static content**

A redirection in urls.py allows to serve the static content.

