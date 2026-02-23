# yachiyo-qwen-voice-reply

> 八千代 ヤチヨ (Yachiyo) — 动画《超时空辉夜姬》中的 AI 助手角色，以温柔、亲和的声音陪伴主角。  
> 本项目将她的声音克隆并集成到 OpenClaw 智能助手中，让 AI 助手能以八千代的声音进行语音回复。

## 项目简介

两个配套的 [OpenClaw](https://openclaw.ai) Agent Skills：

| Skill | 功能 |
|---|---|
| `yachiyo-qwen-voice-reply` | 使用 Qwen3-TTS 克隆音色生成 Telegram 语音回复，并在本地自动播放 |
| `qwen3-tts-voice-clone` | 管理阿里云百炼声音复刻（创建 / 查询 / 删除克隆音色） |

## 功能特性

- 🎙️ **声音克隆**：基于 `qwen-voice-enrollment`，10~20 秒音频即可复刻音色
- 🌐 **多语言支持**：`--voice-tag jp/zh/en` 约束语言，确保发音自然
- 📱 **Telegram 集成**：ogg/opus 格式，caption 自动设为 TTS 输入文本
- 🔊 **本地自动播放**：发送 Telegram 同时本地播放，互不阻塞
- 🧹 **自动清理**：临时 wav 播完后自动删除

## 安装

```bash
cp -R yachiyo-qwen-voice-reply ~/.openclaw/workspace/skills/
cp -R qwen3-tts-voice-clone ~/.openclaw/workspace/skills/
```

依赖：`python3`、`ffmpeg`、`pip install dashscope`

```bash
export DASHSCOPE_API_KEY="<your-api-key>"
```

## 使用

```bash
# 日语语音回复（默认自动播放）
skills/yachiyo-qwen-voice-reply/bin/voice-reply --voice-tag jp "こんにちは！"

# 关闭本地播放
skills/yachiyo-qwen-voice-reply/bin/voice-reply --voice-tag jp --no-autoplay "テスト"
```

| `--voice-tag` | 语言 |
|---|---|
| `jp` | 日语 |
| `zh` | 中文 |
| `en` | 英文 |

## 工作流程

```
输入文本 + voice-tag
    ↓
Qwen3-TTS 合成（国际区）→ ffmpeg 转码 ogg/opus
    ↓
输出路径 → 发送 Telegram 语音消息（caption = TTS 输入文本）
    ↓（同时）
后台子进程：ogg → wav → afplay → 删除 wav
```

## 致谢

本项目由 [sdyzjx](https://github.com/sdyzjx) [wkf16](https://github.com/wkf16) 共同完成，AI 协作伙伴 ヤチヨ 全程参与开发。

## License

MIT
