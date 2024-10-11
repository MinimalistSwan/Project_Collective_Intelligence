from enum import Enum, auto
import pygame as pg
import random
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    # You can change these for different starting weights
    alignment_weight: float = 1.0
    cohesion_weight: float = 0.5
    separation_weight: float = 0.6

    # These should be left as is.
    delta_time: float = 0.5                                   # To learn more https://gafferongames.com/post/integration_basics/ 
    mass: int = 20                                            

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)



class Bird(Agent):
    config: FlockingConfig

    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        
        #YOUR CODE HERE -----------
        # Checking neighbors within radius R.
        if not hasattr(self, 'move_initialized'):
            self.move = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 2
            self.move_initialized = True
        neighbors = list(self.in_proximity_accuracy())  # retrieves agents in the given radius

        # Calculate alignment, cohesion, and separation forces
        alignment = self.calculate_alignment(neighbors)
        separation = self.calculate_separation(neighbors)
        cohesion = self.calculate_cohesion(neighbors)

        f_total = (alignment + separation + cohesion)

        # Apply the total force to the bird's movement (task 7)
        self.move += f_total/self.config.mass

        # Clamp the movement to the maximum speed if necessary (task 8)
        if self.move.length() > self.config.movement_speed:
            self.move.scale_to_length(self.config.movement_speed)

        # Move the bird based on the accumulated forces (task 9)
        self.pos += self.move * self.config.delta_time


        if 0 < len(neighbors) <= 5:
            self.change_image(2)
        elif len(neighbors) > 5:
            self.change_image(1)
        else:
            self.change_image(0)
            

    def calculate_alignment(self, neighbors):
        alignment_force = Vector2(0, 0)
        if not neighbors:
            return alignment_force
        n_count = 0

        # Sum the velocities of all neighbors
        for neighbor, dist in self.in_proximity_accuracy():
            if neighbor is not self and dist < self.config.radius:
                alignment_force += neighbor.move.normalize()
                n_count += 1
            
        if n_count > 0:
        # Calculate alignment force
            alignment_force /= n_count
            alignment_force = alignment_force.normalize() * self.config.movement_speed
            alignment_force -= self.move
            alignment_force.scale_to_length(self.config.movement_speed) 
            alignment_force = alignment_force * self.config.alignment_weight

        return alignment_force
    
    def calculate_separation(self, neighbors):
        separation_force = Vector2(0, 0)
        n_count = 0

        if not neighbors:
            return separation_force
        
        # Sum vector differences to all neighbors
        for neighbor, dist in self.in_proximity_accuracy():
            if neighbor is not self and dist < self.config.radius:
                n_force = self.pos - neighbor.pos
                n_force /= (dist ** 2)
                separation_force += n_force
                n_count += 1
        
        # Calculate Separation Force
        if n_count > 0:
            separation_force /= n_count
            separation_force = separation_force.normalize() * self.config.movement_speed
            separation_force -= self.move
            separation_force.scale_to_length(self.config.movement_speed)
            separation_force = separation_force * self.config.separation_weight

        return separation_force
    
    def calculate_cohesion(self, neighbors):
        cohesion_force = Vector2(0, 0)
        n_count = 0

        if not neighbors:
            return cohesion_force
        
        # Sum positions of all neighbors
        for neighbor, dist in self.in_proximity_accuracy():
            if neighbor is not self and dist < self.config.radius:
                cohesion_force += neighbor.pos
                n_count += 1

        # Calculate cohesion force
        if n_count > 0:
            cohesion_force /= n_count
            cohesion_force -= self.pos
            cohesion_force = cohesion_force.normalize() * self.config.movement_speed
            cohesion_force -= self.move
            cohesion_force = cohesion_force * self.config.cohesion_weight

        return cohesion_force

        #END CODE -----------------


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=5,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["Assignments/Assignment_0/images/bird.png",
                                          "Assignments/Assignment_0/images/red-bird.png",
                                          "Assignments/Assignment_0/images/green-bird.png"])
    # .spawn_obstacle("Assignments/Assignment_0/images/triangle@200px.png", x=500 , y= 500)
    .run()
)
