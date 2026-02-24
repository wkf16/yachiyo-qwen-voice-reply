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

## Step 4: Install skills

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

## Step 5: Fix the path placeholder in enable-voice-reply

Replace `{{SKILLS_DIR}}` with the actual skills path on this machine:

```bash
sed -i '' "s|{{SKILLS_DIR}}|$HOME/.openclaw/workspace/skills|g" \
  ~/.openclaw/workspace/skills/enable-voice-reply/SKILL.md
```

## Step 6: If user chose China mainland, patch the API endpoint

```bash
find ~/.openclaw/workspace/skills/yachiyo-qwen-voice-reply -name "*.py" \
  -exec sed -i '' "s|dashscope-intl\.aliyuncs\.com|dashscope.aliyuncs.com|g" {} \;
```

## Step 7: Clean up and confirm

```bash
rm -rf /tmp/yachiyo-install
```

Tell the user:
- Add `export DASHSCOPE_API_KEY="<key>"` to `~/.zshrc` or `~/.bashrc`
- Run `pip install dashscope`
- Say「开启语音讲解」in the OpenClaw chat to enable Yachiyo voice replies
