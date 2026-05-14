# Card art

Drop card images in this directory and they'll appear in Discord embeds.

## Naming convention

```
art/
  maid/
    aurelia.png
    bria.png
    luna.png
    ...
  tool/
    cursed_mop.png
    golden_feather_duster.png
    ...
  chaos/
    dust_goblin.png
    laundry_hydra.png
    ...
  raid_boss/
    great_unwashed_one.png
    laundry_hydra_prime.png
    mold_king_maximus_raid.png
```

**One file per card. Filename = card `id` from `CARDS.json` + `.png`.** Use `.png` for static art (recommended). For animated art use a per-card override (see below).

## How URLs are built

The plugin reads `data/art_config.py:BASE_URL` and appends `/<kind>/<id>.png` at runtime. Default base URL is `https://raw.githubusercontent.com/NotUSeee/Maid-Mayhem/main/art` — i.e. this directory served via GitHub raw. Whatever you commit here becomes visible to Discord within seconds.

If a card has no image file (or you haven't generated it yet), the embed just renders without an image — the existing text card view is unchanged. So you can roll out art card-by-card without breaking anything.

## Per-card overrides

For non-PNG assets, off-repo CDNs, or animated GIFs/WEBPs, add an entry to `OVERRIDES` in [`data/art_config.py`](../data/art_config.py):

```python
OVERRIDES = {
    "maid/aurelia": "https://my-cdn.example.com/aurelia-animated.gif",
    "tool/heart_of_the_manor": "https://imgur.com/xyz.png",
}
```

Override keys are `f"{kind}/{card_id}"`. Override values are fully-qualified URLs.

## Where art appears in Discord

- `/maid card <name>` — full art as the embed `image` (large display).
- `/maid daily` reveal — rarest pulled card shown as the embed `image`.
- `/maid pack` reveal — same: rarest pull featured.
- Collection lists (`/maid cards`) — no art, by design. Showing 8 images per page would be slow and ugly.
- Battle / duel / raid embeds — no art for now. Possible future addition as small `thumbnail` per active maid.

## File size guidance

Discord caches embed images. Aim for **≤500 KB per PNG**. Recommended source resolution: **800 × 1200** (portrait, 2:3) — Discord scales for display but uses the source for full-size click. Larger files load slowly on mobile.

## To add a brand-new card art

1. Drop `art/maid/<id>.png` (or whichever kind).
2. `git add art/<kind>/<id>.png && git commit -m "art: <Card Name>" && git push`.
3. Within a minute or two GitHub raw serves the new URL.
4. Run `/maid card name:<Card Name>` in Discord — image should appear.

No plugin redeploy is required. The plugin just builds the URL string; Discord fetches it on demand.
