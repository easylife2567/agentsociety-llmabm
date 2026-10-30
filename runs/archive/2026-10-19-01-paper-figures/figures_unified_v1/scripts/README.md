# 最终绘图源码

- gen_fig1.py—gen_fig6.py：最终六图。
- paper_plot_style.py：统一配色、Arial、星形事件标记、原生矢量导出。
- audit_panel_alignment.py：绘制时实际区域对齐检查。
- nature_source_preflight.py、audit_pdf_text.py、audit_figure_collisions.py：最终源码/字体/遮挡审计。
- audit_final.py：当前六图源码、PDF实际字号和遮挡审计。
- rebuild_final.py：归档校验与新目录离线重绘，禁止覆盖非空目录。
- requirements.txt：验证时的依赖版本；实际环境指纹见../../recovery/environment.json。

六图不依赖旧候选目录或项目相对层级，不读取原工作簿、不调用LLM或联网。字体Arial/STIX由本机环境提供，未复制字体文件。
