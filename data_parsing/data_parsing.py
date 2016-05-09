import cPickle as pickle
import sys

import utils.utils as utils
import utils.hdf5_getters as Getters


#reuses code from http://labrosa.ee.columbia.edu/millionsong/sites/default/files/tutorial1.py.txt

class DataParser():
  def __init__(self, sqliteLocation, baseLocation, outDir):
    self.sqliteLocation = sqliteLocation
    self.baseLocation = baseLocation
    self.outDir = outDir
    self.styles = {}
    self.pitches_list = []
    self.timbres_list = []
    self.tags_list = []
    self.ids_list = []
    self.dft_list = []
    self.flushIndex = 0

  def process_info(self):
    songs = utils.apply_to_all_files(self.baseLocation, self.process_h5_file_info, self.flushFunc, 1000)
    f = open(self.outDir + '/styles.save', 'wb')
    pickle.dump([self.tags_list, self.pitches_list, self.timbres_list], f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    return 'number of song files:' + str(songs)

  def process_h5_file_info(self, filename):
    """
    This function does 3 simple things:
    - open the song file
    - get info
    - close the file
    """
    h5 = Getters.open_h5_file_read(filename)
    tags = Getters.get_artist_mbtags(h5);

    if len(tags) == 0:
      h5.close()
      return 0
    try:
      preview = utils.get_preview_dft(h5)
    except:
      h5.close()
      return 0
    for tag in tags:
      if tag in self.styles.keys():
        self.styles[tag] += 1
      else:
        self.styles[tag] = 1
    self.ids_list.append(Getters.get_track_id(h5))
    self.tags_list.append(tags)
    self.pitches_list.append(Getters.get_segments_pitches(h5))
    self.timbres_list.append(Getters.get_segments_timbre(h5))
    self.dft_list.append(Getters.get_segments_timbre(h5))
    h5.close()
    return 1

  def flushFunc(self):
    f = open(self.outDir + '/obj_' +"%02d" % (self.flushIndex,) + '.save', 'wb')
    pickle.dump([self.ids_list, self.tags_list, self.pitches_list, self.timbres_list, self.dft_list], f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    self.tags_list = []
    self.pitches_list = []
    self.timbres_list = []
    self.dft_list = []
    self.flushIndex+=1


if __name__ == "__main__":
  kwargs = dict(x.split('=', 1) for x in sys.argv[1:])
  parser = DataParser(kwargs["--sqlite"], kwargs["--basedir"], kwargs["--outDir"])
  print "Files to read:" + parser.process_info();
  print parser.styles
