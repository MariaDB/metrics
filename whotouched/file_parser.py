import re
import itertools
from io import StringIO

class FileParser:
    __file = None

    def open(self, file):
        self.__file = open(file, "r")

    def buffer(self, buffer):
        self.__file = StringIO(buffer)

    def __find_positions(self, name):
        """Goes through each line and looks for "#if* <name>" to find ifdef
        usage. Once each is found __find_end() is called to find the #endif.

        The line numbers for the start and end of the code block are returned.
        """
        counter = 0
        position = 0
        positions = []
        regex = re.compile("#\\s*if[\\s!\\(a-z]+({0})".format(name))
        for line in self.__file:
            counter += 1
            position += len(line)
            found = regex.search(line)
            if found:
                end = self.__find_end(counter)
                positions.append({"start": counter, "end": end})
                self.__file.seek(position)
        return positions

    def __find_end(self, start):
        """Finds the #endif for a corresponding #ifdef, identifies nested
        #ifdefs to get the correct #endif and returns the line number.
        """
        ends = []
        ifreg = re.compile("#\\s*if")
        endreg = re.compile("#\\s*endif")
        ifcount = 1
        pos = 0
        self.__file.seek(0)
        rest_of_file = itertools.islice(self.__file, start, None)
        for line in rest_of_file:
            found = ifreg.search(line)
            if found:
                ifcount += 1
            found = endreg.search(line)
            if found:
                ifcount -= 1
            if ifcount == 0:
                return start + pos + 1
            pos += 1

    def find_define(self, name):
        positions = self.__find_positions(name)
        return positions

    def define_exists(self, name):
        regex = re.compile("#\\s*if[\\s!\\(a-z]+({0})".format(name))
        for line in self.__file:
            if regex.search(line):
                return True
        return False
