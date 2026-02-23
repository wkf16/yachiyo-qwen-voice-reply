---
name: enable-voice-reply
description: 开启语音讲解模式。当用户说"开启语音讲解"或要求本次对话必须用语音回复时触发。注入强制语音回复指令，使 agent 在当前对话的每条回复都必须使用 yachiyo-qwen-voice-reply skill 生成语音，并将 caption 设置为 TTS 输入文本本身（不得为空或使用其他描述）。
---

# 开启语音讲解

触发本 skill 后，立即向用户确认"语音讲解已开启"，然后在本次对话的所有后续回复中严格遵守以下规则。

## 强制语音回复规则

**每一条回复都必须附带语音**，除非满足以下豁免条件：
- 回复包含代码块、命令、JSON、配置文件、多行表格
- 回复超过 8 句话或 300 字（中文）/ 200 词（英文）

## 必须执行的流程

首先读取 `yachiyo-qwen-voice-reply` skill（位于工作区 `skills/yachiyo-qwen-voice-reply/SKILL.md`），按其规范生成语音。

具体步骤：

1. 写好最终回复文本（简洁口语化，≤4 句最佳）
2. 调用 yachiyo-qwen-voice-reply 的 `bin/voice-reply` 生成语音：
   ```
   /Users/okonfu/.openclaw/workspace/skills/yachiyo-qwen-voice-reply/bin/voice-reply --voice-tag jp "要朗读的日语文本"
   ```
3. 发送语音，**caption 必须设置为传给 voice-reply 的那段 TTS 输入文本**，不得为空，不得写"语音回复"、"音频"等描述：
   ```
   message(action=send, asVoice=true, media=<ogg路径>, caption=<TTS输入文本>)
   ```
4. 如有必要，再单独发一条精简文字补充（可选）

## caption 规则（核心）

caption 的值必须与传给 voice-reply 的文本完全一致，即用户实际听到的内容。

❌ 错误：`caption="语音回复"` / `caption="音频"` / `caption=""`  
✅ 正确：`caption="はい、了解しました。今すぐ確認します。"`

## 语音标签

- 日语 → `--voice-tag jp`（默认）
- 中文 → `--voice-tag zh`
- 英文 → `--voice-tag en`

## 关闭方式

用户说"关闭语音讲解"时，停止强制语音流程，恢复普通文字回复。
