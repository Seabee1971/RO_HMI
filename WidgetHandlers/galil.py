import gclib

class galil:
    def __init__(self,parent=None):
        self.g = gclib.py()
        self.IP_address = "169.254.154.33"



    def dmc_connect(self):
        try:
            self.g.GOpen(f'{self.IP_address} --direct')
            return True,self.g
        except:
            return False,self.g

        finally:
            self.g.GClose()
