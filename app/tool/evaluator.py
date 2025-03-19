import json
import os

import aiofiles
import requests

from app.tool.base import BaseTool

import re


def parse_formula(formula):
    # 定义所有可能的元素列表
    elements = ["Cs", "FA", "MA", "Pb", "I", "Br"]

    result = {element: 0 for element in elements}

    # 如果输入为空或无效，直接返回空字典
    if not formula or not isinstance(formula, str):
        return {}

    # 使用正则表达式匹配 "元素符号 + 数值" 的模式
    pattern = re.compile(r"([A-Za-z]+)(\d*\.?\d*)")
    matches = pattern.findall(formula)

    # 遍历匹配结果，更新字典
    for element, value in matches:
        if element in result:
            # 如果有数值，则转换为浮点数；如果没有数值，默认为 1
            result[element] = float(value) if value else 0

    return result


def parse_additive1(formula_value: str, concentration: float):
    # 定义所有可能的添加剂类型
    formula_key = "Formula Additive 1"
    additives = ["BSP", "MACl", "PACl", "PEABr", "PEAI", "PMACl"]

    result = {f"{formula_key}_{additive}": 0.0 for additive in additives}

    # 如果 formula_value 存在且有效，更新对应添加剂的浓度
    if formula_value in additives:
        result[f"{formula_key}_{formula_value}"] = concentration

    return result


def parse_additive2(formula_value: str, concentration: float):
    # 定义所有可能的添加剂类型
    formula_key = "Formula Additive 2"
    additives = ["BSP", "MACl", "PACl", "PEABr", "PEAI", "PMACl"]

    result = {f"{formula_key}_{additive}": 0.0 for additive in additives}

    # 如果 formula_value 存在且有效，更新对应添加剂的浓度
    if formula_value in additives:
        result[f"{formula_key}_{formula_value}"] = concentration

    return result


def parse_sam1(formula_value: str, concentration: float):
    # 定义所有可能的添加剂类型
    formula_key = "Formula SAM 1"
    additives = ["2PACz", "4PACz", "4PADBC", "DMACPA", "Me-2PACz", "Me-4PACz", "MeO-2PACz", "MeO-4PACz", "MeO-4PADBC",
                 "py3"]

    result = {f"{formula_key}_{additive}": 0.0 for additive in additives}

    # 如果 formula_value 存在且有效，更新对应添加剂的浓度
    if formula_value in additives:
        result[f"{formula_key}_{formula_value}"] = concentration

    return result


def parse_sam2(formula_value: str, concentration: float):
    # 定义所有可能的添加剂类型
    formula_key = "Formula SAM 2"
    additives = ["2PACz", "4PACz", "DMACPA", "Me-2PACz", "MeO-2PACz", "MeO-4PADBC", "py3"]

    result = {f"{formula_key}_{additive}": 0.0 for additive in additives}

    # 如果 formula_value 存在且有效，更新对应添加剂的浓度
    if formula_value in additives:
        result[f"{formula_key}_{formula_value}"] = concentration

    return result


