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

version_info = (2, 3, 0, "", "dev")

__version__ = ".".join(map(str, version_info[:3])) + ".".join(version_info[3:])
