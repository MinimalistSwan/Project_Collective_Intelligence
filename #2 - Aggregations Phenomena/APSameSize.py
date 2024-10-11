from enum import Enum, auto
import pygame as pg
import random
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import numpy as np
import polars as pl
import seaborn as sns
import pandas as pd 

# Define agent states
class State(Enum):
    WANDERING = auto()
    JOINING = auto()
    STILL = auto()
    LEAVING = auto()

@deserialize
@dataclass
class AggregationsConfig(Config):
    t_join: float = 5.0  # Time to join
    t_leave: float = 5.0  # Time to leave
    a = 3 # PARAMETER A
    b = 5 #  PARAMETER B
    delta_time: float = 0.5
    mass: int = 20
    width: int = 800
    height: int = 600

class Cockroach(Agent):
    config: AggregationsConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = 'wander'
        self.join_timer = 0
        self.leave_timer = 0

        self.position = Vector2(random.uniform(0, self.config.width), random.uniform(0, self.config.height))
        self.move = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

    def change_position(self):
        self.there_is_no_escape()

        if self.state == 'wander':
            self.wander()
            self.change_image(0)
        elif self.state == 'join':
            self.join()
            self.change_image(2)
        elif self.state == 'still':
            self.stay_still()
            self.change_image(1)
        elif self.state == 'leave':
            self.leave()
            self.change_image(2)

    def wander(self):
        # Random walk
        self.pos += self.move
        self.move = self.add_randomness(self.move, 0.1)

        # Check if agent enters a site
        if self.in_aggregation_site():
            p_join: float = 0.03 + 0.48*(1 - np.exp(-self.config.a * self.count_neighbors())) # Probability to Join
            if random.random() > p_join:
                self.state = 'join'

    def join(self):
        # Continue walking
        self.pos += self.move

        # Timer to transition to Still state
        self.join_timer += self.config.delta_time
        if self.join_timer >= self.config.t_join:
            self.state = 'still'
            self.join_timer = 0

    def stay_still(self):
        # Stay still
        self.pos = self.pos

        neighbors = self.count_neighbors()
        # print(self.p_leave)
        p_leave: float = np.exp(-((self.config.b) * (self.count_neighbors())))  # Probability to leave
        if random.random() < p_leave:
            #self.move = -self.move  
            self.state = 'leave'

    def leave(self):
        # Continue walking without joining again
        self.pos += self.move

        # Timer to transition to Wandering state
        self.leave_timer += self.config.delta_time
        if self.leave_timer >= self.config.t_leave:
            self.state = 'wander'
            self.leave_timer = 0

    def in_aggregation_site(self):
        sites = [(Vector2(575, 375), 55), (Vector2(175, 375), 75)]  # list of sites with their centers and radii
        for site_center, site_radius in sites:
            if self.pos.distance_to(site_center) < site_radius:
                return True
        return False

    def count_neighbors(self):
        return len(list(self.in_proximity_accuracy()))  # get neighbors

    def add_randomness(self, vector, magnitude):
        random_perturbation = Vector2(random.uniform(-magnitude, magnitude), random.uniform(-magnitude, magnitude))
        new_vector = vector + random_perturbation

        return new_vector.normalize()

class AggregationsSimulation(Simulation):
    config: AggregationsConfig

# Simulation setup
aggregations_simulation = AggregationsSimulation(AggregationsConfig(fps_limit=250))

df = (aggregations_simulation.batch_spawn_agents(50, Cockroach, images=["Assignments/Assignment_1/images/green.png",
                                                                         "Assignments/Assignment_1/images/red.png",
                                                                         "Assignments/Assignment_1/images/white.png"])
      .spawn_site("Assignments/Assignment_1/images/circle_filled_200pxx.png", x=575, y=375)
      .spawn_site("Assignments/Assignment_1/images/circle_filled_200pxx.png", x=175, y=375)
      .run()
      .snapshots.group_by(["frame","image_index"])
      .agg(pl.count("id").alias("agents"))
      .sort(["frame","image_index"])
      )

print(df)

plot = sns.relplot( x=df["frame"]/1000, y=df["agents"], hue=df["image_index"], kind="line")


plot.set(xlabel="Time (s)", ylabel="Number of agents")
plot.savefig("agents.png", dpi=300)

