import sys
from panda3d.core import WindowProperties, LVector3, ClockObject
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from level import Level

# Initialise the globalClock object
globalClock = ClockObject.getGlobalClock()

class Game(ShowBase):
    def __init__(self):
        super().__init__()

        # Set up window title
        self.win_props = WindowProperties()
        self.win_props.setTitle("3D Platformer - Proof of Concept")
        self.win.requestProperties(self.win_props)

        # Load the environment model
        self.environment = self.loader.loadModel("src/assets/models/environment/environment.egg.pz")
        self.environment.reparentTo(self.render)

        # Position the environment
        self.environment.setScale(0.25, 0.25, 0.25)
        self.environment.setPos(-8, 42, 0)

        # Add a simple player character
        self.player = self.loader.loadModel("src/assets/models/player/jack.egg.pz")
        self.player.reparentTo(self.render)
        self.player.setScale(0.5, 0.5, 0.5)
        self.player.setPos(0, 10, 0)

        # Set up basic player controls
        self.accept("arrow_left", self.move_player, [-1])
        self.accept("arrow_right", self.move_player, [1])
        self.accept("arrow_up", self.move_player, [0])

        # Set up player movement variables
        self.player_speed = 5
        self.gravity = -9.8
        self.jump_speed = 15
        self.is_jumping = False
        self.player_velocity = LVector3(0, 0, 0)

        # Update the task manager call
        self.taskMgr.add(self.update, "update")

        # Load the initial level
        self.current_level = Level("environment", self)

    def move_player(self, direction):
        if direction == -1:  # Move left
            self.player_velocity.setX(-self.player_speed)
        elif direction == 1:  # Move right
            self.player_velocity.setX(self.player_speed)
        elif direction == 0:  # Jump
            if not self.is_jumping:
                self.is_jumping = True
                self.player_velocity.setZ(self.jump_speed)

    def update(self, task):
        # Apply gravity
        self.player_velocity.setZ(self.player_velocity.getZ() + self.gravity * globalClock.getDt())

        # Move player
        self.player.setPos(self.player.getPos() + self.player_velocity * globalClock.getDt())

        # Simple ground collision check
        if self.player.getZ() < 0:
            self.player.setZ(0)
            self.is_jumping = False
            self.player_velocity.setZ(0)

        return Task.cont

    def load_level(self, level_name):
        # Cleanup the current level
        if self.current_level:
            self.current_level.cleanup()

        # Load the new level
        self.current_level = Level(level_name, self)

game = Game()
game.run()
