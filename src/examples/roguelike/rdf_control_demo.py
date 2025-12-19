"""
Demo: LLM controlling the Roguelike game via RDF/SPARQL interface

This demonstrates how an external agent (LLM) can:
1. Read game state from RDF graph
2. Write commands to RDF graph  
3. Runner executes commands and updates state

Architecture:
    [LLM/External Agent] <--SPARQL--> [RDF Graph] <---> [Runner/Game]
"""
import sys
import os
import threading
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from examples.roguelike.run import get_runner
from examples.roguelike.src.concepts.dungeon import Dungeon


def run_game_with_external_control():
    """Run the roguelike game with external RDF command interface."""
    print("="*60)
    print("CSFW Roguelike - RDF Command Interface Demo")
    print("="*60)
    
    runner = get_runner()
    runner.start()
    
    # Get initial state
    player = runner.get_concept_by_name("Player")
    dungeon = runner.get_concept_by_name("Dungeon")
    game_state = runner.get_concept_by_name("GameState")
    
    # Publish initial state
    runner.publish_all_states()
    
    print(f"\nGame started!")
    print(f"Player position: ({player.get_state_snapshot()['x']}, {player.get_state_snapshot()['y']})")
    print(f"\nCommand file: {runner.logger.command_file}")
    print("\nYou can now add commands to the RDF graph!")
    print("Example command (in the .ttl file):")
    print('''
@prefix cs: <http://cs-framework.org/schema/> .

cs:cmd_test a cs:Command ;
    cs:hasAction "move" ;
    cs:hasTarget "Player" ;
    cs:hasPayload "{\\"dx\\": 1, \\"dy\\": 0}" ;
    cs:commandStatus "pending" .
''')
    
    # Simulate LLM adding commands programmatically
    print("\n--- Simulating LLM adding commands ---")
    
    # Add some test commands
    cmd1 = runner.logger.add_command("move", "Player", {"dx": 1, "dy": 0})
    print(f"Added command: {cmd1}")
    
    cmd2 = runner.logger.add_command("move", "Player", {"dx": 0, "dy": 1})
    print(f"Added command: {cmd2}")
    
    cmd3 = runner.logger.add_command("move", "Player", {"dx": 1, "dy": 0})
    print(f"Added command: {cmd3}")
    
    # Process commands
    print("\n--- Processing commands ---")
    
    for i in range(5):
        executed = runner.poll_and_execute_commands()
        
        # Update state
        runner.publish_all_states()
        
        ps = player.get_state_snapshot()
        print(f"Tick {i+1}: Player at ({ps['x']}, {ps['y']}), HP: {ps['hp']}/{ps['max_hp']}")
        
        if executed == 0:
            break
        
        time.sleep(0.1)
    
    print("\n--- Final State ---")
    ps = player.get_state_snapshot()
    print(f"Player: x={ps['x']}, y={ps['y']}, HP={ps['hp']}/{ps['max_hp']}, Level={ps['level']}")
    
    print("\n--- Checking command statuses ---")
    # Read the command graph to show what happened
    for s, p, o in runner.logger.command_graph.triples((None, None, None)):
        if "commandStatus" in str(p):
            print(f"  {s.split('/')[-1]}: {o}")


def demonstrate_sparql_queries():
    """Show how LLM can query game state via SPARQL."""
    print("\n" + "="*60)
    print("SPARQL Query Examples")
    print("="*60)
    
    print("""
# Query current game state:
PREFIX cs: <http://cs-framework.org/schema/>
SELECT ?concept ?state WHERE {
    ?s a cs:ConceptState ;
       cs:hasName ?concept ;
       cs:hasState ?state .
}

# Query pending commands:
PREFIX cs: <http://cs-framework.org/schema/>
SELECT ?cmd ?action ?target WHERE {
    ?cmd a cs:Command ;
         cs:commandStatus "pending" ;
         cs:hasAction ?action ;
         cs:hasTarget ?target .
}

# Query command history:
PREFIX cs: <http://cs-framework.org/schema/>
SELECT ?cmd ?status ?processed WHERE {
    ?cmd a cs:Command ;
         cs:commandStatus ?status .
    OPTIONAL { ?cmd cs:processedAt ?processed }
}
""")


if __name__ == "__main__":
    run_game_with_external_control()
    demonstrate_sparql_queries()
