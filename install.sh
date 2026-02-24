#!/usr/bin/env bash
# install.sh — yachiyo-qwen-voice-reply 一键安装脚本（OpenClaw clawbot 引导）
# 支持阿里云百炼 国际区（新加坡）/ 中国区（北京）

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$REPO_DIR/skills"
SKILLS_DEST="${HOME}/.openclaw/workspace/skills"
INTL_HOST="dashscope-intl.aliyuncs.com"
CN_HOST="dashscope.aliyuncs.com"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  ヤチヨ Voice Skills — OpenClaw 安装向导      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. 选择区域 ──────────────────────────────────────
echo "请选择阿里云百炼服务区域："
echo "  1) 国际区（新加坡）— 推荐境外 / 海外用户"
echo "  2) 中国区（北京）  — 推荐中国大陆用户"
read -rp "输入 1 或 2 [默认 1]: " region_choice
region_choice="${region_choice:-1}"

if [[ "$region_choice" == "2" ]]; then
    API_HOST="$CN_HOST"
    REGION_CODE="cn"
    REGION_NAME="中国区（北京）"
else
    API_HOST="$INTL_HOST"
    REGION_CODE="intl"
    REGION_NAME="国际区（新加坡）"
fi
echo "✓ 已选择：$REGION_NAME"
echo ""

# ── 2. API Key ────────────────────────────────────────
if [[ -z "${DASHSCOPE_API_KEY:-}" ]]; then
    read -rp "请输入 DASHSCOPE_API_KEY（阿里云百炼控制台获取）: " DASHSCOPE_API_KEY
    if [[ -z "$DASHSCOPE_API_KEY" ]]; then
        echo "✗ API Key 不能为空，退出。"
        exit 1
    fi
    export DASHSCOPE_API_KEY
fi
echo "✓ API Key 已设置"
echo ""

# ── 3. 检查 API 可访问性 ──────────────────────────────
echo "正在检查 https://$API_HOST 连通性..."
if curl -sf --max-time 8 "https://$API_HOST" -o /dev/null 2>&1; then
    echo "✓ $API_HOST 可访问"
else
    echo "⚠ 无法连接 $API_HOST，请检查网络或切换区域后重试。"
    read -rp "是否仍然继续安装？[y/N]: " force_continue
    if [[ "${force_continue,,}" != "y" ]]; then
        exit 1
    fi
fi
echo ""

# ── 4. 安装 skills ────────────────────────────────────
mkdir -p "$SKILLS_DEST"
echo "开始安装 skills → $SKILLS_DEST"
echo ""

for skill_path in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_path" ]] || continue
    skill_name="$(basename "$skill_path")"
    dest="$SKILLS_DEST/$skill_name"

    if [[ -d "$dest" ]]; then
        read -rp "⚠ skill '$skill_name' 已存在，是否覆盖？[y/N]: " overwrite
        if [[ "${overwrite,,}" != "y" ]]; then
            echo "  跳过 $skill_name"
            continue
        fi
        rm -rf "$dest"
    fi

    cp -R "$skill_path" "$dest"

    # 若选择中国区，将脚本中的 intl 端点替换为国内端点
    if [[ "$REGION_CODE" == "cn" ]]; then
        find "$dest" -name "*.py" -exec sed -i '' \
            "s|dashscope-intl\.aliyuncs\.com|dashscope.aliyuncs.com|g" {} \;
    fi

    # 替换 SKILL.md 中的路径占位符为当前机器的实际路径
    find "$dest" -name "SKILL.md" -exec sed -i '' \
        "s|{{SKILLS_DIR}}|$SKILLS_DEST|g" {} \;

    echo "  ✓ $skill_name"
done

echo ""
echo "✅ 安装完成！"
echo ""
echo "后续步骤："
echo "  1. 将以下内容加入 shell 配置（~/.zshrc 或 ~/.bashrc）："
echo "       export DASHSCOPE_API_KEY=\"$DASHSCOPE_API_KEY\""
echo "  2. 安装 Python 依赖："
echo "       pip install dashscope"
echo "  3. 在 OpenClaw 对话中说「开启语音讲解」即可启用八千代语音回复。"
echo ""
