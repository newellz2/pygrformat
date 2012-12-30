import os
import re
from datetime import datetime

__author__ = 'Zachary Newell(zlantern@gmail.com)'

MONTHS= {
    10:'x',
    11:'y',
    12:'z'
}

class SensorData:
    # STARTREC = 00:00 12/12/16
    startrec_dt = None
    month_dt = None
    def __init__(self,raw_data,addtxt=False,datetime_format=r"%H:%M %y/%m/%d"):
        self.raw_data = raw_data
        self.raw_lines = raw_data.split('\r\n')
        self.lines = self.raw_lines[3:]
        self.datetime_format = datetime_format
        self.addtxt = addtxt
        self._process_parameters()
        self._process_date()

    def _process_parameters(self):
        asterisk_lines = [l for l in self.lines if l.startswith("*")]
        for l in asterisk_lines:
            if l.find("=") > -1 :
                bits = l.split("=")
                bits[0] = bits[0][2:].strip()
                bits[1] = bits[1].strip()
                setattr(self,bits[0],bits[1])

    def _process_date(self):
        if self.STARTREC:
            self.startrec_dt = datetime.strptime(self.STARTREC,self.datetime_format)
            self.month_dt = int(self.startrec_dt.month) if self.startrec_dt.month < 10 else MONTHS[self.startrec_dt.month]
            self.month_dt = str(self.month_dt)

    def filename(self,files=None):
        filename = ""
        # pattern = r"\d+_?\d+?\.[xyz]\d{2}"
        # copy_pattern = r"\d+_?(?P<copy>\d+)\.[xyz]\d{2}"
        copy = ""
        if files:
            if self.addtxt:
                pattern = "%s_?\d?\d?\.%s%s.txt" % (self.SITE,self.month_dt,self.startrec_dt.strftime("%d"))
                copy_pattern = "%s_?(?P<copy>\d+)\.%s%s.txt" % (self.SITE,self.month_dt,self.startrec_dt.strftime("%d"))
                if len(re.findall(pattern," ".join(files))) > 0:
                    finds = re.findall(copy_pattern," ".join(files))
                    max_copy = max(finds) if len(finds) > 0 else 0
                    copy = "_%i" % (int(max_copy) + 1)
                filename = "%s%s.%s%s.txt" % (self.SITE,copy,self.month_dt,self.startrec_dt.strftime("%d"))
            else:
                pattern = "%s_?\d?\d?\.%s%s" % (self.SITE,self.month_dt,self.startrec_dt.strftime("%d"))
                copy_pattern = "%s_?(?P<copy>\d+)\.%s%s" % (self.SITE,self.month_dt,self.startrec_dt.strftime("%d"))
                if len(re.findall(pattern," ".join(files))) > 0:
                    finds = re.findall(copy_pattern," ".join(files))
                    max_copy = max(finds) if len(finds) > 0 else 0
                    copy = "_%i" % (int(max_copy) + 1)
                filename = "%s%s.%s%s" % (self.SITE,copy,self.month_dt,self.startrec_dt.strftime("%d"))
        else:

            if self.addtxt:
                filename = "%s%s.%s%s.txt" % (self.SITE,copy,self.month_dt,self.startrec_dt.strftime("%d"))
            else:
                filename = "%s%s.%s%s" % (self.SITE,copy,self.month_dt,self.startrec_dt.strftime("%d"))

        return filename

    def save(self,path,filename):
        body = "\r\n".join(self.lines)
        file_path = os.path.join(path,filename)
        f = file(file_path,"wb")
        f.write(body)
        f.close()

    def data(self):
        return '\r\n'.join(self.lines)