"""Cellularena (Winter Challenge 2024) game model plugin."""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .base import GameModel, SimResult


TESTS_DIR = Path(__file__).parent.parent / "tests" / "cellularena"
TRACES_DIR = Path(__file__).parent.parent / "traces" / "cellularena"


@dataclass
class Entity:
    """An entity on the grid."""
    x: int
    y: int
    type: str  # WALL, ROOT, BASIC, A, B, C, D
    owner: int = -1  # 0, 1, 2, 3 for players, -1 for neutral
    organ_id: int = 0
    organ_dir: str = "N"
    organ_parent_id: int = 0
    organ_root_id: int = 0


@dataclass
class State:
    """Current game state."""
    entities: List[Entity]
    proteins: Dict[int, Dict[str, int]]  # {player_id: {A: 10, B: 0, ...}}
    next_organ_id: int
    turn: int = 0


@dataclass
class Environment:
    """Game environment (static)."""
    width: int
    height: int
    num_players: int
    initial_entities: List[Entity]
    initial_proteins: Dict[int, Dict[str, int]]


# Direction vectors for HARVESTER facing
DIR_VECTORS = {
    "N": (0, -1),
    "S": (0, 1),
    "W": (-1, 0),
    "E": (1, 0)
}

# Organ types that are valid
ORGAN_TYPES = {"ROOT", "BASIC", "HARVESTER", "TENTACLE", "SPORER"}


@dataclass
class Control:
    """Player's output command."""
    player_id: int
    action: str  # WAIT, GROW, SPORE
    organ_id: int = 0  # parent organ id for GROW, sporer id for SPORE
    x: int = 0
    y: int = 0
    organ_type: str = "BASIC"
    organ_dir: str = "N"  # Direction for HARVESTER, TENTACLE, SPORER

    @staticmethod
    def parse(line: str, player_id: int = 0) -> 'Control':
        parts = line.strip().upper().split()
        if not parts:
            return Control(player_id=player_id, action="WAIT")

        if parts[0] == "WAIT":
            return Control(player_id=player_id, action="WAIT")
        elif parts[0] == "GROW" and len(parts) >= 5:
            organ_id = int(parts[1])
            x = int(parts[2])
            y = int(parts[3])
            organ_type = parts[4]
            # Direction is optional, defaults to N
            organ_dir = parts[5] if len(parts) >= 6 else "N"
            return Control(
                player_id=player_id,
                action="GROW",
                organ_id=organ_id,
                x=x,
                y=y,
                organ_type=organ_type,
                organ_dir=organ_dir
            )
        elif parts[0] == "SPORE" and len(parts) >= 4:
            organ_id = int(parts[1])  # SPORER id
            x = int(parts[2])
            y = int(parts[3])
            return Control(
                player_id=player_id,
                action="SPORE",
                organ_id=organ_id,
                x=x,
                y=y
            )
        else:
            raise ValueError(f"Invalid command: {line}")


