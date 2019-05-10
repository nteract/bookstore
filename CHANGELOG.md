# Change Log

## 2.3.0 [Unreleased](https://github.com/nteract/bookstore/compare/2.2.1...HEAD)

[2.3.0 on Github](https://github.com/nteract/bookstore/releases/tag/2.3.0)

### Significant changes

Validation information is now exposed as a dict at the `/api/bookstore` endpoint.

This allows us to distinguish whether different features have been enabled on bookstore.

The structure for 2.3.0 is:

```python
    validation_checks = {
        "bookstore_valid": all(general_settings),
        "archive_valid": all(archive_settings),
        "publish_valid": all(published_settings),
    }
```

## Releases prior to 2.3.0

[2.2.1 (2019-02-03)](https://github.com/nteract/bookstore/releases/tag/2.2.1)

[2.2.0 (2019-01-29)](https://github.com/nteract/bookstore/releases/tag/2.2.0)

[2.1.0 (2018-11-20)](https://github.com/nteract/bookstore/releases/tag/2.1.0)

[2.0.0 (2018-11-13)](https://github.com/nteract/bookstore/releases/tag/2.0.0)

[0.1 (2018=10-16)](https://github.com/nteract/bookstore/releases/tag/0.1)
