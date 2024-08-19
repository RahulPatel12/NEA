from panda3d.core import NodePath

class Level:
    def __init__(self, level_name, base):
        self.level_name = level_name
        self.base = base

        # Load the level model
        self.level_model = self.base.loader.loadModel(f"src/assets/models/{level_name}")
        self.level_model.reparentTo(self.base.render)

        # Additional setup for the level can go here

    def cleanup(self):
        self.level_model.removeNode()
