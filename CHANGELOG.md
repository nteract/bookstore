# Change Log

## 2.3.0

[2.3.0 on Github](https://github.com/nteract/bookstore/releases/tag/2.3.0)

### Significant changes

Validation information is now exposed as a dict at the /api/bookstore endpoint.

This allows us to distinguish whether different features have been enabled on bookstore.

The structure now is 

```python
    validation_checks = {
        "bookstore_valid": all(general_settings),
        "archive_valid": all(archive_settings),
        "publish_valid": all(published_settings),
    }
```
 
## Versions previous to 2.3.0

[2.2.1](https://github.com/nteract/bookstore/releases/tag/2.2.1)

[2.2.0](https://github.com/nteract/bookstore/releases/tag/2.2.0)

[Unreleased](https://github.com/nteract/bookstore/compare/0.2.1...HEAD)

[2.1.0](https://github.com/nteract/bookstore/releases/tag/2.1.0)

[2.0.0](https://github.com/nteract/bookstore/releases/tag/2.0.0)

[0.1](https://github.com/nteract/bookstore/releases/tag/0.1)
