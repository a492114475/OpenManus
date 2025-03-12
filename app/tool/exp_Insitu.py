from app.tool import BaseTool
from typing import List
import re
import json
import os
from app.config import config

class ExpInsitu(BaseTool):
    name: str = "exp_Insitu"
    description: str = '''Process and analyze In-situ test results based on uploaded file names that strictly follow the format: <dirname>/GP_Abs_YYYYMMDD_Number1_Number2.csv.
                        For example: <dirname>/GP_Abs_20240914_201_201.csv, where 'GP_Abs' represents the In-situ test, 
                        'YYYYMMDD' denotes the date, and 'Number1' and 'Number2' are numeric parameters.'''
    parameters: dict = {
        "type": "object",
        "properties": {
            "IV_file": {
                "type": "array",
                "description": "List of file names",
                "items": {
                    "type": "string",
                    "description": "File names"
                }
            }
        },
        "required": ["InSitu_file"]
    }

    db_base_folder: str = config.database.folder

    async def execute(self, **kwargs) -> str:
        # 获取文件名列表
        file_names: List[str] = kwargs.get("InSitu_file", [])

        # 验证文件名格式
        valid_files = []
        invalid_files = []
        for file_name in file_names:
            if self._validate_file_name(file_name):
                valid_files.append(file_name)
            else:
                invalid_files.append(file_name)

        # 处理有效文件
        if valid_files:
            result = "Insitu"
        else:
            result = "No valid files found."

        # 处理无效文件
        if invalid_files:
            result += f"\nInvalid files: {', '.join(invalid_files)}"

        return result

    def _validate_file_name(self, file_name: str) -> bool:
        """验证文件名是否符合指定格式"""
        base_name = os.path.basename(file_name)
        pattern = r"^GP_Abs_\d{8}_\d+_\d+\.csv$"
        return bool(re.match(pattern, base_name))