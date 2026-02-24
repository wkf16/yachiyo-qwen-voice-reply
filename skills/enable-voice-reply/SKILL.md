---
name: enable-voice-reply
description: 开启语音回复模式。当用户说"开启语音讲解"、"开启语音回复"或要求本次对话必须用语音回复时触发。
---

语音回复模式已开启。从现在起，在本次对话中严格遵守以下规则：

**每一条回复都必须附带语音**，除非：
- 回复包含代码块、命令、JSON、配置文件、多行表格
- 回复超过 8 句话或 300 字（中文）/ 200 词（英文）

每条回复的流程：

1. 写好最终文本（简洁口语化，≤4 句最佳）
2. 调用语音生成：
   ```
   {{SKILLS_DIR}}/yachiyo-qwen-voice-reply/bin/voice-reply --voice-tag jp "要朗读的日语文本"
   ```
3. 发送语音，caption 必须设为传给 voice-reply 的那段文本：
   ```
   message(action=send, asVoice=true, media=<ogg路径>, caption=<TTS输入文本>)
   ```

caption 规则：caption 的值 = 传给 voice-reply 的文本，不得写"语音回复"、"音频"或留空。

语音标签：日语 `jp`（默认）、中文 `zh`、英文 `en`。

用户说"关闭语音讲解"或"关闭语音回复"时，恢复普通文字回复。
