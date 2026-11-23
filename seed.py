"""Fill the mods collection with test data (idempotent: no duplicates on re-run)."""
from datetime import datetime, timezone

from db import connect, mods_collection

MODS = [
    ("Sodium", "Fabric", "1.21.1"), ("Sodium", "NeoForge", "1.21.1"), ("Iris Shaders", "Fabric", "1.21.1"),
    ("Lithium", "Fabric", "1.21.1"), ("Lithium", "NeoForge", "1.20.4"), ("Fabric API", "Fabric", "1.21.1"),
    ("Fabric API", "Fabric", "1.20.1"), ("JEI", "Forge", "1.20.1"), ("JEI", "NeoForge", "1.21.1"),
    ("Create", "Forge", "1.20.1"), ("Create", "NeoForge", "1.21.1"), ("Create", "Fabric", "1.20.1"),
    ("Applied Energistics 2", "Forge", "1.20.1"), ("Applied Energistics 2", "NeoForge", "1.21.1"),
    ("Mekanism", "Forge", "1.20.1"), ("Mekanism", "NeoForge", "1.21.1"), ("Waystones", "Forge", "1.20.1"),
    ("Waystones", "Fabric", "1.21.1"), ("Xaero's Minimap", "Fabric", "1.21.1"), ("Xaero's Minimap", "Forge", "1.20.1"),
    ("Journeymap", "NeoForge", "1.21.1"), ("Journeymap", "Forge", "1.20.1"), ("Farmer's Delight", "Forge", "1.20.1"),
    ("Farmer's Delight", "NeoForge", "1.21.1"), ("Farmer's Delight", "Fabric", "1.20.1"),
    ("Quilted Fabric API", "Quilt", "1.20.1"), ("Quilt Standard Libraries", "Quilt", "1.21.1"),
    ("Sodium", "Quilt", "1.20.1"), ("Botania", "Forge", "1.20.1"), ("Botania", "Fabric", "1.20.1"),
    ("Tinkers' Construct", "Forge", "1.20.1"), ("Tinkers' Construct", "NeoForge", "1.21.1"),
    ("Cloth Config", "Fabric", "1.21.1"), ("Cloth Config", "NeoForge", "1.21.1"), ("Mod Menu", "Fabric", "1.21.1"),
    ("Mod Menu", "Quilt", "1.20.1"), ("Distant Horizons", "Fabric", "1.20.4"), ("Distant Horizons", "NeoForge", "1.21.1"),
    ("Immersive Engineering", "Forge", "1.20.1"), ("Alex's Mobs", "Forge", "1.20.1"), ("Supplementaries", "Forge", "1.20.1"),
    ("Supplementaries", "Fabric", "1.20.1"), ("Terralith", "Fabric", "1.20.1"), ("Ender IO", "NeoForge", "1.21.1"),
]


def main():
    mods = mods_collection(connect())
    added = 0
    for name, loader, version in MODS:
        res = mods.update_one(
            {"name": name, "loader": loader, "mc_version": version},
            {"$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True,
        )
        added += bool(res.upserted_id)
    print(f"{added} new mod(s) added. Total in database: {mods.count_documents({})}")


if __name__ == "__main__":
    main()
