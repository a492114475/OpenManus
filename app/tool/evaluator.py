import os

import aiofiles

from app.tool.base import BaseTool


class Evaluator(BaseTool):
    name: str = "Evaluator"
    description: str = """Predict PCE, FF, JSC, and VOC results based on the perovskite formula.
To predict or evaluate the timing of PCE, FF, JSC, and VOC, please use this tool.
This tool receives perovskite formulations for prediction and evaluation."""
    parameters: dict = {
        "type": "object",
        "properties": {
            "Formula_PVK": {
                "type": "string",
                "description": "(required) Formula PVK.",
                "default": "",
            },

        },
        "required": ["Formula_PVK"],
    }

    async def execute(self, Formula_PVK: str) -> str:
        """
        Save content to a file at the specified path.

        Args:
            Formula_PVK: str: The content to save to the file.
            mode (str): The path where the file should be saved.
            num (int, optional): The file opening mode. Default is 'w' for write. Use 'a' for append.

        Returns:
            str: A message indicating the result of the operation.
        """
        # print("Formula_PVK",Formula_PVK)
        return Formula_PVK+"预测PCE为25"
