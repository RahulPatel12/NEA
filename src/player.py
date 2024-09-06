from panda3d.core import *
from direct.showbase.DirectObject import DirectObject

class Player(DirectObject):
    PLAYER_INITIAL_POSITION = (0, 0, 0)
    PLAYER_SCALE = (1, 1, 1)
    PLAYER_VELOCITY = 10
    GRAVITY = -20  # Standard gravity
    JUMP_VELOCITY = 15  # Initial upward velocity for jump
    MAX_FALL_SPEED = -50  # Maximum speed the player can fall

    def __init__(self, render, loader, game):
        self.render = render
        self.loader = loader
        self.game = game

        # Create player model
        self.model = self.loader.loadModel("models/box")
        self.model.reparentTo(self.render)
        self.model.setScale(*self.PLAYER_SCALE)
        self.model.setPos(*self.PLAYER_INITIAL_POSITION)

        # Create collision node for the player
        self.create_collision_node()

        # Initialize movement and jumping variables
        self.forward_move = 0
        self.side_move = 0
        self.velocity = self.PLAYER_VELOCITY
        self.jump_velocity = 0
        self.is_jumping = False
        self.is_on_ground = False

        # Set up controls
        self.setup_controls()

    def create_collision_node(self):
        """Create a collision node for the player."""
        player_collider = CollisionNode('player_cnode')
        player_collider.addSolid(CollisionBox(Point3(0.5, 0.5, 0.5), 0.5, 0.5, 0.5))  # Create a collision box
        self.collider_np = self.model.attachNewNode(player_collider)  # Attach it to the player model
        self.collider_np.show()  # Optional: Show the collision geometry for debugging

        # Set up collision handling with blocks and ground
        self.game.pusher.addCollider(self.collider_np, self.model)
        self.game.cTrav.addCollider(self.collider_np, self.game.pusher)

    def setup_controls(self):
        """Set up player controls."""
        self.game.accept("a", self.start_move_left)
        self.game.accept("d", self.start_move_right)
        self.game.accept("w", self.start_move_forward)
        self.game.accept("s", self.start_move_backward)
        self.game.accept("space", self.jump)

        self.game.accept("a-up", self.stop_move_left)
        self.game.accept("d-up", self.stop_move_right)
        self.game.accept("w-up", self.stop_move_forward)
        self.game.accept("s-up", self.stop_move_backward)

    def start_move_left(self):
        self.side_move = -1

    def start_move_right(self):
        self.side_move = 1

    def start_move_forward(self):
        self.forward_move = 1

    def start_move_backward(self):
        self.forward_move = -1

    def stop_move_left(self):
        if self.side_move == -1:
            self.side_move = 0

    def stop_move_right(self):
        if self.side_move == 1:
            self.side_move = 0

    def stop_move_forward(self):
        if self.forward_move == 1:
            self.forward_move = 0

    def stop_move_backward(self):
        if self.forward_move == -1:
            self.forward_move = 0

    def jump(self):
        """Make the player jump if they are on the ground."""
        if self.is_on_ground:
            self.jump_velocity = self.JUMP_VELOCITY
            self.is_jumping = True
            self.is_on_ground = False  # Player is no longer on the ground after jumping
            print("Jump!")

    def update(self, dt):
        """Update player movement and apply gravity."""
        # Handle horizontal movement
        camera_forward, camera_right = self.game.get_camera_vectors()
        move_direction = (camera_forward * self.forward_move) + (camera_right * self.side_move)
        if move_direction.length() > 0:
            move_direction.normalize()

        self.model.setPos(self.model.getPos() + move_direction * self.velocity * dt)

        # Update player heading to face the camera's yaw direction
        self.model.setH(self.game.camera_yaw)

        # Apply gravity if the player is not on the ground
        if not self.is_on_ground:
            self.jump_velocity += self.GRAVITY * dt
            self.jump_velocity = max(self.jump_velocity, self.MAX_FALL_SPEED)  # Cap falling speed
            self.model.setZ(self.model.getZ() + self.jump_velocity * dt)

        # Simulate simple ground collision check (assuming the ground is at Z = 0)
        if self.model.getZ() <= 0:
            self.model.setZ(0)  # Stop falling when reaching the ground
            self.is_on_ground = True
            self.jump_velocity = 0  # Reset jump velocity
            self.is_jumping = False  # Player is no longer jumping

