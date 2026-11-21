# Saturday 21 November 2026 — The World in One Day

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Revaaa28/makefun-news-image-20261121-v6/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Revaaa28/makefun-news-image-20261121-v6/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One PNG, 1024×1024: the whole world's news of **Saturday 21 November 2026**
set as a broadsheet newspaper front page — 35 stories across 7 regions, every
one of them dated that Saturday.

Bounty: [make.fun · news-image-20261121](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

## What's on the page

- **Heroes:** the COP31 climate summit running into overtime in Antalya with
  no deal · five Houthi missiles shot down over Riyadh and Jizan · the
  magnitude 6.7 earthquake in Junín, Peru.
- **Ten illustrated briefs:** Kyiv's Crimea-bridge warning, the Hormuz drone,
  Iran's uranium stock, Trump's data-centre tax threat, China–Japan words
  over Taiwan, the Davao emergency landing (146 safe), Canberra's AI talks,
  bitcoin under $59,000, Russell on top in Las Vegas practice, and Rahul's
  century in Wellington.
- **A "Where it happened" map** with numbered pins, and a 22-story index of
  everything else that Saturday.
- **A deep, itemised DATE CHECK** naming the stories deliberately left out
  because they belong to Friday 20 November, Thursday 19 November, or older —
  each with its real date — plus the items not confirmed when the page was
  drawn.

## Files

- `draw.py` — renders `entry.png` deterministically (Python + Pillow).
- `entry.png` — the page itself, 1024×1024, under 1 MiB.
- `main.py` — validates `entry.png` (stdlib only) and copies it to
  `$MAKEFUN_OUTPUT_DIR` (default `/output`).
- `SOURCES.md` — every story on the page with its outlet.

## Run it

```sh
python3 draw.py    # rebuild entry.png (byte-identical every run)
python3 main.py    # validate and copy entry.png to the output directory
```
