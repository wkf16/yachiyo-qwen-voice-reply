---
name: yachiyo-qwen-voice-reply
description: 使用 Qwen3-TTS 复刻音色（八千代 voice）生成 Telegram 语音回复。触发优先级：1) 用户消息是语音/音频转写时，优先语音回复；2) 即使用户是文字消息，只要最终答复较短（建议≤4句且无复杂格式），可自主选择语音回复。若内容较长或含代码/表格/链接清单，则改用文字回复。
metadata: {"openclaw":{"emoji":"🌙","requires":{"bins":["python3","ffmpeg"]}}}
---

# Yachiyo Qwen Voice Reply

默认输出：
- 仅输出本地 ogg 路径（例如 `/tmp/yachiyo-voice-xxx.ogg`），由调用方决定发送方式（用于避免重复发送）

## 触发机制（优化版）

### A. 用户发语音时（默认优先语音）
满足以下条件则直接走语音：
- 你的回复是短答（建议 ≤4句）
- 无代码块、无表格、无长链接清单

改为文字回复的例外：
- 需要详细步骤、命令、参数、长清单
- 需要精确复制的文本（如配置、脚本、JSON）

### B. 用户发文字时（可自主选择）
当回复较短且偏口语时，可主动用语音回复。
建议阈值：
- 中文约 ≤120字（或英文 ≤80词）
- 总体 ≤4句

### C. 避免触发
- 长文解释、教程、排障步骤
- 代码/命令输出
- 多链接资料汇总

## 用法

```bash
# 必须传语音标签（jp|zh|en），默认只输出 ogg 路径（由上层 message 工具发送）
{baseDir}/bin/voice-reply --voice-tag jp "要朗读的文本"

# 若上层需要把“音频描述/caption”设置为 TTS 输入文本，使用 manifest 模式
{baseDir}/bin/voice-reply --voice-tag jp --emit-manifest "要朗读的文本"
# 输出 JSON: {audio_path, tts_input_text, ...}
```

语音标签说明：
- `jp`：日语
- `zh`：中文
- `en`：英文

## 默认配置

- model: `qwen3-tts-vc-2026-01-22`
- voice: `qwen-tts-vc-guanyu-voice-20260216143709994-f294`
- key: 优先读取环境变量 `DASHSCOPE_API_KEY`；无环境变量时使用脚本内默认值。

## 建议流程

1. 先写好最终简短文本（1~3句最佳）。
2. 调用 `bin/voice-reply` 生成语音。
3. 发送语音时，**caption 必须设置为 TTS 输入文本**（即传给 voice-reply 的那段日语文本），不得为空或使用其他描述。
   - 使用 `message(action=send, asVoice=true, media=<ogg路径>, caption=<TTS输入文本>)`
   - 如信息密度较高，再补一条精简文字要点。