class Evaluator(BaseTool):
    name: str = "Evaluator"
    description: str = """Predict PCE, FF, JSC, and VOC results based on perovskite formula and process.
To predict or evaluate the timing of PCE, FF, JSC, and VOC, please use this tool.
This tool receives perovskite formulas and processes for prediction and evaluation."""
    parameters: dict = {
        "type": "object",
        "properties": {
            "Etype": {
                "type": "string",
                "description": "(required) The method of generating experimental formulas and process parameters for evaluation.",
                "enum": ["DPO生成", "其他", "普通生成"],
                "default": "其他",
            },
            "Formula_PVK": {
                "type": "string",
                "description": "(required) Formula PVK.",
                "default": "",
            },
            "Concentration_PVK": {
                "type": "float",
                "description": "(optional) Concentration PVK",
                "default": 1.73,
            },
            "Spin_Coating_Speed_1": {
                "type": "float",
                "description": "(required) Spin Coating Speed 1",
                "default": 0,
            },
            "Spin_Coating_Time_1": {
                "type": "float",
                "description": "(required) Spin Coating Time 1",
                "default": 0,
            },
            "Spin_Coating_Speed_2": {
                "type": "float",
                "description": "(required) Spin Coating Speed 2",
                "default": 0,
            },
            "Spin_Coating_Time_2": {
                "type": "float",
                "description": "(required) Spin Coating Time 2",
                "default": 0,
            },
            "Antisolvent_Dropping_Timing": {
                "type": "float",
                "description": "(required) Antisolvent Dropping Timing",
                "default": 0,
            },
            "Antisolvent_Volume": {
                "type": "float",
                "description": "(required) Antisolvent Volume",
                "default": 0,
            },
            "Annealed_Temperature": {
                "type": "float",
                "description": "(required) Annealed Temperature",
                "default": 0,
            },
            "Annealed_Time": {
                "type": "float",
                "description": "(required) Annealed Time",
                "default": 0,
            },
            "Formula_Additive_1": {
                "type": "string",
                "description": "(required) Formula_Additive_1",
                "default": 0,
            },
            "Concentration_Additive_1": {
                "type": "float",
                "description": "(required) Concentration_Additive_1",
                "default": 0,
            },
            "Formula_Additive_2": {
                "type": "string",
                "description": "(required) Formula Additive 2",
                "default": "",
            },
            "Concentration_Additive_2": {
                "type": "float",
                "description": "(required) Concentration Additive 2",
                "default": 0,
            },
            "Formula_SAM_1": {
                "type": "string",
                "description": "(required) Concentration_Additive_1",
                "default": 0,
            },
            "Concentration_SAM_1": {
                "type": "float",
                "description": "(required) Concentration_Additive_1",
                "default": 0,
            },
            "Formula_SAM_2": {
                "type": "string",
                "description": "(required) Concentration_Additive_1",
                "default": 0,
            },
            "Concentration_SAM_2": {
                "type": "float",
                "description": "(required) Concentration_Additive_1",
                "default": 0,
            },
        },

        "required": ["Etype", "Formula_PVK", "Concentration_PVK", "Spin_Coating_Speed_1", "Spin_Coating_Time_1",
                     "Spin_Coating_Speed_2",
                     "Spin_Coating_Time_2", "Antisolvent_Dropping_Timing", "Antisolvent_Volume", "Annealed_Temperature",
                     "Annealed_Time",
                     "Formula_Additive_1", "Concentration_Additive_1", "Formula_Additive_2", "Concentration_Additive_2",
                     "Formula_SAM_1",
                     "Concentration_SAM_1", "Formula_SAM_2", "Concentration_SAM_2"],
    }

    async def execute(self, Etype: str, Formula_PVK: str, Concentration_PVK: float, Spin_Coating_Speed_1: float,
                      Spin_Coating_Time_1: float,
                      Spin_Coating_Speed_2: float, Spin_Coating_Time_2: float, Antisolvent_Dropping_Timing: float,
                      Antisolvent_Volume: float, Annealed_Temperature: float, Annealed_Time: float,
                      Formula_Additive_1: str, Concentration_Additive_1: float,
                      Formula_Additive_2: str, Concentration_Additive_2: float,
                      Formula_SAM_1: str, Concentration_SAM_1: float,
                      Formula_SAM_2: str, Concentration_SAM_2: float) -> str:
        pvk_formula = parse_formula(Formula_PVK)
        Additive_1 = parse_additive1(Formula_Additive_1, Concentration_Additive_1)
        Additive_2 = parse_additive2(Formula_Additive_2, Concentration_Additive_2)
        sam1 = parse_sam1(Formula_SAM_1, Concentration_SAM_1)
        sam2 = parse_sam2(Formula_SAM_2, Concentration_SAM_2)
        # 打印输出
        if Etype == "普通生成":
            output = {
                **pvk_formula,  # PVK 公式的解析结果
                "Concentration PVK": Concentration_PVK,
                "Spin Coating Speed 1": Spin_Coating_Speed_1,
                "Spin Coating Time 1": Spin_Coating_Time_1,
                "Spin Coating Speed 2": Spin_Coating_Speed_2,
                "Spin Coating Time 2": Spin_Coating_Time_2,
                "Antisolvent Dropping Timing": Antisolvent_Dropping_Timing,
                "Antisolvent Volume": Antisolvent_Volume,
                "Annealed Temperature": Annealed_Temperature,
                "Annealed Time": Annealed_Time,
                **Additive_1,
                **Additive_2,
                **sam1,
                **sam2
            }
            # 将数据转换为 JSON 格式
            json_data = json.dumps(output)
            # 设置请求头
            headers = {
                "Content-Type": "application/json"
            }
            url = "http://39.174.223.92:9988/predict"
            try:
                # 发送 POST 请求
                response = requests.post(url, data=json_data, headers=headers)

                # 检查响应状态码
                if response.status_code == 200:
                    # 解析返回的 JSON 数据
                    result = response.json()

                    # 提取 prediction 列表
                    prediction = result.get("prediction", [])

                    # 确保 prediction 列表长度正确
                    if len(prediction) == 4:
                        # 映射到目标字段
                        mapped_result = {
                            "PCE": prediction[0],
                            "FF": prediction[1],
                            "Voc": prediction[2],
                            "Jsc": prediction[3]
                        }

                        # 打印映射后的结果
                        print("映射后的结果：", json.dumps(mapped_result, ensure_ascii=False, indent=4))
                    else:
                        print("返回的 prediction 列表长度不正确")
                else:
                    print(f"请求失败，状态码：{response.status_code}")
                    print("错误信息：", response.text)
            except requests.exceptions.RequestException as e:
                print("请求过程中发生错误：", e)

            # print("Formula_PVK",Formula_PVK)
            return mapped_result
        if Etype == "DPO生成":
            return "评估结束，DPO评估结果已保存"
        if Etype == "其他":
            return "数据格式不符合要求，评估结束"