def load_test_cases_from_files() -> dict:
    """Load all test cases from JSON files."""
    test_cases = {}
    if not TESTS_DIR.exists():
        return test_cases

    for json_file in sorted(TESTS_DIR.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            name = json_file.stem
            test_cases[name] = data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load {json_file}: {e}")

    return test_cases


class CellularenaModel(GameModel):
    """Cellularena (Winter Challenge 2024) game model."""

    name = "cellularena"
    description = "Cellularena - Winter Challenge 2024"

    def __init__(self):
        self._test_cases = load_test_cases_from_files()

    def get_test_cases(self) -> dict[str, str]:
        return {name: tc.get("name", name) for name, tc in self._test_cases.items()}

    def load_test_case(self, name: str) -> Tuple[Environment, State]:
        if name not in self._test_cases:
            raise ValueError(f"Unknown test case: {name}. Available: {list(self._test_cases.keys())}")

        tc = self._test_cases[name]
        width = tc["width"]
        height = tc["height"]
        num_players = tc.get("num_players", 2)

        # Parse entities
        entities = []
        max_organ_id = 0
        for e in tc.get("entities", []):
            entity = Entity(
                x=e["x"],
                y=e["y"],
                type=e["type"],
                owner=e.get("owner", -1),
                organ_id=e.get("organId", 0),
                organ_dir=e.get("organDir", "N"),
                organ_parent_id=e.get("organParentId", 0),
                organ_root_id=e.get("organRootId", 0)
            )
            entities.append(entity)
            if entity.organ_id > max_organ_id:
                max_organ_id = entity.organ_id

        # Parse proteins
        proteins = {}
        for player_id in range(num_players):
            pid_str = str(player_id)
            if pid_str in tc.get("proteins", {}):
                proteins[player_id] = tc["proteins"][pid_str].copy()
            else:
                proteins[player_id] = {"A": 10, "B": 0, "C": 0, "D": 0}

        env = Environment(
            width=width,
            height=height,
            num_players=num_players,
            initial_entities=[Entity(
                x=e.x, y=e.y, type=e.type, owner=e.owner,
                organ_id=e.organ_id, organ_dir=e.organ_dir,
                organ_parent_id=e.organ_parent_id, organ_root_id=e.organ_root_id
            ) for e in entities],
            initial_proteins={p: v.copy() for p, v in proteins.items()}
        )

        state = State(
            entities=entities,
            proteins=proteins,
            next_organ_id=max_organ_id + 1,
            turn=0
        )

        return env, state

    def format_init_input(self, env: Environment) -> List[str]:
        """Format initialization input."""
        return [f"{env.width} {env.height}"]

    def format_turn_input(self, state: State, player_id: int = 0) -> str:
        """Format turn input for a specific player."""
        lines = []

        # Entity count
        lines.append(str(len(state.entities)))

        # Entities (swap owner perspective for player)
        for e in state.entities:
            # For player's perspective: 1=me, 0=opponent
            # Remap owner based on player_id
            if e.owner == -1:
                owner = -1  # Neutral (proteins, walls)
            elif e.owner == player_id:
                owner = 1   # My organ
            else:
                owner = 0   # Opponent's organ
            organ_id = e.organ_id if e.organ_id > 0 else 0
            organ_dir = e.organ_dir if e.organ_id > 0 else "X"
            organ_parent = e.organ_parent_id if e.organ_id > 0 else 0
            organ_root = e.organ_root_id if e.organ_id > 0 else 0
            lines.append(f"{e.x} {e.y} {e.type} {owner} {organ_id} {organ_dir} {organ_parent} {organ_root}")

        # My proteins
        my_p = state.proteins.get(player_id, {"A": 0, "B": 0, "C": 0, "D": 0})
        lines.append(f"{my_p['A']} {my_p['B']} {my_p['C']} {my_p['D']}")

        # Opponent proteins (sum of all others, or just the other player for 2-player)
        opp_a, opp_b, opp_c, opp_d = 0, 0, 0, 0
        for pid, p in state.proteins.items():
            if pid != player_id:
                opp_a += p['A']
                opp_b += p['B']
                opp_c += p['C']
                opp_d += p['D']
        lines.append(f"{opp_a} {opp_b} {opp_c} {opp_d}")

        # Required actions count = number of unique organisms for this player
        organism_roots = set()
        for e in state.entities:
            if e.organ_id > 0 and e.type in ORGAN_TYPES and e.owner == player_id:
                organism_roots.add(e.organ_root_id)
        required_actions = max(1, len(organism_roots))
        lines.append(str(required_actions))

        return "\n".join(lines)

    def parse_output(self, line: str) -> Control:
        return Control.parse(line)

    def _get_entity_at(self, entities: List[Entity], x: int, y: int) -> Optional[Entity]:
        """Get entity at position."""
        for e in entities:
            if e.x == x and e.y == y:
                return e
        return None

    def _get_organ_by_id(self, entities: List[Entity], organ_id: int) -> Optional[Entity]:
        """Get organ by ID."""
        for e in entities:
            if e.organ_id == organ_id:
                return e
        return None

    def _is_adjacent(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if two positions are adjacent (4-connectivity)."""
        return abs(x1 - x2) + abs(y1 - y2) == 1

    def _apply_grow(
        self,
        state: State,
        control: Control,
        env: Environment
    ) -> Tuple[State, Optional[str]]:
        """Apply GROW command. Returns (new_state, error_message)."""
        player_id = control.player_id

        # Find parent organ
        parent = self._get_organ_by_id(state.entities, control.organ_id)
        if parent is None:
            return state, f"Parent organ {control.organ_id} not found"
        if parent.owner != player_id:
            return state, f"Parent organ {control.organ_id} not owned by player {player_id}"

        # Check adjacency
        if not self._is_adjacent(parent.x, parent.y, control.x, control.y):
            return state, f"Position ({control.x},{control.y}) not adjacent to parent ({parent.x},{parent.y})"

        # Check bounds
        if control.x < 0 or control.x >= env.width or control.y < 0 or control.y >= env.height:
            return state, f"Position ({control.x},{control.y}) out of bounds"

        # Check target cell
        target = self._get_entity_at(state.entities, control.x, control.y)

        # Can grow on protein sources or empty cells, not on WALL or organs
        absorbed_protein = None
        if target is not None:
            if target.type == "WALL":
                return state, f"Cannot grow on WALL at ({control.x},{control.y})"
            if target.type in ("ROOT", "BASIC", "HARVESTER", "TENTACLE", "SPORER"):
                return state, f"Cannot grow on organ at ({control.x},{control.y})"
            if target.type in ("A", "B", "C", "D"):
                absorbed_protein = target.type

        # Check proteins cost based on organ type
        cost = {"A": 0, "B": 0, "C": 0, "D": 0}
        if control.organ_type == "BASIC":
            cost["A"] = 1
        elif control.organ_type == "HARVESTER":
            cost["C"] = 1
            cost["D"] = 1
        elif control.organ_type == "TENTACLE":
            cost["B"] = 1
            cost["C"] = 1
        elif control.organ_type == "SPORER":
            cost["B"] = 1
            cost["D"] = 1

        player_proteins = state.proteins[player_id]
        for ptype, amount in cost.items():
            if player_proteins.get(ptype, 0) < amount:
                return state, f"Not enough {ptype} protein (need {amount}, have {player_proteins.get(ptype, 0)})"

        # Apply the GROW
        new_entities = [e for e in state.entities]

        # Remove absorbed protein source
        if absorbed_protein:
            new_entities = [e for e in new_entities if not (e.x == control.x and e.y == control.y)]

        # Create new organ with direction
        new_organ = Entity(
            x=control.x,
            y=control.y,
            type=control.organ_type,
            owner=player_id,
            organ_id=state.next_organ_id,
            organ_dir=control.organ_dir,
            organ_parent_id=control.organ_id,
            organ_root_id=parent.organ_root_id
        )
        new_entities.append(new_organ)

        # Update proteins
        new_proteins = {p: v.copy() for p, v in state.proteins.items()}
        for ptype, amount in cost.items():
            new_proteins[player_id][ptype] -= amount

        # Add absorbed protein (+3)
        if absorbed_protein:
            new_proteins[player_id][absorbed_protein] += 3

        new_state = State(
            entities=new_entities,
            proteins=new_proteins,
            next_organ_id=state.next_organ_id + 1,
            turn=state.turn
        )

        return new_state, None

    def _apply_spore(
        self,
        state: State,
        control: Control,
        env: Environment
    ) -> Tuple[State, Optional[str]]:
        """Apply SPORE command. Returns (new_state, error_message)."""
        player_id = control.player_id

        # Find the SPORER organ
        sporer = self._get_organ_by_id(state.entities, control.organ_id)
        if sporer is None:
            return state, f"SPORER {control.organ_id} not found"
        if sporer.owner != player_id:
            return state, f"SPORER {control.organ_id} not owned by player {player_id}"
        if sporer.type != "SPORER":
            return state, f"Organ {control.organ_id} is not a SPORER"

        # Check target is in line of sight
        dx, dy = DIR_VECTORS.get(sporer.organ_dir, (0, 0))
        if dx == 0 and dy == 0:
            return state, f"Invalid SPORER direction"

        # Target must be along the direction
        target_x, target_y = control.x, control.y
        if dx != 0:
            # Horizontal line
            if target_y != sporer.y:
                return state, f"Target ({target_x},{target_y}) not in line of SPORER facing {sporer.organ_dir}"
            if dx > 0 and target_x <= sporer.x:
                return state, f"Target ({target_x},{target_y}) not in front of SPORER"
            if dx < 0 and target_x >= sporer.x:
                return state, f"Target ({target_x},{target_y}) not in front of SPORER"
        else:
            # Vertical line
            if target_x != sporer.x:
                return state, f"Target ({target_x},{target_y}) not in line of SPORER facing {sporer.organ_dir}"
            if dy > 0 and target_y <= sporer.y:
                return state, f"Target ({target_x},{target_y}) not in front of SPORER"
            if dy < 0 and target_y >= sporer.y:
                return state, f"Target ({target_x},{target_y}) not in front of SPORER"

        # Check bounds
        if target_x < 0 or target_x >= env.width or target_y < 0 or target_y >= env.height:
            return state, f"Target ({target_x},{target_y}) out of bounds"

        # Check path is clear (no obstacles between sporer and target, excluding target)
        cx, cy = sporer.x + dx, sporer.y + dy
        while (cx, cy) != (target_x, target_y):
            if cx < 0 or cx >= env.width or cy < 0 or cy >= env.height:
                return state, f"Path to target blocked by bounds"
            blocker = self._get_entity_at(state.entities, cx, cy)
            if blocker is not None and blocker.type not in ("A", "B", "C", "D"):
                return state, f"Path to target blocked at ({cx},{cy})"
            cx += dx
            cy += dy

        # Check target cell is empty or protein
        target = self._get_entity_at(state.entities, target_x, target_y)
        absorbed_protein = None
        if target is not None:
            if target.type == "WALL":
                return state, f"Cannot spore onto WALL at ({target_x},{target_y})"
            if target.type in ORGAN_TYPES:
                return state, f"Cannot spore onto organ at ({target_x},{target_y})"
            if target.type in ("A", "B", "C", "D"):
                absorbed_protein = target.type

        # Check protein cost for ROOT (1A + 1B + 1C + 1D)
        player_proteins = state.proteins[player_id]
        cost = {"A": 1, "B": 1, "C": 1, "D": 1}
        for ptype, amount in cost.items():
            if player_proteins.get(ptype, 0) < amount:
                return state, f"Not enough {ptype} protein for ROOT (need {amount}, have {player_proteins.get(ptype, 0)})"

        # Apply the SPORE
        new_entities = [e for e in state.entities]

        # Remove absorbed protein source
        if absorbed_protein:
            new_entities = [e for e in new_entities if not (e.x == target_x and e.y == target_y)]

        # Create new ROOT (no parent, is its own root)
        new_root = Entity(
            x=target_x,
            y=target_y,
            type="ROOT",
            owner=player_id,
            organ_id=state.next_organ_id,
            organ_dir="N",
            organ_parent_id=0,  # ROOT has no parent
            organ_root_id=state.next_organ_id  # ROOT is its own root
        )
        new_entities.append(new_root)

        # Update proteins
        new_proteins = {p: v.copy() for p, v in state.proteins.items()}
        for ptype, amount in cost.items():
            new_proteins[player_id][ptype] -= amount

        # Add absorbed protein (+3)
        if absorbed_protein:
            new_proteins[player_id][absorbed_protein] += 3

        new_state = State(
            entities=new_entities,
            proteins=new_proteins,
            next_organ_id=state.next_organ_id + 1,
            turn=state.turn
        )

        return new_state, None

    def _apply_tentacle_attacks(self, state: State, env: Environment) -> State:
        """Apply TENTACLE attack phase - TENTACLEs destroy facing enemy organs."""
        # Collect all tentacle attacks
        attacks = []  # list of (attacker_owner, target_x, target_y)

        for e in state.entities:
            if e.type == "TENTACLE" and e.owner >= 0:
                dx, dy = DIR_VECTORS.get(e.organ_dir, (0, 0))
                target_x, target_y = e.x + dx, e.y + dy
                attacks.append((e.owner, target_x, target_y))

        if not attacks:
            return state

        # Find all organs to destroy (attacked organs + their children)
        organs_to_destroy = set()

        for attacker_owner, target_x, target_y in attacks:
            target = self._get_entity_at(state.entities, target_x, target_y)
            if target and target.type in ORGAN_TYPES and target.owner != attacker_owner and target.owner >= 0:
                # Mark this organ and all its children for destruction
                self._mark_organ_tree(state.entities, target.organ_id, organs_to_destroy)

        if not organs_to_destroy:
            return state

        # Remove destroyed organs
        new_entities = [e for e in state.entities if e.organ_id not in organs_to_destroy]

        return State(
            entities=new_entities,
            proteins=state.proteins,
            next_organ_id=state.next_organ_id,
            turn=state.turn
        )

    def _mark_organ_tree(self, entities: List[Entity], organ_id: int, marked: set):
        """Mark an organ and all its children for destruction."""
        marked.add(organ_id)
        # Find all children
        for e in entities:
            if e.organ_parent_id == organ_id and e.organ_id not in marked:
                self._mark_organ_tree(entities, e.organ_id, marked)

    def _apply_harvest(self, state: State, env: Environment) -> State:
        """Apply harvest phase - HARVESTERs collect proteins from facing sources."""
        new_proteins = {p: v.copy() for p, v in state.proteins.items()}

        # Build a set of protein source positions
        protein_sources = {}
        for e in state.entities:
            if e.type in ("A", "B", "C", "D"):
                protein_sources[(e.x, e.y)] = e.type

        # Track which sources each player has already harvested (1 per source per player)
        harvested = {pid: set() for pid in new_proteins.keys()}

        # Process all HARVESTERs
        for e in state.entities:
            if e.type == "HARVESTER" and e.owner >= 0:
                # Get facing direction
                dx, dy = DIR_VECTORS.get(e.organ_dir, (0, 0))
                target_x, target_y = e.x + dx, e.y + dy

                # Check if facing a protein source
                if (target_x, target_y) in protein_sources:
                    ptype = protein_sources[(target_x, target_y)]
                    # Each player gets 1 protein per source per turn (even with multiple harvesters)
                    if (target_x, target_y) not in harvested[e.owner]:
                        new_proteins[e.owner][ptype] += 1
                        harvested[e.owner].add((target_x, target_y))

        return State(
            entities=state.entities,
            proteins=new_proteins,
            next_organ_id=state.next_organ_id,
            turn=state.turn
        )

    def simulate(
        self,
        state: State,
        controls,  # Can be List[Control] or single Control
        env: Environment
    ) -> Tuple[State, SimResult]:
        """Simulate one turn with commands from all players."""
        current_state = state

        # Handle single control (from run_program for single agent testing)
        if not isinstance(controls, list):
            controls = [controls]

        # Phase 1: Collect GROW targets and detect collisions
        grow_targets = {}  # (x, y) -> list of (control, player_id)
        valid_grows = []

        for control in controls:
            if control is None or control.action != "GROW":
                continue

            target_pos = (control.x, control.y)
            if target_pos not in grow_targets:
                grow_targets[target_pos] = []
            grow_targets[target_pos].append(control)

        # Phase 2: Handle collisions - when multiple players grow to same cell, create WALL
        collision_positions = set()
        for pos, grow_controls in grow_targets.items():
            if len(grow_controls) > 1:
                # Collision detected - both fail, WALL appears
                collision_positions.add(pos)
            else:
                valid_grows.append(grow_controls[0])

        # Create WALLs at collision positions
        if collision_positions:
            new_entities = list(current_state.entities)
            for pos in collision_positions:
                # Check if cell is empty (can create wall)
                existing = self._get_entity_at(new_entities, pos[0], pos[1])
                if existing is None:
                    wall = Entity(x=pos[0], y=pos[1], type="WALL", owner=-1)
                    new_entities.append(wall)
            current_state = State(
                entities=new_entities,
                proteins=current_state.proteins,
                next_organ_id=current_state.next_organ_id,
                turn=current_state.turn
            )

        # Phase 3: Apply valid GROW commands
        for control in valid_grows:
            current_state, error = self._apply_grow(current_state, control, env)
            if error:
                # Log error but continue (invalid command = skip)
                pass

        # Phase 3.5: Apply SPORE commands
        for control in controls:
            if control is None or control.action != "SPORE":
                continue
            current_state, error = self._apply_spore(current_state, control, env)
            if error:
                # Log error but continue (invalid command = skip)
                pass

        # Phase 4: Apply harvest phase
        current_state = self._apply_harvest(current_state, env)

        # Phase 5: Apply TENTACLE attacks
        current_state = self._apply_tentacle_attacks(current_state, env)

        # Update turn
        new_state = State(
            entities=current_state.entities,
            proteins=current_state.proteins,
            next_organ_id=current_state.next_organ_id,
            turn=state.turn + 1
        )

        # Check game end conditions
        if new_state.turn >= 100:
            return new_state, SimResult('success', 'Max turns reached')

        # Check if all players did WAIT (no progress)
        all_wait = all(c is None or c.action == "WAIT" for c in controls)
        if all_wait and state.turn > 5:  # Allow at least 5 turns before stopping
            return new_state, SimResult('success', 'No progress - all WAIT')

        return new_state, SimResult('running')

    def format_result(self, state: State) -> str:
        p0_organs = sum(1 for e in state.entities if e.type in ORGAN_TYPES and e.owner == 0)
        p1_organs = sum(1 for e in state.entities if e.type in ORGAN_TYPES and e.owner == 1)
        return f"Turn {state.turn}: P0={p0_organs} organs, P1={p1_organs} organs"

    def get_traces_dir(self):
        return TRACES_DIR

    def get_required_actions(self, state: State, player_id: int = 0) -> int:
        """Return number of actions expected from player each turn."""
        organism_roots = set()
        for e in state.entities:
            if e.organ_id > 0 and e.type in ORGAN_TYPES and e.owner == player_id:
                organism_roots.add(e.organ_root_id)
        return max(1, len(organism_roots))

    def compare_state(self, state: State, expected: dict) -> List[str]:
        """Compare state with expected trace entry."""
        mismatches = []

        # Compare proteins
        exp_proteins = expected.get("proteins", {})
        for pid_str, exp_p in exp_proteins.items():
            pid = int(pid_str)
            actual_p = state.proteins.get(pid, {})
            for ptype in ("A", "B", "C", "D"):
                actual_val = actual_p.get(ptype, 0)
                exp_val = exp_p.get(ptype, 0)
                if actual_val != exp_val:
                    mismatches.append(f"P{pid} {ptype}: got {actual_val}, expected {exp_val}")

        # Compare new organs
        exp_organs = expected.get("new_organs", [])
        for exp_o in exp_organs:
            found = False
            for e in state.entities:
                if (e.x == exp_o["x"] and e.y == exp_o["y"] and
                    e.type == exp_o["type"] and e.owner == exp_o["owner"]):
                    found = True
                    if e.organ_id != exp_o.get("organId", e.organ_id):
                        mismatches.append(f"Organ at ({e.x},{e.y}): id {e.organ_id}, expected {exp_o['organId']}")
                    break
            if not found:
                mismatches.append(f"Expected organ at ({exp_o['x']},{exp_o['y']}) not found")

        return mismatches
