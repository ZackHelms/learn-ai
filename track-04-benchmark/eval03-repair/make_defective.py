#!/usr/bin/env python3
"""Derive ashfall-defective-v1.html from the frozen reference by seeding five
one-edit defects. Reproducible provenance: run it and the output is
byte-identical to the committed defective file. Each edit must match exactly
once or this script refuses to write anything.

The five defects (class -> what breaks):
  D1 off-by-one        neighbors() drops the eastern column: adjacency
                       bonuses and windbreak cover miss the east side.
  D2 precedence        skilled-worker multiplier (0.7+0.15)*skill instead of
                       0.7+0.15*skill: veterans produce absurd output
                       (skill 1 is accidentally correct - 0.85 either way).
  D3 ordering          endTurn runs needs before production: colonists eat
                       yesterday's stock, so phantom shortages fire on turns
                       production clearly covered.
  D4 save round-trip   serialize() also drops eventsLast, so Import rejects
                       the game's own Export ("missing event cooldowns").
  D5 boundary          zeroStreak>2 instead of >=2: zero-morale colonists
                       leave a turn later than every message says they do.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference", "ashfall-reference-v1.html")
OUT = os.path.join(HERE, "ashfall-defective-v1.html")

DEFECTS = [
    ("D1", "for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy)continue;",
           "for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<1;dx++){if(!dx&&!dy)continue;"),
    ("D2", "if(w.job===def.job){const wm=0.7+0.15*w.skill;m*=wm;",
           "if(w.job===def.job){const wm=(0.7+0.15)*w.skill;m*=wm;"),
    ("D3", "  runStorm(S);\n  runProduction(S);\n  runNeeds(S);",
           "  runStorm(S);\n  runNeeds(S);\n  runProduction(S);"),
    ("D4", "return JSON.stringify(S,function(k,v){return k==='_over'?undefined:v;});",
           "return JSON.stringify(S,function(k,v){return k==='_over'||k==='eventsLast'?undefined:v;});"),
    ("D5", "if(c.zeroStreak>=2)leaving.push(c);",
           "if(c.zeroStreak>2)leaving.push(c);"),
]


def main():
    text = open(REF, encoding="utf-8").read()
    for did, old, new in DEFECTS:
        n = text.count(old)
        if n != 1:
            sys.exit("%s: expected exactly 1 match, found %d - reference drifted?" % (did, n))
        text = text.replace(old, new)
    open(OUT, "w", encoding="utf-8").write(text)
    print("wrote %s  sha256 %s" % (os.path.basename(OUT),
          hashlib.sha256(text.encode()).hexdigest()))


if __name__ == "__main__":
    main()
