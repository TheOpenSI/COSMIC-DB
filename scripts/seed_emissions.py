"""
scripts/seed_emissions.py

Generates fake CodeCarbon-style emissions rows and inserts them DIRECTLY into
PostgreSQL via psycopg, bypassing the FastAPI layer entirely.

This lets us backdate `timestamp` values (impossible through the API, since
the Emissions table model auto-generates `timestamp = now()` server-side).

Run from the COSMIC-DB project root (host machine, not inside container),
after exposing Postgres on localhost:5432 in docker-compose.yml.

Usage:
    uv run scripts/seed_emissions.py --rows 50 --users 2
    uv run scripts/seed_emissions.py --rows 300 --users 2 --days-back 60

Requires (already in pyproject.toml):
    psycopg>=3.3.3
    faker>=37.0.0   (add this if not present)
"""

### Core modules ###
import argparse
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4, uuid7

### Third-party modules ###
import psycopg
from faker import Faker


fake = Faker()

# ── DB CONNECTION — matches docker/secrets/*.txt values ───────────────────
DB_HOST: str = "localhost"   # host machine, after port mapping 5432:5432
DB_PORT: int = 5432
DB_NAME: str = "demo"
DB_USER: str = "demo"
DB_PASSWORD: str = "demo123"
# ────────────────────────────────────────────────────────────────────────────

# ── FAKE DATA CONFIG — tweak these to change realism / variety ────────────
REGIONS: list[str] = [
    "new south wales", "victoria", "queensland",
    "western australia", "south australia", "tasmania",
]

OS_STRINGS: list[str] = [
    "Linux-6.6.114.1-microsoft-standard-WSL2-aarch64-with-glibc2.41",
    "Linux-5.15.0-generic-x86_64-with-glibc2.35",
    "Linux-6.8.0-aws-x86_64-with-glibc2.39",
]

CPU_MODELS: list[str] = ["Oryon", "AMD EPYC 7763", "Intel Xeon Platinum 8275CL"]

TRACKING_MODES: list[str] = ["process", "machine"]

BASE_LONGITUDE: float = 151.0973
BASE_LATITUDE: float = -33.8829
# ────────────────────────────────────────────────────────────────────────────


# ── REAL EXISTING USERS — must satisfy FK_EMISSIONS_USER_ID constraint ────
# user_id has a FOREIGN KEY referencing users(id), so random fake UUIDs will
# fail on insert. Emissions rows are juggled between these two real users.
REAL_USER_IDS: list[str] = [
    "019ef783-5bb2-7277-8bd5-15714570ceb6",  # cosmic
    "019ef783-5bb2-7277-8bd5-1572d246ea55",  # test_user
]
# ────────────────────────────────────────────────────────────────────────────


def uuid7_like() -> str:
    """
    Generate a UUID7 for the emissions 'id' primary key column. The 'id'
    column has no FK constraint (it's the PK, auto-generated), so a fresh
    uuid7() per row is fine — it doesn't need to reference anything.
    """
    return str(uuid7())


def get_user_id_pool(num_users: int) -> list[str]:
    """
    Return user IDs to attribute fake emissions to.

    NOTE: Unlike 'id', user_id IS constrained by FK_EMISSIONS_USER_ID
    referencing users(id). We can't invent random UUIDs here — we must
    juggle between the real existing users. --users is capped at the
    number of real users available.
    """
    if num_users > len(REAL_USER_IDS):
        print(
            f"NOTE: --users {num_users} requested, but only "
            f"{len(REAL_USER_IDS)} real user(s) exist. Using all {len(REAL_USER_IDS)}."
        )
        return REAL_USER_IDS
    return REAL_USER_IDS[:num_users]


def random_backdated_timestamp(days_back: int) -> datetime:
    """Random timestamp within the last `days_back` days, timezone-aware UTC."""
    now = datetime.now(tz=timezone.utc)
    delta_seconds = random.randint(0, days_back * 24 * 60 * 60)
    return now - timedelta(seconds=delta_seconds)


