"""
AI Agent playing the Roguelike game using C-S Framework
Demonstrates LLM-driven gameplay without GUI
"""
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from examples.roguelike.run import get_runner
from examples.roguelike.src.concepts.dungeon import Dungeon


class RoguelikeAIPlayer:
    """AI agent that plays the roguelike game."""
    
    def __init__(self, max_turns: int = 50):
        self.runner = get_runner()
        self.runner.start()
        
        self.dungeon = self.runner.get_concept_by_name("Dungeon")
        self.player = self.runner.get_concept_by_name("Player")
        self.game_state = self.runner.get_concept_by_name("GameState")
        self.item_manager = self.runner.get_concept_by_name("ItemManager")
        
        self.monsters = []
        for concept in self.runner.concepts.values():
            if concept.name.startswith("Monster_"):
                self.monsters.append(concept)
        
        self.max_turns = max_turns
        
    def get_game_state_text(self) -> str:
        """Get a text representation of the current game state for the AI."""
        player_state = self.player.get_state_snapshot()
        dungeon_state = self.dungeon.get_state_snapshot()
        game_state = self.game_state.get_state_snapshot()
        
        # Find nearby tiles
        px, py = player_state["x"], player_state["y"]
        
        # Get visible area (5x5 around player)
        visible = []
        for dy in range(-2, 3):
            row = []
            for dx in range(-2, 3):
                x, y = px + dx, py + dy
                if 0 <= x < dungeon_state["width"] and 0 <= y < dungeon_state["height"]:
                    tile = dungeon_state["tiles"][y][x]
                    char = "#" if tile == Dungeon.TILE_WALL else "." if tile == Dungeon.TILE_FLOOR else ">"
                    
                    # Check for entities at this position
                    if dx == 0 and dy == 0:
                        char = "@"  # Player
                    else:
                        for m in self.monsters:
                            ms = m.get_state_snapshot()
                            if ms["is_alive"] and ms["x"] == x and ms["y"] == y:
                                char = ms["char"]
                    row.append(char)
                else:
                    row.append("#")
            visible.append("".join(row))
        
        # Find monsters
        monster_info = []
        for m in self.monsters:
            ms = m.get_state_snapshot()
            if ms["is_alive"]:
                dist = abs(ms["x"] - px) + abs(ms["y"] - py)
                monster_info.append(f"{ms['monster_type']} at ({ms['x']},{ms['y']}), HP:{ms['hp']}, distance:{dist}")
        
        # Build state text
        state_text = f"""
=== GAME STATE ===
Turn: {game_state['turn']} | Floor: {game_state['floor']}
Player: HP {player_state['hp']}/{player_state['max_hp']} | Lv {player_state['level']} | ATK {player_state['attack']} | DEF {player_state['defense']}
Position: ({px}, {py})

Visible Area (@ = you, # = wall, . = floor, > = stairs, g/O/T = monsters):
{chr(10).join(visible)}

Monsters:
{chr(10).join(monster_info) if monster_info else "None visible"}

Available Actions:
- move_up: Move north (dy=-1)
- move_down: Move south (dy=+1)  
- move_left: Move west (dx=-1)
- move_right: Move east (dx=+1)
- attack_up/down/left/right: Attack in that direction
- wait: Do nothing
"""
        return state_text
    
    def decide_action(self) -> tuple:
        """
        Simple AI logic to decide the next action.
        Returns (action, dx, dy, attack)
        """
        player_state = self.player.get_state_snapshot()
        px, py = player_state["x"], player_state["y"]
        
        # Check for adjacent monsters
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            for m in self.monsters:
                ms = m.get_state_snapshot()
                if ms["is_alive"] and ms["x"] == px + dx and ms["y"] == py + dy:
                    return ("attack", dx, dy, m)
        
        # Find nearest monster and move towards it
        nearest_monster = None
        nearest_dist = float('inf')
        for m in self.monsters:
            ms = m.get_state_snapshot()
            if ms["is_alive"]:
                dist = abs(ms["x"] - px) + abs(ms["y"] - py)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_monster = m
        
        if nearest_monster:
            ms = nearest_monster.get_state_snapshot()
            dx = 1 if ms["x"] > px else -1 if ms["x"] < px else 0
            dy = 1 if ms["y"] > py else -1 if ms["y"] < py else 0
            
            # Try to move in one direction
            if dx != 0:
                tile = self.dungeon.check_tile({"x": px + dx, "y": py})
                if tile != Dungeon.TILE_WALL:
                    return ("move", dx, 0, None)
            if dy != 0:
                tile = self.dungeon.check_tile({"x": px, "y": py + dy})
                if tile != Dungeon.TILE_WALL:
                    return ("move", 0, dy, None)
        
        # Random exploration if no monsters
        import random
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            tile = self.dungeon.check_tile({"x": px + dx, "y": py + dy})
            if tile != Dungeon.TILE_WALL:
                return ("move", dx, dy, None)
        
        return ("wait", 0, 0, None)
    
    def execute_action(self, action: str, dx: int, dy: int, target=None):
        """Execute the decided action."""
        player_state = self.player.get_state_snapshot()
        
        if action == "attack" and target:
            self.runner.dispatch(target.id, "take_damage", {
                "amount": player_state["attack"]
            })
            ms = target.get_state_snapshot()
            print(f"  -> Attacked {ms['monster_type']}!")
        elif action == "move":
            self.runner.dispatch(self.player.id, "move", {"dx": dx, "dy": dy})
            print(f"  -> Moved ({dx}, {dy})")
        else:
            print(f"  -> Waited")
        
        # Process turn
        self.runner.dispatch(self.game_state.id, "next_turn", {})
        
        # Monster turns
        player_state = self.player.get_state_snapshot()
        for m in self.monsters:
            ms = m.get_state_snapshot()
            if not ms["is_alive"]:
                continue
            
            # Move towards player
            self.runner.dispatch(m.id, "ai_move", {
                "target_x": player_state["x"],
                "target_y": player_state["y"]
            })
            
            # Check if adjacent and attack
            ms = m.get_state_snapshot()
            if abs(ms["x"] - player_state["x"]) + abs(ms["y"] - player_state["y"]) == 1:
                self.runner.dispatch(self.player.id, "take_damage", {"amount": ms["attack"]})
                print(f"  <- {ms['monster_type']} attacks!")
    
    def play(self):
        """Run the AI player."""
        print("="*50)
        print("CSFW Roguelike - AI Player Demo")
        print("="*50)
        
        turn = 0
        while turn < self.max_turns:
            gs = self.game_state.get_state_snapshot()
            ps = self.player.get_state_snapshot()
            
            if gs["status"] != "playing":
                if gs["status"] == "game_over":
                    print("\n*** GAME OVER ***")
                else:
                    print("\n*** VICTORY ***")
                break
            
            if not ps["is_alive"]:
                print("\n*** PLAYER DIED ***")
                break
            
            # Check if all monsters dead
            alive_monsters = [m for m in self.monsters if m.get_state_snapshot()["is_alive"]]
            if not alive_monsters:
                print("\n*** ALL MONSTERS DEFEATED ***")
                break
            
            print(f"\n--- Turn {turn + 1} ---")
            print(f"HP: {ps['hp']}/{ps['max_hp']} | Pos: ({ps['x']}, {ps['y']})")
            
            # Decide and execute action
            action, dx, dy, target = self.decide_action()
            self.execute_action(action, dx, dy, target)
            
            turn += 1
        
        print("\n" + "="*50)
        print(f"Game ended after {turn} turns")
        final_ps = self.player.get_state_snapshot()
        print(f"Final HP: {final_ps['hp']}/{final_ps['max_hp']}")
        print(f"Level: {final_ps['level']}")


if __name__ == "__main__":
    ai_player = RoguelikeAIPlayer(max_turns=100)
    ai_player.play()
