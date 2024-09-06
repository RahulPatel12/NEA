# level.py

from panda3d.core import NodePath, PandaNode

class Level:
    def __init__(self, game, level_name):
        self.game = game
        self.level_name = level_name
        self.root = NodePath(PandaNode(level_name))  # Create a proper PandaNode root

    def load(self):
        """Load the level assets and initialize the level."""
        # Load models, textures, etc. here. For now, we will use a simple box to represent the level.
        self.level_model = self.game.loader.loadModel("models/box")
        self.level_model.reparentTo(self.root)
        self.level_model.setScale(5, 5, 0.5)  # Scale the box
        self.level_model.setPos(0, 0, 0)  # Position it

        self.root.reparentTo(self.game.render)  # Attach the level node to the render

    def unload(self):
        """Unload the level assets."""
        self.root.removeNode()  # Remove the level node

    def update(self):
        """Update logic for the level (if needed)."""
        pass
