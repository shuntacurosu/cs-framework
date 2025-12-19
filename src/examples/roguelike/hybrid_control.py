"""
Hybrid-Control Roguelike
- Human: Keyboard input (WASD/Arrows)
- AI/LLM: RDF command file (external process writes to .ttl)

Both use the same Runner.dispatch() - unified interface!
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pyxel

from cs_framework.engine.runner import Runner
from cs_framework.core.yaml_loader import YamlLoader
from cs_framework.logging.logger import RDFLogger
from examples.roguelike.src.concepts.player import Player
from examples.roguelike.src.concepts.monster import Monster
from examples.roguelike.src.concepts.dungeon import Dungeon
from examples.roguelike.src.concepts.item import Item
from examples.roguelike.src.concepts.gamestate import GameState


class HybridControlGame:
    """Game controllable by both human (keyboard) and AI (RDF commands)."""
    
    TILE_SIZE = 8
    
    def __init__(self):
        # Use a fixed command file path
        self.command_file = os.path.abspath("src/examples/roguelike/hybrid_commands.ttl")
        
        # Setup game with RDF logging
        self.logger = RDFLogger("src/examples/roguelike/hybrid_execution.ttl", console_output=False)
        self.runner = Runner(logger=self.logger)
        
        self.dungeon = Dungeon("Dungeon", width=30, height=20)
        self.dungeon.generate({"floor": 1})
        
        player_start = self.dungeon.get_player_start()
        monster_spawns = self.dungeon.get_monster_spawn_positions(2)
        
        self.player = Player("Player", start_x=player_start[0], start_y=player_start[1])
        self.game_state = GameState("GameState")
        
        self.monsters = []
        for i, (mx, my) in enumerate(monster_spawns):
            m = Monster(f"Monster_{i}", monster_id=f"m{i}", monster_type="goblin", x=mx, y=my)
            self.monsters.append(m)
        
        self.runner.register(self.dungeon)
        self.runner.register(self.player)
        self.runner.register(self.game_state)
        for m in self.monsters:
            self.runner.register(m)
        
        self.runner.start()
        self.runner.publish_all_states()

        
        # Track who made the last move
        self.last_controller = "None"
        self.command_count = {"human": 0, "ai": 0}
        
        # Screen
        ds = self.dungeon.get_state_snapshot()
        self.map_width = ds["width"]
        self.map_height = ds["height"]
        
        print(f"\n{'='*60}")
        print("HYBRID CONTROL ROGUELIKE")
        print(f"{'='*60}")
        print(f"Command file: {self.command_file}")
        print("\nControls:")
        print("  Human: WASD or Arrow keys")
        print("  AI: Write to command file")
        print("  Q: Quit")
        print(f"{'='*60}\n")
        
        pyxel.init(self.map_width * self.TILE_SIZE, 
                   self.map_height * self.TILE_SIZE + 40, 
                   title="Hybrid Control Roguelike")
        pyxel.run(self.update, self.draw)
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            return
        
        gs = self.game_state.get_state_snapshot()
        if gs["status"] != "playing":
            return
        
        ps = self.player.get_state_snapshot()
        if not ps["is_alive"]:
            return
        
        action_taken = False
        
        # === Check for HUMAN input (keyboard) ===
        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            dy = -1
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            dy = 1
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            dx = -1
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            dx = 1
        
        if dx != 0 or dy != 0:
            # Human input - check valid move
            new_x = ps["x"] + dx
            new_y = ps["y"] + dy
            tile = self.dungeon.check_tile({"x": new_x, "y": new_y})
            
            if tile != Dungeon.TILE_WALL:
                # Check for monster
                monster = self.get_monster_at(new_x, new_y)
                if monster:
                    self.attack_monster(monster)
                else:
                    self.runner.dispatch(self.player.id, "move", {"dx": dx, "dy": dy})
                
                self.last_controller = "HUMAN"
                self.command_count["human"] += 1
                action_taken = True
        
        # === Check for AI input (RDF commands) ===
        if not action_taken:
            # Manually poll commands to add validation logic
            commands = self.runner.logger.get_pending_commands()
            executed_count = 0
            
            for cmd in commands:
                try:
                    target_name = cmd["target"]
                    action_name = cmd["action"]
                    payload = cmd["payload"]
                    
                    if target_name == "Player" and action_name == "move":
                        # Validate move
                        dx = payload.get("dx", 0)
                        dy = payload.get("dy", 0)
                        
                        new_x = ps["x"] + dx
                        new_y = ps["y"] + dy
                        tile = self.dungeon.check_tile({"x": new_x, "y": new_y})
                        
                        print(f"AI Move Attempt: ({ps['x']},{ps['y']}) -> ({new_x},{new_y}). Tile: {tile} (Wall={Dungeon.TILE_WALL})")

                        if tile != Dungeon.TILE_WALL:
                            # Check monster interactions
                            monster = self.get_monster_at(new_x, new_y)
                            if monster:
                                self.attack_monster(monster)
                            else:
                                self.runner.dispatch(self.player.id, "move", payload)
                            
                            executed_count += 1
                            self.runner.logger.mark_command_done(cmd["uri"])
                        else:
                            # Hit wall - invalid move
                            print(f"  BLOCKED BY WALL at ({new_x}, {new_y})")
                            self.runner.logger.mark_command_done(cmd["uri"], "Hit wall")

                    
                    else:
                        # Other commands (no validation currently implanted)
                        concept = self.runner.get_concept_by_name(target_name)
                        if concept:
                            self.runner.dispatch(concept.id, action_name, payload)
                            executed_count += 1
                            self.runner.logger.mark_command_done(cmd["uri"])
                        else:
                            self.runner.logger.mark_command_done(cmd["uri"], f"Concept {target_name} not found")

                except Exception as e:
                    self.runner.logger.mark_command_done(cmd["uri"], str(e))
            
            if executed_count > 0:
                self.last_controller = "AI"
                self.command_count["ai"] += executed_count
                action_taken = True
        
        # Process monster turns after any action
        if action_taken:
            self.process_monster_turns()
            # Publish state so external agents can see
            self.runner.publish_all_states()

    
    def get_monster_at(self, x, y):
        for m in self.monsters:
            ms = m.get_state_snapshot()
            if ms["is_alive"] and ms["x"] == x and ms["y"] == y:
                return m
        return None
    
    def attack_monster(self, monster):
        ps = self.player.get_state_snapshot()
        self.runner.dispatch(monster.id, "take_damage", {"amount": ps["attack"]})
        self.game_state.add_message({"message": "You attack!"})
    
    def process_monster_turns(self):
        ps = self.player.get_state_snapshot()
        for m in self.monsters:
            ms = m.get_state_snapshot()
            if not ms["is_alive"]:
                continue
            
            # Move towards player
            dx = 1 if ms["x"] < ps["x"] else -1 if ms["x"] > ps["x"] else 0
            dy = 1 if ms["y"] < ps["y"] else -1 if ms["y"] > ps["y"] else 0
            
            if dx != 0 or dy != 0:
                m._state["x"] += dx if dx != 0 else 0
            
            # Attack if adjacent
            ms = m.get_state_snapshot()
            if abs(ms["x"] - ps["x"]) + abs(ms["y"] - ps["y"]) == 1:
                self.runner.dispatch(self.player.id, "take_damage", {"amount": ms["attack"]})
    
    def draw(self):
        pyxel.cls(0)
        
        ds = self.dungeon.get_state_snapshot()
        tiles = ds["tiles"]
        
        # Draw tiles
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                px = x * self.TILE_SIZE
                py = y * self.TILE_SIZE
                
                if tile == Dungeon.TILE_WALL:
                    pyxel.rect(px, py, self.TILE_SIZE, self.TILE_SIZE, 5)
                elif tile == Dungeon.TILE_FLOOR:
                    pyxel.rect(px, py, self.TILE_SIZE, self.TILE_SIZE, 13)
                elif tile == Dungeon.TILE_STAIRS:
                    pyxel.rect(px, py, self.TILE_SIZE, self.TILE_SIZE, 10)
        
        # Draw monsters
        for m in self.monsters:
            ms = m.get_state_snapshot()
            if ms["is_alive"]:
                mx = ms["x"] * self.TILE_SIZE + 1
                my = ms["y"] * self.TILE_SIZE + 1
                pyxel.rect(mx, my, 6, 6, 8)
        
        # Draw player
        ps = self.player.get_state_snapshot()
        px = ps["x"] * self.TILE_SIZE + 1
        py = ps["y"] * self.TILE_SIZE + 1
        pyxel.rect(px, py, 6, 6, 11)
        
        # UI
        ui_y = self.map_height * self.TILE_SIZE
        pyxel.rect(0, ui_y, self.map_width * self.TILE_SIZE, 40, 1)
        
        # HP bar
        hp_pct = ps["hp"] / ps["max_hp"] if ps["max_hp"] > 0 else 0
        pyxel.rect(4, ui_y + 4, 50, 6, 8)
        pyxel.rect(4, ui_y + 4, int(50 * hp_pct), 6, 11)
        pyxel.text(58, ui_y + 4, f"{ps['hp']}/{ps['max_hp']}", 7)
        
        # Stats
        pyxel.text(4, ui_y + 14, f"Pos:({ps['x']},{ps['y']}) Lv:{ps['level']}", 7)
        
        # Controller indicator
        ctrl_color = 11 if self.last_controller == "HUMAN" else 9 if self.last_controller == "AI" else 5
        pyxel.text(4, ui_y + 26, f"Last: {self.last_controller}", ctrl_color)
        pyxel.text(100, ui_y + 26, f"H:{self.command_count['human']} AI:{self.command_count['ai']}", 7)
        
        # Game over
        gs = self.game_state.get_state_snapshot()
        if gs["status"] == "game_over" or not ps["is_alive"]:
            pyxel.text(80, 80, "GAME OVER", 8)


if __name__ == "__main__":
    HybridControlGame()
