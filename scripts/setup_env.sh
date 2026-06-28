#!/usr/bin/env bash
set -euo pipefail

# 环境准备脚本（在有外网的主机上运行）
# 用法: bash scripts/setup_env.sh

PYTHON=python3
VENV_DIR=.venv

echo "创建虚拟环境 -> ${VENV_DIR}"
$PYTHON -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

echo "升级 pip setuptools wheel"
pip install -U pip setuptools wheel

echo "安装 PyTorch（请根据你的 CUDA 版本调整）"
echo "示例（CUDA 10.1）："
echo "pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html"

echo "安装项目依赖（requirements.txt）"
pip install -r requirements.txt

echo "安装 timm 指定提交（可选，但 README 推荐）"
if [ ! -d pytorch-image-models ]; then
  git clone https://github.com/rwightman/pytorch-image-models.git
fi
cd pytorch-image-models
git fetch --all --tags
git checkout 9cc7dda6e5fcbbc7ac5ba5d2d44050d2a8e3e38d || true
pip install -e .
cd -

echo "完成：虚拟环境已创建并安装依赖。请确认 CUDA / PyTorch 兼容性。"
