from typing import TypeVar, Generic

T = TypeVar('T')

class Ref(Generic[T]):
    def __init__(self, value: T):
        self.value: T = value

class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for line, name in enumerate(names.split('\n')):
            if name.find(",") >= 0:
                # strip out the spaces
                while name.find(" ") != -1:
                    name = name[:name.find(" ")] + name[(name.find(" ") + 1):]

                # strip out the commas
                while name.find(",") != -1:
                    name = name[:name.find(",")] + name[(name.find(",") + 1):]

                # if the value was specified
                if name.find("=") != -1:
                    number = int(float(name[(name.find("=") + 1):]))
                    name = name[:name.find("=")]

                # optionally print to confirm that it's working correctly
                #print "%40s has a value of %d" % (name, number)

                setattr(self, name, number)
                number = number + 1