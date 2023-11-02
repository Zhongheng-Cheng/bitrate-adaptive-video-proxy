class Logs(object):
    def __init__(self, filepath):
        '''
        Proxy logging: <time> <duration> <tput> <avg-tput> <bitrate> <server-ip> <chunkname>
        '''
        self.filepath = filepath
        return

    def log(self):
        with open(self.filepath, 'a') as fo:
            fo.write("<time> <duration> <tput> <avg-tput> <bitrate> <server-ip> <chunkname>\n")
        return