# Our S3 path delimiter will remain fixed as '/' in all uses
delimiter = "/"


def _join(*args):
    '''Join S3 bucket args together, removing empty entries and stripping left-leading
    '''
    return delimiter.join(filter(lambda s: s != '', map(lambda s: s.lstrip(delimiter), args)))


def s3_path(bucket, prefix, path=''):
    """compute the s3 path based on the bucket, prefix, and the path to the notebook"""
    return _join(bucket, prefix, path)


def s3_key(prefix, path=''):
    """compute the s3 key based on the prefix, and the path to the notebook"""
    return _join(prefix, path)


def s3_display_path(bucket, prefix, path=''):
    """create a display name for use in logs"""
    return 's3://' + s3_path(bucket, prefix, path)
