"""仅在本轮离线分析命令中阻止网络连接；不修改全局环境或实验代码。"""
import os
import socket
import json
from pathlib import Path
os.environ['BDR_ANALYSIS_OFFLINE_GUARD']='active'
def blocked(self,address):
    if self.family in (socket.AF_INET,socket.AF_INET6):
        target=os.environ.get('BDR_ANALYSIS_NETWORK_AUDIT')
        if target:
            with Path(target).open('a') as f:f.write(json.dumps({'blocked':True,'address':str(address)})+'\n')
        raise OSError('BDR analysis is offline; network connections are disabled')
    return original_connect(self,address)
original_connect=socket.socket.connect
socket.socket.connect=blocked
socket.socket.connect_ex=blocked
