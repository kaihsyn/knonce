from knonce.exception import PreconditionError, PostconditionError

class Contract:

    @staticmethod
    def requires(test):
        if not test:
            raise PreconditionError()

    @staticmethod
    def requires_not_none(object):
        if object is None:
            raise PreconditionError()

    @staticmethod
    def requires_not_none_or_empty(object):
        if object is None or object == '':
            raise PreconditionError()

    @staticmethod
    def ensures(test):
        if not test:
            raise PostconditionError()
