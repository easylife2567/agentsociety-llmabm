"""离线进程（含官方生成器子进程）的网络硬阻断，不加载任何凭据。"""
import os
import sys


def deny_network(event, args):
    if event in {'socket.connect', 'socket.getaddrinfo', 'socket.sendto'}:
        target = os.environ.get('BDR_NETWORK_AUDIT')
        if target:
            with open(target, 'a') as file:
                file.write(event + '\n')
        raise RuntimeError('BDR offline acceptance forbids network: ' + event)


sys.addaudithook(deny_network)
