# Data structures


try:
	import sys
	from dataclasses import dataclass
	from pygame import Rect
except ImportError as importErr:
	print("Couldn't load module. {}".format(importErr))
	sys.exit(2)


# -------------------------------------------------------------------------------------------------


@dataclass
class ObjQuadTreeItem():
	entity: int
	rect: Rect

	def __eq__(self, other):
		return self.entity == other.entity and self.rect == other.rect

	def __hash__(self):
		return hash((self.entity, self.rect.x, self.rect.y, self.rect.w, self.rect.h))


# -------------------------------------------------------------------------------------------------


# Authors: ???
class StaticQuadTree():
	"""An implementation of a quad-tree.
 
	This QuadTree started life as a version of [1] but found a life of its own
	when I realised it wasn't doing what I needed. It is intended for static
	geometry, ie, items such as the landscape that don't move.
 
	This implementation inserts items at the current level if they overlap all
	4 sub-quadrants, otherwise it inserts them recursively into the one or two
	sub-quadrants that they overlap.
 
	Items being stored in the tree must be a pygame.Rect or have have a
	.rect (pygame.Rect) attribute that is a pygame.Rect
		...and they must be hashable.
	
	Acknowledgements:
	[1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
	"""

	def __init__(self, items, depth=8, bounding_rect=None):
		"""Creates a quad-tree.
 
		@param items:
			A sequence of items to store in the quad-tree.
			Note that these must be a pygame.Rect instance
			
		@param depth:
			The maximum recursion depth.
			
		@param bounding_rect:
			The bounding rectangle of all of the items in the quad-tree. For
			internal use only.
		"""

		# The current depth items
		self.items = []

		# The sub-quadrants are empty to start with.
		self.nw = None
		self.ne = None
		self.se = None
		self.sw = None

		# Bounding rect center coordinates
		self.cx = 0
		self.cy = 0

		# Initialize this QuadTree instance
		self._reset(items, depth, bounding_rect)

	def _reset(self, items, depth, bounding_rect):
		# If we've reached the maximum depth then insert all items into this quadrant.
		depth -= 1
		if depth == 0 or not items:
			self.items = items
			return
 
		# Find this quadrant's center.
		if bounding_rect:
			bounding_rect = Rect( bounding_rect )
		else:
			# If there isn't a bounding rect, then calculate it from the items.
			bounding_rect = Rect( items[0] )
			for item in items[1:]:
				bounding_rect.union_ip( item )
		# Bounding rect center coordinates
		self.cx = bounding_rect.centerx
		self.cy = bounding_rect.centery

		nw_items = []
		ne_items = []
		se_items = []
		sw_items = []
		self.items = []

		for item in items:
			# Which of the sub-quadrants does the item overlap?
			in_nw = item.left <= self.cx and item.top <= self.cy
			in_sw = item.left <= self.cx and item.bottom >= self.cy
			in_ne = item.right >= self.cx and item.top <= self.cy
			in_se = item.right >= self.cx and item.bottom >= self.cy

			# If it overlaps all 4 quadrants then insert it at the current depth,
			# otherwise append it to a list to be inserted under every quadrant that it overlaps.
			if in_nw and in_ne and in_se and in_sw:
				self.items.append(item)
			else:
				if in_nw: nw_items.append(item)
				if in_ne: ne_items.append(item)
				if in_se: se_items.append(item)
				if in_sw: sw_items.append(item)

		# Create the sub-quadrants, recursively.
		if nw_items:
			self.nw = StaticQuadTree(nw_items, depth, (bounding_rect.left, bounding_rect.top, self.cx, self.cy))
		if ne_items:
			self.ne = StaticQuadTree(ne_items, depth, (self.cx, bounding_rect.top, bounding_rect.right, self.cy))
		if se_items:
			self.se = StaticQuadTree(se_items, depth, (self.cx, self.cy, bounding_rect.right, bounding_rect.bottom))
		if sw_items:
			self.sw = StaticQuadTree(sw_items, depth, (bounding_rect.left, self.cy, self.cx, bounding_rect.bottom))
 
 
	def hit(self, rect):
		"""Returns the items that overlap a bounding rectangle.
 
		Returns the set of all items in the quad-tree that overlap with a
		bounding rectangle.

		@param rect:
			The bounding rectangle being tested against the quad-tree. This
			must possess left, top, right and bottom attributes.
		"""

		# TODO Use sets instead of lists (implement __hash__ inside pygame.Rect or something like StaticQuadTreeItem)

		# Find the hits at the current level.
		hits = [ self.items[n] for n in rect.collidelistall( self.items ) ]

		# Recursively check the lower quadrants.
		lower_hits = []
		if self.nw and rect.left <= self.cx and rect.top <= self.cy:
			lower_hits = self.nw.hit(rect)
			if len(lower_hits) > 0:
				hits.extend(self.nw.hit(rect))
		if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
			lower_hits = self.sw.hit(rect)
			if len(lower_hits) > 0:
				hits.extend(self.sw.hit(rect))
		if self.ne and rect.right >= self.cx and rect.top <= self.cy:
			lower_hits = self.ne.hit(rect)
			if len(lower_hits) > 0:
				hits.extend(self.ne.hit(rect))
		if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
			lower_hits = self.se.hit(rect)
			if len(lower_hits) > 0:
				hits.extend(self.se.hit(rect))

		return hits


