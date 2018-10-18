from s3contents.ipycompat import ContentsManager
from s3contents.ipycompat import HasTraits, Unicode

from traitlets import (
    Any,
    Bool,
    Dict,
    Instance,
    List,
    TraitError,
    Type,
    Unicode,
    validate,
    default,
)

class BookstoreContentsArchiver(ContentsManager, HasTraits):
    """
    Archives contents via one ContentsManager and passes through to
    another ContentsManager
    """
    pass