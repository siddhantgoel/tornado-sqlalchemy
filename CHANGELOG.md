# CHANGELOG

## v0.8.0

- Support SQLAlchemy 2.x (thanks [@aemitos])

## v0.7.0

- Support for multiple databases (thanks [@dingyaguang117])
  - Drop `session_factory` and `make_session_factory` in favor of the new
    `SQLAlchemy` instance
  - Drop `declarative_base` in favor of the new `SQLAlchemy.Model` property
  - Allow models to be associated to separate databases using `__bind_key__`

- [Please refer to [UPGRADING.md] for help with upgrading.]

## v0.6.1

- Pass `SessionMixin` arguments directly to `create_engine`
- Format code using `black`
- Add test cases for concurrent session usage

## v0.5.0

- Avoid initializing the pool executor at import time
- Drop support for Python 3.3 and 3.4
- Improve documentation and example code

## v0.4.1

- Update README

## v0.4.0

- Drop support for Python 2
- Extend `SessionMixin` to suport `self.session`
- Use `__call__` pattern on `declarative_base`
- Add more test cases
- Improve documentation and example code

## v0.3.3

- Limit `use_native_unicode` only to PostgreSQL connections
- Update example code

## v0.3.2

- Set `default_max_workers` default value to CPU count

## v0.3.1

- Minor improvements to `setup.py`

## v0.3.0

- Include README and LICENSE files in the package

## v0.2.2

- Support SQLAlchemy's `use_native_unicode` argument
- Remove unused code
- Improve documentation

## v0.2.1

- Add default value for `pool_size` argument
- Add request handler test cases

## v0.2.0

- Introduce `SessionFactory` class
- Support `session_events`
- Replace `wrap_in_future` with `as_future`
- Update documentation

## v0.1.1

- Initial release

[@aemitos]: https://github.com/aemitos
[@dingyaguang117]: https://github.com/dingyaguang117
[UPGRADING.md]: https://github.com/siddhantgoel/tornado-sqlalchemy/blob/main/UPGRADING.md
