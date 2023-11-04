class Logger(object):
    def __init__(self, filepath):
        '''
        Proxy logging: <time> <duration> <tput> <avg-tput> <bitrate> <server-ip> <chunkname>
        DNS Server logging: 
            After each response from a client: <time> "request-report" <decision-method> <returned-web-server-ip>
            After each measurement to the web server: <time> "measurement-report" <video-server-ip> <latency>
        '''
        self.filepath = filepath
        return

    def log(self):
        with open(self.filepath, 'a') as fo:
            fo.write("logging...\n")
        return