# 数据与模型准备说明

下面列出训练所需的主要数据与预训练模型，以及如何将它们放到仓库中的相对路径（按 README 说明）。

1) Matterport3D Simulator
- 请按照 `Matterport3DSimulator` 官方仓库的安装说明编译并安装模拟器。安装后请设置环境变量：

```
export PYTHONPATH=Matterport3DSimulator/build:$PYTHONPATH
```

2) 数据集目录（仓库内期望路径）
- 将所有数据放到仓库根目录的 `datasets/` 下，例如：

- `datasets/R2R/annotations/`    -> 含 train/val/test json/jsonl
- `datasets/R2R/features/`       -> 含 ViT 特征 hdf5 文件，例如 `pth_vit_base_patch16_224_imagenet.hdf5`
- `datasets/R2R/features/panoimages.lmdb` -> 全景图像数据库（可选，某些脚本需要）
- `datasets/R2R/connectivity/`   -> Matterport 的 connectivity json 文件（仓库内已有示例位于 `Matterport3DSimulator/connectivity/`）

3) 预训练检查点与特征（README 提供的 Box 链接）
- 从 README 中的 Box 链接下载以下文件并放置到对应位置（或自定义后在运行脚本时调整路径）：
  - off-the-shelf ViT 特征（用于 `imaginate_features_type off-the-shelf-vit`）
  - HAMT ViT 特征
  - HAMT-Imagine R2R checkpoint
  - DUET-Imagine R2R checkpoint

4) （可选）想象生成结果与元数据
- README 提示可以下载想象生成的图像与元数据，放到 `datasets/R2R/imagination/` 或类似位置，并在训练脚本中把 `--imag_*_features` 指向这些特征。

5) 检查点与训练模型目录
- 训练脚本默认将模型输出到 `imagination-experiments/` 或 `datasets/R2R/trained_models/`。运行前确保目标输出目录存在且有写权限。

6) 常见问题
- 仓库中的训练/测试脚本通常在各子目录下的 `scripts/run_r2r.sh`，运行前请根据你本地 `datasets` 路径修改 `--root_dir` 和 `--resume_file`。

7) 无法直接从此环境下载数据
- 当前运行环境可能无法直接访问外网（例如 GitHub/Box），请在有网络的机器上下载数据并通过 SCP/上传或外部存储拷贝到本环境。

如果你愿意，我可以：
- 生成一个更完整的 `setup_data.sh`（包含目录创建与占位符下载命令），便于你在本地运行后把数据拷贝回此环境；
- 或根据你已经下载的数据的路径，帮你生成具体的符号链接与配置文件，直接指向这些文件。
