# Geospatial Queries in MongoDB

MongoDB has first-class support for geographic data through **GeoJSON** objects and two dedicated index types: `2dsphere` (for earth-like spherical geometry) and `2d` (for flat planes). Most production use cases need `2dsphere`.

## Storing Geographic Data

MongoDB supports the GeoJSON standard. Common types:

```javascript
// Point — a single location (longitude first, then latitude)
{ type: "Point", coordinates: [31.2357, 30.0444] }  // Cairo

// Polygon — a region
{ type: "Polygon", coordinates: [[
  [31.22, 30.04], [31.26, 30.04], [31.26, 30.07], [31.22, 30.07], [31.22, 30.04]
]] }

// LineString — a route
{ type: "LineString", coordinates: [[31.22, 30.04], [31.50, 30.08]] }
```

Note: GeoJSON always stores `[longitude, latitude]`, not `[lat, lng]`. Getting this backward is the most common mistake.

## Creating a 2dsphere Index

```javascript
db.locations.createIndex({ geo: "2dsphere" });
```

All geospatial operators require this index to perform efficiently.

## $near — Find Closest Points

```javascript
db.locations.find({
  geo: {
    $near: {
      $geometry: { type: "Point", coordinates: [31.2357, 30.0444] },
      $maxDistance: 5000,   // meters
      $minDistance: 100
    }
  }
});
```

Results are returned sorted by distance (closest first) automatically.

## $geoWithin — Find Points Inside a Region

```javascript
// Find all restaurants inside a polygon
db.restaurants.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[[31.22, 30.04], [31.26, 30.04], [31.26, 30.07], [31.22, 30.07], [31.22, 30.04]]]
      }
    }
  }
});
```

`$geoWithin` does not sort by distance. Use it when you need all points within a region, not "nearest first".

## $geoIntersects — Find Overlapping Geometries

Useful when your stored documents contain polygons or lines (e.g., delivery zones) and you want to know which zones overlap with a given geometry:

```javascript
db.zones.find({
  boundary: { $geoIntersects: { $geometry: { type: "Point", coordinates: [31.24, 30.05] } } }
});
```

## Practical Pattern: Delivery App

```javascript
// Store drivers with live location
db.drivers.insertOne({
  name: "Ahmed",
  location: { type: "Point", coordinates: [31.235, 30.044] },
  available: true
});

db.drivers.createIndex({ location: "2dsphere" });

// Find available drivers within 3 km of customer
db.drivers.find({
  available: true,
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [31.240, 30.048] },
      $maxDistance: 3000
    }
  }
}).limit(5);
```

## Summary of Operators

| Operator | Purpose |
|---|---|
| `$near` / `$nearSphere` | Points sorted by distance from a location |
| `$geoWithin` | Points/shapes entirely inside a boundary |
| `$geoIntersects` | Shapes that intersect with a geometry |
| `$centerSphere` | Legacy circle query in radians |

For most new code, prefer `$near` with GeoJSON and `$geometry` over the older `$center`/`$centerSphere` syntax.
