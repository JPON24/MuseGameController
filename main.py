import constants

from muselsl import stream, list_muses, record
import os


# muses = list_muses()
# stream(muses[0]['address'])

os.remove(constants.FILE_NAME)
record(duration=10, filename=constants.FILE_NAME)

print('End program')