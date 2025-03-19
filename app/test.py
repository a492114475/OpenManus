from openai import OpenAI
import json



# 设置模型路径   本地调用
# model_path = "/opt/LLM_Base_Model/DeepSeek-R1-Distill-Llama-32B/"
client = OpenAI(api_key="sk-01a8937c3e4141fdb47ade134c01fbb6", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

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

# 参考 120 条数据推荐

# json_file_path = "test/data_pvk_dpo_1th.json"  # 替换为您的 JSON 文件路径
num =1
# question = "Generate diversify 1 sets of perovskite data PCE of 21%-23% fill them in json format."  # 替换为您的问题
question = "Generate diversify " + str(
    num) + " sets of perovskite data PCE of 21%-23% fill them in json format."  # 替换为您的问题
print(question)
# 加载上下文
# context = load_context(json_file_path)
context =""
# 创建提示
messages = create_prompt(context, question)

# 获取回答
answer = get_answer(messages)

# 输出回答
print("回答:", answer)
