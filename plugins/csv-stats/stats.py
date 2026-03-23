#!/usr/bin/env python3
"""CSV Stats plugin for AeroFTP. Reads JSON args from stdin, outputs JSON result."""

import csv
import json
import os
import sys

def detect_delimiter(path):
    with open(path, 'r', newline='', encoding='utf-8', errors='replace') as f:
        sample = f.read(4096)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
    except csv.Error:
        return ','

def analyze(path, delimiter=None, sample_rows=5):
    if not os.path.isfile(path):
        return {"error": f"file not found: {path}"}

    if delimiter is None:
        delimiter = detect_delimiter(path)

    rows = []
    with open(path, 'r', newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            rows.append(row)
            if len(rows) > 10000:
                break

    if not rows:
        return {"error": "empty file"}

    headers = rows[0]
    data_rows = rows[1:]
    total_rows = len(data_rows)

    # Numeric stats per column
    col_stats = []
    for i, h in enumerate(headers):
        vals = []
        for r in data_rows:
            if i < len(r) and r[i].strip():
                try:
                    vals.append(float(r[i].strip()))
                except ValueError:
                    pass
        stat = {"column": h, "type": "numeric" if len(vals) > total_rows * 0.5 else "text"}
        if vals:
            stat["min"] = min(vals)
            stat["max"] = max(vals)
            stat["mean"] = round(sum(vals) / len(vals), 2)
        col_stats.append(stat)

    sample = [dict(zip(headers, r)) for r in data_rows[:sample_rows]]

    return {
        "file": os.path.basename(path),
        "size": os.path.getsize(path),
        "delimiter": delimiter,
        "columns": len(headers),
        "rows": total_rows,
        "headers": headers,
        "sample": sample,
        "stats": col_stats
    }

if __name__ == '__main__':
    args = json.load(sys.stdin)
    path = args.get('path', '')
    delimiter = args.get('delimiter')
    sample_rows = int(args.get('sample_rows', 5))

    if not path:
        print(json.dumps({"error": "path parameter is required"}))
        sys.exit(1)

    result = analyze(path, delimiter, sample_rows)
    print(json.dumps(result))
