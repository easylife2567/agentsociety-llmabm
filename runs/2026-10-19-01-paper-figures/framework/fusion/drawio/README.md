# 本地 draw.io 可编辑版

2026-10-21按用户要求，把上一层的`framework_fusion_en_v1.svg`重建为本地draw.io文件。保留英文长横版、约三七开的互补研究结构、圆环机制、局部蓝/橙配色、白菊花束/缎带/蜡烛及全部科学文字；原SVG未修改。

| 文件 | 用途 |
|---|---|
| [framework_fusion_en_v1.drawio](framework_fusion_en_v1.drawio) | 本地直接打开的可编辑主文件 |
| [framework_fusion_drawio_preview.png](framework_fusion_drawio_preview.png) | 由本机draw.io实际导出的预览 |
| [convert_to_drawio.py](convert_to_drawio.py) | 标准库转换脚本，读取上一级SVG并生成主文件和清单 |
| [conversion_manifest.json](conversion_manifest.json) | 来源指纹、对象数量及文字清单 |
| [framework_fusion_roundtrip.xml](framework_fusion_roundtrip.xml) | 经draw.io读取后重新导出的未压缩XML，供验证可读取性 |

## 本地使用

双击`.drawio`即可用已安装的draw.io打开；也可以在draw.io中选择“文件→打开”，选取该文件。已在本机draw.io 32.5.5中实际打开，窗口标题和文字对象均确认正确。

58处文字均为独立原生标签，双击可改文字，公式下标使用可编辑HTML下标。矩形、菱形、花瓣均为原生形状；流程线为原生连接线，其中16条至少一端附着到模块，其余保留自由端点。选择多个对象后可按需组合，再整体移动。圆环和少量图标路径为文件内置的矢量自定义形状，可移动、缩放、改色；改变其精确路径时使用形状编辑功能。全部资源随文件保存，未将整图或装饰转成图片，无外部图片依赖。

## 实际验证

- 214个独立对象：58个文本、23条连接线、100个椭圆、16个矩形、1个判断菱形、16个自定义矢量形状；包括3条圆环弧线。
- 58处文字逐项与SVG一致，公式下标仍可编辑。全部16个矢量形状解码为有效XML；没有image节点、位图或外部图片。
- 本机draw.io实际导出PNG并查看，保留整体构图、局部配色与图标。页面2600×980绘图单位，预览导出2600×981像素，末行像素差来自draw.io边界取整。
- 再由draw.io导出未压缩XML，216个模型cell（含2个结构cell）及全部标签与主文件一致。没有借用原SVG渲染冒充draw.io显示验证。
- 对源SVG的SHA256复核一致。科学内容未新增或改写；字体与基线在两种渲染器间存在轻微差别。未修改正式论文、实验与数据。

复现时用项目`.env`的`PYTHON_PATH`运行本目录转换脚本，再用本机draw.io CLI导出，例如：

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io --export --format png \
  --width 2600 --size page --theme light --timeout 45 --disable-update \
  --output framework_fusion_drawio_preview.png framework_fusion_en_v1.drawio
```

以上命令从本目录运行。生成文件仅位于当前run；未覆盖SVG、未commit、push或归档。
