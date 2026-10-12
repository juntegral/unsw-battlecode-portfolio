#!/usr/bin/env python3
"""Print notable.json compactly."""
import json

for n in json.load(open("notable.json")):
    print(n["game_id"], n["battle_id"], n["map"], n["map_size"], "vs", n["opponent_name"], n["opponent_elo"],
          n["result"], n["end_type"], n["margin_metric"], round(n["margin"], 2))
