# Geospatial Indexes

Redis has built-in geospatial support via the `GEO` family of commands. Under the hood each location is encoded as a **geohash** stored in a sorted set, giving you fast radius and bounding-box queries with no external library.

## Core commands

| Command | Description |
|---|---|
| `GEOADD key lon lat member …` | Add one or more locations |
| `GEODIST key m1 m2 [unit]` | Distance between two members |
| `GEOPOS key member …` | Get (lon, lat) for members |
| `GEOSEARCH key FROMMEMBER m BYRADIUS r unit …` | Find members within radius |
| `GEOSEARCHSTORE dest key …` | Like GEOSEARCH but stores results |

Units for distances: `m` (meters), `km`, `mi`, `ft`.

## Building a store locator

```
# Load stores
GEOADD stores 31.2357 30.0444 "cairo-central"
GEOADD stores 31.2231 30.0594 "cairo-north"
GEOADD stores 29.9553 31.1376 "giza-mall"

# Find stores within 5 km of a user's position
GEOSEARCH stores
  FROMLONLAT 31.235 30.044
  BYRADIUS 5 km
  ASC
  WITHCOORD WITHDIST
  COUNT 10
```

Sample result:
```
1) 1) "cairo-central"
   2) "0.0412"       <- distance in km
   3) 1) "31.23570"
      2) "30.04440"
```

`ASC` returns nearest-first. `COUNT` limits results before returning them (cheap — avoids a full scan of the sorted set).

## How geohashes work

Redis encodes longitude and latitude into a 52-bit integer using a **geohash** algorithm. This integer is the score in the backing sorted set. Nearby coordinates produce similar scores, so a range scan on the sorted set approximates a spatial radius query.

The precision is about 0.6 mm at the equator for 52 bits — more than enough for any real use case.

## Worked example: Ride-sharing nearby drivers

```python
import redis

r = redis.Redis()

# Driver reports position
def update_driver(driver_id, lon, lat):
    r.geoadd("drivers:online", [lon, lat, driver_id])
    r.expire(f"driver:{driver_id}:pos", 60)  # Remove stale positions

# Rider requests a driver
def find_nearby_drivers(lon, lat, radius_km=5, limit=5):
    results = r.geosearch(
        "drivers:online",
        longitude=lon, latitude=lat,
        radius=radius_km, unit="km",
        sort="ASC",
        count=limit,
        withcoord=True,
        withdist=True,
    )
    return results
```

## Memory footprint

A geo key is just a sorted set. Each member costs roughly 50 bytes. One million driver positions ≈ 50 MB — very manageable.

## Limitations to know

- No native polygon queries (only radius / box).
- No automatic expiry of members; you must `ZREM` or use a separate TTL on a companion key.
- Precision is ~0.6 mm — overkill for most applications, but the encoding means very long geohashes (high precision) differ by many integer steps, which can make range scans slightly less efficient for extremely tight radii.

## Common use cases

- Store locators and branch finders.
- Ride-sharing and delivery driver proximity.
- Geo-targeted notifications ("send push if within 200 m of this store").
- Social features ("friends nearby").
