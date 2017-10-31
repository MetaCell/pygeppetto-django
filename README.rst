=====
PyGeppetto-Server
=====

PyGeppetto-Server is a simple Django app that implements the basic functionality to run a Geppetto instance.

- Implement basic socket communication
- Redirect to geppetto.vm
- Implement redirection for Geppetto Frontend static content.



Quick start
-----------

1. Add "pygeppetto_server" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'pygeppetto_server',
    ]

2. Include the pygeppetto_server URLconf in your project urls.py like this::

    url(r'^polls/', include('polls.urls')),

//3. Run `python manage.py migrate` to create the polls models.

//4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

//5. Visit http://127.0.0.1:8000/polls/ to participate in the poll.