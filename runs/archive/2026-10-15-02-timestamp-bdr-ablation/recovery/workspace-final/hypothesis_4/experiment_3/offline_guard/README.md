# 禁网入口

[sitecustomize.py](sitecustomize.py)注册Python审计钩子，在连接、地址解析及发送之前抛错；被阻止的尝试写入验收目录。verify_offline.py导入同一钩子，并通过PYTHONPATH让生成器子进程加载它。验收另拦截真实litellm异步Provider入口，固定正文替身不经过服务。
