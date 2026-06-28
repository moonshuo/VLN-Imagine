#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(dirname "$(dirname "$0")")
cd ${ROOT_DIR}

echo "创建 datasets/R2R 目录结构（若不存在）"
mkdir -p datasets/R2R/annotations/pretrain
mkdir -p datasets/R2R/features
mkdir -p datasets/R2R/imagination
mkdir -p datasets/R2R/connectivity
mkdir -p datasets/R2R/trained_models

echo "创建占位 README 文件，说明需要放置的文件"
cat > datasets/README.txt <<'TXT'
请把 R2R 数据与特征放到本目录结构下：

- annotations/pretrain: train.jsonl, val_seen.jsonl, val_unseen.jsonl 等
- features: pth_vit_base_patch16_224_imagenet.hdf5 等图像特征
- panoimages.lmdb: 全景图像数据库（如果需要）
- imagination: 想象生成图 / 特征（可选）
- trained_models: 训练产生的模型检查点

TXT

echo "已创建目录，下一步请将数据文件复制到对应位置或上传到此环境。"
