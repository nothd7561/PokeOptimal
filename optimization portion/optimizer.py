import random
import pandas as pd
import pulp as pl

# ======================= CONFIG (edit here, not at runtime) =======================
PLAYSTYLE_CSV = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\optimization portion\playstyle_compositions_corrected.csv'
ROLES_CSV = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\role assignments\final_role_assignment(1).csv'
MOVES_CSV = r'C:\Users\lucas\Downloads\personal coding\pokemon optimizer v2\moves\pokemon_has_moves.csv'

# Automatic speed rules per playstyle (key = lowercase part of the playstyle name).
# Tier names must match the values in your speed_tier column (the script prints them at startup).
FAST_TIERS = ["High", "Very High"]
SPEED_DEFAULTS = {
    "trick room":      {"tiers": FAST_TIERS, "min": 0, "max": 1},
    "hyper offensive": {"tiers": FAST_TIERS, "min": 3, "max": None},
    "volt-turn":       {"tiers": FAST_TIERS, "min": 2, "max": None},
    "stalwart":        {"tiers": FAST_TIERS, "min": 0, "max": 1},
}

# Roles the fallback ladder may NEVER leave unfilled
HARD_ROLES = {"Trick Room Setter"}

# Trick Room compatibility from actual base Speed (a score, not a hard rule)
SPEED_COL_CANDIDATES = ["Speed", "Spe", "base_speed", "Base Speed", "BaseSpeed"]
SPEED_SCORE_WEIGHT = 0.5

def trick_room_score(spe):
    if spe <= 60:
        return 1.0
    if spe <= 70:
        return 0.6
    if spe <= 85:
        return 0.2
    if spe <= 100:
        return -0.4
    return -1.0

VARIETY_LEVELS = {"1": ("Safe (best-usage picks)", 0.1),
                  "2": ("Mixed", 0.4),
                  "3": ("Wild (more surprises)", 0.8)}
ANCHOR_SYNERGY_WEIGHT = 0.6   # how strongly teammates are chosen to cover the locked-in Pokemon
MIN_NEW_POKEMON = 2           # each extra team differs from earlier ones by at least this many
SLACK_PENALTY = 0.5           # cost of leaving a (non-hard) role slot unfilled

