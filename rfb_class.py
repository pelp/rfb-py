class RFB:
    def int_to_4byte(self, i):
        b = bytearray([0, 0, 0, 0])
        b[3] = i & 0xFF
        i >>= 8
        b[2] = i & 0xFF
        i >>= 8
        b[1] = i & 0xFF
        i >>= 8
        b[0] = i & 0xFF
        return b

    def int_to_2byte(self, i):
        b = bytearray([0, 0])
        b[1] = i & 0xFF
        i >>= 8
        b[0] = i & 0xFF
        return b

    def int_to_byte(self, i):
        b = bytearray([0])
        b[0] = i & 0xFF
        return b

    def byte_to_int(self, b):
        t = 8 * len(b)
        r = 0
        for i in range(len(b)):
            t -= 8
            r += b[i] << t
        return r

    def send_protocol_version(self, g):
        g.send(b"RFB 003.003\n")
        retry = True
        while (retry):
            try:
                l = g.recv(64).decode("utf-8")
                retry = False
            except BlockingIOError:
                pass

    def send_authentication(self, g):
        g.send(b"\x00\x00\x00\x01")
        retry = True
        while (retry):
            try:
                l = g.recv(64).decode("utf-8")
                retry = False
            except BlockingIOError:
                pass

    def server_init(self, g):
        name_length = len(self.name)
        bpp = 8
        depth = 8
        bef = 0
        tcf = 1
        rm = 2**2 - 1
        gm = 2**3 - 1
        bm = 2**3 - 1
        rs = 6
        gs = 3
        bs = 0
        t = self.int_to_2byte(self.width) + self.int_to_2byte(self.height) + self.int_to_byte(bpp) + self.int_to_byte(depth) + self.int_to_byte(bef) + self.int_to_byte(tcf) + self.int_to_2byte(rm) + self.int_to_2byte(gm) + self.int_to_2byte(bm) + self.int_to_byte(rs) + self.int_to_byte(gs) + self.int_to_byte(bs) + b"\x00\x00\x00" + self.int_to_4byte(name_length) + self.name.encode("utf-8")
        g.send(t)

    def handle_message(self, c):
        g = c[0]
        try:
            m = g.recv(64)
            if (m != b''):
                if (m[0] == 4):
                    c[3] = m[4:]
                    c[2] = m[1]
                    if (self.onKey_event != None):
                        self.onKey_event(c, bool(c[2]), self.byte_to_int(c[3]))
                elif (m[0] == 5):
                    c[7] = c[6]
                    c[4] = m[2] << 8
                    c[4] += m[3]
                    c[5] = m[4] << 8
                    c[5] += m[5]
                    c[6] = m[1]
                    if (self.onMouse_event != None):
                        self.onMouse_event(c, bool(c[6]), [c[4], c[5]], c[6] != c[7])
        except BlockingIOError:
            pass

    def send_bitmap(self, g, fb, w, h, x, y):
        try:
            t = b"\x00\x00\x00\x01" + self.int_to_2byte(x) + self.int_to_2byte(y) + self.int_to_2byte(w) + self.int_to_2byte(h) + b"\x00\x00\x00\x00"
            for i in range(h):
                for j in range(w):
                    t += self.int_to_byte(fb[w * i + j])
            g.send(t)
        except BlockingIOError:
            pass

    def send_rect(self, g, x, y, w, h, c):
        try:
            t = b"\x00\x00\x00\x01" + self.int_to_2byte(x) + self.int_to_2byte(y) + self.int_to_2byte(w) + self.int_to_2byte(h) + b"\x00\x00\x00\x02"
            t += b"\x00\x00\x00\x00" + self.int_to_byte(c)
            g.send(t)
        except BlockingIOError:
            pass

    def send_bell(self, c):
        g = c[0]
        g.send(b"\x02")

    def init_client(self, client):
        self.send_protocol_version(client)
        self.send_authentication(client)
        self.server_init(client)
    def handle(self):
        import time
        k = 0
        try:
            c, addr = self.s.accept()
            self.clients += [[c, addr, 0, 0, 0, 0, 0, 0, 0]]
            self.init_client(c)
            if (self.connect_event != None):
                self.connect_event(self.clients[len(self.clients)-1])
        except BlockingIOError:
            pass
        for i in range(len(self.clients)):
            try:
                self.handle_message(self.clients[i])
                if (self.clients[i][8] + 5 < time.clock()):
                    self.send_rect(self.clients[i][0], 0, 0, 0, 0, 0)
                    self.clients[i][8] = time.clock()
                k = i
                for j in self.draw_buffer:
                    if (j[0] == 2):
                        self.send_rect(j[5][0], j[1], j[2], j[3], j[4], self.color)
                        self.draw_buffer.remove(j)
            except ConnectionAbortedError:
                if (self.disconnect_event != None):
                    self.disconnect_event(self.clients[k])
                self.clients.remove(self.clients[k])

            except ConnectionResetError:
                if (self.disconnect_event != None):
                    self.disconnect_event(self.clients[k])
                self.clients.remove(self.clients[k])

    def __init__(self, w, h, p):
        import socket
        self.s = socket.socket()
        self.port = p
        self.width = w
        self.height = h
        self.FPS = 30
        self.clients = []
        self.draw_buffer = []
        self.name = "Untitled RFB connection"
        
        self.disconnect_event = None
        self.connect_event = None
        self.onKey_event = None
        self.onMouse_event = None

        self.s.bind(("", self.port))
        self.s.listen(5)
        self.s.setblocking(0)
        
    def rect(self, x, y, w, h, c):
        self.draw_buffer += [[2, x, y, w, h, c]]

    def fill(self, c):
        self.color = c
        
    def get_address(self, c):
        return c[1][0]
