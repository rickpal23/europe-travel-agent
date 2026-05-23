# Europe Travel Agent

A demo multi-agent travel planner written in plain Python. It shows how a set of specialized agents can collaborate to produce a scored, day-by-day family trip plan to Europe — using Amex Membership Rewards and Marriott Bonvoy points.

## What it does

Given a hardcoded traveler profile (origin, dates, points balances, city preferences), the planner:

1. Generates candidate departure dates (weekend + mid-week deal-hunter options)
2. Builds three itinerary templates (2-city, 3-city train loop, 3-city triangle)
3. Plans flights and hotels for each itinerary using loyalty points
4. Scores every itinerary on a 0–100 family-tuned scale
5. Prints a ranked comparison and a full day-by-day plan for the winner

## Agent architecture

```
trip_planner_agent          ← orchestrator
├── date_selection_agent    ← candidate departure dates
├── itinerary_builder_agent ← day-by-day skeletons for 3 routes
└── per-itinerary loop:
    ├── flight_points_agent ← Amex MR points + best date selection
    ├── hotel_points_agent  ← Marriott certs → Bonvoy points → cash
    ├── city_flow_agent     ← transit efficiency score
    └── deal_scorer_agent   ← combined 0–100 ranking
        └── day_by_day_itinerary_agent  ← calendar plan for winner
```

Each agent is a plain Python function. No framework required.

## Quick start

```bash
# Clone / download the repo, then:
python3 main.py
```

No dependencies to install. The planner runs entirely on Python stdlib.

**With live web search** (optional):

```bash
export TAVILY_API_KEY="your-key-here"
python3 main.py
```

Without the key, web-search steps are skipped gracefully and the planner falls back to its built-in data.

## Configuration

Edit the constants at the top of `main.py`:

| Variable | What it controls |
|---|---|
| `USER_PROFILE` | Travelers, origin, date window, required/optional cities, points balances, preferences |
| `TRAVEL_YEAR` | The departure year |
| `AMEX_FLIGHT_OPTIONS` | Points cost per destination city and preferred airline |
| `CITY_AVAIL` | Award-space availability score per city (1–3) |
| `SAMPLE_ITINERARIES` | The three route templates |
| `CITY_DATA` | Hotel name, room type, sqft, nightly cost/points, family notes per city |

## Scoring breakdown (out of 100)

| Factor | Max pts |
|---|---|
| Includes required cities (London + Paris) | 20 |
| Travel flow / transit efficiency | 10 |
| Amex MR points utilization | 15 |
| Marriott certs + Bonvoy points usage | 15 |
| Family comfort (room size, pace, hotel changes) | 15 |
| Trip pace | 10 |
| Hotel quality (average rating) | 10 |
| Cash outlay | 5 |
| Penalties (small rooms, extra hotel changes) | −5 each |

## Requirements

- Python 3.8+
- No pip packages required
- Optional: [Tavily](https://tavily.com) API key for live web search
