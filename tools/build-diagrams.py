#!/usr/bin/env python3
"""Build the portfolio's stack-diagram HTML sources with one shared theme.

Icons are supplied from a local stack-diagram icon cache. PNGs are screenshots
of these HTML files, so the diagram and its exported image share one layout.
"""

import argparse
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/designs"


def icon_uri(icons, name):
    file = next(path for path in icons.glob(f"{name}.*") if path.suffix in {".svg", ".png", ".webp"})
    mime = {".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp"}[file.suffix]
    return f"data:{mime};base64,{base64.b64encode(file.read_bytes()).decode()}"


def anchor(node, side):
    x, y = node["x"], node["y"]
    return {"right": (x + 38, y + 32), "left": (x - 38, y + 32),
            "top": (x, y - 6), "bottom": (x, y + 124)}[side]


def path_points(edge, nodes):
    start, end = nodes[edge["from"]], nodes[edge["to"]]
    if "sides" in edge:
        a, b = edge["sides"]
    elif start["y"] == end["y"]:
        a, b = ("right", "left") if start["x"] < end["x"] else ("left", "right")
    elif start["x"] == end["x"]:
        a, b = ("bottom", "top") if start["y"] < end["y"] else ("top", "bottom")
    else:
        a, b = ("bottom", "top") if start["y"] < end["y"] else ("top", "bottom")
    p, q = anchor(start, a), anchor(end, b)
    if "via" in edge:
        return [p, *[tuple(point) for point in edge["via"]], q]
    if p[0] == q[0] or p[1] == q[1]:
        return [p, q]
    if a in {"top", "bottom"} and b in {"top", "bottom"}:
        mid = round((p[1] + q[1]) / 2)
        return [p, (p[0], mid), (q[0], mid), q]
    if a in {"left", "right"} and b in {"left", "right"}:
        mid = round((p[0] + q[0]) / 2)
        return [p, (mid, p[1]), (mid, q[1]), q]
    return [p, (p[0], q[1]) if a in {"top", "bottom"} else (q[0], p[1]), q]


def render(diagram, icons, css):
    esc = html.escape
    nodes = {node["id"]: node for node in diagram["nodes"]}
    height = diagram.get("height", 860)
    groups = "".join(
        f'<div class="group" style="left:{g["x"]}px;top:{g["y"]}px;width:{g["w"]}px;height:{g["h"]}px">'
        f'<div class="g-label">{esc(g["label"])}</div></div>' for g in diagram.get("groups", []))
    paths = []
    for i, edge in enumerate(diagram["edges"]):
        points = path_points(edge, nodes)
        commands = "M" + " L".join(f"{x} {y}" for x, y in points)
        kind = edge.get("kind", "primary")
        paths.append(f'<path class="edge {kind}" data-edge="{i}" d="{commands}" marker-end="url(#arrow)"/>')
        if label := edge.get("label"):
            if "labelAt" in edge:
                x, y = edge["labelAt"]
            else:
                p, q = max(zip(points, points[1:]), key=lambda pair: abs(pair[0][0]-pair[1][0])+abs(pair[0][1]-pair[1][1]))
                x, y = ((p[0]+q[0])/2, (p[1]+q[1])/2 - 10) if p[1] == q[1] else (p[0]+32, (p[1]+q[1])/2)
            paths.append(f'<text class="edge-label" data-edge="{i}" x="{x}" y="{y}" text-anchor="middle">{esc(label)}</text>')
    node_markup = []
    for node in nodes.values():
        grouped = any(g["x"] < node["x"] < g["x"]+g["w"] and g["y"] < node["y"] < g["y"]+g["h"] for g in diagram.get("groups", []))
        classes = "node" + (" decision" if node.get("decision") else "") + (" grouped" if grouped else "")
        tile_class = "tile dark" if node["icon"] == "jitsi" else "tile"
        role = "<br>".join(esc(line) for line in node["role"].split("\n"))
        node_markup.append(f'<div class="{classes}" data-id="{esc(node["id"])}" style="left:{node["x"]-95}px;top:{node["y"]}px">'
                           f'<div class="{tile_class}"><img src="{icon_uri(icons, node["icon"])}" alt=""></div>'
                           f'<div class="name"><span>{esc(node["label"])}</span></div><div class="role"><span>{role}</span></div></div>')
    kinds = {edge.get("kind", "primary") for edge in diagram["edges"]}
    legend = "".join(f'<span class="{kind}">{esc(label)}</span>' for kind, label in diagram.get("legend", [["primary", "주 흐름"], ["secondary", "연동·보조 경로"], ["dashed", "배포·비동기 처리"]]) if kind in kinds)
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(diagram["title"])}</title><style>{css}</style></head>
<body><div class="page"><header class="head"><h1>{esc(diagram["title"])}</h1></header>
<div class="canvas" style="height:{height}px">{groups}<svg class="edges" height="{height}" viewBox="0 0 1400 {height}" aria-hidden="true"><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="context-stroke"/></marker></defs>{''.join(paths)}</svg>{''.join(node_markup)}</div>
<div class="legend">{legend}</div></div></body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--icons", required=True, type=Path)
    args = parser.parse_args()
    diagrams = json.loads((SOURCE / "stack-diagrams.json").read_text())
    css = (SOURCE / "stack-theme.css").read_text()
    for diagram in diagrams:
        (SOURCE / f'{diagram["id"]}.html').write_text(render(diagram, args.icons, css))
    print(f"Built {len(diagrams)} diagram sources")


if __name__ == "__main__":
    main()
