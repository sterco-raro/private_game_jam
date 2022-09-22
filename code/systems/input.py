import random
import pygame # TODO Only import necessary variables/functions/classes
from copy 	import deepcopy
from esper 	import Processor
from code.components.controller import PlayerController
from code.components.physics 	import PhysicsBody
from code.components.sprite 	import AnimatedSprite
from code.settings import (
	ANIM_DURATION_EXPLOSION,
	ANIM_SPEED_EXPLOSION,
	ANIM_TABLE_EXPLOSION,
	RENDERING_LAYERS,
)


# -------------------------------------------------------------------------------------------------


class InputHandler(Processor):
	"""Player controls management: movement, actions, animation status, etc."""

	def _test_spawn_explosion(self, position):
		"""Create an explosion with random dimensions centered at @position"""

		explosion = self.world.create_entity()

		scale = random.randint(48, 256)
		spawn = position

		sprite = AnimatedSprite(	duration = ANIM_DURATION_EXPLOSION,
									folder = "explosions",
									frames_table = deepcopy( ANIM_TABLE_EXPLOSION ),
									layer = RENDERING_LAYERS["main"],
									scale_size = ( scale, scale ),
									spawn_point = spawn,
									speed = ANIM_SPEED_EXPLOSION )

		self.world.add_component( explosion, sprite )

	def process(self, dt):
		pressed = pygame.key.get_pressed()
		for ent, (body, ctrl, sprite) in self.world.get_components(PhysicsBody, PlayerController, AnimatedSprite):

			# Skip inactive controllers
			if not ctrl.active: continue

			# Update timers and cooldowns
			ctrl.update()

			# Reset movement direction
			body.direction = pygame.Vector2(0, 0)

			# Update direction based on user input
			if pressed[pygame.K_w] or pressed[pygame.K_UP]: 	body.direction += (0, -1)
			if pressed[pygame.K_s] or pressed[pygame.K_DOWN]: 	body.direction += (0,  1)
			if pressed[pygame.K_a] or pressed[pygame.K_LEFT]: 	body.direction += (-1, 0)
			if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]: 	body.direction += ( 1, 0)

			# Spawn a "bomb" (explosion with usage cooldown)
			if not ctrl.cooldowns["bomb"].active:
				if pressed[pygame.K_n]:
					self._test_spawn_explosion(body.position)
					ctrl.cooldowns["bomb"].activate()

			# Continuously spawn explosions
			if pressed[pygame.K_b]:
				self._test_spawn_explosion(body.position)

			# Test "hurt" animation
			if not ctrl.timers["hurt"].active:
				if pressed[pygame.K_h]:
					sprite.status = "hurt"
					sprite.frame_index = 0
					ctrl.timers["hurt"].activate()
					continue

			# Attack animation (cannot attack while getting hurt)
			if not ctrl.timers["kick"].active and not ctrl.timers["hurt"].active:
				if pressed[pygame.K_m]:
					sprite.status = "kick"
					sprite.frame_index = 0
					ctrl.timers["kick"].activate()
					continue

			# When no other animations have been activated, default to "idle" or "moving"
			if not ctrl.timers_active:
				# Update movement status
				if body.direction == (0, 0): 	sprite.status = "idle"
				else: 							sprite.status = "moving"
