import logging
import os
import uuid
import json
import os.path

# Based configuration file class from omplex and plex_mpv_shim. 
# Licensed under MIT License from Weston Nielson.

log = logging.getLogger('conf')

class Settings(object):
    _listeners = []

    _path = None
    _data = {
        "release_after_img":    True,
        "lock_cmd":             "xscreensaver-command -lock",
        "blank_cmd":            "xset dpms force off",
        "unblank_cmd":          "xset dpms force on",
        "interval":             5,
        "blank_interval":       10,
        "lock_if_not_present":  True,
        "blank_if_not_present": True,
        "lock_if_np_unkn":      True,
        "blank_if_unknown":     False,
        "lock_if_unknown":      False,
        "tolerance":            0.54,
        "lock_tolerance":       1, 
    }

    def __getattr__(self, name):
        return self._data[name]

    def __setattr__(self, name, value):
        if name in self._data:
            self._data[name] = value
            self.save()

            for callback in self._listeners:
                try:
                    callback(name, value)
                except:
                    pass
        else:
            super(Settings, self).__setattr__(name, value)

    def __get_file(self, path, mode="r", create=True):
        created = False

        if not os.path.exists(path):
            try:
                fh = open(path, mode)
            except IOError as e:
                if e.errno == 2 and create:
                    fh = open(path, 'w')
                    json.dump(self._data, fh, indent=4, sort_keys=True)
                    fh.close()
                    created = True
                else:
                    raise e
            except Exception as e:
                log.error("Error opening settings from path: %s" % path)
                return None

        # This should work now
        return open(path, mode), created

    def load(self, path, create=True):
        fh, created = self.__get_file(path, "r", create)
        self._path = path
        if not created:
            try:
                data = json.load(fh)
                self._data.update(data)
                log.info("Loaded settings from json: %s" % path)
                if len(data) < len(self._data):
                    self.save()
            except Exception as e:
                log.error("Error loading settings from json: %s" % e)
                fh.close()
                return False

        fh.close()
        return True

    def save(self):
        fh, _ = self.__get_file(self._path, "w", True)

        try:
            json.dump(self._data, fh, indent=4, sort_keys=True)
            fh.flush()
            fh.close()
        except Exception as e:
            log.error("Error saving settings to json: %s" % e)
            return False

        return True

    def add_listener(self, callback):
        """
        Register a callback to be called anytime a setting value changes.
        An example callback function:

            def my_callback(key, value):
                # Do something with the new setting ``value``...

        """
        if callback not in self._listeners:
            self._listeners.append(callback)

settings = Settings()
