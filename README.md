# depository

This repository provides tooling and workflow recommendations for storing, scheduling, and publishing notebooks.

## Automatic Notebook Versioning

Every save of a notebook creates an immutable copy of the notebook on object storage. 

To ease implementation, we'll rely on S3 as the object store, using [versioned buckets](https://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html).

<!--

Include diagram for versioning

-->

## Storage Paths

All notebooks are archived to a single versioned S3 bucket with specific prefixes denoting the lifecycle of the notebook:

* `/workspace` - where users edit
* `/scheduled` - notebooks currently scheduled
* `/published` - public notebooks (to an organization)

Each notebook path is a namespace that an external service ties into the schedule. We archive off versions, keeping the path intact (until a user changes them). 

| Prefix |  Intent | 
|---|---|
| `/workspace/kylek/notebooks/mine.ipynb`  | Notebook in “draft”  | 
| `/scheduled/kylek/notebooks/mine.ipynb`  | Current scheduled copy  | 
| `/published/kylek/notebooks/mine.ipynb`  | Current published copy  | 


## Transitioning to this Storage Plan

Since most people are on a regular filesystem, we'll start with writing to the `/workspace` prefix as Archival Storage (writing on save using a `post_save_hook` for a Jupyter contents manager).

## Configuration

```python
from depository import depositoryContentsArchiver

# jupyter config
# At ~/.jupyter/jupyter_notebook_config.py for user installs
# At __ for system installs
c = get_config()

c.NotebookApp.contents_manager_class = depositoryContentsArchiver

c.depository.workspace_prefix = "/workspace/kylek/notebooks"
c.depository.published_prefix = "/published/kylek/notebooks"  
c.depository.scheduled_prefix = "/scheduled/kylek/notebooks"  

# Optional, in case you're using a different contents manager
# This defaults to notebook.services.contents.manager.ContentsManager
# c.depository.Archiver.underlying_contents_manager_class = ADifferentContentsManager

c.depository.Backend = "s3"
c.depository.S3.bucket = "<bucket-name>"

# Note: if depository is used from an EC2 instance with the right IAM role, you don't
# have to specify these
c.depository.S3.access_key_id = <AWS Access Key ID / IAM Access Key ID>
c.depository.S3.secret_access_key = <AWS Secret Access Key / IAM Secret Access Key>
```

