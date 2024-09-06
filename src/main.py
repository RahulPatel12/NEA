from panda3d.core import *
from direct.task import Task
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, radians
from ui_manager import UIManager
from level import Level
from player import Player
import sys

# Get the global clock
globalClock = ClockObject.getGlobalClock()

class Game(ShowBase):
    # --- Configuration Constants ---
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    INITIAL_CAMERA_DISTANCE = 20
    INITIAL_CAMERA_PITCH = 10
    INITIAL_CAMERA_YAW = 0
    CAMERA_SPEED = 0.1
    ZOOM_SPEED = 1
    CAMERA_SMOOTHNESS = 0.1
    MOUSE_SENSITIVITY = 100
    ENVIRONMENT_SCALE = (0.25, 0.25, 0.25)
    ENVIRONMENT_POSITION = (-8, 42, 0)
    BLOCK_POSITIONS = [(2, 10, 0), (4, 15, 0), (6, 20, 0)]
    BLOCK_SCALE = (2, 2, 2)
    AMBIENT_LIGHT_COLOR = Vec4(0.5, 0.5, 0.5, 1)
    DIRECTIONAL_LIGHT_COLOR = Vec4(1, 1, 1, 1)
    DIRECTIONAL_LIGHT_HPR = (0, -60, 0)

    def __init__(self):
        super().__init__()

        # Disable Panda3D's default camera control
        self.disableMouse()

        # Set up collision system
        self.cTrav = CollisionTraverser()  # Create a collision traverser
        self.pusher = CollisionHandlerPusher()  # Create a pusher to handle collisions

        # Set window properties
        props = WindowProperties()
        props.setSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.win.requestProperties(props)

        # Initialize instance variables
        self.camera_distance = self.INITIAL_CAMERA_DISTANCE
        self.camera_pitch = self.INITIAL_CAMERA_PITCH
        self.camera_yaw = self.INITIAL_CAMERA_YAW
        self.camera_speed = self.CAMERA_SPEED
        self.zoom_speed = self.ZOOM_SPEED
        self.smoothness = self.CAMERA_SMOOTHNESS

        self.mouse_sense = self.MOUSE_SENSITIVITY
        self.last_mouse_pos = (0, 0)

        # Load the environment
        self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(*self.ENVIRONMENT_SCALE)
        self.environ.setPos(*self.ENVIRONMENT_POSITION)

        # Create blocks and player
        self.blocks = self.create_blocks()

        # Initialize Player
        self.player = Player(self.render, self.loader, self)

        # Setup camera and collision system
        self.setup_camera()

        # Add tasks
        self.taskMgr.add(self.update, "update")
        self.taskMgr.add(self.update_camera, "update_camera")
        self.taskMgr.add(self.update_mouse, "update_mouse")

        # Set the background color
        self.set_background_color((0.5, 0.5, 1, 1))

        # Set up lights
        self.setup_lights()

        # Set up player controls
        self.player.setup_controls()

        # Initialize UI Manager
        self.ui_manager = UIManager(self)

        # Current Level State
        self.current_level = None

        # Bind the Escape key to quit the game
        self.accept("escape", self.quit_game)

    def load_level(self, level_name):
        """Load the specified level."""
        if self.current_level:
            self.current_level.unload()  # Unload the previous level

        self.current_level = Level(self, level_name)
        self.current_level.load()  # Load the new level

        self.ui_manager.clear_ui()  # Clear the UI after loading the level

    def setup_camera(self):
        """Setup the initial camera position and orientation."""
        self.camera.setPos(self.player.model.getPos() - LVector3f(self.camera_distance, 0, 0))
        self.camera.lookAt(self.player.model)

    def setup_lights(self):
        """Set up ambient and directional lights."""
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(self.AMBIENT_LIGHT_COLOR)
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)

        directional_light = DirectionalLight('directional_light')
        directional_light.setColor(self.DIRECTIONAL_LIGHT_COLOR)
        directional_light_np = self.render.attachNewNode(directional_light)
        directional_light_np.setHpr(*self.DIRECTIONAL_LIGHT_HPR)
        self.render.setLight(directional_light_np)

    def create_blocks(self):
        """Create and return a list of blocks."""
        blocks = []
        for pos in self.BLOCK_POSITIONS:
            block = self.loader.loadModel("models/box")
            block.reparentTo(self.render)
            block.setPos(*pos)
            block.setScale(*self.BLOCK_SCALE)

            # Add collision node for each block
            block_collider = block.attachNewNode(CollisionNode('block_cnode'))
            block_collider.node().addSolid(CollisionBox(Point3(0.5, 0.5, 0.5), 0.5, 0.5, 0.5))
            block_collider.show()  # Show collision geometry for debugging

            blocks.append(block)
        return blocks

    def zoom_in(self):
        """Zoom in by decreasing the camera distance."""
        self.camera_distance = max(5, self.camera_distance - self.zoom_speed)

    def zoom_out(self):
        """Zoom out by increasing the camera distance."""
        self.camera_distance = min(50, self.camera_distance + self.zoom_speed)

    def update_camera(self, task):
        """Update the camera position and orientation based on player position, heading, and pitch."""
        player_pos = self.player.model.getPos()
        player_heading = self.player.model.getH()

        heading_rad = radians(player_heading)
        pitch_rad = radians(self.camera_pitch)

        offset_x = -self.camera_distance * cos(heading_rad) * cos(pitch_rad)
        offset_y = -self.camera_distance * sin(heading_rad) * cos(pitch_rad)
        offset_z = self.camera_distance * sin(pitch_rad)

        camera_pos = LVector3f(player_pos.getX() + offset_x,
                               player_pos.getY() + offset_y,
                               player_pos.getZ() + offset_z + 1.5)

        self.camera.setPos(camera_pos)
        self.camera.lookAt(player_pos + LVector3f(0, 0, 1.5))

        return Task.cont

    def get_camera_vectors(self):
        """Return the forward and right vectors of the camera, flattened to the horizontal plane."""
        camera_forward = self.camera.getQuat().getForward()
        camera_right = self.camera.getQuat().getRight()

        # Flatten the vectors to be parallel to the ground (horizontal plane)
        flattened_forward = LVector3f(camera_forward.getX(), camera_forward.getY(), 0).normalized()
        flattened_right = LVector3f(camera_right.getX(), camera_right.getY(), 0).normalized()

        return flattened_forward, flattened_right

    def update_mouse(self, task):
        """Update camera angles based on mouse movement."""
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()

            if (mouse_x, mouse_y) != self.last_mouse_pos:
                self.camera_yaw -= (mouse_x - self.last_mouse_pos[0]) * self.mouse_sense
                self.camera_pitch -= (mouse_y - self.last_mouse_pos[1]) * self.mouse_sense
                self.camera_pitch = max(min(self.camera_pitch, 89), -89)
                self.last_mouse_pos = (mouse_x, mouse_y)

        return Task.cont

    def update(self, task):
        dt = globalClock.getDt()

        # Update player movement
        self.player.update(dt)

        # Perform collision detection to find surfaces under the player
        self.cTrav.traverse(self.render)

        return Task.cont

    def quit_game(self):
        """Quit the game when the Escape key is pressed."""
        sys.exit()  # Exit the game

game = Game()
game.run()