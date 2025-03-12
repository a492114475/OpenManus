from app.tool import BaseTool
from typing import Optional
import os
from datetime import datetime
from app.config import config

class PathGenerator(BaseTool):
    name: str = "path_generator"
    description: str = '''Generate a dynamic path based on the experiment ID (exp_id), optional test number, and path type. 
                          The path will follow the format: <db_base_folder>/<exp_id>/all/<path_type>/<test_number>.'''
    parameters: dict = {
        "type": "object",
        "properties": {
            "exp_id": {
                "type": "string",
                "description": "The experiment ID (required)."
            },
            "test_number": {
                "type": "integer",
                "description": "The test number (optional)."
            },
            "path_type": {
                "type": "string",
                "enum": ["IV", "In-situ"],
                "description": "The type of path to generate (optional, default is 'IV')."
            }
        },
        "required": ["exp_id"]
    }

    db_base_folder: str = config.database.folder

    async def execute(self, **kwargs) -> str:
        # 获取传入参数
        exp_id: str = kwargs.get("exp_id")
        test_number: Optional[int] = kwargs.get("test_number")  # 可选参数
        path_type: str = kwargs.get("path_type", "IV")  # 默认为 "IV"

        # 生成路径
        path = self.generate_path(exp_id, test_number, path_type)

        # 规范化路径
        path = os.path.normpath(path)

        return path

    def generate_path(self, exp_id: str, test_number: Optional[int], path_type: str) -> str:
        """根据 exp_id、test_number（可选）和 path_type 生成路径"""
        # 获取当前日期并格式化为 "YYYYMMDD"
        current_date = datetime.now().strftime("%Y%m%d")

        # 动态生成路径
        if test_number is not None:
            # 如果 test_number 存在，将其包含在路径中
            path = os.path.join(
                self.db_base_folder,
                exp_id,
                "all",
                path_type,
                str(test_number)
            )
        else:
            # 如果 test_number 不存在，不包含 test_number
            path = os.path.join(
                self.db_base_folder,
                exp_id,
                "all",
                path_type
            )

        return path
