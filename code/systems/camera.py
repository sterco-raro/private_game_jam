from esper import Processor
from code.components.camera import CameraFollow


# -------------------------------------------------------------------------------------------------


class CameraFollowManager(Processor):
	"""Handle current CameraFollow instance movement"""

	def __init__(self, max_width, max_height, camera_id):
		# World map boundaries
		self.max_width = max_width
		self.max_height = max_height

		self.camera_id = camera_id

		# Current world camera component
		self.camera = None

	def process(self, dt):
		# Get camera reference
		if not self.camera:
			self.camera = self.world.component_for_entity(self.camera_id, CameraFollow)

		# Center the screen viewport to the camera viewport
		x = self.camera.target.rect.centerx - self.camera.width // 2
		y = self.camera.target.rect.centery - self.camera.height // 2

		# Clamp values to keep the camera inside the world view
		x = min(self.max_width - self.camera.width, max(0, x))
		y = min(self.max_height - self.camera.height, max(0, y))

		# Update camera position
		self.camera.rect.x = x
		self.camera.rect.y = y
