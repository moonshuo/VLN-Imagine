import json
import argparse
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def get_pred_items(pred_data):
    if isinstance(pred_data, list):
        return pred_data
    if isinstance(pred_data, dict):
        items = []
        for k, v in pred_data.items():
            if isinstance(v, dict):
                if "instr_id" not in v:
                    v["instr_id"] = k
                items.append(v)
            else:
                items.append({"instr_id": k, "trajectory": v})
        return items
    raise TypeError(type(pred_data))

def extract_path(traj):
    path = []
    for item in traj:
        if isinstance(item, (list, tuple)):
            path.append(item[0])
        elif isinstance(item, dict):
            if "viewpoint" in item:
                path.append(item["viewpoint"])
            elif "viewpointId" in item:
                path.append(item["viewpointId"])
            elif "viewpoint_id" in item:
                path.append(item["viewpoint_id"])
        else:
            path.append(item)
    return path

def find_gt_item(anno, instr_id):
    path_id = str(instr_id).split("_")[0]
    for x in anno:
        if str(x.get("path_id")) == path_id:
            return x
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True)
    parser.add_argument("--split", default="val_unseen")
    parser.add_argument("--idx", type=int, default=0)
    parser.add_argument("--instr_id", default=None)
    parser.add_argument("--out", default="duet_path_vis.html")
    args = parser.parse_args()

    pred_data = load_json(args.pred)
    pred_items = get_pred_items(pred_data)

    if args.instr_id is not None:
        pred_item = None
        for x in pred_items:
            if str(x.get("instr_id")) == str(args.instr_id):
                pred_item = x
                break
        if pred_item is None:
            raise ValueError(f"Cannot find instr_id={args.instr_id}")
    else:
        pred_item = pred_items[args.idx]

    instr_id = str(pred_item.get("instr_id", "unknown"))

    traj = pred_item.get("trajectory", None)
    if traj is None:
        traj = pred_item.get("path", None)
    if traj is None:
        traj = pred_item.get("pred_path", None)
    if traj is None:
        raise KeyError(f"Cannot find trajectory/path/pred_path in pred item keys: {pred_item.keys()}")

    pred_path = extract_path(traj)

    anno_path = Path("../datasets/R2R/annotations") / f"R2R_{args.split}.json"
    anno = load_json(anno_path)

    gt_item = find_gt_item(anno, instr_id)
    if gt_item is None:
        raise ValueError(f"Cannot find GT annotation for instr_id={instr_id}")

    scan = gt_item["scan"]
    gt_path = gt_item["path"]

    try:
        instr_idx = int(instr_id.split("_")[-1])
        instruction = gt_item["instructions"][instr_idx]
    except Exception:
        instruction = gt_item.get("instructions", [""])[0]

    conn_path = Path("../datasets/R2R/connectivity") / f"{scan}_connectivity.json"
    conn = load_json(conn_path)

    nodes = {}
    edges = []

    for x in conn:
        if not x.get("included", True):
            continue
        vid = x["image_id"]
        pose = x.get("pose", [])
        if len(pose) >= 12:
            nodes[vid] = {"x": pose[3], "y": pose[7]}
        else:
            nodes[vid] = {"x": 0.0, "y": 0.0}

    for i, x in enumerate(conn):
        if not x.get("included", True):
            continue
        src = x["image_id"]
        for j, ok in enumerate(x.get("unobstructed", [])):
            if ok and j < len(conn):
                dst = conn[j]["image_id"]
                if src in nodes and dst in nodes and src < dst:
                    edges.append((src, dst))

    xs = [v["x"] for v in nodes.values()]
    ys = [v["y"] for v in nodes.values()]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    def sx(x):
        return 60 + (x - minx) / (maxx - minx + 1e-9) * 880

    def sy(y):
        return 60 + (y - miny) / (maxy - miny + 1e-9) * 620

    def points(path):
        pts = []
        for vid in path:
            if vid in nodes:
                pts.append(f'{sx(nodes[vid]["x"]):.1f},{sy(nodes[vid]["y"]):.1f}')
        return " ".join(pts)

    gt_points = points(gt_path)
    pred_points = points(pred_path)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>DUET R2R Path Visualization</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; background: #f7f7f7; }}
.card {{ max-width: 1120px; margin: auto; background: white; padding: 20px; border-radius: 12px; }}
svg {{ border: 1px solid #ddd; background: #fafafa; border-radius: 8px; }}
pre {{ white-space: pre-wrap; background: #f3f3f3; padding: 12px; border-radius: 8px; }}
.badge {{ display:inline-block; padding:4px 8px; border-radius:4px; margin-right:8px; }}
</style>
</head>
<body>
<div class="card">
<h2>DUET R2R Path Visualization</h2>
<p><b>split:</b> {args.split} &nbsp; <b>scan:</b> {scan} &nbsp; <b>instr_id:</b> {instr_id}</p>
<p>
<span class="badge" style="background:#e8f2ff;">Blue = ground truth path</span>
<span class="badge" style="background:#fff1e6;">Orange = DUET predicted path</span>
<span class="badge" style="background:#f0e8ff;">Purple = overlap node</span>
</p>
<p><b>Instruction:</b></p>
<pre>{instruction}</pre>
<svg width="1000" height="740" viewBox="0 0 1000 740">
"""

    for a, b in edges:
        html += f'<line x1="{sx(nodes[a]["x"]):.1f}" y1="{sy(nodes[a]["y"]):.1f}" x2="{sx(nodes[b]["x"]):.1f}" y2="{sy(nodes[b]["y"]):.1f}" stroke="#ddd" stroke-width="1"/>\n'

    gt_set = set(gt_path)
    pred_set = set(pred_path)

    for vid, pos in nodes.items():
        fill = "#aaa"
        r = 2.5
        if vid in gt_set:
            fill = "#2f80ed"
            r = 4.5
        if vid in pred_set:
            fill = "#f2994a"
            r = 4.5
        if vid in gt_set and vid in pred_set:
            fill = "#9b51e0"
            r = 5.5
        html += f'<circle cx="{sx(pos["x"]):.1f}" cy="{sy(pos["y"]):.1f}" r="{r}" fill="{fill}"><title>{vid}</title></circle>\n'

    if gt_points:
        html += f'<polyline points="{gt_points}" fill="none" stroke="#2f80ed" stroke-width="5" opacity="0.75"/>\n'
    if pred_points:
        html += f'<polyline points="{pred_points}" fill="none" stroke="#f2994a" stroke-width="5" opacity="0.75"/>\n'

    html += f"""
</svg>
<h3>DUET predicted path</h3>
<pre>{json.dumps(pred_path, indent=2)}</pre>
<h3>Ground truth path</h3>
<pre>{json.dumps(gt_path, indent=2)}</pre>
</div>
</body>
</html>
"""

    Path(args.out).write_text(html, encoding="utf-8")
    print("saved:", args.out)
    print("instr_id:", instr_id)
    print("scan:", scan)
    print("pred path length:", len(pred_path))
    print("gt path length:", len(gt_path))

if __name__ == "__main__":
    main()
