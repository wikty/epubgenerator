import abc

class BaseConfig(metaclass=abc.ABCMeta):

	@abc.abstractmethod
	def get_configuration(self):
		pass

	@abc.abstractmethod
	def validate_configuration(self):
		pass

	@abc.abstractmethod
	def get_validation(self):
		pass

	@abc.abstractmethod
	def confirm_configuration(self):
		pass