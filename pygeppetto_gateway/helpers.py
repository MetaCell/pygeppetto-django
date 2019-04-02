from lxml import etree
from django.conf import settings as s
import os
import requests


def process_includes(model_file_url, dir_path=None):
    tree = etree.fromstring(requests.get(model_file_url).text)
    file_name = os.path.basename(model_file_url)
    model_directory = s.DOWNLOADED_MODEL_DIR if dir_path is None else dir_path

    included_files_directory = model_file_url.replace(
        file_name, ''
    )

    nml_paths = [
        x.attrib['file']
        for x in tree.xpath("Include[contains(@file, '.nml')]")
    ]

    for path in nml_paths:
        url = "{}{}".format(
                included_files_directory,
                path
            )
        content = requests.get(url).text

        with open(os.path.join(model_directory, path), 'w') as f:
            f.write(content)

    return nml_paths
