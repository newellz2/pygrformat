import os
import sys
import subprocess

from ctypes import c_int, WINFUNCTYPE, windll
from ctypes.wintypes import HWND, LPCSTR, UINT

import gflags

from sensordata import SensorData

__author__ = 'Zachary Newell(zlantern@gmail.com)'

CURRENT_DIRECTORY = os.getcwd()
FLAGS = gflags.FLAGS

gflags.DEFINE_string("input",os.path.join(CURRENT_DIRECTORY,"data"),"Input directory",short_name="i")
gflags.DEFINE_string("output",os.path.join(CURRENT_DIRECTORY,"output"),"Output directory",short_name="o")
gflags.DEFINE_string("exe",os.path.join(CURRENT_DIRECTORY,"grformat.exe"),"Path to grformat executable",short_name="e")
gflags.DEFINE_boolean('addtxt', False, 'Adds .txt to the end of the filename')
gflags.DEFINE_boolean('debug', False, 'Produces debugging output')

def GetFilenames(path):
    return os.listdir(path)

def GetInputFiles(path,FLAGS=FLAGS):
    if FLAGS.debug:
        print "DEBUG Input files path: %s" % path
    files = os.listdir(path)
    files = [os.path.join(path,f) for f in files]
    return files

def DisplayMessage(message):
    prototype = WINFUNCTYPE(c_int, HWND, LPCSTR, LPCSTR, UINT)
    paramflags = (1, "hwnd", 0), (1, "text", message), (1, "caption", None), (1, "flags", 0)
    MessageBox = prototype(("MessageBoxA", windll.user32), paramflags)
    MessageBox()

def ConvertFiles(command,files,FLAGS=FLAGS,addtxt=False):
    error_flag = False
    error_messages = []
    sensor_data = []
    for f in files:
        try:
            output = subprocess.check_output([command,"/i2",f])
            s = SensorData(output,addtxt=addtxt)
            sensor_data.append(s)
        except WindowsError, e:
            error_flag = True
            error_messages.append("Failed to launch grformat.exe. grformat.exe only runs in a 32bit version of windows.")
            # error_messages.append(repr(e))
        except subprocess.CalledProcessError, e:
            error_flag = True
            error_messages.append("Failed to launch the executable. Is it in the same directory?")
            # error_messages.append(repr(e))

    if error_flag:
        messages = "%i Errors \r\n" % len(error_messages)
        messages += "\r\n".join(error_messages[0:10])
        DisplayMessage(messages)
        sys.exit(1)

    return sensor_data

def main(argv):
    try:
        argv = FLAGS(argv)
    except gflags.FlagsError, e:
        print '%s\\nUsage: %s ARGS\\n%s' % (e, sys.argv[0], FLAGS)
        sys.exit(1)

    # Suppress windows errors
    windll.kernel32.SetErrorMode(3)

    if FLAGS.debug:
        import pprint
        print 'non-flag arguments:', argv

    # Get input files
    input_files = GetInputFiles(FLAGS.input)

    if FLAGS.debug:
        print "DEBUG Input files:"
        pprint.pprint(input_files)

    # Convert the files and extract the data
    sensor_data = ConvertFiles(FLAGS.exe,input_files,addtxt=FLAGS.addtxt)

    if FLAGS.debug:
        print "DEBUG Sensor data:"
        print "DEBUG %i Sensors" % len(sensor_data)
        output_files = GetFilenames(FLAGS.output)
        for s in sensor_data:
            pprint.pprint("SITE=%s, OUTPUT=%s" % (s.SITE,s.filename(output_files)))

    for s in sensor_data:
        output_files = GetFilenames(FLAGS.output)
        filename = s.filename(output_files)
        if FLAGS.debug:
            print "DEBUG Files in output directory:"
            pprint.pprint(output_files)
            print "Filename : %s" % filename
        s.save(FLAGS.output,filename)



if __name__ == "__main__":
    main(sys.argv)