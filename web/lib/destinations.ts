// ─── Types ───────────────────────────────────────────────────────────────────

export interface Destination {
  id: string;       // stable kebab-case slug
  name: string;     // display name passed to the planning API
  country: string;  // shown in search results
  regionId: string; // foreign key → Region.id
  plannerReady: boolean; // true = engine has full hotel/flight data for this city
}

export interface Region {
  id: string;
  label: string;
  destinations: Destination[];
}

// ─── Helper ──────────────────────────────────────────────────────────────────

// Cities with full engine data (hotel + flight pricing, award availability).
// Expand this set as backend data is added for new cities.
const PLANNER_READY = new Set([
  "Amsterdam", "Barcelona", "London", "Paris", "Rome",
]);

function d(id: string, name: string, country: string, regionId: string): Destination {
  return { id, name, country, regionId, plannerReady: PLANNER_READY.has(name) };
}

// ─── Dataset ─────────────────────────────────────────────────────────────────
// Curated list — add new entries here; search + UI update automatically.
// Planning engine currently supports Europe destinations only.
// Other regions are fully browsable; backend support is future work.

export const REGIONS: Region[] = [
  {
    id: "europe",
    label: "Europe",
    destinations: [
      d("amsterdam",  "Amsterdam",  "Netherlands",    "europe"),
      d("athens",     "Athens",     "Greece",         "europe"),
      d("barcelona",  "Barcelona",  "Spain",          "europe"),
      d("berlin",     "Berlin",     "Germany",        "europe"),
      d("budapest",   "Budapest",   "Hungary",        "europe"),
      d("copenhagen", "Copenhagen", "Denmark",        "europe"),
      d("dubrovnik",  "Dubrovnik",  "Croatia",        "europe"),
      d("dublin",     "Dublin",     "Ireland",        "europe"),
      d("edinburgh",  "Edinburgh",  "Scotland",       "europe"),
      d("florence",   "Florence",   "Italy",          "europe"),
      d("lisbon",     "Lisbon",     "Portugal",       "europe"),
      d("london",     "London",     "England",        "europe"),
      d("madrid",     "Madrid",     "Spain",          "europe"),
      d("nice",       "Nice",       "France",         "europe"),
      d("paris",      "Paris",      "France",         "europe"),
      d("porto",      "Porto",      "Portugal",       "europe"),
      d("prague",     "Prague",     "Czech Republic", "europe"),
      d("rome",       "Rome",       "Italy",          "europe"),
      d("santorini",  "Santorini",  "Greece",         "europe"),
      d("stockholm",  "Stockholm",  "Sweden",         "europe"),
      d("vienna",     "Vienna",     "Austria",        "europe"),
      d("zurich",     "Zurich",     "Switzerland",    "europe"),
    ],
  },
  {
    id: "japan",
    label: "Japan",
    destinations: [
      d("fukuoka",   "Fukuoka",   "Japan", "japan"),
      d("hakone",    "Hakone",    "Japan", "japan"),
      d("hiroshima", "Hiroshima", "Japan", "japan"),
      d("kanazawa",  "Kanazawa",  "Japan", "japan"),
      d("kyoto",     "Kyoto",     "Japan", "japan"),
      d("nara",      "Nara",      "Japan", "japan"),
      d("nikko",     "Nikko",     "Japan", "japan"),
      d("okinawa",   "Okinawa",   "Japan", "japan"),
      d("osaka",     "Osaka",     "Japan", "japan"),
      d("sapporo",   "Sapporo",   "Japan", "japan"),
      d("takayama",  "Takayama",  "Japan", "japan"),
      d("tokyo",     "Tokyo",     "Japan", "japan"),
    ],
  },
  {
    id: "hawaii",
    label: "Hawaii",
    destinations: [
      d("big-island", "Big Island", "Hawaii", "hawaii"),
      d("honolulu",   "Honolulu",   "Hawaii", "hawaii"),
      d("kauai",      "Kauai",      "Hawaii", "hawaii"),
      d("lanai",      "Lanai",      "Hawaii", "hawaii"),
      d("maui",       "Maui",       "Hawaii", "hawaii"),
      d("molokai",    "Molokai",    "Hawaii", "hawaii"),
    ],
  },
  {
    id: "caribbean",
    label: "Caribbean",
    destinations: [
      d("antigua",      "Antigua",        "Antigua & Barbuda",  "caribbean"),
      d("aruba",        "Aruba",          "Aruba",              "caribbean"),
      d("bahamas",      "Bahamas",        "Bahamas",            "caribbean"),
      d("barbados",     "Barbados",       "Barbados",           "caribbean"),
      d("belize",       "Belize City",    "Belize",             "caribbean"),
      d("cancun",       "Cancún",         "Mexico",             "caribbean"),
      d("curacao",      "Curaçao",        "Curaçao",            "caribbean"),
      d("jamaica",      "Montego Bay",    "Jamaica",            "caribbean"),
      d("punta-cana",   "Punta Cana",     "Dominican Republic", "caribbean"),
      d("st-lucia",     "St. Lucia",      "St. Lucia",          "caribbean"),
      d("st-martin",    "St. Martin",     "St. Martin",         "caribbean"),
      d("turks-caicos", "Turks & Caicos", "Turks & Caicos",     "caribbean"),
    ],
  },
  {
    id: "us_cities",
    label: "US Cities",
    destinations: [
      d("austin",        "Austin",        "Texas",        "us_cities"),
      d("boston",        "Boston",        "Massachusetts","us_cities"),
      d("chicago",       "Chicago",       "Illinois",     "us_cities"),
      d("denver",        "Denver",        "Colorado",     "us_cities"),
      d("las-vegas",     "Las Vegas",     "Nevada",       "us_cities"),
      d("los-angeles",   "Los Angeles",   "California",   "us_cities"),
      d("miami",         "Miami",         "Florida",      "us_cities"),
      d("nashville",     "Nashville",     "Tennessee",    "us_cities"),
      d("new-orleans",   "New Orleans",   "Louisiana",    "us_cities"),
      d("new-york",      "New York",      "New York",     "us_cities"),
      d("portland",      "Portland",      "Oregon",       "us_cities"),
      d("san-francisco", "San Francisco", "California",   "us_cities"),
      d("savannah",      "Savannah",      "Georgia",      "us_cities"),
      d("seattle",       "Seattle",       "Washington",   "us_cities"),
      d("washington-dc", "Washington DC", "DC",           "us_cities"),
    ],
  },
  {
    id: "se_asia",
    label: "SE Asia",
    destinations: [
      d("bali",          "Bali",             "Indonesia", "se_asia"),
      d("bangkok",       "Bangkok",          "Thailand",  "se_asia"),
      d("chiang-mai",    "Chiang Mai",       "Thailand",  "se_asia"),
      d("hanoi",         "Hanoi",            "Vietnam",   "se_asia"),
      d("ho-chi-minh",   "Ho Chi Minh City", "Vietnam",   "se_asia"),
      d("kuala-lumpur",  "Kuala Lumpur",     "Malaysia",  "se_asia"),
      d("lombok",        "Lombok",           "Indonesia", "se_asia"),
      d("phuket",        "Phuket",           "Thailand",  "se_asia"),
      d("siem-reap",     "Siem Reap",        "Cambodia",  "se_asia"),
      d("singapore",     "Singapore",        "Singapore", "se_asia"),
    ],
  },
];

// ─── Flat list for cross-region search ───────────────────────────────────────

export const ALL_DESTINATIONS: Destination[] = REGIONS.flatMap(r => r.destinations);

// ─── Lookup helpers ───────────────────────────────────────────────────────────

export function getRegion(id: string): Region | undefined {
  return REGIONS.find(r => r.id === id);
}
