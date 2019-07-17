"""Bookstore version info

Use pep 440 version rules.

No dot before alpha/beta/rc. Use dot before `.dev`. Examples::

- 0.1.0rc1
- 0.1.0a1
- 0.1.0b1.dev
- 0.1.0.dev

`version_info` tuple::

- major
- minor
- micro
- type of release (b1, rc1, or "" for final or dev)
- suffix (dev or "" to designate a final version)
"""

version_info = (2, 3, 1, "")

__version__ = ".".join(map(str, version_info[:3])) + ".".join(version_info[3:])


def _check_version(bookstore_version, log):
    """Check version and log status"""
    if not bookstore_version:
        log.warning(
            f"Bookstore has no version header, which means it is likely < 2.0. Expected {__version__}"
        )
    elif bookstore_version[:1].isdigit() is False:
        log.warning(f"Invalid version format. Expected {__version__}")
    else:
        if bookstore_version[:1] < '2':
            log.warning(
                f"{bookstore_version} is the deprecated bookstore project for Openstack. Expected {__version__}"
            )
        else:
            log.debug(f"Bookstore version is {bookstore_version}.")
