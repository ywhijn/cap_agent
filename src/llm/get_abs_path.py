
import os
from loguru import logger
from typing import Optional

class get_abs_path(object):

    def __init__(self, file_abspath: Optional[str] = None) -> None:
        self.file_abspath = file_abspath

    def __call__(self, file_relpath: str):
        """将相对路径转换为绝对路径
        """
        if self.file_abspath is None:
            logger.warning('SIM: 没有设置当前文件路径')
            self.file_abspath = os.path.abspath(__file__)

        folder_abspath = os.path.dirname(self.file_abspath)
        return os.path.join(folder_abspath, file_relpath)