# ======================= TYPE CHART =======================
CHART = {  # attacker: (super effective, not very effective, no effect)
    "normal": ([], ["rock", "steel"], ["ghost"]),
    "fire": (["grass", "ice", "bug", "steel"], ["fire", "water", "rock", "dragon"], []),
    "water": (["fire", "ground", "rock"], ["water", "grass", "dragon"], []),
    "electric": (["water", "flying"], ["electric", "grass", "dragon"], ["ground"]),
    "grass": (["water", "ground", "rock"], ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"], []),
    "ice": (["grass", "ground", "flying", "dragon"], ["fire", "water", "ice", "steel"], []),
    "fighting": (["normal", "ice", "rock", "dark", "steel"], ["poison", "flying", "psychic", "bug", "fairy"], ["ghost"]),
    "poison": (["grass", "fairy"], ["poison", "ground", "rock", "ghost"], ["steel"]),
    "ground": (["fire", "electric", "poison", "rock", "steel"], ["grass", "bug"], ["flying"]),
    "flying": (["grass", "fighting", "bug"], ["electric", "rock", "steel"], []),
    "psychic": (["fighting", "poison"], ["psychic", "steel"], ["dark"]),
    "bug": (["grass", "psychic", "dark"], ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"], []),
    "rock": (["fire", "ice", "flying", "bug"], ["fighting", "ground", "steel"], []),
    "ghost": (["psychic", "ghost"], ["dark"], ["normal"]),
    "dragon": (["dragon"], ["steel"], ["fairy"]),
    "dark": (["psychic", "ghost"], ["fighting", "dark", "fairy"], []),
    "steel": (["ice", "rock", "fairy"], ["fire", "water", "electric", "steel"], []),
    "fairy": (["fighting", "dragon", "dark"], ["fire", "poison", "steel"], []),
}

def multiplier(attack, def_types):
    se, nve, imm = CHART[attack]
    m = 1.0
    for d in def_types:
        if d in imm:
            return 0.0
        if d in se:
            m *= 2
        if d in nve:
            m *= 0.5
    return m

def types_of(row):
    ts = [str(row['Type1']).strip().lower()]
    if pd.notna(row['Type2']) and str(row['Type2']).strip():
        ts.append(str(row['Type2']).strip().lower())
    return [t for t in ts if t in CHART]

# ======================= LOAD & CLEAN =======================
playstyle_df = pd.read_csv(PLAYSTYLE_CSV)
roles_df = pd.read_csv(ROLES_CSV)
playstyle_df.columns = [str(c).strip() for c in playstyle_df.columns]
roles_df.columns = [str(c).strip() for c in roles_df.columns]
playstyle_df = playstyle_df.loc[:, ~playstyle_df.columns.str.startswith("Unnamed")]
playstyle_df['Playstyle'] = playstyle_df['Playstyle'].astype(str).str.strip()

# --- Trick Room Setter + base Speed come from the moves CSV (step 1 output) ---
moves_df = pd.read_csv(MOVES_CSV)
moves_df.columns = [str(c).strip() for c in moves_df.columns]
if 'has_trick_room' not in moves_df.columns:
    raise SystemExit("ERROR: has_trick_room not in the moves CSV. Re-run the move categories script first.")

keep_cols = ['Pokemon', 'has_trick_room']
speed_col = next((c for c in SPEED_COL_CANDIDATES if c in roles_df.columns), None)
if speed_col is None:  # pull base Speed from the moves CSV if the roles CSV doesn't have it
    from_moves = next((c for c in SPEED_COL_CANDIDATES if c in moves_df.columns), None)
    if from_moves:
        keep_cols.append(from_moves)
        speed_col = from_moves
moves_df = moves_df[keep_cols].drop_duplicates(subset='Pokemon')

roles_df = roles_df.drop(columns=['Trick Room Setter', 'has_trick_room'], errors='ignore')
roles_df = roles_df.merge(moves_df, on='Pokemon', how='left')
roles_df['Trick Room Setter'] = pd.to_numeric(roles_df['has_trick_room'], errors='coerce').fillna(0).astype(int) == 1

n_setters = int(roles_df['Trick Room Setter'].sum())
print(f"Trick Room setters in dataset: {n_setters}")
if n_setters:
    print("  ", roles_df.loc[roles_df['Trick Room Setter'], 'Pokemon'].tolist())
print("Speed tiers in data:", sorted(roles_df['speed_tier'].astype(str).unique()))
print("Base Speed column:", speed_col if speed_col else "not found (using speed tiers only)")

# --- Playstyle template: Trick Room needs 2 setters unless the CSV already says otherwise ---
if 'Trick Room Setter' not in playstyle_df.columns:
    playstyle_df['Trick Room Setter'] = 0
    playstyle_df.loc[playstyle_df['Playstyle'].str.lower().str.contains('trick room'), 'Trick Room Setter'] = 2

role_columns = [c for c in playstyle_df.columns if c != 'Playstyle']
playstyle_df[role_columns] = playstyle_df[role_columns].fillna(0).astype(int)
role_map = {c: c.replace(" (Remover)", "").strip() for c in role_columns}

def to_bool(s):
    return s.astype(str).str.strip().str.lower().isin(["true", "1", "1.0", "yes"])

for col in set(role_map.values()):
    if col in roles_df.columns:
        roles_df[col] = to_bool(roles_df[col])

roles_df['Usage'] = pd.to_numeric(roles_df['Usage'], errors='coerce').fillna(0)
roles_df['speed_tier'] = roles_df['speed_tier'].astype(str).str.strip()
roles_df = roles_df.drop_duplicates(subset='Pokemon', keep='first').reset_index(drop=True)

pokemon_names = roles_df['Pokemon'].tolist()
name_ids = {n: i for i, n in enumerate(pokemon_names)}
idx = roles_df.set_index('Pokemon')
max_usage = roles_df['Usage'].max() or 1.0

# ======================= HIDE PLAYSTYLES THE DATA CAN'T SUPPORT =======================
def blockers(row):
    out = []
    for rc in role_columns:
        need = int(row[rc])
        col = role_map[rc]
        if need and (col not in roles_df.columns or roles_df[col].sum() < need):
            have = int(roles_df[col].sum()) if col in roles_df.columns else 0
            out.append(f"{rc} (need {need}, have {have})")
    return out

keep_mask = []
for _, r in playstyle_df.iterrows():
    b = blockers(r)
    if b:
        print(f"Hiding '{r['Playstyle']}': {', '.join(b)}")
    keep_mask.append(not b)
playstyle_df = playstyle_df[keep_mask].reset_index(drop=True)
if playstyle_df.empty:
    raise SystemExit("No playstyle can be built with the current data.")

# ======================= INPUTS (5 total) =======================
styles = list(playstyle_df['Playstyle'])
print("\nPlaystyles:")
for i, s in enumerate(styles, 1):
    print(f"  {i}. {s}")
raw = input("Pick a playstyle (number or name): ").strip().lower()
if raw.isdigit() and 1 <= int(raw) <= len(styles):
    playstyle_choice = styles[int(raw) - 1]
else:
    hits = [s for s in styles if raw and raw in s.lower()]
    if len(hits) != 1:
        raise SystemExit("Couldn't match one playstyle. Run again and pick a number.")
    playstyle_choice = hits[0]
comp_row = playstyle_df[playstyle_df['Playstyle'] == playstyle_choice].iloc[0]

anchor_in = input("Build around a Pokemon (blank = none): ").strip().lower()
anchor = next((n for n in pokemon_names if n.lower() == anchor_in), None) if anchor_in else None
if anchor_in and not anchor:
    print(f"  '{anchor_in}' not found, building without one.")

type_in = input("Types you want on the team, comma-separated (blank = any): ").strip()
preferred_types = [t.strip().lower() for t in type_in.split(",") if t.strip()]

print("Team variety:")
for k, (label, _) in VARIETY_LEVELS.items():
    print(f"  {k}. {label}")
v_choice = input("Pick 1-3 [2]: ").strip()
variety = VARIETY_LEVELS.get(v_choice, VARIETY_LEVELS["2"])[1]

n_raw = input("How many teams? [3]: ").strip()
n_teams = min(max(int(n_raw), 1), 10) if n_raw.isdigit() else 3

# ======================= SETUP =======================
required_roles = {}
problems = []
for role_col in role_columns:
    required = int(comp_row[role_col])
    if required == 0:
        continue
    col = role_map[role_col]
    if col not in roles_df.columns:
        problems.append(f"{role_col}: column '{col}' is missing from the data")
        continue
    cands = roles_df.loc[roles_df[col], 'Pokemon'].tolist()
    if len(cands) < required:
        problems.append(f"{role_col}: need {required}, only {len(cands)} available in the data")
        continue
    required_roles[role_col] = (required, cands)

if problems:
    print(f"\nCannot build a valid '{playstyle_choice}' team.\n")
    for p in problems:
        print(f"  - {p}")
    raise SystemExit("\nNo team can satisfy this playstyle with the current data.")
if sum(r for r, _ in required_roles.values()) > 6:
    raise SystemExit("ERROR: this playstyle needs more than 6 role slots.")
role_ids = {rc: j for j, rc in enumerate(required_roles)}

# Speed rule for this playstyle (automatic)
speed_rule = None
for key, rule in SPEED_DEFAULTS.items():
    if key in playstyle_choice.lower():
        lookup = {t.lower(): t for t in roles_df['speed_tier'].unique()}
        tiers = [lookup[t.lower()] for t in rule['tiers'] if t.lower() in lookup]
        if tiers:
            members = roles_df.loc[roles_df['speed_tier'].isin(tiers), 'Pokemon'].tolist()
            speed_rule = (members, rule['min'], rule['max'])
        else:
            print(f"  Note: speed tiers {rule['tiers']} not found in data, so the speed rule is skipped.")
        break

# Anchor synergy: reward teammates that resist the anchor's weaknesses, punish shared ones
synergy = {n: 0.0 for n in pokemon_names}
anchor_weak = []
if anchor:
    a_types = types_of(idx.loc[anchor])
    anchor_weak = [t for t in CHART if multiplier(t, a_types) >= 2]
    for n in pokemon_names:
        if n == anchor or not anchor_weak:
            continue
        n_types = types_of(idx.loc[n])
        score = 0.0
        for w in anchor_weak:
            m = multiplier(w, n_types)
            score += 1.5 if m == 0 else 1.0 if m < 1 else -0.5 if m > 1 else 0.0
        synergy[n] = score / len(anchor_weak)

# Trick Room compatibility from base Speed
speed_score = {n: 0.0 for n in pokemon_names}
if 'trick room' in playstyle_choice.lower():
    if speed_col:
        for n in pokemon_names:
            spe = pd.to_numeric(idx.loc[n, speed_col], errors='coerce')
            speed_score[n] = trick_room_score(spe) if pd.notna(spe) else 0.0
    else:
        print(f"  Note: no base Speed column found (looked for {SPEED_COL_CANDIDATES}), using speed tiers only.")

# ======================= SOLVER =======================
def solve_team(coef, previous, use_speed, loosen, use_diversity):
    m = pl.LpProblem("Team", pl.LpMaximize)
    x = {n: pl.LpVariable(f"x_{name_ids[n]}", cat="Binary") for n in pokemon_names}
    slack, y = {}, {}
    for rc, (required, cands) in required_roles.items():
        slack[rc] = pl.LpVariable(f"s_{role_ids[rc]}", 0, 0 if rc in HARD_ROLES else required, cat="Integer")
        for n in cands:
            y[n, rc] = pl.LpVariable(f"y_{name_ids[n]}_{role_ids[rc]}", cat="Binary")
            m += y[n, rc] <= x[n]
        m += pl.lpSum(y[n, rc] for n in cands) + slack[rc] == required

    m += pl.lpSum(coef[n] * x[n] for n in pokemon_names) - SLACK_PENALTY * pl.lpSum(slack.values())
    m += pl.lpSum(x.values()) == 6
    m += pl.lpSum(slack.values()) <= loosen

    for n in pokemon_names:  # one Pokemon fills at most one role slot
        slots = [y[n, r] for r in required_roles if (n, r) in y]
        if slots:
            m += pl.lpSum(slots) <= 1

    if anchor:
        m += x[anchor] == 1
        own = [y[anchor, r] for r in required_roles if (anchor, r) in y]
        if own:  # the anchor fills one of its roles, so the others cover what it doesn't
            m += pl.lpSum(own) == 1

    if use_speed and speed_rule:
        members, mn, mx = speed_rule
        total = pl.lpSum(x[n] for n in members)
        if mn > 0:
            m += total >= mn
        if mx is not None:
            m += total <= mx

    for ptype in preferred_types:
        cands = roles_df[(roles_df['Type1'].astype(str).str.lower() == ptype) |
                         (roles_df['Type2'].astype(str).str.lower() == ptype)]['Pokemon'].tolist()
        if cands:
            m += pl.lpSum(x[n] for n in cands) >= 1
        else:
            print(f"  Note: no Pokemon of type '{ptype}' in the data, skipping that type.")

    if use_diversity:
        for prev in previous:
            m += pl.lpSum(x[n] for n in prev) <= 6 - MIN_NEW_POKEMON

    m.solve(pl.PULP_CBC_CMD(msg=0))
    if pl.LpStatus[m.status] != "Optimal":
        return None
    team = [n for n in pokemon_names if pl.value(x[n]) > 0.5]
    roles = {n: [rc for rc in required_roles if (n, rc) in y and pl.value(y[n, rc]) > 0.5] for n in team}
    skipped = [rc for rc in required_roles if pl.value(slack[rc]) > 0.5]
    return team, roles, skipped

# Strictest settings first; relax step by step only if no team exists.
# HARD_ROLES are never relaxed.
# (use_speed, role slots allowed open, enforce team differences, note)
LADDER = [
    (True,  0, True,  None),
    (False, 0, True,  "ignored the speed rule"),
    (False, 1, True,  "left one role slot open"),
    (False, 2, True,  "left two role slots open"),
    (False, 2, False, "allowed teams to overlap more"),
]

# ======================= RUN =======================
if anchor:
    print(f"\nBuilding around {anchor}. Its weaknesses: {', '.join(anchor_weak) or 'none'}")

previous = []
for t in range(1, n_teams + 1):
    coef = {n: (idx.loc[n, 'Usage'] / max_usage) ** (1 - 0.8 * variety)
               + variety * random.uniform(0, 0.5)
               + ANCHOR_SYNERGY_WEIGHT * synergy[n]
               + SPEED_SCORE_WEIGHT * speed_score[n]
            for n in pokemon_names}
    result, note = None, None
    for use_speed, loosen, diverse, relax_note in LADDER:
        result = solve_team(coef, previous, use_speed, loosen, diverse)
        if result:
            note = relax_note
            break
    if result is None:
        print(f"\nTeam {t}: couldn't build one. Try fewer type requirements or a different Pokemon.")
        break

    team, roles, skipped = result
    previous.append(team)
    print(f"\n=== Team {t}: {playstyle_choice} ===")
    for n in team:
        r = idx.loc[n]
        t2 = f"/{r['Type2']}" if pd.notna(r['Type2']) else ""
        tag = " (locked)" if n == anchor else ""
        covers = ""
        if anchor and n != anchor:
            res = [w for w in anchor_weak if multiplier(w, types_of(r)) < 1]
            covers = f"  Covers: {', '.join(res)}" if res else ""
        setter = "  [Trick Room]" if r['Trick Room Setter'] else ""
        spe = f"  Spe {int(r[speed_col])}" if speed_col and pd.notna(r[speed_col]) else ""
        print(f"  {n + tag:<20} {str(r['Type1']) + t2:<18} Speed: {r['speed_tier']:<10}{spe} "
              f"Usage {r['Usage']:.1%}  Role: {', '.join(roles[n]) or 'flex'}{setter}{covers}")
    if skipped:
        print(f"  Unfilled roles: {', '.join(skipped)}")
    if note:
        print(f"  Note: to find this team the optimizer {note}.")