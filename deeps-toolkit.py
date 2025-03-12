from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.styles import Style
from openai import OpenAI
from colorama import init, Fore
import socket
import threading
import signal
import sys
import markdown
import os
import subprocess

# 定义命令行样式
style = Style.from_dict({
    'prompt': '#00ffff bold',     # 蓝绿色加粗
    'user': '#ffaf00',            # 橙色
    'assistant': '#FFC0CB',#'#5fd700',     #pink  # 绿色
})

# 初始化对话历史，系统消息提示助手身份
messages = [{"role": "system", "content": "你是一个有帮助的助手,所有回答都使用中文"}]
# 配置 DeepSeek 客户端
def initialize_client():
    api_key=os.getenv("DEEPSEEK_KEY")
    if not api_key:
        print_formatted_text(HTML('\n<assistant>API未设置</assistant>\n'), style=style)
        return None
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        return client
    except Exception as e:
        return None

def main():
    client = initialize_client()
    if not client:
        return

    print_formatted_text(HTML('\n<assistant>DeepSeek-R1(esc+enter输入)</assistant>\n'), style=style) 
    session = PromptSession(multiline=True,style=style)
    
    #session = PromptSession(style=style)
    #初始化 colorama
    init(autoreset=True)
    while True:
        try:
            # 使用自定义提示符接收用户输入
            # 支持多行输入
            # 获取用户输入
            user_input = session.prompt(HTML('<prompt>> </prompt>'), style=style,prompt_continuation=(HTML('<prompt>> </prompt>')))

            # 过滤空行
            if user_input.strip().lower() in ['\n','']:
                continue
            # 退出关键字
            if user_input.strip().lower() in ['exit', 'quit']:
                print_formatted_text(HTML('<assistant>再见！</assistant>'), style=style) 
                break

            messages.append({"role": "user", "content": user_input})

            stream = client.chat.completions.create(
                model="deepseek-r1-250120",
                messages=messages,
                stream=True
            )

            full_response = []

            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response.append(content)
                    print(Fore.YELLOW + content,end="",flush=True)
            print('\n')

            # 更新对话历史记录
            if full_response:
                assistant_response = "".join(full_response)
                messages.append({"role": "assistant", "content": assistant_response})


        except KeyboardInterrupt:
            # 捕获 Ctrl+C 后继续
            continue
        except EOFError:
            # 捕获 Ctrl+D 退出
            break


if __name__ == '__main__':
    main()

