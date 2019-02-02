"""S3 path utilities"""


# Our S3 path delimiter will remain fixed as '/' in all uses
delimiter = "/"


def _join(*args):
    """Join S3 bucket args together.

    Remove empty entries and strip left-leading ``/``
    """
    return delimiter.join(filter(lambda s: s != '', map(lambda s: s.lstrip(delimiter), args)))


def s3_path(bucket, prefix, path=''):
    """Compute the s3 path.

    Parameters
    ----------
    bucket : str
      S3 bucket name
    prefix : str
      prefix for workspace or publish
    path : str
      The storage location
    """
    return _join(bucket, prefix, path)


def s3_key(prefix, path=''):
    """Compute the s3 key

    Parameters
    ----------
    prefix : str
      prefix for workspace or publish
    path : str
      The storage location
    """
    return _join(prefix, path)


def s3_display_path(bucket, prefix, path=''):
    """Create a display name for use in logs

    Parameters
    ----------
    bucket : str
      S3 bucket name
    prefix : str
      prefix for workspace or publish
    path : str
      The storage location
    """
    return 's3://' + s3_path(bucket, prefix, path)
