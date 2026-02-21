---
name: qwen3-tts-voice-clone
description: 接入阿里云百炼 Qwen 声音复刻（qwen-voice-enrollment）与 Qwen3-TTS。用于创建/查询/删除复刻音色，并指导如何上传10-20秒样本音频并在qwen3-tts-vc或qwen3-tts-vc-realtime中使用该音色。
metadata: {"openclaw":{"emoji":"🗣️","requires":{"bins":["python3"]}}}
---

# Qwen3 TTS Voice Clone

用这个 skill 完成三件事：
1. 上传音频并创建复刻音色（voice id）
2. 查询/管理已有复刻音色
3. 把 voice id 用到 Qwen3-TTS 合成

## Quick Start

### 1) 安装依赖

```bash
cd skills/qwen3-tts-voice-clone
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) 配置 API Key

```bash
export DASHSCOPE_API_KEY="你的百炼API Key"
```

### 3) 创建复刻音色

```bash
python scripts/qwen_tts_clone.py create \
  --audio /绝对路径/voice.mp3 \
  --name t0ryam-voice \
  --target-model qwen3-tts-vc-2026-01-22 \
  --voice-out /tmp/qwen_voice_id.txt \
  --json
```

> 若你要给实时双向流式合成用，请把 `--target-model` 换成 `qwen3-tts-vc-realtime-2026-01-15`（或同系列版本）。

### 4) 查询已创建音色

```bash
python scripts/qwen_tts_clone.py list --json
```

### 5) 删除音色

```bash
python scripts/qwen_tts_clone.py delete --voice <voice_id>
```

## 上传样本音频规范（关键）

- 格式：WAV(16bit) / MP3 / M4A
- 时长：推荐 10~20 秒（最长 60 秒）
- 大小：< 10MB
- 采样率：≥ 24kHz
- 声道：单声道
- 内容：至少 3 秒连续清晰朗读，无背景音乐、无噪声、无人声重叠
- 建议：用自然说话，不要用唱歌片段

## 复刻与合成的一致性规则

创建音色时的 `target_model`，必须与后续合成使用的模型一致，否则合成会失败。

- 例1（非流式）：
  - create target_model: `qwen3-tts-vc-2026-01-22`
  - synthesis model: `qwen3-tts-vc-2026-01-22`
- 例2（实时流式）：
  - create target_model: `qwen3-tts-vc-realtime-2026-01-15`
  - synthesis model: `qwen3-tts-vc-realtime-2026-01-15`

## 地域

脚本默认中国站点（`--region cn`）。
如果使用国际站点，改为：

```bash
python scripts/qwen_tts_clone.py --region intl create --audio voice.mp3
```

## 合成接入（最小思路）

拿到 `voice_id` 后，在 Qwen3-TTS 请求中传 `voice=voice_id` 即可。

- 非流式/单向流式：使用 qwen3-tts-vc 系列模型 + `voice`
- 双向流式实时：使用 qwen3-tts-vc-realtime 系列模型 + `voice`

