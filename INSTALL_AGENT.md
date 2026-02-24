# Yachiyo Voice Skills — Agent Install Guide

> You are an OpenClaw agent. Follow these steps in order to install the skills on this machine.

## Step 1: Collect info from user

Ask the user to confirm:

1. **Region**: Alibaba Cloud international (Singapore) or China mainland (Beijing)?
2. **API Key**: Check if `DASHSCOPE_API_KEY` is already set in the environment. If not, ask the user to provide it.

## Step 2: Test API connectivity

Run the command for the chosen region. If unreachable, inform the user and suggest switching regions.

```bash
# International (Singapore)
curl -sf --max-time 8 https://dashscope-intl.aliyuncs.com -o /dev/null && echo "✓ reachable" || echo "✗ unreachable"

# China mainland (Beijing)
curl -sf --max-time 8 https://dashscope.aliyuncs.com -o /dev/null && echo "✓ reachable" || echo "✗ unreachable"
```

## Step 3: Clone the repo

```bash
git clone https://github.com/wkf16/yachiyo-qwen-voice-reply.git /tmp/yachiyo-install
```

## Step 4: Create Yachiyo voice clone

Tell the user: "API key confirmed. Starting voice clone creation now."

### 4.1 Check dependencies

```bash
which yt-dlp || pip install yt-dlp
which ffmpeg   || echo "ffmpeg not found — install with: brew install ffmpeg"
```

If ffmpeg is missing, stop and ask the user to install it first.

### 4.2 Download voice sample from Bilibili

```bash
yt-dlp -x --audio-format mp3 \
  -o /tmp/yachiyo-raw.%(ext)s \
  "https://www.bilibili.com/video/BV11Tz9BREJq/"
```

If the download fails (geo-block, login required, etc.), tell the user and ask them to provide a local audio file (10–20 s, clear voice, no BGM) at `/tmp/yachiyo-sample.mp3`, then skip to step 4.4.

### 4.3 Extract a clean 15-second clip

```bash
ffmpeg -i /tmp/yachiyo-raw.mp3 \
  -ss 0 -t 15 \
  -ac 1 -ar 24000 \
  /tmp/yachiyo-sample.mp3 -y
```

### 4.4 Create voice clone

Use `--region intl` for Singapore, `--region cn` for Beijing:

```bash
python /tmp/yachiyo-install/skills/qwen3-tts-voice-clone/scripts/qwen_tts_clone.py \
  --region <intl|cn> \
  create \
  --audio /tmp/yachiyo-sample.mp3 \
  --name yachiyo-voice \
  --target-model qwen3-tts-vc-2026-01-22 \
  --voice-out /tmp/yachiyo-voice-id.txt \
  --json
```

Read the returned voice ID:

```bash
cat /tmp/yachiyo-voice-id.txt
```

Save this value — you will use it in Step 6.

### 4.5 Clean up temp audio

```bash
rm -f /tmp/yachiyo-raw.mp3 /tmp/yachiyo-sample.mp3
```

## Step 5: Install skills

For each of the following skills: `yachiyo-qwen-voice-reply`, `qwen3-tts-voice-clone`, `enable-voice-reply`, `disable-voice-reply`

First check if it already exists:

```bash
ls ~/.openclaw/workspace/skills/<skill-name> 2>/dev/null && echo "exists" || echo "not found"
```

If it exists, ask the user whether to overwrite. Then copy:

```bash
cp -R /tmp/yachiyo-install/skills/yachiyo-qwen-voice-reply ~/.openclaw/workspace/skills/
cp -R /tmp/yachiyo-install/skills/qwen3-tts-voice-clone ~/.openclaw/workspace/skills/
cp -R /tmp/yachiyo-install/skills/enable-voice-reply ~/.openclaw/workspace/skills/
cp -R /tmp/yachiyo-install/skills/disable-voice-reply ~/.openclaw/workspace/skills/
```

## Step 6: Write voice ID and fix paths

Replace `DEFAULT_VOICE` in the voice-reply script with the voice ID obtained in Step 4:

```bash
VOICE_ID=$(cat /tmp/yachiyo-voice-id.txt)
sed -i '' "s|DEFAULT_VOICE = \".*\"|DEFAULT_VOICE = \"$VOICE_ID\"|" \
  ~/.openclaw/workspace/skills/yachiyo-qwen-voice-reply/scripts/qwen_voice_reply.py
```

Replace `{{SKILLS_DIR}}` with the actual skills path on this machine:

```bash
sed -i '' "s|{{SKILLS_DIR}}|$HOME/.openclaw/workspace/skills|g" \
  ~/.openclaw/workspace/skills/enable-voice-reply/SKILL.md
```

## Step 7: If user chose China mainland, patch the API endpoint

```bash
find ~/.openclaw/workspace/skills/yachiyo-qwen-voice-reply -name "*.py" \
  -exec sed -i '' "s|dashscope-intl\.aliyuncs\.com|dashscope.aliyuncs.com|g" {} \;
```

## Step 8: Clean up and confirm

```bash
rm -rf /tmp/yachiyo-install /tmp/yachiyo-voice-id.txt
```

Tell the user:
- Add `export DASHSCOPE_API_KEY="<key>"` to `~/.zshrc` or `~/.bashrc`
- Run `pip install dashscope`
- Say「开启语音讲解」in the OpenClaw chat to enable Yachiyo voice replies
