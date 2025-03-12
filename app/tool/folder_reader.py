import os
from typing import Optional
from app.tool.base import BaseTool


class FolderReader(BaseTool):
    name: str = "folder_reader"
    description: str = """Navigate through directories and list their contents in a hierarchical format.
Use this tool when you need to explore the filesystem and list files or subdirectories in a structured way.
The tool accepts a directory path and can step into subdirectories to list their contents.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "(required) The initial directory path to start from.",
            },
            "step_into": {
                "type": "string",
                "description": "(optional) The name of a subdirectory to step into. Use this to navigate through directories.",
            },
            "depth": {
                "type": "integer",
                "description": "(optional) The maximum depth to traverse. Default is 1 (only list immediate contents).",
                "default": 1,
            },
        },
        "required": ["path"],
    }

    async def execute(self, path: str, step_into: Optional[str] = None, depth: int = 1) -> str:
        """
        Navigate through directories and list their contents in a hierarchical format.

        Args:
            path (str): The initial directory path to start from.
            step_into (Optional[str]): The name of a subdirectory to step into.
            depth (int): The maximum depth to traverse. Default is 1 (only list immediate contents).

        Returns:
            str: A hierarchical list of items in the current directory, or an error message if the path is invalid.
        """
        try:
            # Normalize the path to handle any relative paths
            path = os.path.abspath(path)

            # If step_into is provided, navigate into the specified subdirectory
            if step_into:
                new_path = os.path.join(path, step_into)
                if not os.path.exists(new_path):
                    return f"Error: '{step_into}' does not exist in '{path}'."
                path = new_path

            # If the path is a directory, list its contents in a hierarchical format
            if os.path.isdir(path):
                return self._list_directory(path, depth)

            return f"Error: '{path}' is not a directory."
        except Exception as e:
            return f"Error: {str(e)}"

    def _list_directory(self, path: str, depth: int, indent: int = 0) -> str:
        """
        Recursively list the contents of a directory in a hierarchical format.

        Args:
            path (str): The directory path to list.
            depth (int): The remaining depth to traverse.
            indent (int): The current indentation level (used for formatting).

        Returns:
            str: A hierarchical list of items in the directory.
        """
        if depth < 0:
            return ""

        items = os.listdir(path)
        output = []

        for item in items:
            item_path = os.path.join(path, item)
            output.append("  " * indent + item_path)  # os.path.abspath(item_path)   item

            # If the item is a directory and depth > 0, recursively list its contents
            if os.path.isdir(item_path) and depth > 0:
                output.append(self._list_directory(item_path, depth - 1, indent + 1))

        return "\n".join(output)