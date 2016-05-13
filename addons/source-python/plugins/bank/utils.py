import collections


class KeyDefaultDict(collections.defaultdict):
	"""Default dict where the factory takes the key as argument."""

	def __missing__(self, key):
		"""Create a new value with the default factory."""
		if self.default_factory is None:
			raise KeyError(key)
		value = self[key] = self.default_factory(key)
		return value
