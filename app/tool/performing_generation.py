import os
from openai import OpenAI
import json
import aiofiles
import requests

from app.tool.base import BaseTool

client = OpenAI(api_key="sk-01a8937c3e4141fdb47ade134c01fbb6",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")


def get_answer(messages):
    """
    发送请求到 API 并获取回答。

    参数:
        messages (list): 消息列表，包括系统消息和用户消息。
        model_path (str): 模型的路径或标识符。

    返回:
        str: 模型生成的回答内容。
    """
    try:
        result = client.chat.completions.create(
            messages=messages,
            model='qwen-plus',
            temperature=0.7,
            top_p=0.9,
            max_tokens=4096,
        )
        # 提取回答内容
        answer = result.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"请求 API 时出错: {e}")
        return ""


def remove_unwanted_fields(data, unwanted_fields):
    """
    递归删除数据中的指定字段。
    :param data: 输入数据（可以是字典、列表或 JSON 字符串）
    :param unwanted_fields: 需要删除的字段列表
    :return: 清理后的数据
    """
    # 如果数据是 JSON 字符串，先解析为 Python 数据结构
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("输入数据不是有效的 JSON 字符串")

    # 定义递归函数
    def recursive_remove(obj):
        if isinstance(obj, dict):  # 如果是字典
            for field in unwanted_fields:
                obj.pop(field, None)  # 删除字段（如果存在）
            for key, value in obj.items():
                recursive_remove(value)  # 递归处理值
        elif isinstance(obj, list):  # 如果是列表
            for item in obj:
                recursive_remove(item)  # 递归处理每个元素

    # 调用递归函数
    recursive_remove(data)
    return data

def load_context(json_file_path):
    """
    从 JSON 文件加载上下文信息。

    参数:
        json_file_path (str): JSON 文件的路径。

    返回:
        str: 格式化后的上下文字符串。
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 检查 JSON 数据是否为列表
            if isinstance(data, list):
                # 格式化每个条目
                formatted_entries = []
                for idx, entry in enumerate(data, 1):
                    formatted_entry = f"No. {idx}:\n"
                    for key, value in entry.items():
                        formatted_entry += f"  - {key}: {value}\n"
                    formatted_entries.append(formatted_entry)
                # 将所有条目合并为一个字符串
                context = "\n".join(formatted_entries)
                return context
            else:
                print("JSON 数据不是一个列表。")
                return ""
    except Exception as e:
        print(f"加载 JSON 文件时出错: {e}")
        return ""


def create_prompt(context, question):
    """
    创建用于模型的提示，将上下文和问题结合起来。

    参数:
        context (str): 上下文信息。
        question (str): 用户的问题。

    返回:
        list: 包含一个系统消息和一个用户消息的消息列表。
    """
    prompt = f"""
    You are an expert in perovskite materials. Based on the provided perovskite solar cell data, learn the relationships between the parameters and performance metrics.

    Parameters:
    - Formula PVK
    - Formula SAM 1
    - Concentration SAM 1
    - Formula SAM 2
    - Concentration SAM 2
    - Formula Additive 1
    - Formula Additive 2
    - Spin Coating Speed 1
    - Spin Coating Time 1
    - Spin Coating Speed 2
    - Spin Coating Time 2
    - Antisolvent Volume
    - Antisolvent Dropping Timing
    - Annealed Temperature
    - Annealed Time

    Performance Metrics:
    - PCE
    - FF
    - Voc
    - Jsc

    Focus on mimicking the data to generate 10 new sets of parameters that are similar and diverse to the given data. Provide the results in JSON format with the following keys:
    'Formula PVK', 'Formula SAM 1', 'Concentration SAM 1', 'Formula SAM 2', 'Concentration SAM 2', 'Formula Additive 1', 'Concentration Additive 1', 'Formula Additive 2', 'Concentration Additive 2', 'Spin Coating Speed 1', 'Spin Coating Time 1', 'Spin Coating Speed 2', 'Spin Coating Time 2', 'Antisolvent Volume', 'Antisolvent Dropping Timing', 'Annealed Temperature', 'Annealed Time', 'PCE', 'FF', 'Voc', 'Jsc'.

    Please avoid generating NA values and exclude any code or extraneous text.

    Data:
    {context}

    Question: 
    {question}

    """

    messages = [
        {"role": "system",
         "content": "You are an expert in perovskite materials. Focus on mimicking the data to generate parameters data that are similar to the given parameters data."},
        {"role": "user", "content": prompt}
    ]

    return messages


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
                "enum": ["生成", "DPO生成", "插值生成"],
                "default": "生成",
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

        if mode == "生成":
            if os.path.exists(formula_filepath):
                print("文件存在，配方将基于所给文件生成")
                context = load_context(formula_filepath)
                question = "Generate diversify " + str(
                    num) + " sets of perovskite data PCE of 21%-23% fill them in json format."  # 替换为您的问题
                messages = create_prompt(context, question)
                # 获取回答
                answer = get_answer(messages)
                unwanted_fields = ["PCE", "FF", "Voc", "Jsc"]

                # 调用函数移除字段
                cleaned_data = remove_unwanted_fields(answer, unwanted_fields)
                output = json.dumps(cleaned_data, ensure_ascii=False, indent=4)

                # 确保 output 是字符串后再拼接
                if not isinstance(output, str):
                    raise ValueError("Expected output to be a string, but got:", type(output))

                # 打印结果

                return ("基于文件生成完毕, 配方如下" + output)
            else:
                print("文件不存在, 将由模型推荐")
                question = "Generate diversify " + str(
                    num) + " sets of perovskite data PCE of 21%-23% fill them in json format."  # 替换为您的问题
                context = ""
                # 创建提示
                messages = create_prompt(context, question)

                # 获取回答
                answer = get_answer(messages)
                return "普通生成完毕, 配方如下" + answer
            # formula_filepath = r"C:\\Users\\Administrator\\PycharmProjects\\MetaGPT-main\\MetaGPT-main\\metagpt\\dpo_data.json"
            # _, ext = os.path.splitext(formula_filepath)
            # if ext.lower() == '.json':
            #     url = "http://39.174.223.92:9988/upload_generate"
            #     file = {'file': open(formula_filepath, 'rb')}
            #     data = {'size': num}
            #     response = requests.post(url, files=file, data=data)
            #
            #
            #     response = response.json()
            #     cleaned_data = [
            #         {key: value for key, value in item.items() if key not in {"PCE", "FF", "Voc", "Jsc"}}
            #         for item in response
            #     ]
            # return "配方已生成完毕, 配方如下"+str(cleaned_data)
        if mode == "DPO生成":
            if not os.path.exists(formula_filepath):
                return "文件不存在，需要上传.json格式文件"

            _, ext = os.path.splitext(formula_filepath)
            if ext.lower() != '.json':
                return "文件格式存在问题，需要上传.json格式文件"

            url = "http://39.174.223.92:9988/upload_dpo"
            files = {'file': open(formula_filepath, 'rb')}
            response = requests.post(url, files=files)
            return response.text + "，结果将保存在results.txt中"
        if mode == "插值生成":
            return "ERROR"

