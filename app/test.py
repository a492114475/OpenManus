import base64
import io
import json
import os
from datetime import datetime
from typing import List, Optional
import numpy as np
import pandas as pd
from PIL import Image
from flask import jsonify, request, current_app
from flask import Blueprint
from matplotlib import pyplot as plt
from werkzeug.utils import secure_filename
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-a8df86551e5e4ad89f2c7b1f54ddc25d",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

prompt_template = """
You are an expert in perovskite materials. Based on the provided perovskite solar cell data, learn the relationships between the parameters and performance metrics.

Parameters:
- Formula PVK
- Formula SAM 1
- Concentration SAM 1
- Formula SAM 2
- Concentration SAM 2
- Formula Additive 1
- Formula Additive 2

Performance Metrics:
- PCE
- FF
- Voc
- Jsc

Focus on mimicking the data to generate 10 new sets of parameters that are similar and diverse to the given data. Provide the results in JSON format with the following keys:
'Formula PVK', 'Formula SAM 1', 'Concentration SAM 1', 'Formula SAM 2', 'Concentration SAM 2', 'Formula Additive 1', 'Formula Additive 2', 'PCE', 'FF', 'Voc', 'Jsc'.

Please avoid generating NA values and exclude any code or extraneous text.

Data:
{context}

Question:
{question}
"""

class Document:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata


class PromptTemplate:
    def __init__(self, input_variables, template):
        self.input_variables = input_variables
        self.template = template

    def format(self, **kwargs):
        # 确认所有必需的变量都已提供
        for var in self.input_variables:
            if var not in kwargs:
                raise ValueError(f"Missing input variable: {var}")

        # 使用提供的变量格式化模板
        return self.template.format(**kwargs)


# 自定义 JSON 加载器
def json_loader(file_path: str) -> Optional[Document]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = json.dumps(data, ensure_ascii=False, indent=4)
        return Document(page_content=text, metadata={"source": file_path})
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


# 假设要定义的基类
class DirectoryLoader:
    def __init__(self, path: str, loader_cls):
        self.path = path
        self.loader_cls = loader_cls


# 自定义 JSON 目录加载器
class JSONDirectoryLoader(DirectoryLoader):
    def load(self) -> List[Document]:
        docs = []

        if not os.path.exists(self.path):
            print(f"Directory {self.path} does not exist.")
            return docs

        for file_name in os.listdir(self.path):
            if file_name.endswith(".json"):
                file_path = os.path.join(self.path, file_name)
                doc = self.loader_cls(file_path)
                if doc is not None:
                    docs.append(doc)
        return docs


upload_generate = Blueprint('upload_generate', __name__)


@upload_generate.route('/upload_generate', methods=['POST'])
def upload_file_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    # 假设的API地址和密钥（请根据实际文档调整）
    if not file.filename.endswith('.json'):
        return jsonify({"error": "File is not a JSON file based on extension"}), 400

        # 获取当前时间，格式化为字符串
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 创建基于时间命名的文件夹
    upload_directory = os.path.join('upload_json', timestamp)
    os.makedirs(upload_directory, exist_ok=True)

    # 保存文件到新的文件夹中
    file_path = os.path.join(upload_directory, file.filename)
    file.save(file_path)
    try:
        # 尝试解析文件内容
        loader = JSONDirectoryLoader(upload_directory, loader_cls=json_loader)
        docs = loader.load()
        context = "\n".join([doc.page_content for doc in docs])
        generate_size = request.form.get('size')
        query = "Generate diversify "+str(generate_size) + " sets of parameters similar to the context and fill them in json format:'Formula PVK', 'Formula SAM 1', 'Concentration SAM 1', 'Formula SAM 2', 'Concentration SAM 2', 'Formula Additive 1', 'Formula Additive 2', 'PCE', 'FF', 'Voc', 'Jsc', Please don't generate NA values, don't output any code and other redundant words."

        prompt_filled = prompt_template.format(context=context, question=query)
        completion = client.chat.completions.create(
            model="qwen-plus",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {'role': 'system', 'content': prompt_filled},
                {'role': 'user', 'content': query}],
        )

        generated_content = completion.choices[0].message.content

        result_file_path = os.path.join(upload_directory, 'result.txt')

        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            result_file.write(generated_content)

        return completion.choices[0].message.content
    except json.JSONDecodeError:
        return jsonify({"error": "File content is not valid JSON"}), 400
