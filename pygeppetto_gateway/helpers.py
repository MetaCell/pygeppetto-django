import logging
import os
import re

import requests
from django.conf import settings as s

db_logger = logging.getLogger('db')


def process_includes(model_file_url: str, dir_path: str = None):
    """ Downloading all included models in model file
        :type model_file_url:
        :param model_file_url:

        :type dir_path:
        :param dir_path:

        :raises:

        :rtype:
    """
    regex = {'lems': '<Include file="(.*)"', 'nml': '<include href="(.*)"'}
    file_content = requests.get(model_file_url).text

    is_lems = re.search('^<Lems>', file_content) is not None

    result = re.findall(
        regex.get('lems') if is_lems else regex.get('nml'), file_content
    )

    file_name = os.path.basename(model_file_url)
    model_directory = s.DOWNLOADED_MODEL_DIR if dir_path is None else dir_path

    included_files_directory = model_file_url.replace(file_name, '')

    nml_paths = [file_name for file_name in result]

    for path in nml_paths:
        db_logger.info(f"Processing {path} for model {model_file_url}")

        url = "{}{}".format(included_files_directory, path)
        process_includes(url, dir_path)

        content = requests.get(url)

        if content.status_code == 404:
            continue
        else:
            content = content.text

        with open(os.path.join(model_directory, path), 'w') as f:
            f.write(content)

    return nml_paths
