from enum import Enum, auto
import pygame as pg
import random
from pygame.math import Vector2
from vi import Agent, Simulation, HeadlessSimulation
from vi.config import Config, dataclass, deserialize
import matplotlib.pyplot as plt
import pandas as pd
import os

@deserialize
@dataclass
class CompetitionConfig(Config):
    sleeper: int = 1
    init_foxes: int = 25                         # Starting amount of foxes
    init_rabbits: int = 50                       # Starting amount of rabbitsx

    width: int = 800
    height: int = 800
    radius: int = 25                             # Proximity radius
    movement_speed: float = 1                    # Movement speed for agents
    mass: int = 20  

    delta_time: float = 1 / 60                   # Time step for the simulation
    image_rotation: bool = True                  # Enable image rotation for agents
    
    rabbit_birth_rate: float = 0.2               # Natural birth rate of rabbits per time step
    fox_natural_death_rate: float = 0.06         # Natural death rate of foxes per time step
    predation_rate: float = 0.12                 # Rate at which foxes catch rabbits per time step
    fox_reproduction_rate: float = 0.08          # Reproduction rate of foxes per caught rabbit

    alignment_weight: float = 1.0
    cohesion_weight: float = 0.5
    separation_weight: float = 0.6

class Foxes(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        self.move = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.movement_speed

    def update(self):
        # Movement
        self.pos += self.move
        self.move = self.add_randomness(self.move, 0.1)

        # Natural death
        if random.random() < self.config.fox_natural_death_rate * self.config.delta_time:
            self.kill()

        # Look for rabbits in close proximity
        rabbits_in_proximity = self.in_proximity_accuracy().filter_kind(Rabbits).first()
        if rabbits_in_proximity:
            rabbit, distance = rabbits_in_proximity

            # Check for predation chance
            if random.random() < self.config.predation_rate:
                rabbit.kill()

                # Reproduce based on predation
                if random.random() < self.config.fox_reproduction_rate:
                    self.reproduce()

        self.save_data("Type", "Fox")

    def add_randomness(self, vector, magnitude):
        random_perturbation = Vector2(random.uniform(-magnitude, magnitude), random.uniform(-magnitude, magnitude))
        new_vector = vector + random_perturbation
        return new_vector.normalize() * self.config.movement_speed

class Rabbits(Agent):
    config: CompetitionConfig

    def on_spawn(self):
        self.move = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.movement_speed

    def update(self):
        # Check for neighbors
        neighbors = list(self.in_proximity_accuracy().filter_kind(Rabbits))
        if neighbors:
            # Flocking behavior
            alignment = self.alignment(neighbors) * self.config.alignment_weight
            cohesion = self.cohesion(neighbors) * self.config.cohesion_weight
            separation = self.separation(neighbors) * self.config.separation_weight

            # Combine the behaviors
            flocking_vector = alignment + cohesion + separation

            # Apply the flocking vector to movement
            self.move = self.add_randomness(flocking_vector, 0.1)
        else:
            # Random movement
            self.move = self.add_randomness(self.move, 0.1)

        # Update position
        self.pos += self.move

        # Natural birth rate
        if random.random() < self.config.rabbit_birth_rate * self.config.delta_time:
            self.reproduce()

        self.save_data("Type", "Rabbit")

    def alignment(self, neighbors):
        avg_heading = sum((neighbor.move for neighbor, _ in neighbors), Vector2(0, 0))
        if avg_heading.length() == 0:
            return Vector2(0, 0)
        return avg_heading.normalize() * self.config.movement_speed

    def cohesion(self, neighbors):
        avg_position = sum((neighbor.pos for neighbor, _ in neighbors), Vector2(0, 0))
        avg_position /= len(neighbors)
        cohesion_vector = avg_position - self.pos
        if cohesion_vector.length() == 0:
            return Vector2(0, 0)
        return cohesion_vector.normalize() * self.config.movement_speed

    def separation(self, neighbors):
        separation_vector = sum((self.pos - neighbor.pos for neighbor, _ in neighbors), Vector2(0, 0))
        if separation_vector.length() == 0:
            return Vector2(0, 0)
        return separation_vector.normalize() * self.config.movement_speed

    def add_randomness(self, vector, magnitude):
        random_perturbation = Vector2(random.uniform(-magnitude, magnitude), random.uniform(-magnitude, magnitude))
        new_vector = vector + random_perturbation
        if new_vector.length() == 0:
            return Vector2(0, 0)
        return new_vector.normalize() * self.config.movement_speed
    
# Invisible agent to ensure data being saved until the final frame    
class Sleeper(Agent):

    def on_spawn(self):
        # Place the Sleeper agent in the middle of the simulation area
        self.pos = Vector2(self.config.width / 2, self.config.height / 2)
    
    def update(self):
        # Sleeper does nothing, remains inactive
    
        self.save_data("Type", "Sleeper")

class LotkaVolterra(Simulation):
    config: CompetitionConfig

# Set up the simulation with our custom configuration
config = CompetitionConfig(duration=60*120, fps_limit=600000)

# Run the simulation n times
for i in range(1, 11):
    print(f"Running simulation {i}")
    simulation = HeadlessSimulation(config)
    #simulation = LotkaVolterra(config)

    simulation.batch_spawn_agents(simulation.config.init_foxes, Foxes, ["Assignments/Assignment_2/images/red-bird.png"])
    simulation.batch_spawn_agents(simulation.config.init_rabbits, Rabbits, ["Assignments/Assignment_2/images/green-bird.png"])

    # To Ensure that no DataFrame Errors appear
    simulation.batch_spawn_agents(simulation.config.sleeper, Sleeper, ["Assignments/Assignment_2/images/invis_agent.png"])

    df = simulation.run()

    # Ensure the directory exists before writing the file
    output_dir = "Assignments/Assignment_2/EneaEnergyFreeFlocking"
    os.makedirs(output_dir, exist_ok=True)

    # Construct the filename based on the iteration number
    csv_filename = os.path.join(output_dir, f"DataTest_{i}.csv")

    # Write the DataFrame to CSV
    df.snapshots.write_csv(csv_filename)

    # Optionally, read and process the data if needed
    # df = pd.read_csv(csv_filename)

    print(f"Simulation {i} completed and data saved to {csv_filename}")

print("All simulations completed")
