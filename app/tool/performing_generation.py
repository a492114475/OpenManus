import os

import aiofiles
import requests

from app.tool.base import BaseTool


class PerformingGeneration(BaseTool):
    name: str = "PerformingGeneration"
    description: str = """Provide perovskite formula and process according to user needs.
When recommending perovskite formulas or processes to users, please use this tool.
This tool accepts the formula_filepath, the method of generating formulas, the quantity of generating formulas."""
    parameters: dict = {
        "type": "object",
        "properties": {
            "formula_filepath": {
                "type": "string",
                "description": "(optional) the location for recommending formulas.",
                "default": "none.txt",
            },
            "mode": {
                "type": "string",
                "description": "(optional) The method of generating formulas.",
                "enum": ["gen", "dpo", "ins"],
                "default": "gen",
            },
            "num": {
                "type": "integer",
                "description": "(optional) The quantity of generating formulas.",
                "default": "1",
            },
        },
        # "required": ["content", "file_path"],
    }

    async def execute(self, formula_filepath: str, mode: str, num: int = 1) -> str:
        """
        Save content to a file at the specified path.

        Args:
            formula_filepath (str): The content to save to the file.
            mode (str): The path where the file should be saved.
            num (int, optional): The file opening mode. Default is 'w' for write. Use 'a' for append.

        Returns:
            str: A message indicating the result of the operation.
        """

        if mode == "gen":
            formula_filepath = r"C:\\Users\\Administrator\\PycharmProjects\\MetaGPT-main\\MetaGPT-main\\metagpt\\data_4th_two_all92.json"
            _, ext = os.path.splitext(formula_filepath)
            if ext.lower() == '.json':
                url = "http://39.174.223.92:9988/upload_generate"
                file = {'file': open(formula_filepath, 'rb')}
                data = {'size': num}
                response = requests.post(url, files=file, data=data)


                response = response.json()
                cleaned_data = [
                    {key: value for key, value in item.items() if key not in {"PCE", "FF", "Voc", "Jsc"}}
                    for item in response
                ]
            return "配方已生成完毕, 配方如下"+str(cleaned_data)
        if mode == "dpo":
            file_path = r"C:\\Users\\Administrator\\PycharmProjects\\MetaGPT-main\\MetaGPT-main\\metagpt\\data_4th_two_all92.json"
            _, ext = os.path.splitext(file_path)
            if ext.lower() == '.json':
                url = "http://39.174.223.92:9988/upload_dpo"
                files = {'file': open(file_path, 'rb')}
                response = requests.post(url, files=files)
                return "DPO推荐中，结果将保存在results.txt中"
            else:
                raise Exception("The file format is not json")