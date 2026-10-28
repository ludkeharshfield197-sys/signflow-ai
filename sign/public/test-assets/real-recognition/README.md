# SignFlow AI 真实识别测试素材

这套素材用于产品验证和上线前冒烟测试。它不会触发训练，也不会修改 `ASl-v8.pt` 权重。

## 使用方法

1. 登录网页并打开 `/app/workbench`。
2. 选择“图片”或“视频”。
3. 上传本目录中对应类型的文件。
4. 保持“标准”预设，点击“开始识别”。

## 已验证正样例

| 文件 | 期望结果 | API 实测置信度 |
| --- | --- | ---: |
| `images/bread.jpg` | `bread` | 93.5% |
| `images/hello.jpg` | `hello` | 88.0% |
| `images/milk.jpg` | `milk` | 80.0% |
| `images/thank-you.jpg` | `thank-you` | 91.7% |
| `images/water.jpg` | `water` | 85.5% |
| `videos/hello-thank-you.mp4` | `hello thank-you` | 88.8% |
| `videos/hello.mp4` | `hello` | 87.9% |
| `videos/milk.mp4` | `milk` | 79.9% |
| `videos/thank-you.mp4` | `thank-you` | 91.3% |

正样例图片来自项目已有验证集并做了演示命名整理；MP4 是本次基于已验证帧生成的轻微镜头运动测试视频。每个文件都已通过网页所调用的本地 HTTP API 和真实模型推理，任务 ID 与精确结果记录在 `manifest.json`。

## 负样例

`negative/generated-milk-candidate-no-detection.png` 是本次生成的写实候选图，但当前模型在标准阈值下没有检出。它被明确保留为负样例，用来验证页面会诚实显示“未检出”，不能作为模型准确率或正样例展示。

## 模型边界

当前 `ASl-v8.pt` 是 80 类 ASL 餐饮与服务场景词汇检测模型，不是通用中国手语翻译模型。真实人物、机位、光线和动作差异会影响置信度；产品验收时建议先使用本目录正样例验证完整推理链路，再补充现场采集素材。
