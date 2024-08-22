from panda3d.core import (AmbientLight, DirectionalLight, Vec4, WindowProperties,
                          CollisionTraverser, CollisionHandlerPusher, CollisionNode, CollisionSphere,
                          NodePath, ClockObject, BitMask32, LVector3f)
from direct.task import Task
from direct.showbase.ShowBase import ShowBase
from math import sin, cos, radians

# Get the global clock
globalClock = ClockObject.getGlobalClock()

class Game(ShowBase):
    def __init__(self):
        super().__init__()

        # Disable Panda3D's default camera control
        self.disableMouse()

        # Set window properties
        props = WindowProperties()
        props.setSize(800, 600)
        self.win.requestProperties(props)

        # Initialize instance variables
        self.camera_distance = 20  # Initial camera distance from player
        self.camera_pitch = 10  # Initial vertical angle of the camera
        self.camera_yaw = 0  # Initial horizontal angle of the camera
        self.camera_speed = 0.1  # Speed of mouse look
        self.zoom_speed = 1  # Speed of zooming
        self.smoothness = 0.1  # Smoothness of camera movement

        self.forward_move = 0
        self.side_move = 0
        self.velocity = 10
        self.jumping = False
        self.gravity = -9.8
        self.vertical_velocity = 0

        self.mouse_sense = 50  # Sensitivity for mouse movement
        self.last_mouse_pos = (0, 0)  # Track previous mouse position

        # Load the environment
        self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        # Initialize collision handling
        self.collision_traverser = CollisionTraverser()
        self.collision_handler = CollisionHandlerPusher()

        # Create blocks and player
        self.blocks = self.create_blocks()
        self.player = self.create_player()

        # Set the gravity and jump speed values
        self.gravity = -30  # Increase this value for faster falling
        self.jump_velocity = 15  # Adjust this value for jump height

        # Setup collisions
        self.setup_collisions()

        # Setup the camera
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
        self.setup_controls()

    def setup_camera(self):
        """Setup the initial camera position and orientation."""
        # Set the camera's position
        self.camera.setPos(self.player.getPos() - LVector3f(self.camera_distance, 0, 0))
        # Make the camera look at the player
        self.camera.lookAt(self.player)

    def setup_controls(self):
        """Set up player controls."""
        self.accept("a", self.start_move_left)
        self.accept("d", self.start_move_right)
        self.accept("w", self.start_move_forward)
        self.accept("s", self.start_move_backward)
        self.accept("space", self.jump)
        self.accept("wheel_up", self.zoom_in)  # Mouse wheel up for zoom in
        self.accept("wheel_down", self.zoom_out)  # Mouse wheel down for zoom out

        self.accept("a-up", self.stop_move_left)
        self.accept("d-up", self.stop_move_right)
        self.accept("w-up", self.stop_move_forward)
        self.accept("s-up", self.stop_move_backward)

    def setup_lights(self):
        """Set up ambient and directional lights."""
        ambient_light = AmbientLight('ambient_light')
        ambient_light.setColor(Vec4(0.5, 0.5, 0.5, 1))
        ambient_light_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_light_np)

        directional_light = DirectionalLight('directional_light')
        directional_light.setColor(Vec4(1, 1, 1, 1))
        directional_light_np = self.render.attachNewNode(directional_light)
        directional_light_np.setHpr(0, -60, 0)
        self.render.setLight(directional_light_np)

    def create_blocks(self):
        """Create and return a list of blocks."""
        blocks = []
        block_positions = [(2, 10, 0.5), (4, 15, 0.5), (6, 20, 0.5)]
        for pos in block_positions:
            block = self.loader.loadModel("models/box")
            block.reparentTo(self.render)
            block.setPos(*pos)
            block.setScale(1, 1, 1)
            block.setCollideMask(BitMask32.bit(1))  # Block can be collided into
            blocks.append(block)
        return blocks

    def create_player(self):
        """Create and return the player model with collision handling."""
        player = self.loader.loadModel("models/box")
        player.reparentTo(self.render)
        player.setScale(1, 1, 1)
        player.setPos(0, 0, 1)

        # Set up player collision
        self.player_collider = CollisionNode('player')
        self.player_collider.addSolid(CollisionSphere(0, 0, 0, 1))
        self.player_collider.setFromCollideMask(BitMask32.bit(0))  # Player can initiate collisions
        self.player_collider.setIntoCollideMask(BitMask32.allOff())  # Player can't be collided into
        self.player_collider_np = player.attachNewNode(self.player_collider)
        self.player_collider_np.show()
        self.collision_traverser.addCollider(self.player_collider_np, self.collision_handler)
        self.collision_handler.addCollider(self.player_collider_np, player)

        return player

    def zoom_in(self):
        """Zoom in by decreasing the camera distance."""
        self.camera_distance = max(5, self.camera_distance - self.zoom_speed)

    def zoom_out(self):
        """Zoom out by increasing the camera distance."""
        self.camera_distance = min(50, self.camera_distance + self.zoom_speed)

    def update_camera(self, task):
        """Update the camera position and orientation based on player and mouse input."""
        # Get player head position (adjust to match the player's head or upper body)
        player_head_pos = self.player.getPos() + LVector3f(0, 0, 1.5)

        # Calculate the new camera position using spherical coordinates
        camera_pos = LVector3f(
            player_head_pos.getX() - self.camera_distance * cos(radians(self.camera_yaw)) * cos(
                radians(self.camera_pitch)),
            player_head_pos.getY() - self.camera_distance * sin(radians(self.camera_yaw)) * cos(
                radians(self.camera_pitch)),
            player_head_pos.getZ() + self.camera_distance * sin(radians(self.camera_pitch))
        )

        # Set the camera's position and make it look at the player's head
        self.camera.setPos(camera_pos)
        self.camera.lookAt(player_head_pos)

        return Task.cont

    def get_camera_vectors(self):
        """Return the forward and right vectors of the camera."""
        # Get the camera's forward vector (direction it is facing)
        camera_forward = self.camera.getQuat().getForward()
        # Get the camera's right vector (perpendicular to the forward direction)
        camera_right = self.camera.getQuat().getRight()
        return camera_forward, camera_right

    def update_mouse(self, task):
        """Update camera angles based on mouse movement."""
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()

            # Check if the mouse has moved
            if (mouse_x, mouse_y) != self.last_mouse_pos:
                # Adjust camera yaw and pitch based on mouse movement
                self.camera_yaw -= (mouse_x - self.last_mouse_pos[0]) * self.mouse_sense
                self.camera_pitch -= (mouse_y - self.last_mouse_pos[1]) * self.mouse_sense

                # Clamp pitch to prevent flipping
                self.camera_pitch = max(min(self.camera_pitch, 89), -89)

                # Update the last mouse position
                self.last_mouse_pos = (mouse_x, mouse_y)

        return Task.cont

    def start_move_left(self):
        """Start moving the player left."""
        self.side_move = -1

    def start_move_right(self):
        """Start moving the player right."""
        self.side_move = 1

    def start_move_forward(self):
        """Start moving the player forward."""
        self.forward_move = 1

    def start_move_backward(self):
        """Start moving the player backward."""
        self.forward_move = -1

    def stop_move_left(self):
        """Stop moving the player left."""
        if self.side_move == -1:
            self.side_move = 0

    def stop_move_right(self):
        """Stop moving the player right."""
        if self.side_move == 1:
            self.side_move = 0

    def stop_move_forward(self):
        """Stop moving the player forward."""
        if self.forward_move == 1:
            self.forward_move = 0

    def stop_move_backward(self):
        """Stop moving the player backward."""
        if self.forward_move == -1:
            self.forward_move = 0

    def jump(self):
        """Make the player jump."""
        if not self.jumping:
            self.jumping = True
            self.initial_jump_height = self.player.getZ()
            self.vertical_velocity = self.jump_velocity  # Use the adjusted jump velocity

    def setup_collisions(self):
        """Setup collision handling for blocks."""
        for block in self.blocks:
            block_collider = CollisionNode('block')
            block_collider.addSolid(CollisionSphere(0, 0, 0, 1))
            block_collider.setFromCollideMask(BitMask32.bit(1))  # Blocks can initiate collisions
            block_collider.setIntoCollideMask(BitMask32.bit(0))  # Blocks can be collided into
            block_collider_np = block.attachNewNode(block_collider)
            block_collider_np.show()
            self.collision_traverser.addCollider(block_collider_np, self.collision_handler)
            self.collision_handler.addCollider(block_collider_np, block)

    def update(self, task):
        """Update the player and handle gravity and collisions."""
        dt = globalClock.getDt()

        # Get the camera's forward and right vectors
        camera_forward, camera_right = self.get_camera_vectors()

        # Flatten the camera's forward vector to ignore vertical movement
        camera_forward.setZ(0)
        camera_forward.normalize()

        # Flatten the camera's right vector to ignore vertical movement (this is technically not needed as right should already be horizontal)
        camera_right.setZ(0)
        camera_right.normalize()

        # Calculate the movement direction based on player input
        move_direction = (camera_forward * self.forward_move) + (camera_right * self.side_move)

        # Normalize to prevent faster diagonal movement
        if move_direction.length() > 0:
            move_direction.normalize()

        # Update player position based on movement direction
        self.player.setPos(self.player.getPos() + move_direction * self.velocity * dt)

        # Apply gravity and handle jumping
        if self.jumping:
            self.vertical_velocity += self.gravity * dt
            new_z = self.player.getZ() + self.vertical_velocity * dt
            if new_z <= self.initial_jump_height:  # Land back on the ground
                self.jumping = False
                new_z = self.initial_jump_height
            self.player.setZ(new_z)

        # Collision detection
        self.collision_traverser.traverse(self.render)

        return Task.cont

game = Game()
game.run()