# -------------------------------------------------------------------------------------------------


# Authors: ???
class ObjectsQuadTree():
	"""An implementation of a quad-tree.
 
	This QuadTree started life as a version of [1] but found a life of its own
	when I realised it wasn't doing what I needed. It is intended for static
	geometry, ie, items such as the landscape that don't move.
 
	This implementation inserts items at the current level if they overlap all
	4 sub-quadrants, otherwise it inserts them recursively into the one or two
	sub-quadrants that they overlap.
 
	Items being stored in the tree must be a pygame.Rect or have have a
	.rect (pygame.Rect) attribute that is a pygame.Rect
		...and they must be hashable.

	Acknowledgements:
	[1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
	"""

	def __init__(self, items, depth=8, bounding_rect=None):
		"""Creates a quad-tree.
 
		@param items:
			A sequence of items to store in the quad-tree.
			Note that these items must have a .rect attribute.

		@param depth:
			The maximum recursion depth.

		@param bounding_rect:
			The bounding rectangle of all of the items in the quad-tree. For
			internal use only.
		"""

		# The items stored at the current depth
		self.items = []

		# The current depth
		self.depth = -1

		# The sub-quadrants are empty to start with.
		self.nw = None
		self.ne = None
		self.se = None
		self.sw = None

		# Bounding rect center coordinates
		self.cx = 0
		self.cy = 0

		# Initialize this QuadTree instance
		self._reset(items, depth, bounding_rect)

	def _reset(self, items, depth, bounding_rect):
		# If we've reached the maximum depth then insert all items into this quadrant.
		depth -= 1
		self.depth = depth
		if depth == 0 or not items:
			self.items = items
			return
 
		# Find this quadrant's center.
		if bounding_rect:
			bounding_rect = Rect( bounding_rect )
		else:
			# If there isn't a bounding rect, then calculate it from the items.
			bounding_rect = Rect( items[0].rect )
			for item in items[1:]:
				bounding_rect.union_ip( item.rect )
		# Bounding rect center coordinates
		self.cx = bounding_rect.centerx
		self.cy = bounding_rect.centery

		nw_items = []
		ne_items = []
		se_items = []
		sw_items = []

		for item in items:
			# Which of the sub-quadrants does the item overlap?
			in_nw = item.rect.left <= self.cx and item.rect.top <= self.cy
			in_sw = item.rect.left <= self.cx and item.rect.bottom >= self.cy
			in_ne = item.rect.right >= self.cx and item.rect.top <= self.cy
			in_se = item.rect.right >= self.cx and item.rect.bottom >= self.cy

			# If it overlaps all 4 quadrants then insert it at the current depth,
			if in_nw and in_ne and in_se and in_sw:
				self.items.append(item)
			# otherwise append it to a list to be inserted under every quadrant that it overlaps.
			else:
				if in_nw: nw_items.append(item)
				if in_ne: ne_items.append(item)
				if in_se: se_items.append(item)
				if in_sw: sw_items.append(item)

		# Create the sub-quadrants, recursively.
		if nw_items:
			self.nw = ObjectsQuadTree(nw_items, depth, (bounding_rect.left, bounding_rect.top, self.cx, self.cy))
		if ne_items:
			self.ne = ObjectsQuadTree(ne_items, depth, (self.cx, bounding_rect.top, bounding_rect.right, self.cy))
		if se_items:
			self.se = ObjectsQuadTree(se_items, depth, (self.cx, self.cy, bounding_rect.right, bounding_rect.bottom))
		if sw_items:
			self.sw = ObjectsQuadTree(sw_items, depth, (bounding_rect.left, self.cy, self.cx, bounding_rect.bottom))
 
 
	def hit(self, rect):
		"""Returns the items that overlap a bounding rectangle.
 
		Returns the list of all items in the quad-tree that overlap with a bounding rectangle.

		@param rect:
			The bounding rectangle being tested against the quad-tree. This
			must possess left, top, right and bottom attributes.
		"""

		# Find the hits at the current level.
		hits = set( [ self.items[n] for n in rect.collidelistall( list(map(lambda x: x.rect, self.items)) ) ] )

		# Recursively check the lower quadrants.
		lower_hits = []
		if self.nw and rect.left <= self.cx and rect.top <= self.cy:
			hits |= self.nw.hit(rect)
		if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
			hits |= self.sw.hit(rect)
		if self.ne and rect.right >= self.cx and rect.top <= self.cy:
			hits |= self.ne.hit(rect)
		if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
			hits |= self.se.hit(rect)

		return hits

	def delete_object(self, object_id):
		"""TODO docstring for delete()"""
		# Try to find the target object at the current depth level
		index = -1
		for idx, item in enumerate(self.items):
			if item.entity == object_id:
				index = idx
		# Remove object when successfully found
		if index >= 0:
			self.items.pop(index)
			return
		# Item not found, delegate deletion to children quadrants
		if self.nw: self.nw.delete_object(object_id)
		if self.ne: self.ne.delete_object(object_id)
		if self.sw: self.sw.delete_object(object_id)
		if self.se: self.se.delete_object(object_id)

	def delete_objects_list(self, object_ids):
		"""Remove each object in the given list from this QuadTree instance"""
		for item in object_ids: self.delete_object(item)
