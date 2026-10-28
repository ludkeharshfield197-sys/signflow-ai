# SignFlow AI 比赛演示视频：无字幕新闻主播最终版

## 最终成片

| 项目 | 内容 |
| --- | --- |
| 源成片 | `SignFlow-AI-competition-full-demo-2026-08-28-news-anchor-no-disclosure.mp4` |
| 交付文件 | `SignFlow-AI-competition-FINAL-news-anchor-no-subtitles.mp4` |
| 时长 | 4 分 33 秒 |
| 分辨率 | 1280 × 720 |
| 帧率 | 24 FPS |
| 视频编码 | H.264，原始无字幕录屏码流直拷贝 |
| 音频编码 | AAC LC，48 kHz，单声道 |
| 字幕 | 无烧录字幕、无内封字幕轨 |
| 播报风格 | 庄重、清晰、字正腔圆、节奏稳定的普通话新闻主播风格 |
| 声音来源 | Windows 本地中文男声 `Microsoft Kangkang`，经过广播级后期处理，非真人录音 |
| 文件大小 | 79.54 MiB（83,403,192 字节） |

## 片头内容

```text
各位评委，大家好。欢迎观看无界手语，Sign Flow A I 产品演示。
```

视频旁白不会朗读任何合成语音声明，片头直接进入产品演示。

## 声音处理

1. 全部 14 个章节统一采用 0.90 播报速度，避免各段语速忽快忽慢。
2. 音高轻微下调，使男声更加稳重，但不模仿任何具体主持人。
3. 先转换为 48 kHz，再执行低频噪声清理、高频控制、语音存在感均衡。
4. 使用动态压缩、峰值限幅和响度统一，保证电脑、投影仪和手机播放时清楚稳定。
5. 不添加背景音乐，避免干扰产品说明和产生音乐版权风险。

## 验收结果

| 检查项 | 结果 |
| --- | --- |
| 禁止字样检查 | 旁白源稿中不存在指定声明 |
| 媒体流结构 | 1 路 H.264 视频 + 1 路中文 AAC 音频；0 路字幕流 |
| 完整解码 | 通过，4 分 33 秒视频和音频均无解码错误 |
| 画面一致性 | 新成片视频码流与原始无字幕录屏 SHA-256 完全一致 |
| 平均音量 | -17.0 dB |
| 峰值音量 | -1.4 dB |
| 成片 SHA-256 | `154A66AEBCB52DF9997441C93B7B7B5F4B4D466DB19CBB0B487A55D12ACB96BA` |
| 视频码流 SHA-256 | `bcb4d5089f873b7cba9669c4e66f394a273b42176bc072bbbaaeaa4082a691e6` |

## 本地播放

```text
http://127.0.0.1:8090/SignFlow-AI-competition-full-demo-2026-08-28-news-anchor-no-disclosure.mp4
```

## 重新生成

在项目根目录运行：

```powershell
& .\docs\demo-video\build_host_voice_no_subtitles.ps1
```

相关源文件：

- 播报时间轴：`SignFlow-AI-competition-host-narration-zh-CN.json`
- OneCore 中文语音生成辅助脚本：`synthesize_onecore_speech.ps1`
- 视频合成脚本：`build_host_voice_no_subtitles.ps1`
