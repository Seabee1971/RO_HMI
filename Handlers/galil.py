import gclib

class galil:
    def __init__(self,parent=None):
        self.g = gclib.py()
        self.IP_address = "169.254.154.33"

    def dmc_connect(self):
        try:
            self.g.GOpen(f'{self.IP_address} --direct')
            return self.g.GInfo(),self.g
        except Exception as e:
            return e,self.g

    def dmc_disconnect(self):
        try:
            self.g.GClose()
        except Exception as e:
            return e,self.g
        return "closed",self.g


    def readInputValues(self):
        pass
