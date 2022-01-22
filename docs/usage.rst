Usage
=====

This package implements the Healthchecks.io Management and Ping APIs as documented here https://healthchecks.io/docs/api/.

Context Manager
---------------

Either the Client or AsyncClient can be used as a ContextManager (or Async Context Manager)

.. code-block:: python

    from healthchecks_io import Client, CheckCreate

    with Client(api_key="myapikey") as client:
        check = client.create_check(CheckCreate(name="New Check", tags="tag1 tag2"))
    print(check)

This is probably the easiest way to use the Clients for one-off scripts. If you do not need to keep a client open for multiple requests, just use
the context manager.

.. note::
    When using either of the client types as a context manager, the httpx client underlying the client will be closed when the context manager exits.

    Since we allow you to pass in a client on creation, its possible to use a shared client with this library. If you then use the client as a contextmanager,
    it will close that shared client.

    Just a thing to be aware of!


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

    check = client.create_check(CheckCreate(name="New Check", tags="tag1 tag2")
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

    async def main():
        client = AsyncClient(api_key="myapikey")

        check = await client.create_check(CheckCreate(name="New Check", tags="tag1 tag2"))
        print(check)

    if __name__ == "__main__":
        asyncio.run(main())


CheckTrap
---------

Ever wanted to run some code and wrape it in a healthcheck check without thinking about it?

That's what CheckTrap is for.

.. code-block:: python

    from healthchecks_io import Client, AsyncClient, CheckCreate, CheckTrap

    client = Client(api_key="myapikey")

    # create a new check, or use an existing one already with just its uuid.
    check = await client.create_check(CreateCheck(name="New Check", tags="tag1 tag2")

    with CheckTrap(client, check.uuid):
        # when entering the context manager, sends a start ping to your check
        run_my_thing_to_monitor()

    # If your method exits without an exception, sends a success ping
    # If there's an exception, a failure ping will be sent with the exception and traceback

    client = AsyncClient(ping_key="ping_key")

    # works with async too, and the ping api and slugs
    async with CheckTrap(client, check.slug) as ct:
        # when entering the context manager, sends a start ping to your check
        # Add custom logs to what gets sent to healthchecks. Reminder, only the first 10k bytes get saved
        ct.add_log("My custom log message")
        run_my_thing_to_monitor()

    # If your method exits without an exception, sends a success ping
    # If there's an exception, a failure ping will be sent with the exception and traceback
