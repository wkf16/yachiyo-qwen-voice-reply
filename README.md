# yachiyo-qwen-voice-reply

> 八千代 ヤチヨ (Yachiyo) — 动画《超时空辉夜姬》中的 AI 助手角色，以温柔、亲和的声音陪伴主角。  
> 本项目将她的声音克隆并集成到 OpenClaw 智能助手中，让 AI 助手能以八千代的声音进行语音回复。

## 项目简介

三个配套的 [OpenClaw](https://openclaw.ai) Agent Skills：

| Skill | 功能 |
|---|---|
| `yachiyo-qwen-voice-reply` | 使用 Qwen3-TTS 克隆音色生成 Telegram 语音回复，并在本地自动播放 |
| `qwen3-tts-voice-clone` | 管理阿里云百炼声音复刻（创建 / 查询 / 删除克隆音色） |
| `enable-voice-reply` | 开启语音回复模式，注入强制语音回复指令，使 agent 在当前对话每条回复都附带语音 |

## 功能特性

- 🎙️ **声音克隆**：基于 `qwen-voice-enrollment`，10~20 秒音频即可复刻音色
- 🌐 **多语言支持**：`--voice-tag jp/zh/en` 约束语言，确保发音自然
- 📱 **Telegram 集成**：ogg/opus 格式，caption 自动设为 TTS 输入文本
- 🔊 **本地自动播放**：发送 Telegram 同时本地播放，互不阻塞
- 🧹 **自动清理**：临时 wav 播完后自动删除
- 💬 **语音回复模式**：一句话开启，当前对话全程语音回复

## 自动安装（推荐）

使用一键安装脚本，适合通过 OpenClaw clawbot 引导安装：

```bash
git clone https://github.com/wkf16/yachiyo-qwen-voice-reply.git
cd yachiyo-qwen-voice-reply
chmod +x install.sh
./install.sh
```

脚本会交互式引导完成以下步骤：

1. **选择服务区域** — 国际区（新加坡）或中国区（北京），自动配置对应 API 端点
2. **输入 API Key** — 若环境变量 `DASHSCOPE_API_KEY` 未设置，提示输入
3. **连通性检测** — 验证所选区域的 API 端点是否可访问
4. **安装 skills** — 将 `skills/` 下所有 skill 复制到 `~/.openclaw/workspace/skills/`，若已存在同名 skill 会询问是否覆盖
5. **路径修正** — 自动将 `enable-voice-reply/SKILL.md` 中的路径占位符替换为当前机器的实际 skills 路径

> **clawbot 用法**：在 OpenClaw 对话中直接说「帮我安装 yachiyo voice skills」，agent 会自动 clone 仓库并运行 `install.sh`。
>
> 若手动复制 skills 而未运行脚本，需要让 clawbot 执行以下命令修正路径：
> ```bash
> sed -i '' "s|{{SKILLS_DIR}}|$HOME/.openclaw/workspace/skills|g" \
>   ~/.openclaw/workspace/skills/enable-voice-reply/SKILL.md
> ```

---

## 手动安装

```bash
cp -R skills/yachiyo-qwen-voice-reply ~/.openclaw/workspace/skills/
cp -R skills/qwen3-tts-voice-clone ~/.openclaw/workspace/skills/
cp -R skills/enable-voice-reply ~/.openclaw/workspace/skills/
cp -R skills/disable-voice-reply ~/.openclaw/workspace/skills/
```

依赖：`python3`、`ffmpeg`、`pip install dashscope`

```bash
export DASHSCOPE_API_KEY="<your-api-key>"
```

> **区域说明**：默认使用国际区（新加坡）。若需切换至中国区（北京），将脚本中的
> `dashscope-intl.aliyuncs.com` 替换为 `dashscope.aliyuncs.com`。

## 使用

### 语音回复

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

### 开启语音回复模式

在对话中说「开启语音讲解」即可触发 `enable-voice-reply` skill。

触发后，agent 在当前对话的每条回复都会：
1. 调用 `yachiyo-qwen-voice-reply` 生成语音
2. 发送语音消息，caption 设为 TTS 输入文本本身（用户实际听到的内容）
3. 可选附加一条精简文字补充

说「关闭语音讲解」恢复普通文字回复。

豁免条件（自动改为文字回复）：
- 回复包含代码块、命令、JSON、配置文件、多行表格
- 回复超过 8 句话或 300 字（中文）/ 200 词（英文）

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
