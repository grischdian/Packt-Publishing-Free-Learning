import configparser
import owncloud
import logging
import os

from .logger import get_logger

logger = get_logger(__name__)

SCOPES = 'https://github.com/owncloud/pyocclient'
FILE_TYPE = frozenset(["FILE", "FOLDER"])


class OwncloudManager(object):
    """Allows to upload and download new content to owncloud or nextcloud"""

    def __init__(self, cfg_file_path):
        self._set_config_data(cfg_file_path)
        self._mimetypes = {
            'pdf': 'application/pdf',
            'zip': 'application/zip',
            'mobi': 'application/x-mobipocket-ebook',
            'epub': 'application/epub+zip'
        }
        self.oc = owncloud.Client(self.url)
        self.oc.login(self.username, self.password)
        self.folder_name = self.__ensure_folder_name_value(self.folder_name)
        self.__check_if_folder_exists_and_create_if_missing(self.folder_name)

        logging.getLogger("apiclient").setLevel(logging.WARNING)  # downgrading logging level for pyocclient

    def _set_config_data(self, cfg_file_path):
        """Sets all the config data for Google drive manager"""
        configuration = configparser.ConfigParser()
        if not configuration.read(cfg_file_path):
            raise configparser.Error('{} file not found'.format(cfg_file_path))
        self.cfg_file_path = cfg_file_path
        self.url = configuration.get("OWNCLOUD_DATA", 'oc_url')
        self.folder_name = configuration.get("OWNCLOUD_DATA", 'oc_folder_name')
        self.username = configuration.get("OWNCLOUD_DATA", 'oc_username')
        self.password = configuration.get("OWNCLOUD_DATA", 'oc_password')
        self.separate_folder = configuration.get("OWNCLOUD_DATA", 'oc_separate_folder')

    def __ensure_folder_name_value(self, folder_name):
        if folder_name is None or len(folder_name) == 0:
            raise ValueError("Incorrect folder path argument format")
        if not folder_name.startswith("/"):
            folder_name = "/" + folder_name
        if not folder_name.endswith("/"):
            folder_name = folder_name + "/"
        return folder_name

    def __check_if_folder_exists_and_create_if_missing(self, folder_name):
        folder_path = folder_name[:-1]
        for path in self.oc.list(os.path.dirname(folder_path)):
            if path.path == folder_name:
                logger.info("Upload-folder already exist - move on")
                break
        else:
            self.oc.mkdir(folder_name)
            logger.info("Upload-folder created")

    def send_files(self, file_paths):
        if file_paths is None or len(file_paths) == 0:
            raise ValueError("Incorrect file paths argument format")
        for path in file_paths:
            if os.path.exists(path):
                remote_file = os.path.join(self.folder_name, os.path.basename(path))
                try:
                    if self.separate_folder:
                        self.__check_if_folder_exists_and_create_if_missing(
                            self.__ensure_folder_name_value(os.path.splitext(remote_file)[0])
                        )
                        remote_file = os.path.join(os.path.splitext(remote_file)[0], os.path.basename(path))

                    if self.oc.put_file(remote_file, path):
                        logger.success('File {} succesfully sent to owncloud or nextcloud'.format(path))
                    else:
                        logger.info('File {} already exists on owncloud or nextcloud'.format(path))
                except Exception as e:
                    logger.error('Error {} occurred while sending file: {} to ownCloud or Nextcloud'.format(e, path)
                    )


class OwncloudFile(object):
    """Helper class that describes File or Folder stored on ownCloud and Nextcloud server"""
    def __init__(self, file_name):
        self.name = file_name
        self.id = None
        self.parent_id = ''
