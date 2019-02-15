# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zip file tests."""

from __future__ import absolute_import, print_function

import zipfile

from flask import render_template_string, url_for
from invenio_db import db
from invenio_files_rest.models import ObjectVersion
from invenio_previewer import current_previewer
from invenio_previewer.api import PreviewFile
from invenio_previewer.extensions import zip as preview_zip
from invenio_records_files.api import RecordsBuckets
from mock import patch
from six import BytesIO, b


def create_file(record, bucket, filename, stream):
    """Create a file and add in record."""
    obj = ObjectVersion.create(bucket, filename, stream=stream)
    rb = RecordsBuckets(record_id=record.id, bucket_id=obj.bucket_id)
    db.session.add(rb)
    record.update(dict(
        _files=[dict(
            bucket=str(bucket.id),
            key=filename,
            size=obj.file.size,
            checksum=str(obj.file.checksum),
            version_id=str(obj.version_id),
        ), ]
    ))
    record.commit()
    db.session.commit()
    return obj


def test_zip_file(app, bucket, record):
    """Test view for a zip file."""
    with app.app_context():
        with open('file_5000M.zip', 'rb') as f:
            fileobj = create_file(record, bucket, 'file_5000M.zip', f)
            preview_file = PreviewFile(record['control_number'], record, fileobj)
            # import ipdb; ipdb.set_trace()
            tree, limit_reached, error = preview_zip.make_tree(preview_file)
            with app.test_request_context():
                template = preview_zip.preview(preview_file)
                with open('test_5000M.html', 'w+') as ff:
                    ff.write(template)
            print('tree', tree)
            print('limit_reached', limit_reached)
            print('error', error)
            children_list = preview_zip.children_to_list(tree)['children']
            print(children_list)
