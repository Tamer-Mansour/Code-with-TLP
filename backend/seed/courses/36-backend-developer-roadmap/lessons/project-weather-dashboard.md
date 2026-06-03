# Project: Weather Dashboard

## Overview

In this project you'll build a small full-stack **Weather Dashboard**. The browser front end (HTML5, CSS3, vanilla ES6+ JavaScript) lets a user type a city name and see the current weather. The Java + Spring Boot back end exposes a tiny REST API that proxies a public weather provider, caches results in MySQL, and serves a search history.

This project ties together everything in the JavaScript Essentials module — `fetch`, promises/`async`-`await`, DOM manipulation, and event handling — while reinforcing the Spring + MySQL skills from earlier modules. It is the kind of vertical slice you build constantly as a backend developer: client → controller → service → database.

## Learning Objectives

- Call a remote HTTP API from Spring using `RestClient` and map JSON to DTOs.
- Expose a clean REST endpoint and consume it from the browser with `fetch` + `async/await`.
- Persist and query data with Spring Data JPA and MySQL 8.
- Render dynamic content into the DOM and handle loading/error states.
- Keep secrets (API keys) out of code using configuration properties.

## Prerequisites & Setup

- Java 17+, Maven, MySQL 8, and a free API key from [open-meteo.com](https://open-meteo.com) (no key needed) or OpenWeatherMap.
- We'll use **Open-Meteo** — it requires no API key, which keeps setup simple.

```bash
# Create the database
mysql -u root -p -e "CREATE DATABASE weather_dashboard CHARACTER SET utf8mb4;"

# Generate a Spring Boot project (or use start.spring.io) with:
#   Web, Spring Data JPA, MySQL Driver, Validation
mvn spring-boot:run
```

```properties
# src/main/resources/application.properties
spring.datasource.url=jdbc:mysql://localhost:3306/weather_dashboard
spring.datasource.username=root
spring.datasource.password=your_password
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
weather.api.base-url=https://api.open-meteo.com/v1
geo.api.base-url=https://geocoding-api.open-meteo.com/v1
```

## Requirements

| # | Requirement |
|---|-------------|
| 1 | `GET /api/weather?city={name}` returns current temperature, wind speed, and a timestamp |
| 2 | Each successful lookup is saved as a row in a `search_history` table |
| 3 | `GET /api/history` returns the 10 most recent searches |
| 4 | A single-page front end calls these endpoints and renders results |
| 5 | Invalid/unknown city returns HTTP 404 with a JSON error body |

## Step-by-Step Tasks

### 1. Define the persistence layer

- [ ] Create a `SearchHistory` JPA entity.
- [ ] Create a `SearchHistoryRepository` with a "top 10 recent" finder.

```java
@Entity
@Table(name = "search_history")
public class SearchHistory {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String city;
    private double temperature;
    private double windSpeed;
    private Instant searchedAt = Instant.now();
    // getters & setters
}
```

```java
public interface SearchHistoryRepository extends JpaRepository<SearchHistory, Long> {
    List<SearchHistory> findTop10ByOrderBySearchedAtDesc();
}
```

### 2. Model the external API responses

- [ ] Add DTOs that match Open-Meteo's JSON. Use records for brevity.

```java
public record GeoResponse(List<Geo> results) {
    public record Geo(double latitude, double longitude, String name) {}
}

public record ForecastResponse(@JsonProperty("current") Current current) {
    public record Current(double temperature_2m, double wind_speed_10m) {}
}
```

### 3. Build the service

- [ ] Geocode the city name to coordinates, then fetch the current weather.
- [ ] Throw a custom `CityNotFoundException` when no match exists.
- [ ] Save a `SearchHistory` row on success.

```java
@Service
public class WeatherService {
    private final RestClient geo;
    private final RestClient forecast;
    private final SearchHistoryRepository repo;

    public WeatherService(@Value("${geo.api.base-url}") String geoUrl,
                          @Value("${weather.api.base-url}") String fcUrl,
                          SearchHistoryRepository repo) {
        this.geo = RestClient.create(geoUrl);
        this.forecast = RestClient.create(fcUrl);
        this.repo = repo;
    }

    public SearchHistory lookup(String city) {
        GeoResponse g = geo.get()
            .uri("/search?name={c}&count=1", city)
            .retrieve().body(GeoResponse.class);
        if (g == null || g.results() == null || g.results().isEmpty())
            throw new CityNotFoundException(city);

        var loc = g.results().get(0);
        ForecastResponse f = forecast.get()
            .uri("/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m",
                 loc.latitude(), loc.longitude())
            .retrieve().body(ForecastResponse.class);

        SearchHistory s = new SearchHistory();
        s.setCity(loc.name());
        s.setTemperature(f.current().temperature_2m());
        s.setWindSpeed(f.current().wind_speed_10m());
        return repo.save(s);
    }
}
```

### 4. Expose the REST controller

- [ ] Add `GET /api/weather` and `GET /api/history`.
- [ ] Map `CityNotFoundException` to a 404 with `@ExceptionHandler`.

```java
@RestController
@RequestMapping("/api")
public class WeatherController {
    private final WeatherService service;
    private final SearchHistoryRepository repo;
    // constructor

    @GetMapping("/weather")
    public SearchHistory weather(@RequestParam String city) {
        return service.lookup(city);
    }

    @GetMapping("/history")
    public List<SearchHistory> history() {
        return repo.findTop10ByOrderBySearchedAtDesc();
    }

    @ExceptionHandler(CityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Map<String, String> notFound(CityNotFoundException e) {
        return Map.of("error", e.getMessage());
    }
}
```

### 5. Build the front end

- [ ] Add `src/main/resources/static/index.html` with a search input and results area.
- [ ] Wire up `fetch` with `async/await` and render the response.

```html
<input id="city" placeholder="Enter a city" />
<button id="go">Search</button>
<div id="result"></div>
```

```javascript
document.getElementById('go').addEventListener('click', async () => {
  const city = document.getElementById('city').value.trim();
  const out = document.getElementById('result');
  out.textContent = 'Loading...';
  try {
    const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error((await res.json()).error);
    const w = await res.json();
    out.textContent = `${w.city}: ${w.temperature}°C, wind ${w.windSpeed} km/h`;
  } catch (err) {
    out.textContent = `Error: ${err.message}`;
  }
});
```

## Acceptance Criteria

- [ ] `GET /api/weather?city=London` returns 200 with `city`, `temperature`, `windSpeed`, `searchedAt`.
- [ ] An unknown city returns 404 with a JSON `error` field.
- [ ] Every successful search inserts exactly one `search_history` row.
- [ ] `GET /api/history` returns at most 10 rows, newest first.
- [ ] The front page loads at `http://localhost:8080/`, searches work, and errors are shown to the user (no uncaught promise rejections in the console).
- [ ] No API keys or passwords are hard-coded in Java source.

## Stretch Challenges

1. Add a 5-minute cache: skip the external call if the same city was queried recently.
2. Render the search history as a live-updating list under the result.
3. Add a unit test for `WeatherService` using a mocked `RestClient` / `MockRestServiceServer`.
4. Show a weather icon based on a `weather_code` field from the API.
5. Add pagination to `/api/history` with `Pageable`.

## Hints

- `RestClient` is the modern replacement for `RestTemplate`; create it once and reuse it.
- Open-Meteo field names use snake_case — either match them in your record or annotate with `@JsonProperty`.
- Always `encodeURIComponent` the city before putting it in a URL.
- Check `response.ok` before calling `response.json()`; `fetch` only rejects on network errors, not HTTP 4xx/5xx.
- Spring serves anything in `src/main/resources/static/` at the web root automatically.
