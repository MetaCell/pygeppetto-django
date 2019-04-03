from lxml import etree
import re
from django.conf import settings as s
import os
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def process_includes(model_file_url, dir_path=None):
    result = re.findall(
        '<include href="(.*)"',
        requests.get(model_file_url).text
    )

    file_name = os.path.basename(model_file_url)
    model_directory = s.DOWNLOADED_MODEL_DIR if dir_path is None else dir_path

    included_files_directory = model_file_url.replace(
        file_name, ''
    )

    nml_paths = [
        file_name
        for file_name in result
    ]

    for path in nml_paths:
        print(f"Processing {path}")
        url = "{}{}".format(
                included_files_directory,
                path
            )
        process_includes(url, dir_path)

        content = requests.get(url).text

        with open(os.path.join(model_directory, path), 'w') as f:
            f.write(content)

    return nml_paths
