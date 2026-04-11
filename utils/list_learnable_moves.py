#!/usr/bin/env python3
"""List each Pokémon's learnable moves by source.

Sources:
- evos_attacks level-up moves up to a max level (default: 5)
- egg moves
- TM/HM moves
- Move tutor moves

Supports both:
- Tk GUI mode with species dropdown (default)
- CLI output for all species via --cli
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_species_names() -> list[str]:
    names_path = ROOT / "data/pokemon/names.asm"
    names: list[str] = []
    in_table = False
    for raw_line in names_path.read_text().splitlines():
        line = raw_line.strip()
        if line.startswith("PokemonNames::"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("assert_table_length"):
            break
        match = re.match(r'dname\s+"([^"]+)"', line)
        if match:
            names.append(match.group(1))
    return names


def parse_base_stats_files() -> list[str]:
    base_stats_path = ROOT / "data/pokemon/base_stats.asm"
    files: list[str] = []
    for raw_line in base_stats_path.read_text().splitlines():
        line = raw_line.strip()
        match = re.match(r'INCLUDE\s+"data/pokemon/base_stats/([^"]+)"', line)
        if match:
            files.append(match.group(1))
    return files


def parse_tmhm_and_tutor_sets() -> tuple[set[str], set[str]]:
    item_constants_path = ROOT / "constants/item_constants.asm"
    tmhm_moves: set[str] = set()
    tutor_moves: set[str] = set()

    for raw_line in item_constants_path.read_text().splitlines():
        line = raw_line.split(";", 1)[0].strip()
        if not line:
            continue

        tmhm_match = re.match(r"add_(?:tm|hm)\s+([A-Z0-9_]+)$", line)
        if tmhm_match:
            tmhm_moves.add(tmhm_match.group(1))
            continue

        tutor_match = re.match(r"add_mt\s+([A-Z0-9_]+)$", line)
        if tutor_match:
            tutor_moves.add(tutor_match.group(1))

    return tmhm_moves, tutor_moves


def parse_evos_attacks_moves(max_level: int) -> tuple[list[str], dict[str, set[str]]]:
    species_labels: list[str] = []
    result: dict[str, set[str]] = {}
    for rel in ("data/pokemon/evos_attacks_kanto.asm", "data/pokemon/evos_attacks_johto.asm"):
        path = ROOT / rel
        lines = path.read_text().splitlines()
        current_label = ""
        in_levelup = False
        for raw_line in lines:
            line = raw_line.split(";", 1)[0].strip()
            if not line:
                continue

            pointer_match = re.match(r"dw\s+([A-Za-z0-9_]+)EvosAttacks$", line)
            if pointer_match:
                species_labels.append(pointer_match.group(1))
                continue

            label_match = re.match(r"^([A-Za-z0-9_]+)EvosAttacks:$", line)
            if label_match:
                current_label = label_match.group(1)
                result[current_label] = set()
                in_levelup = False
                continue

            if not current_label:
                continue

            if line == "db 0":
                if not in_levelup:
                    in_levelup = True
                    continue
                current_label = ""
                in_levelup = False
                continue

            if not in_levelup:
                continue

            move_match = re.match(r"dbw\s+(\d+),\s*([A-Z0-9_]+)$", line)
            if move_match:
                level = int(move_match.group(1))
                if level <= max_level:
                    result[current_label].add(move_match.group(2))

    return species_labels, result


def parse_egg_moves() -> tuple[list[str], dict[str, set[str]]]:
    species_pointers: list[str] = []
    result: dict[str, set[str]] = {}
    for rel in ("data/pokemon/egg_moves_kanto.asm", "data/pokemon/egg_moves_johto.asm"):
        path = ROOT / rel
        lines = path.read_text().splitlines()
        current_label = ""

        for raw_line in lines:
            line = raw_line.split(";", 1)[0].strip()
            if not line:
                continue

            pointer_match = re.match(r"dw\s+([A-Za-z0-9_]+)EggMoves$", line)
            if pointer_match:
                species_pointers.append(pointer_match.group(1))
                continue
            if re.match(r"dw\s+NoEggMoves[12]$", line):
                species_pointers.append("")
                continue

            label_match = re.match(r"^([A-Za-z0-9_]+)EggMoves:$", line)
            if label_match:
                current_label = label_match.group(1)
                if current_label.startswith("NoEggMoves"):
                    current_label = ""
                else:
                    result[current_label] = set()
                continue

            if not current_label:
                continue

            if line == "dw -1":
                current_label = ""
                continue

            move_match = re.match(r"dw\s+([A-Z0-9_]+)$", line)
            if move_match:
                result[current_label].add(move_match.group(1))

    return species_pointers, result


def parse_tmhm_tutor_by_species(
    species_names: list[str], base_stats_files: list[str], tmhm_set: set[str], tutor_set: set[str]
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    tmhm_by_species: dict[str, set[str]] = {}
    tutor_by_species: dict[str, set[str]] = {}

    for species_name, rel_file in zip(species_names, base_stats_files):
        path = ROOT / "data/pokemon/base_stats" / rel_file
        tmhm_by_species[species_name] = set()
        tutor_by_species[species_name] = set()
        for raw_line in path.read_text().splitlines():
            if "tmhm" not in raw_line:
                continue
            code = raw_line.split(";", 1)[0]
            match = re.search(r"\btmhm\b(.*)$", code)
            if not match:
                continue
            moves_str = match.group(1).strip()
            if not moves_str:
                continue
            for raw_move in moves_str.split(","):
                move = raw_move.strip()
                if not move:
                    continue
                if move in tmhm_set:
                    tmhm_by_species[species_name].add(move)
                if move in tutor_set:
                    tutor_by_species[species_name].add(move)
            break

    return tmhm_by_species, tutor_by_species


def format_moves(moves: set[str]) -> str:
    if not moves:
        return "-"
    return ", ".join(sorted(moves))


def load_learnsets(max_level: int) -> list[dict[str, str]]:
    species_names = parse_species_names()
    base_stats_files = parse_base_stats_files()
    if len(species_names) != len(base_stats_files):
        raise RuntimeError(
            f"species/base stats count mismatch: {len(species_names)} names vs {len(base_stats_files)} base stats files"
        )

    tmhm_set, tutor_set = parse_tmhm_and_tutor_sets()
    evos_order, evos_moves = parse_evos_attacks_moves(max_level)
    egg_order, egg_moves = parse_egg_moves()
    tmhm_moves, tutor_moves = parse_tmhm_tutor_by_species(species_names, base_stats_files, tmhm_set, tutor_set)

    if len(species_names) != len(evos_order):
        raise RuntimeError(f"species/evos count mismatch: {len(species_names)} names vs {len(evos_order)} evos pointers")
    if len(species_names) != len(egg_order):
        raise RuntimeError(f"species/egg count mismatch: {len(species_names)} names vs {len(egg_order)} egg pointers")

    rows: list[dict[str, str]] = []
    for idx, species_name in enumerate(species_names):
        evos_key = evos_order[idx]
        egg_key = egg_order[idx]
        rows.append(
            {
                "species": species_name,
                "evos_attacks": format_moves(evos_moves.get(evos_key, set())),
                "egg_moves": format_moves(egg_moves.get(egg_key, set())),
                "tmhm": format_moves(tmhm_moves.get(species_name, set())),
                "move_tutor": format_moves(tutor_moves.get(species_name, set())),
            }
        )
    return rows


def to_move_list(moves: str) -> list[str]:
    if moves == "-":
        return []
    return [move.strip() for move in moves.split(",")]


def run_gui(rows: list[dict[str, str]], max_level: int) -> int:
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError as exc:
        raise RuntimeError("Tkinter is required for --gui mode.") from exc

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        raise RuntimeError("Unable to start GUI (no display available).") from exc
    root.title("Pokémon Learnable Move Browser")
    root.geometry("1150x700")

    frame = ttk.Frame(root, padding=12)
    frame.pack(fill=tk.BOTH, expand=True)

    header = ttk.LabelFrame(frame, text="Selection", padding=10)
    header.pack(fill=tk.X, pady=(0, 10))
    ttk.Label(header, text="Species:").grid(row=0, column=0, sticky=tk.W)
    species_var = tk.StringVar(value=rows[0]["species"])
    dropdown = ttk.Combobox(
        header, textvariable=species_var, values=[row["species"] for row in rows], state="readonly", width=40
    )
    dropdown.grid(row=0, column=1, sticky=tk.W, padx=(8, 20))
    ttk.Label(header, text=f"Level cap for evos_attacks: {max_level}").grid(row=0, column=2, sticky=tk.W)

    body = ttk.Frame(frame)
    body.pack(fill=tk.BOTH, expand=True)
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)
    body.rowconfigure(0, weight=1)
    body.rowconfigure(1, weight=1)

    fields = [
        (f"evos_attacks (<=L{max_level})", "evos_attacks", 0, 0),
        ("egg_moves", "egg_moves", 0, 1),
        ("tmhm", "tmhm", 1, 0),
        ("move_tutor", "move_tutor", 1, 1),
    ]
    listboxes: dict[str, tk.Listbox] = {}

    for title, key, r, c in fields:
        box_frame = ttk.LabelFrame(body, text=title, padding=8)
        box_frame.grid(row=r, column=c, sticky=tk.NSEW, padx=4, pady=4)
        box_frame.rowconfigure(0, weight=1)
        box_frame.columnconfigure(0, weight=1)

        listbox = tk.Listbox(box_frame, exportselection=False)
        listbox.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar = ttk.Scrollbar(box_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        listbox.configure(yscrollcommand=scrollbar.set)
        listboxes[key] = listbox

    row_by_species = {row["species"]: row for row in rows}

    def refresh_view(*_args: object) -> None:
        species = species_var.get()
        row = row_by_species[species]
        for key, listbox in listboxes.items():
            listbox.delete(0, tk.END)
            move_list = to_move_list(row[key])
            if not move_list:
                listbox.insert(tk.END, "(none)")
                continue
            for move in move_list:
                listbox.insert(tk.END, move)

    dropdown.bind("<<ComboboxSelected>>", refresh_view)
    refresh_view()
    root.mainloop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-level",
        type=int,
        default=5,
        help="Maximum level from evos_attacks level-up list to include (default: 5)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--gui",
        action="store_true",
        help="Launch GUI mode (default if no mode flag is provided).",
    )
    mode.add_argument(
        "--cli",
        action="store_true",
        help="Print all species to terminal.",
    )
    args = parser.parse_args()

    rows = load_learnsets(args.max_level)
    if args.cli:
        for row in rows:
            print(row["species"])
            print(f"  evos_attacks(<=L{args.max_level}): {row['evos_attacks']}")
            print(f"  egg_moves: {row['egg_moves']}")
            print(f"  tmhm: {row['tmhm']}")
            print(f"  move_tutor: {row['move_tutor']}")
        return 0

    return run_gui(rows, args.max_level)


if __name__ == "__main__":
    raise SystemExit(main())
