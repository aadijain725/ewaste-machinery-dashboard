#!/usr/bin/env python3
"""Seed the e-waste SQLite database from extracted HTML data."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ewaste.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


# ── Category data ──────────────────────────────────────────────

CATEGORIES = [
    ("itew", "ITEW", "IT & Telecom Equipment", "ITEW 1-16",
     "Laptops, desktops, servers, phones, printers, networking, tablets",
     1, 34000, 112000,
     "High — corporate bulk, kabadiwala, auction",
     "Largest e-waste stream in India",
     "Data destruction (degausser/wiper) mandatory for corporate",
     "Core 10 items + #13 (data wipe). No compressor/CRT/refrigerant needed.",
     "PCBs from servers and motherboards have highest gold density. Mobile phone PCBs are premium (Rs 400-600/kg). CPU pins from older models extremely gold-rich. This category drives the gold certificate market."),

    ("ceew", "CEEW", "Consumer Electronics & PV", "CEEW 1-19",
     "TVs (LCD/LED/CRT), refrigerators, ACs, washing machines, solar panels, audio",
     1, 22000, 74000,
     "Medium — household collection, scrap dealers, municipal",
     "Second largest, growing with solar PV",
     "CRT cutting (#10), compressor cutting (#7), refrigerant recovery (#8), oil recovery (#9)",
     "Core 10 + #7,#8,#9,#10. Triggers most expensive Annexure 1 items.",
     "Highest iron content (steel chassis from fridges/TVs/ACs). Good for Fe certificates. Triggers compressor + CRT + refrigerant machinery (Rs 15-50L extra). Solar PV is a growing sub-category with silver recovery potential."),

    ("lseew", "LSEEW", "Large & Small Equipment", "LSEEW 1-34",
     "Large household (dishwashers, ovens), small (vacuum, toasters, clocks, fans)",
     1, 10000, 30000,
     "Medium — mixed with CEEW in practice",
     "Broad category, variable composition",
     "Similar to CEEW for large items; small items are simpler",
     "Core 10 + possibly #7,#8 for large appliances with compressors.",
     "Highest ferrous content overall. Small EEE (fans, irons, toasters) are easier to process — no compressors, no CRT, no refrigerant. Consider registering for small LSEEW only to avoid triggering heavy machinery."),

    ("eetw", "EETW", "Electrical & Electronic Tools", "EETW 1-8",
     "Drills, saws, sewing machines, soldering irons, lawnmowers",
     2, 10000, 30000,
     "Low — niche, industrial sources",
     "Small volume nationally",
     "None beyond core — simple electromechanical devices",
     "Core 10 items only. No special machinery triggered.",
     "Electric motors = high copper content (windings). Simple steel housings. No hazardous components like CRT or refrigerant. Easy to process but low volume. Good as an add-on category."),

    ("tlsew", "TLSEW", "Toys, Leisure & Sports", "TLSEW 1-6",
     "Electric trains, video games, slot machines, sports equipment with electronics",
     3, 10000, 25000,
     "Very low",
     "Negligible in India currently",
     "None — simple electronics in plastic housings",
     "Core 10 items only.",
     "Mostly plastic with small PCBs. Very low metal recovery per tonne. Not viable as primary category. Add only if collecting mixed e-waste that includes these."),

    ("mdw", "MDW", "Medical Devices", "MDW 1-10",
     "Radiotherapy, dialysis, cardiology, lab analyzers, ventilators, nuclear medicine",
     0, 20000, 50000,
     "Niche — hospital auctions, refurbishers",
     "Growing with healthcare expansion",
     "May need specialized decontamination protocols",
     "Core 10 + decontamination/sterilization area.",
     "Medical equipment often has high-quality PCBs with precious metals. Regulated supply — hospitals must channel through authorized entities. Skip in Phase 1 due to decontamination infrastructure requirements."),

    ("liw", "LIW", "Laboratory Instruments", "LIW 1-2",
     "Measuring, control, laboratory equipment",
     3, 15000, 40000,
     "Very niche — research institutions, universities",
     "Small",
     "None beyond core",
     "Core 10 items only.",
     "Precision instruments often contain quality copper and gold-plated connectors. Small volume but good metal density. Add-on category for institutions."),
]

# ── Material composition (% per tonne) ─────────────────────────
# Format: (category_id, material, pct, price_per_unit, unit)
# Prices: gold=Rs 7500/g, copper=Rs 700/kg, aluminum=Rs 175/kg, iron=Rs 28/kg, plastic=Rs 20/kg

MATERIALS = [
    # ITEW
    ("itew", "gold", 0.0004, 7500, "g"),
    ("itew", "copper", 3.0, 700, "kg"),
    ("itew", "aluminum", 11.0, 175, "kg"),
    ("itew", "iron", 5.0, 28, "kg"),
    ("itew", "plastic", 30.0, 20, "kg"),
    # CEEW
    ("ceew", "gold", 0.00015, 7500, "g"),
    ("ceew", "copper", 5.0, 700, "kg"),
    ("ceew", "aluminum", 8.0, 175, "kg"),
    ("ceew", "iron", 20.0, 28, "kg"),
    ("ceew", "plastic", 25.0, 20, "kg"),
    # LSEEW
    ("lseew", "gold", 0.0001, 7500, "g"),
    ("lseew", "copper", 4.0, 700, "kg"),
    ("lseew", "aluminum", 6.0, 175, "kg"),
    ("lseew", "iron", 25.0, 28, "kg"),
    ("lseew", "plastic", 35.0, 20, "kg"),
    # EETW
    ("eetw", "gold", 0.00005, 7500, "g"),
    ("eetw", "copper", 8.0, 700, "kg"),
    ("eetw", "aluminum", 4.0, 175, "kg"),
    ("eetw", "iron", 30.0, 28, "kg"),
    ("eetw", "plastic", 20.0, 20, "kg"),
    # TLSEW
    ("tlsew", "gold", 0.00008, 7500, "g"),
    ("tlsew", "copper", 2.0, 700, "kg"),
    ("tlsew", "aluminum", 3.0, 175, "kg"),
    ("tlsew", "iron", 8.0, 28, "kg"),
    ("tlsew", "plastic", 50.0, 20, "kg"),
    # MDW
    ("mdw", "gold", 0.0003, 7500, "g"),
    ("mdw", "copper", 6.0, 700, "kg"),
    ("mdw", "aluminum", 5.0, 175, "kg"),
    ("mdw", "iron", 15.0, 28, "kg"),
    ("mdw", "plastic", 20.0, 20, "kg"),
    # LIW
    ("liw", "gold", 0.0002, 7500, "g"),
    ("liw", "copper", 5.0, 700, "kg"),
    ("liw", "aluminum", 4.0, 175, "kg"),
    ("liw", "iron", 10.0, 28, "kg"),
    ("liw", "plastic", 25.0, 20, "kg"),
]

# ── Machines (21 CPCB Annexure 1) ──────────────────────────────

MACHINES = [
    (1, "Dismantling Tables", "core", "MUST HAVE", 0.55, 3.8, None, None,
     "1T/day with 5 tables + 10 workers",
     "4x6 ft workstations with suction hoods connected to cyclone dust collector, 3m+ stack above roof. Workers manually disassemble e-waste here.",
     "Size: 4x6 ft per table | Weight: ~210 kg each | Connects to shared suction pipe + cyclone + 3m stack"),
    (2, "Shredder", "core", "MUST HAVE", 5.5, 15.0, 15, 55,
     "200 kg/hr rated, ~125 kg/hr sustained",
     "Twin-shaft or quad-shaft cutter that reduces dismantled fractions to 10-25mm pieces. Bottleneck machine — throughput determines CTO capacity.",
     "Blade: D2 hardened steel | Motor: 10-200 HP | Output: 20-80mm | Auto reverse + forward | Weight: 1200-14000 kg"),
    (3, "Magnetic Separator", "core", "MUST HAVE", 2.0, 4.0, 1, 2,
     "Continuous — belt speed matched to shredder",
     "Overband magnet mounted above conveyor belt. Pulls ferrous metals (iron, steel) from shredded stream. First separation stage.",
     "Type: Ferrite or Rare Earth | Belt width: 400-800mm | Maintenance: very low, magnets last 5-10 years"),
    (4, "Density Separator", "core", "MUST HAVE", 2.0, 5.0, 3.1, 11.1,
     "100-1000 kg/hr",
     "Air gravity table that separates by density — heavy metals sink, light plastics float.",
     "Weight: 450 kg | Dims: 36x40x55 in | Separates metal / non-metal / carbonaceous"),
    (5, "Eddy Current Separator", "core", "MUST HAVE", 5.0, 12.0, 8, 8,
     "Up to 500 kg/hr",
     "Rotating magnetic field repels and ejects non-ferrous metals (Al, Cu, brass) from mixed stream. Key machine for Cu/Al certificate generation.",
     "Weight: 1500 kg | Dims: 96x48x84 in | VFD for tuning | 95%+ ferrous removal efficiency"),
    (6, "Conveyors", "core", "MUST HAVE", 3.0, 6.0, 1, 2,
     "3-5 sections, 400-800mm belt width",
     "Feed conveyors from shredder to separators, sorting conveyors for manual picking, transfer conveyors between machines.",
     "Speed adjustable | Low power ~1-2 kW each | Material must flow ONE DIRECTION through plant"),
    (7, "Compressor Cutting Machine", "appliance", "CEEW TRIGGER", 2.0, 5.0, 5, 10,
     "15-30 compressors/hr",
     "Cuts open sealed hermetic compressors from fridges/ACs. Extracts copper windings, iron body, oil.",
     "Compressor range: 15-55 cm | Outer dia: 12-26 cm | Weight: 310 kg | Dims: 60x36x84 in"),
    (8, "Refrigerant Gas Recovery", "appliance", "CEEW TRIGGER", 1.0, 3.0, None, None,
     "200-350 g/min recovery rate",
     "Extracts CFC/HCFC/HFC refrigerant gases from AC and fridge cooling systems. Mandatory environmental compliance.",
     "Operating temp: 10-50C | Voltage: 110V | Portable unit 28x30x42 in | Recovered gas must go to authorized TSDF"),
    (9, "Compressor Oil Recovery", "appliance", "CEEW TRIGGER", 0.5, 2.0, None, None,
     "Batch processing",
     "Drills into compressor and drains oil before cutting. Oil is hazardous waste.",
     "Bench drill with collection drum | Low cost, low tech | Oil goes to authorized waste oil recycler"),
    (10, "CRT Cutting Machine", "appliance", "DECLINING RELEVANCE", 8.0, 15.0, 2, 2,
     "80-100 units/hr",
     "Hot-wire or diamond saw to cut CRT glass. Separates leaded funnel glass from unleaded panel glass.",
     "Air pressure: 0.6-0.8 MPa | CRT range: 14-29 in | Weight: 450 kg | CRT TVs declining — consider outsourcing initially"),
    (11, "Component Removing Machine (CRM)", "specialized", "PCB VALUE UNLOCK", 2.0, 3.0, 1, 1,
     "150-1000 kg/day",
     "Heated rotating drum that melts solder to remove components from populated PCBs. Creates bare boards + component stream.",
     "Material: Mild steel | Weight: 600 kg | Dims: 48x48x60 in | Separated components sell at Rs 400-800/kg"),
    (12, "Baling Machine / Hydraulic Press", "specialized", "MUST HAVE", 7.0, 13.0, 5, 10,
     "50 kg/min",
     "Compresses sorted metal fractions into dense bales for storage and transport. Baled metal sells 10-15% more than loose.",
     "Max force: 0-30 MT | CNC control | Weight: 1800-6000 kg | Horizontal and vertical configs"),
    (13, "Data Destruction (Degausser + HDD Crusher)", "specialized", "MUST HAVE for ITEW", 5.75, 11.0, None, None,
     "~10 sec/drive (degausser)",
     "Degausser erases magnetic media, physical crusher destroys HDDs/SSDs. Corporate clients require destruction certificates.",
     "Revenue opportunity: Rs 50-200/device for certified destruction | 1000 drives/month = Rs 50K-2L/month in fees alone"),
    (14, "Furnace / Smelting Furnace", "specialized", "STAGE 2 — GOLD RECOVERY", 5.0, 15.0, None, None,
     "25-50 kg crucible",
     "Melts Cu/Al scrap into ingots. Required for precious metal recovery pathway. Needs upgraded APCD (30m stack + scrubber).",
     "LPG fired | 440 VAC | Silicon Carbide crucible | APCD upgrade alone Rs 15-30L | Do NOT add at Day 1"),
    (15, "Precious Metal Recovery System", "specialized", "STAGE 2 — THE ENDGAME", 5.75, 42.75, None, None,
     "Depends on capacity — grams/day",
     "Pyro/hydro/electrometallurgical system for gold, silver, palladium from PCBs. Only ~11 recyclers in India have this.",
     "Full system: furnace (5-15L) + hydromet (10-25L) + electrowinning (5-12L) + APCD upgrade (15-30L) + ETP upgrade (10-20L) + lab (3-8L). Total Rs 45L-1.25Cr additional"),
    (16, "Wire Stripper / Cutter / Peeler", "support", "MUST HAVE", 0.75, 0.75, None, None,
     "150-200 kg/hr",
     "Strips insulation from cables to recover pure copper/aluminium wire. ~10% of kabadiwala intake is cables.",
     "Wire: 1-40mm dia (up to 120mm with attachments) | Weight: 100-600 kg | Cable at Rs 200/kg -> stripped Cu at Rs 700/kg = 3x markup"),
    (17, "Tube Light / CFL Recycling", "support", "COMPLIANCE", 1.75, 1.75, None, None,
     "20 lamps/min",
     "Crushes fluorescent tubes/CFLs while capturing mercury vapor through carbon filter.",
     "Motor: 1/6 HP 220V | Weight: 450 kg | Mercury is controlled substance — needs carbon filter for vapor + sealed phosphor collection"),
    (18, "Air Pollution Control Devices (APCD)", "support", "CRITICAL COMPLIANCE", 4.0, 30.0, None, None,
     "Matched to plant capacity",
     "Cyclone + bag house + alkaline scrubber + off-gas treatment + stack. #1 reason facilities fail CTE inspection.",
     "Basic (no furnace): cyclone + bag filter + 3m stack = Rs 4-8L | Full (with furnace): + scrubber + carbon filter + 30m stack = Rs 15-30L"),
    (19, "ETP (Effluent Treatment Plant)", "support", "CRITICAL COMPLIANCE", 5.0, 20.0, None, None,
     "2-5 KLD",
     "Treats wastewater from processing. Capacity must match operations.",
     "Config 2 (no furnace): 2 KLD + sludge bed = Rs 5-10L | Config 4 (gold): 5 KLD ZLD preferred = Rs 10-20L | Sludge is hazardous waste"),
    (20, "Weighbridge", "support", "MUST HAVE", 2.0, 4.0, None, None,
     "10-30 tonne capacity",
     "Platform scale at intake zone. Required for EPR portal reporting and material balance tracking.",
     "Typically 3x3m platform scale at 500 sqm | Every lot must be weighed, photographed, lot-numbered"),
    (21, "Weighing Machines / Equipment", "support", "MUST HAVE", 0.5, 1.0, None, None,
     "Various capacities",
     "Bench scales and floor scales at each processing stage for material flow tracking.",
     "Need at: intake, post-dismantling, post-shredding, post-separation, dispatch, HW storage | 3-5 bench + 1-2 floor scales"),
]

# ── Configurations ─────────────────────────────────────────────

CONFIGURATIONS = [
    ("mvp", "MVP", "Bare Minimum Recycler (Config 1)", 20.0, 31.0, 330,
     "Essentially a dismantler with data destruction. Sells dismantled fractions to other recyclers. Probably insufficient for CPCB recycler registration.",
     False),
    ("config2", "MFP", "Core Mechanical Recycler (Config 2)", 54.0, 107.0, 330,
     "Day 1 EPR recycler status. Self-sustaining at Rs 30-40/kg input. Generates Fe/Cu/Al certificates. Processes all categories kabadiwalas bring. Target: 1T/day, 8hrs, 1 shift.",
     True),
    ("config4", "Full + Gold", "Full Recycler + Gold Recovery (Config 4)", 150.0, 350.0, 660,
     "Config 2 + furnace + hydromet + electrowinning + upgraded APCD/ETP. Rs 45L-1.25Cr over Config 2. Only ~11 recyclers in India have gold recovery. The endgame.",
     False),
]

# Config -> machine mappings
CONFIG_MACHINES = {
    "mvp": [(1, True), (11, True), (13, True), (12, True), (16, True),
            (20, True), (21, True), (18, True), (19, True),
            (2, False), (3, False), (4, False), (5, False), (6, False),
            (7, False), (8, False), (9, False), (10, False)],
    "config2": [(1, True), (2, True), (3, True), (4, True), (5, True), (6, True),
                (7, True), (8, True), (9, True), (10, True), (11, True), (12, True),
                (13, True), (16, True), (17, True), (18, True), (19, True),
                (20, True), (21, True),
                (14, False), (15, False)],
    "config4": [(i, True) for i in range(1, 22)],
}

# Category -> machine mappings
CATEGORY_MACHINES = {
    "itew":  [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core"), (16, "core"), (13, "extra")],
    "ceew":  [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core"), (16, "core"),
              (7, "extra"), (8, "extra"), (9, "extra"), (10, "extra")],
    "lseew": [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core")],
    "eetw":  [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core"), (16, "core")],
    "tlsew": [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core")],
    "mdw":   [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core")],
    "liw":   [(1, "core"), (2, "core"), (3, "core"), (4, "core"), (5, "core"),
              (6, "core"), (12, "core")],
}

# ── Revenue items (Config 2, mixed kabadiwala e-waste) ─────────

REVENUE_ITEMS = [
    ("config2", "Copper (shreds/wire)", 40, 700, 28000, "Mixed ITEW/CEEW/LSEEW blend"),
    ("config2", "Aluminium (shreds)", 80, 175, 14000, None),
    ("config2", "Iron (bales)", 150, 28, 4200, None),
    ("config2", "PCBs (sold to refiners)", 30, 350, 10500, "Rs 250-600/kg depending on grade"),
    ("config2", "Plastic (sorted)", 280, 20, 5600, None),
    ("config2", "EPR Certificates (Cu+Al+Fe)", 270, 25, 6750, "Rs 15-35/kg avg, using midpoint"),
]

# ── Cost items (Config 2) ─────────────────────────────────────

COST_ITEMS = [
    ("config2", "Raw material (mixed e-waste)", 30000, 40000, "Kabadiwala lots at Rs 30-40/kg"),
    ("config2", "Labour (15 workers)", 4500, 4500, "Rs 15K/worker/month ÷ 22 days ÷ 1T/day"),
    ("config2", "Electricity (80kW × 8hrs)", 6400, 6400, "Rs 10/kWh industrial rate"),
    ("config2", "Rent", 4500, 7500, "Rs 1.5-2.5L/month ÷ 22T/month"),
    ("config2", "Consumables (blades, belts, PPE)", 2000, 2000, "Shredder blades Rs 20-80K/3-6 months"),
    ("config2", "Compliance (TSDF, testing, filing)", 1500, 1500, "Hazardous waste disposal, lab tests"),
    ("config2", "Transport + logistics", 2000, 2000, "Incoming and outgoing material movement"),
]

# ── Sourcing profile ──────────────────────────────────────────

SOURCING = [
    ("ceew", "kabadiwala", 35, "Old TVs, fridges, ACs, washing machines, stabilizers"),
    ("lseew", "kabadiwala", 25, "Fans, irons, mixers, geysers, small appliances"),
    ("itew", "kabadiwala", 20, "Old phones, chargers, routers, keyboards, some laptops"),
    (None, "kabadiwala", 10, "Mixed cables, wires, transformers"),
    ("eetw", "kabadiwala", 5, "Drills, sewing machines"),
    (None, "kabadiwala", 5, "Misc — tube lights, batteries (segregate immediately)"),
]

# ── Rental locations ──────────────────────────────────────────

RENTALS = [
    ("Sahibabad, Ghaziabad", 20, 35, 1.7, 3.0,
     "Close to Purva, NCR scrap market, Seelampur",
     "Congested, pollution board strict"),
    ("Greater Noida", 10, 20, 0.86, 1.7,
     "Cheaper, newer industrial areas, UPPCB",
     "Farther from Delhi scrap markets"),
    ("Haridwar SIDCUL", 8, 15, 0.69, 1.3,
     "Cheapest, Uttarakhand incentives possible",
     "Far from NCR, limited local scrap supply"),
    ("Manesar/Dharuhera, Haryana", 15, 25, 1.3, 2.15,
     "Haryana SPCB, good highway access",
     "Need Haryana-specific SPCB NOC process"),
    ("Sonipat/Kundli, Haryana", 12, 22, 1.03, 1.9,
     "Close to Delhi, Haryana, cheaper than Ghaziabad",
     "Mixed-use areas, check zoning"),
]

# ── Space zones ───────────────────────────────────────────────

SPACE_ZONES = [
    ("Intake Zone", 50, "Weighbridge, logging, photography"),
    ("Raw Material Storage", 80, "Sorted by type, batteries fire-rated separate"),
    ("Dismantling Area", 100, "5 tables + suction hoods, 3m+ ceiling, PPE"),
    ("Data Destruction Room", 20, "Secure, locked, degausser + crusher + wiping"),
    ("Mechanical Processing", 120, "Shredder→conveyor→mag→eddy→density, 3-4m ceiling"),
    ("Appliance Line", 40, "Compressor cut, refrigerant, oil recovery"),
    ("PCB Processing", 50, "CRM + PCB line"),
    ("Output Storage", 60, "Sorted metals, plastics, baling, dispatch"),
    ("APCD + ETP Zone", 50, "Cyclone, bag filter, stack, ETP, sludge bed"),
    ("Admin + HW Storage", 50, "Office, PPE, first aid, records, HW store"),
]


def seed(conn):
    cur = conn.cursor()

    # Categories
    cur.executemany(
        "INSERT OR REPLACE INTO categories VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        CATEGORIES)

    # Materials
    cur.executemany(
        "INSERT OR REPLACE INTO materials (category_id, material, pct, price_per_unit, unit) VALUES (?,?,?,?,?)",
        MATERIALS)

    # Machines
    cur.executemany(
        "INSERT OR REPLACE INTO machines VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        MACHINES)

    # Category-machine mappings
    for cat_id, machines in CATEGORY_MACHINES.items():
        for mid, req in machines:
            cur.execute(
                "INSERT OR REPLACE INTO category_machines VALUES (?,?,?)",
                (cat_id, mid, req))

    # Configurations
    cur.executemany(
        "INSERT OR REPLACE INTO configurations VALUES (?,?,?,?,?,?,?,?)",
        CONFIGURATIONS)

    # Config-machine mappings
    for config_id, machines in CONFIG_MACHINES.items():
        for mid, included in machines:
            cur.execute(
                "INSERT OR REPLACE INTO config_machines VALUES (?,?,?)",
                (config_id, mid, included))

    # Revenue items
    cur.executemany(
        "INSERT OR REPLACE INTO revenue_items (config_id, stream, yield_per_tonne_kg, price_per_kg, revenue_per_tonne, notes) VALUES (?,?,?,?,?,?)",
        REVENUE_ITEMS)

    # Cost items
    cur.executemany(
        "INSERT OR REPLACE INTO cost_items (config_id, item, cost_per_tonne_min, cost_per_tonne_max, notes) VALUES (?,?,?,?,?)",
        COST_ITEMS)

    # Sourcing
    cur.executemany(
        "INSERT OR REPLACE INTO sourcing_profile (category_id, source, percentage, notes) VALUES (?,?,?,?)",
        SOURCING)

    # Rentals
    cur.executemany(
        "INSERT OR REPLACE INTO rental_locations (location, rate_min_psf, rate_max_psf, monthly_800sqm_min_lakhs, monthly_800sqm_max_lakhs, pros, cons) VALUES (?,?,?,?,?,?,?)",
        RENTALS)

    # Space zones
    cur.executemany(
        "INSERT OR REPLACE INTO space_zones (zone_name, required_sqm, contents) VALUES (?,?,?)",
        SPACE_ZONES)

    # ── Build FTS search index ─────────────────────────────────
    cur.execute("DELETE FROM search_index")

    # Index categories
    for c in CATEGORIES:
        cur.execute(
            "INSERT INTO search_index VALUES (?,?,?,?)",
            ("category", c[0], f"{c[1]}: {c[2]}",
             f"{c[4]} | Supply: {c[8]} | Volume: {c[9]} | {c[12]}"))

    # Index machines
    for m in MACHINES:
        cur.execute(
            "INSERT INTO search_index VALUES (?,?,?,?)",
            ("machine", str(m[0]), f"#{m[0]} {m[1]}",
             f"{m[9]} | {m[10]} | Group: {m[2]} | Badge: {m[3]}"))

    # Index configurations
    for c in CONFIGURATIONS:
        cur.execute(
            "INSERT INTO search_index VALUES (?,?,?,?)",
            ("configuration", c[0], f"{c[1]}: {c[2]}",
             f"{c[6]} | Price: Rs {c[3]}-{c[4]}L | Target: {c[5]} TPA"))

    conn.commit()
    print(f"Database seeded at {DB_PATH}")

    # Print summary
    for table in ["categories", "materials", "machines", "configurations",
                   "revenue_items", "cost_items", "sourcing_profile",
                   "rental_locations", "space_zones", "search_index"]:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")


if __name__ == "__main__":
    conn = init_db()
    seed(conn)
    conn.close()
