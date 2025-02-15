"""
LXJAI 命令行版 v1.0
安全智能终端助手
"""

import os
import re
import ast
import json
import time
import psutil
import platform
import tiktoken
import requests
import subprocess
from typing import Dict, List, Tuple

# ============ 配置管理模块 ============
AA = {  # 原 DEFAULT_CONFIG
    "A": "sk-",
    "B": "https://api.siliconflow.com/v1/chat/completions",
    "C": "deepseek-ai/DeepSeek-R1",
    "D": 2,
    "E": "zh-CN",
    "F": 5,
    "G": True,
    "H": -1,
    "I": 0.7
}


def AB():  # 原 load_config
    AC = os.path.expanduser("~/.lxjai_config")  # 配置文件路径
    if os.path.exists(AC):
        with open(AC, "r") as AD:
            return json.load(AD)
    AE(AA)
    return AA


def AE(AF):  # 原 save_config
    with open(os.path.expanduser("~/.lxjai_config"), "w") as AG:
        json.dump(AF, AG, indent=2)


# ============ 核心功能模块 ============
class AH:  # 原 SystemUtils
    @staticmethod
    def AI():  # 获取系统信息
        return {
            "AJ": platform.system(),  # OS
            "AK": platform.version(),  # Version
            "AL": platform.machine(),  # Arch
            "AM": f"{psutil.cpu_count()} cores",
            "AN": f"{psutil.virtual_memory().total // (1024 ** 3)}GB"
        }

    @staticmethod
    def AO(AP, AQ):  # 安全执行代码
        with tempfile.TemporaryDirectory() as AR:
            AS = os.path.join(AR, "script.py")
            with open(AS, "w") as AT:
                AT.write(f"# SAFE EXECUTION CONTEXT\n{AP}")

            try:
                AU = subprocess.run(
                    ["python", AS],
                    capture_output=True,
                    text=True,
                    timeout=AQ if AQ > 0 else 30,
                )
                return AU.stdout.strip(), AU.stderr.strip()
            except subprocess.TimeoutExpired:
                return "", "执行超时"
            except Exception as AV:
                return "", str(AV)


class AW:  # 原 NeoAIEngine
    def __init__(self, AX):
        self.AY = AX
        self.AZ = []
        self.BA = {
            0: {"BB": ["query"], "BC": ["exec", "write"]},
            1: {"BB": ["read", "simple_write"], "BC": ["system"]},
            2: {"BB": ["system_call"], "BC": ["admin"]},
            3: {"BB": ["*"], "BC": []}
        }

    def BD(self, BE):  # 生成提示词
        BF = f"""
        当前安全级别：{self.AY['D']}
        允许操作：{self.BA[self.AY['D']]['BB']}
        系统信息：{AH.AI()}

        执行要求：
        1. 代码必须包裹在 >>>RUN>>> 中
        2. 复杂操作需分步确认
        3. 危险操作需添加警告标识

        用户请求：{BE}
        """
        return BF.replace("\n", " ").strip()

    def BG(self, BH):  # 处理查询
        self.BI("解析请求", 20)

        BJ = self.BD(BH)
        BK = self.BL(BJ)

        self.BI("分析响应", 40)
        BM = self.BN(BK)

        BO = []
        for BP in BM:
            self.BI("执行阶段", 60)
            BQ = self.BR(BP)
            BS, BT = AH.AO(BP, BQ)
            BO.append({
                "BU": BP,
                "BV": BS,
                "BW": BT,
                "BX": time.time()
            })

        return {
            "BY": BK,
            "BZ": BO,
            "CA": self.AY["D"]
        }

    def BL(self, CB):  # 调用API
        CC = {
            "Authorization": f"Bearer {self.AY['A']}",
            "Content-Type": "application/json"
        }

        CD = {
            "model": self.AY["C"],
            "messages": [
                {"role": "system", "content": "你是智能终端助手"},
                {"role": "user", "content": CB}
            ],
            "temperature": self.AY["I"]
        }

        try:
            CE = requests.post(
                self.AY["B"],
                headers=CC,
                json=CD,
                timeout=30
            )
            return CE.json()["choices"][0]["message"]["content"]
        except Exception as CF:
            return f"API错误: {str(CF)}"

    def BN(self, CG):  # 提取代码
        return re.findall(r">>>RUN>>>([\s\S]*?)<<<RUN<<<", CG)

    def BR(self, CH):  # 计算超时
        if self.AY["H"] > 0:
            return self.AY["H"]
        CI = len(ast.parse(CH).body)
        return min(max(CI * 2, 5), 60)

    def BI(self, CJ, CK):  # 显示进度条
        CL = "[" + "#" * (CK // 5) + " " * (20 - CK // 5) + "]"
        print(f"\r{CJ} {CL}", end="", flush=True)


# ============ 界面交互模块 ============
class CM:  # 原 TerminalInterface
    def __init__(self):
        self.CN = AB()
        self.CO = AW(self.CN)

    def CP(self):  # 主循环
        while True:
            self.CQ()
            print(f"""
            ╦  ╔╗╔┬┌─┐┌┬┐┌─┐┬─┐
            ║  ║║║├┤  │ ├┤ ├┬┘
            ╩═╝╝╚╝└─┘ ┴ └─┘┴└─

            安全级别: {self.CN['D']} | 模型: {self.CN['C']}
            """)

            CR = input("\n请输入指令（输入help查看帮助）> ").strip()

            if CR.lower() in ["exit", "quit"]:
                print("📴 已终止会话")
                break

            self.CS(CR)

    def CS(self, CT):  # 命令路由
        if CT.startswith("!"):
            self.CU(CT[1:])
        elif CT.lower() == "help":
            self.CV()
        elif CT.lower().startswith("config"):
            self.CW()
        else:
            self.CX(CT)

    def CU(self, CY):  # 系统命令
        if CY == "clear":
            self.CO.AZ = []
            print("✅ 已清除执行历史")
        elif CY.startswith("level"):
            CZ = int(CY.split()[-1])
            if 0 <= CZ <= 3:
                self.CN["D"] = CZ
                AE(self.CN)
                print(f"🛡️ 已切换至安全级别 {CZ}")
        else:
            print(f"⚠️ 无效系统命令: {CY}")

    def CX(self, DA):  # AI处理
        DB = self.CO.BG(DA)
        print("\n\n=== 智能响应 ===")
        print(DB["BY"])

        if DB["BZ"]:
            print("\n=== 执行报告 ===")
            for DC, DD in enumerate(DB["BZ"], 1):
                DE = "✅ 完成" if not DD["BW"] else "❌ 失败"
                print(f"{DC}. {DE}")
                if DD["BW"]:
                    print(f"   错误详情: {DD['BW']}")

    def CV(self):  # 帮助信息
        print("""
        LXJAI 帮助文档：

        基础命令：
        help    - 显示本帮助
        exit    - 退出程序
        !clear  - 清除执行历史
        !level [0-3] - 设置安全级别

        查询示例：
        list files    查看当前目录
        check network 检查网络状态
        system info   获取系统信息
        """)

    def CQ(self):  # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')

    def CW(self):  # 配置管理
        print("\n=== 配置管理 ===")
        print(f"1. API密钥: {self.CN['A'][:6]}***")
        print(f"2. 安全级别: {self.CN['D']}")
        print(f"3. 模型版本: {self.CN['C']}")
        CF = input("选择配置项（回车返回）> ")
        # 配置编辑逻辑...


if __name__ == "__main__":
    CM().CP()
