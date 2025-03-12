from app.tool import BaseTool
from typing import List
import re
import json
import os
from app.config import config

class ExpIv(BaseTool):
    name: str = "exp_IV"
    description: str = '''Process and analyze IV test results based on uploaded files with names that strictly follow one of the three formats: <dirname>/IV_Number1_YYYYMMDD_Number2_Number3_CHX.txt
                     For example: <dirname>/IV_1_20240914_201_201_CH1.txt, where 'IV' represents the current-voltage(IV) test, 
                     'YYYYMMDD' is the date (format: YYYY-MM-DD), 'Number1' is the test number, 'Number2' and 'Number3' are numeric parameters, and 'CHX' is channel number.'''
    # , IV_Number1_YYYYMMDD_Number2_Number3_CHX.csv or IV_Number1_YYYYMMDD_Number2_Number3_CHX.jpg.
    # , IV_1_20240914_201_201_CH1.csv or IV_1_20240914_201_201_CH1.jpg
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
        "required": ["IV_file"]
    }

    db_base_folder: str = config.database.folder

    # folder: str = None  # 显式定义 folder 字段
    # def __init__(self, folder: str = None):
    #     super().__init__()
    #     self.folder = folder  # 存储传入的 folder 参数

    async def execute(self, **kwargs) -> str:
        # 获取文件名列表
        file_names: List[str] = kwargs.get("IV_file", [])

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
            # result = f"Processing valid files: {', '.join(valid_files)}\n"
            result = self.process_files(valid_files)  # , self.folder
            # result += "IV process completed."
        else:
            result = "No valid files found."

        # 处理无效文件
        if invalid_files:
            result += f"\nInvalid files: {', '.join(invalid_files)}"

        return result

    def _validate_file_name(self, file_name: str) -> bool:
        """验证文件名是否符合指定格式"""
        base_name = os.path.basename(file_name)
        pattern = r"^IV_\d+_\d{8}_\d+_\d+_CH\d+\.(txt|csv|jpg)$"
        return bool(re.match(pattern, base_name))


    def process_files(self, file_name_list):  # , folder
        json_result = []

        for file in file_name_list:
            json_content = {}
            file_path = os.path.abspath(os.path.join(file))  # folder,

            try:
                with open(file_path, 'r', encoding='utf-8') as reader:
                    line_number = 0
                    for line in reader:
                        line_number += 1
                        if line_number > 30:
                            break

                        if line_number == 18:
                            voc = float(line.split("=")[1].replace(" mV", "").strip())
                            json_content["开路电压（Voc）"] = f"{voc:.2f} mV"
                        elif line_number == 19:
                            isc = float(line.split("=")[1].replace(" mA", "").strip())
                            json_content["短路电流（Isc）"] = f"{isc:.2f} mA"
                        elif line_number == 24:
                            ff = float(line.split("=")[1].strip()) / 100
                            json_content["填充因子（FF）"] = f"{ff:.2f}"
                        elif line_number == 25:
                            eff = float(line.split("=")[1].strip())
                            json_content["效率（Efficiency）"] = f"{eff:.2f} %"

            except Exception as e:
                print(f"Error processing file {file}: {e}")

            if not json_content:
                return "请先上传本次查询的文件"

            # 将文件名和内容放入一个字典中
            file_result = {os.path.basename(file): json_content}

            # 将该结果添加到 JSON 列表中
            json_result.append(file_result)

        # 将结果转换为 JSON 字符串
        return json.dumps(json_result, ensure_ascii=False, indent=4)