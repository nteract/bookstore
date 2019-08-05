"""Utility and helper functions."""
import os

from tempfile import TemporaryDirectory


def url_path_join(*pieces):
    """Join components into a relative url.
    
    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place.
    
    Code based on Jupyter notebook `url_path_join`.
    """
    initial = pieces[0].startswith('/')
    final = pieces[-1].endswith('/')
    stripped = [s.strip('/') for s in pieces]
    result = '/'.join(s for s in stripped if s)
    if initial:
        result = '/' + result
    if final:
        result = result + '/'
    if result == '//':
        result = '/'
    return result


class TemporaryWorkingDirectory(TemporaryDirectory):
    """Utility for creating a temporary working directory.
    """

    def __enter__(self):
        self.cwd = os.getcwd()
        os.chdir(self.name)
        return super().__enter__()

    def __exit__(self, exc, value, tb):
        os.chdir(self.cwd)
        return super().__exit__(exc, value, tb)
