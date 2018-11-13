#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bookstore import BookstoreContentsArchiver, BookstoreSettings

# jupyter config
# At ~/.jupyter/jupyter_notebook_config.py for user installs
# At __ for system installs
c = get_config()

c.NotebookApp.contents_manager_class = BookstoreContentsArchiver

c.BookstoreSettings.workspace_prefix = "ci-workspace"

# If using minio for development
c.BookstoreSettings.s3_endpoint_url = "http://127.0.0.1:9000"
c.BookstoreSettings.s3_bucket = "bookstore"

# Straight out of `circleci/config.yml`
c.BookstoreSettings.s3_access_key_id = "ONLY_ON_CIRCLE"
c.BookstoreSettings.s3_secret_access_key = "CAN_WE_DO_THIS"
