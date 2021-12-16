Usage
=====

This package implements the Healthchecks.io Management and Ping APIs as documented here https://healthchecks.io/docs/api/.

Sync
----

Instantiate a Client
^^^^^^^^^^^^^^^^^^^^

If you want to work with the healthchecks.io API for the SaaS healthchecks, you
can create a client like below:

.. code-block:: python

   from healthchecks_io import Client

   client = Client(api_key="myapikey", ping_key="optional_ping_key")

If you are using a self-hosted healthchecks instance, you can set the api url when creating the client.

.. code-block:: python

   from healthchecks_io import Client

   client = Client(api_key="myapikey",
                   api_url="https://myhealthchecksinstance.com/api/",
                   ping_key="optional_ping_key")


Creating a new Check
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from healthchecks_io import Client, CheckCreate

    client = Client(api_key="myapikey")

    check = client.create_check(CreateCheck(name="New Check", tags="tag1 tag2")
    print(check)

Getting a Check
^^^^^^^^^^^^^^^

.. code-block:: python

    from healthchecks_io import Client

    client = Client(api_key="myapikey")

    check = client.get_check(uuid="mychecksuuid")
    print(check)

Pinging a Check
^^^^^^^^^^^^^^^

.. code-block:: python
    from healthchecks_io import Client

    client = Client(api_key="myapikey")
    result, text = client.success_ping(uuid="mychecksuuid")
    print(text)

Async
-----

If you want to use the client in an async program, use AsyncClient instead of Client



.. code-block:: python

    from healthchecks_io import AsyncClient, CheckCreate

    client = AsyncClient(api_key="myapikey")

    check = await client.create_check(CreateCheck(name="New Check", tags="tag1 tag2")
    print(check)
