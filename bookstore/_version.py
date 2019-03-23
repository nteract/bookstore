"""Bookstore version info

Follows pep 440 version rules

No dot before alpha/beta/rc, but before .dev
0.1.0rc1
0.1.0a1
0.1.0b1.dev
0.1.0.dev

version info type of release (b1, rc1, or "" for final or dev)
dev or "" to designate a final version
"""

version_info = (2, 3, 0, "", "dev")

__version__ = ".".join(map(str, version_info[:3])) + ".".join(version_info[3:])
