#!/usr/bin/env python

# Copyright (C) 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Application for uploading an object using the Cloud Storage API.

This sample is used on this page:

    https://cloud.google.com/storage/docs/json_api/v1/json-api-python-samples

For more information, see the README.md under /storage.
"""

import argparse
import filecmp
import json
import os
import tempfile

import datetime
from time import strftime, gmtime

from googleapiclient import discovery
from googleapiclient import http

from oauth2client.client import GoogleCredentials


def main(bucket, filename):
    resp = upload_object(bucket, filename, readers, owners)
    print(json.dumps(resp, indent=2))

    # with tempfile.NamedTemporaryFile(mode='w+b') as tmpfile:
    #     get_object(bucket, filename, out_file=tmpfile)
    #     tmpfile.seek(0)
    #
    #     if not filecmp.cmp(filename, tmpfile.name):
    #         raise Exception('Downloaded file != uploaded object')
    #
    # resp = delete_object(bucket, filename)
    # if resp:
    #     print(json.dumps(resp, indent=2))
    #

def create_service():
    credentials = GoogleCredentials._get_implicit_credentials()

    return discovery.build('storage', 'v1', credentials=credentials)


def upload_object(bucket, filename, readers = None, owners = None):
    service = create_service()

    # This is the request body as specified:
    # http://g.co/cloud/storage/docs/json_api/v1/objects/insert#request
    body = {
        'name': "/images/img" + strftime("%Y-%m-%d%H:%M:%S",gmtime()) + ".jpg"
    }



    # Now insert them into the specified bucket as a media insertion.
    # http://g.co/dev/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#insert
    with open(filename, 'rb') as f:
        req = service.objects().insert(
            bucket=bucket, body=body,
            # You can also just set media_body=filename, but for the sake of
            # demonstration, pass in the more generic file handle, which could
            # very well be a StringIO or similar.
            media_body=http.MediaIoBaseUpload(f, 'image/jpeg'))
        resp = req.execute()

    return resp


def get_object(bucket, filename, out_file):
    service = create_service()

    # Use get_media instead of get to get the actual contents of the object.
    # http://g.co/dev/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#get_media
    req = service.objects().get_media(bucket=bucket, object=filename)

    downloader = http.MediaIoBaseDownload(out_file, req)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {}%.".format(int(status.progress() * 100)))

    return out_file


def delete_object(bucket, filename):
    service = create_service()

    req = service.objects().delete(bucket=bucket, object=filename)
    resp = req.execute()

    return resp


def list_bucket():
    """Returns a list of metadata of the objects within the given bucket."""
    service = create_service()

    # Create a request to objects.list to retrieve a list of objects.
    fields_to_return = \
        'nextPageToken,items(name,size,contentType,metadata(my-key))'
    req = service.objects().list(bucket="skaffarisw20160924" ,fields=fields_to_return)

    all_objects = []
    # If you have too many items to list in one request, list_next() will
    # automatically handle paging with the pageToken.
    while req:
        resp = req.execute()
        all_objects.extend(resp.get('items', []))
        req = service.objects().list_next(req, resp)
    return all_objects



if __name__ == '__main__':
    print upload_object(bucket="skaffarisw20160924",filename="/Users/momo/Downloads/test.jpg")
