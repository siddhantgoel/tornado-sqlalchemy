CHANGELOG
=========

v0.7.0 (under development)
--------------------------
- Support for multiple databases (thanks `@dingyaguang117`_)

v0.6.1
------
- Pass :code:`SessionMixin` arguments directly to :code:`create_engine`
- Format code using :code:`black`
- Add test cases for concurrent session usage

v0.5.0
------
- Avoid initializing the pool executor at import time
- Drop support for Python 3.3 and 3.4
- Improve documentation and example code

v0.4.1
------
- Update README

v0.4.0
------
- Drop support for Python 2
- Extend :code:`SessionMixin` to suport :code:`self.session`
- Use :code:`__call__` pattern on :code:`declarative_base`
- Add more test cases
- Improve documentation and example code

v0.3.3
------
- Limit :code:`use_native_unicode` only to PostgreSQL connections
- Update example code

v0.3.2
------
- Set :code:`default_max_workers` default value to CPU count

v0.3.1
------
- Minor improvements to :code:`setup.py`

v0.3.0
------
- Include README and LICENSE files in the package

v0.2.2
------
- Support SQLAlchemy's :code:`use_native_unicode` argument
- Remove unused code
- Improve documentation

v0.2.1
------
- Add default value for :code:`pool_size` argument
- Add request handler test cases

v0.2.0
------
- Introduce :code:`SessionFactory` class
- Support :code:`session_events`
- Replace :code:`wrap_in_future` with :code:`as_future`
- Update documentation

v0.1.1
------
- Initial release


.. _@dingyaguang117: https://github.com/dingyaguang117
