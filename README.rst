Py Healthchecks.Io
==================

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/healthchecks-io.svg
   :target: https://pypi.org/project/healthchecks-io/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/healthchecks-io.svg
   :target: https://pypi.org/project/healthchecks-io/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/healthchecks-io
   :target: https://pypi.org/project/healthchecks-io
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/healthchecks-io
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/py-healthchecksio/latest.svg?label=Read%20the%20Docs
   :target: https://py-healthchecksio.readthedocs.io/en/latest/
   :alt: Read the documentation at https://py-healthchecksio.readthedocs.io/en/latest/
.. |Tests| image:: https://github.com/andrewthetechie/py-healthchecks.io/workflows/Tests/badge.svg
   :target: https://github.com/andrewthetechie/py-healthchecks.io/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/andrewthetechie/py-healthchecks.io/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/andrewthetechie/py-healthchecks.io
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black

A python client for healthchecks.io. Supports the management api and ping api.

Features
--------

* Sync and Async clients based on HTTPX
* Supports the management api and the ping api
* Supports Healthchecks.io SAAS and self-hosted instances


Requirements
------------

* httpx
* pytz
* pydantic


Installation
------------

You can install *Py Healthchecks.Io* via pip_ from PyPI_:

.. code:: console

   $ pip install healthchecks-io


Usage
-----

Please see the `Usage <Usage_>`_ for details.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `MIT license`_,
*Py Healthchecks.Io* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.

.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT license: https://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _file an issue: https://github.com/andrewthetechie/py-healthchecks.io/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://py-healthchecksio.readthedocs.io/en/latest/usage.html
