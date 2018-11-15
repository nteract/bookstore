from traitlets import Int, Unicode
from traitlets.config import LoggingConfigurable


class BookstoreSettings(LoggingConfigurable):
    """The same settings to be shared across archival, publishing, and scheduling
    """

    workspace_prefix = Unicode(
        "workspace", help="Prefix for the live workspace notebooks"
    ).tag(config=True)
    published_prefix = Unicode("published", help="Prefix for published notebooks").tag(
        config=True
    )

    ## S3 Settings for the S3 backed storage (other implementations can add on below)
    # Allowed to not set these as we can pick up IAM roles instead
    s3_access_key_id = Unicode(
        help="S3/AWS access key ID", allow_none=True, default_value=None
    ).tag(config=True, env="JPYNB_S3_ACCESS_KEY_ID")
    s3_secret_access_key = Unicode(
        help="S3/AWS secret access key", allow_none=True, default_value=None
    ).tag(config=True, env="JPYNB_S3_SECRET_ACCESS_KEY")

    s3_endpoint_url = Unicode("https://s3.amazonaws.com", help="S3 endpoint URL").tag(
        config=True, env="JPYNB_S3_ENDPOINT_URL"
    )
    s3_region_name = Unicode("us-east-1", help="Region name").tag(
        config=True, env="JPYNB_S3_REGION_NAME"
    )
    s3_bucket = Unicode("bookstore", help="Bucket name to store notebooks").tag(
        config=True, env="JPYNB_S3_BUCKET"
    )

    max_threads = Int(
        16,
        help="Maximum number of threads for the threadpool allocated for S3 read/writes",
    ).tag(config=True)
