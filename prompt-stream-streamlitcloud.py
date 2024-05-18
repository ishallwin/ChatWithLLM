import os
from zhipuai import ZhipuAI
#from dotenv import load_dotenv, find_dotenv
import streamlit as st

#_ = load_dotenv(find_dotenv())
api_key = st.secrets["api_key"]
if api_key is None:
    raise ValueError("API Key is not set in the .env file")
client = ZhipuAI(api_key=api_key)

def get_stream_completion(prompt, model="glm-4", temperature=0.01):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True  # 启用流式输出
    )
    return response

def check_password():      
    # 预设的密码  
    correct_password = "llssys57"  
    #返回值
    ret = False 
    
    # 检查是否已经设置了session_state.is_authenticated  
    if 'is_authenticated' not in st.session_state:  
        st.session_state.is_authenticated = False  
    
    # 如果尚未验证，则提示用户输入密码  
    if not st.session_state.is_authenticated:  
        password_input = st.text_input("请输入密码以继续：", type='password')  
        
        # 检查密码是否正确  
        if password_input == correct_password:  
            st.session_state.is_authenticated = True  
            st.success("密码正确，欢迎进入！")  
            ret = True
        else:  
            st.error("密码错误，请重试。")  
    else:  
        # 如果已经验证过密码，则显示欢迎信息或进行其他操作  
        ret = True
        #st.write("欢迎回来！密码已经验证过，现在可以进行其他操作。")  
        # 在这里继续你的程序逻辑  
    
    return ret



# 头像配置
ICON_AI = '💻'
ICON_USER = '🧑'

# 显示一条消息（包含头像与消息内容）
def dspMessage(role, content, container):
    with container:
        if role == 'assistant':
            st.markdown(f"{ICON_AI} {content}")
        else:
            st.markdown(f"{ICON_USER} {content}")

# 追加并显示一条消息
def append_and_show(role, content, container):
    st.session_state.messages.append({"role": role, "content": content})      
    dspMessage(role, content, container)

# Streamlit 应用程序入口
def main():
    try:
        if not check_password():
            return

# 如果还没有消息，则添加第一条提示消息
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "我是你的信息助手，请问你查询什么信息？"}]

# 将会话中的messages列表中的消息全部显示出来
for msg in st.session_state.messages:
    container = st.empty()  # 创建一个新的动态区域
    dspMessage(msg["role"], msg["content"], container)

# 接受用户输入的提示词，并调用大模型API获得反馈
if prompt := st.chat_input():
    user_container = st.empty()  # 用户消息的动态区域
    assistant_container = st.empty()  # 助手消息的动态区域
    
    append_and_show("user", prompt, user_container)
    
    # 初始化回复内容为空
    assistant_response = ""
    
    # 在会话状态中创建或重置assistant的响应
    response_key = "assistant_response"
    st.session_state[response_key] = ""
    
    # 获取流式输出的生成器
    stream_response = get_stream_completion(prompt, temperature=0.9)
    
    # 逐步接收流式数据并显示
    for chunk in stream_response:
        content_chunk = chunk.choices[0].delta.content
        st.session_state[response_key] += content_chunk
        assistant_container.markdown(f"{ICON_AI} {st.session_state[response_key]}")
    
    # 保存并显示已经完成的回复
    append_and_show("assistant", st.session_state[response_key], assistant_container)