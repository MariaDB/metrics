#!/usr/bin/python3
import re

def ReadConfigLine(file):
    line = file.readline()
    if not line:
        return None
    line = line.split('#')[0] # Get rid of any comments
    line = line.strip() # and extra white space
    if len(line) == 0: # we got rid of everything
        return ReadConfigLine(file)
    return line

def ReadCategories(name):
    try:
        file = open(name, 'r')
    except IOError:
        raise Exception("Unable to open categories file {}".format(name))

    categories = {}
    line = ReadConfigLine(file)
    while line:
        m = re.match('^("[^"]+"|\S+)\s+("[^"]+"|\S+)$', line)
        if not m or len(m.groups()) != 2:
            raise Exception("Could not parse category line {}".format(line))
        categories[m.group(1).replace('"', '')] = m.group(2).replace('"', '')
        #print("{} - {}".format(m.group(1).replace('"', ''), m.group(2).replace('"', '')))
        line = ReadConfigLine(file)
    file.close()
    return categories

def ParseFile(name_in, name_out):
    file_read = open(name_in, "r")
    file_write = open(name_out, "w")

    line = ReadConfigLine(file_read)
    while line:
        for key in categories.keys():
            line = line.replace(key, categories[key])
        file_write.write(line)
        file_write.write('\n')
        line = ReadConfigLine(file_read)

    file_read.close()
    file_write.close()

if __name__ == '__main__':
    categories = ReadCategories("config/mariadb_server/categories")
    ParseFile("config/mariadb_server/domain-map", "config/mariadb_server_categories/domain-map")
    ParseFile("config/mariadb_server/employers", "config/mariadb_server_categories/employers")