def build_fake_row(user_id: str, days_back: int) -> dict:
    """
    Build a single fake emissions row with every column populated.

    Value ranges below are calibrated to match real observed data from this
    WSL2/process-tracking setup:
      - duration ~8-28s
      - cpu_power ~0.006-0.03W
      - ram_power fixed at 3W
      - emissions_rate (per-second rate) ~4.58e-7 to 4.61e-7
      - emissions = energy_consumed * 2.548692  (NSW grid carbon intensity,
        kg CO2 per kWh — derived directly from real rows:
        emissions / energy_consumed = 2.5486920 consistently)
      - ram_utilization ~57-65%
    """
    duration = round(random.uniform(8.0, 28.0), 6)
    cpu_power = round(random.uniform(0.005, 0.035), 10)
    gpu_power = round(random.uniform(0.005, 0.035), 10)   
    ram_power = 3.0
    cpu_energy = round(cpu_power * duration / 3_600_000, 12)
    gpu_energy = round(gpu_power * duration / 3_600_000, 12)
    ram_energy = round(ram_power * duration / 3_600_000, 12)
    energy_consumed = round(cpu_energy + gpu_energy + ram_energy, 12)

    # NSW grid carbon intensity (kg CO2/kWh), matches real data exactly
    GRID_INTENSITY_NSW: float = 2.548692
    emissions = round(energy_consumed * GRID_INTENSITY_NSW, 12)
    emissions_rate = round(emissions / duration, 12)   # matches real ~4.58e-7 to 4.61e-7

    cpu_utilization = round(random.uniform(55.0, 85.0), 6)
    ram_utilization = round(random.uniform(57.0, 65.0), 6)
    ram_used_gb = round(7.55 * (ram_utilization / 100), 6)

    return {
        "id": uuid7_like(),
        "timestamp": random_backdated_timestamp(days_back),
        "run_id": str(uuid4()),
        "duration": duration,
        "emissions": emissions,
        "emissions_rate": emissions_rate,
        "cpu_power": cpu_power,
        "gpu_power": gpu_power,
        "ram_power": ram_power,
        "cpu_energy": cpu_energy,
        "gpu_energy": gpu_energy,
        "ram_energy": ram_energy,
        "energy_consumed": energy_consumed,
        "water_consumed": 0.0,
        "region": random.choice(REGIONS),
        "cloud_provider": "",
        "cloud_region": "",
        "os": random.choice(OS_STRINGS),
        "cpu_count": 10,
        "cpu_model": random.choice(CPU_MODELS),
        "gpu_count": 0,
        "gpu_model": None,
        "longitude": round(BASE_LONGITUDE + random.uniform(-0.05, 0.05), 6),
        "latitude": round(BASE_LATITUDE + random.uniform(-0.05, 0.05), 6),
        "ram_total_size": 7.548999786376953,
        "tracking_mode": random.choice(TRACKING_MODES),
        "cpu_utilization_percent": cpu_utilization,
        "gpu_utilization_percent": 0.0,
        "ram_utilization_percent": ram_utilization,
        "ram_used_gb": ram_used_gb,
        "on_cloud": "N",
        "pue": 1.0,
        "wue": 0.0,
        "user_id": user_id,
    }


INSERT_SQL: str = """
    INSERT INTO emissions (
        id, "timestamp", run_id, duration, emissions, emissions_rate,
        cpu_power, gpu_power, ram_power, cpu_energy, gpu_energy, ram_energy,
        energy_consumed, water_consumed, region, cloud_provider, cloud_region,
        os, cpu_count, cpu_model, gpu_count, gpu_model, longitude, latitude,
        ram_total_size, tracking_mode, cpu_utilization_percent,
        gpu_utilization_percent, ram_utilization_percent, ram_used_gb,
        on_cloud, pue, wue, user_id
    ) VALUES (
        %(id)s, %(timestamp)s, %(run_id)s, %(duration)s, %(emissions)s, %(emissions_rate)s,
        %(cpu_power)s, %(gpu_power)s, %(ram_power)s, %(cpu_energy)s, %(gpu_energy)s, %(ram_energy)s,
        %(energy_consumed)s, %(water_consumed)s, %(region)s, %(cloud_provider)s, %(cloud_region)s,
        %(os)s, %(cpu_count)s, %(cpu_model)s, %(gpu_count)s, %(gpu_model)s, %(longitude)s, %(latitude)s,
        %(ram_total_size)s, %(tracking_mode)s, %(cpu_utilization_percent)s,
        %(gpu_utilization_percent)s, %(ram_utilization_percent)s, %(ram_used_gb)s,
        %(on_cloud)s, %(pue)s, %(wue)s, %(user_id)s
    )
"""


def seed(num_rows: int, num_users: int, days_back: int) -> None:
    user_ids = get_user_id_pool(num_users)
    print(f"Seeding {num_rows} fake emission rows, juggled across {len(user_ids)} real user(s)...")
    print(f"Using user IDs:")
    for uid in user_ids:
        print(f"  - {uid}")
    print()

    conn_str = (
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
        f"user={DB_USER} password={DB_PASSWORD}"
    )

    rows = [
        build_fake_row(user_id=random.choice(user_ids), days_back=days_back)
        for _ in range(num_rows)
    ]

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.executemany(INSERT_SQL, rows)
            conn.commit()
        print(f"Successfully inserted {num_rows} rows into 'emissions' table.")
    except Exception as e:
        print(f"FAILED to seed data: {e}")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed fake emissions data directly into Postgres.")
    parser.add_argument("--rows", type=int, default=50, help="Number of fake emission rows to create.")
    parser.add_argument("--users", type=int, default=2, help="Number of real existing user IDs to juggle rows across (capped at available real users).")
    parser.add_argument("--days-back", type=int, default=30, help="Spread timestamps randomly across the last N days.")
    args = parser.parse_args()

    seed(num_rows=args.rows, num_users=args.users, days_back=args.days_back)


if __name__ == "__main__":
    main()