"""Card art URL resolution.

Convention: every card with art lives at
``art/<kind>/<card_id>.png`` in the repo root, where ``<kind>`` is
``maid`` | ``tool`` | ``chaos`` | ``raid_boss``. The plugin builds the
public URL from ``BASE_URL`` + the convention path at runtime — no
need to maintain a list as long as filenames match card IDs.

``OVERRIDES`` lets you point a specific card at any URL (handy for
non-PNG files, cross-repo assets, or per-card CDN overrides).

If a card has no art (file missing AND no override), the embed renders
without an image — exactly the text card view we already had.
"""
from __future__ import annotations

# Public base URL where the art directory is served. Defaults to the
# raw view of the main branch in NotUSeee/Maid-Mayhem. Bump this to a
# CDN URL later if you want faster loads.
BASE_URL = "https://raw.githubusercontent.com/NotUSeee/Maid-Mayhem/main/art"


# Per-card URL overrides. Keyed by ``f"{kind}/{card_id}"``. Map to any
# fully-qualified URL. Useful for non-PNG assets, animated WEBPs for
# Mythic cards, or temporary placeholders.
#
# Example::
#
#     OVERRIDES = {
#         "maid/aurelia": "https://example.com/aurelia-animated.gif",
#         "tool/golden_feather_duster": "https://imgur.com/xyz.png",
#     }
OVERRIDES: dict[str, str] = {}


# Cards we know lack art so we can suppress 404 fetches by Discord.
# Populate as you ship art per-card. Listing cards here is purely an
# optimisation — Discord will silently 404 anyway, just less cleanly.
KNOWN_MISSING: set[str] = set()


def image_url_for(kind: str, card_id: str) -> str | None:
    """Return the public image URL for a card, or None if no art is
    expected to exist. Always returns None when ``card_id`` is empty.
    """
    if not card_id or not kind:
        return None
    key = f"{kind}/{card_id}"
    if key in OVERRIDES:
        return OVERRIDES[key]
    if key in KNOWN_MISSING:
        return None
    if not BASE_URL:
        return None
    return f"{BASE_URL.rstrip('/')}/{kind}/{card_id}.png"
