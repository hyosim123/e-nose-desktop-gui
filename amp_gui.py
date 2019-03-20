""" Graphical user interface to control PSoC electrochemical device main file
"""
# standard libraries
import csv
import time
import logging
import os
import sys
import tkFont
import Tkinter as tk
import FileDialog    
import ttk
# local files
import change_toplevel as change_top
import cv_frame
import sensor_frame
import graph_properties
import option_menu
import properties
import usb_comm

__author__ = 'Karthik Gangadhara'

OPTIONS_BACKGROUND = 'LightCyan4'


class ElectroChemGUI(tk.Tk):
    """ Graphical User Interface to interact with the PSoC electrochemical device
    """
    def __init__(self, parent=None):
        if not os.path.exists('logging'):  # make a directory to store logging files
            os.makedirs('logging')
        date = time.strftime("%Y_%m_%d")
        logging.basicConfig(level=logging.INFO, filename="logging/"+date+"_logging_file.log",
                            format="%(asctime)-15s %(levelname)s %(module)s %(lineno)d: %(message)s")
        self.sensor_settings = properties.SensorSettings()                   
        self.serialsettings = None
        self.data_save_type = "Converted"
        self.device_params = properties.DeviceParameters()
        self.display_type = check_display_type()
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.voltage_source_label = tk.StringVar()
        self.electrode_config_label = tk.StringVar()
        self.device = usb_comm.AmpUsb(self, self.device_params, self.sensor_settings.port, self.sensor_settings.baud_rate)
        # let the user see if the device is set for 2 or 3 electrodes
        if hasattr(self.device, "found"):
            if self.device.found and self.device.connected:
                self.electrode_config_label.set("connected to the serial device")
            elif self.device.found:  # device i
                self.electrode_config_label.set("unable to connect to device")
            else:
                self.electrode_config_label.set("unable to connect to device")
       
        graph_props = graph_properties.GraphProps()
        # frame to put the connection button, graph toolbar and label for VDAC source
        self.frames = self.make_bottom_frames()

        # Make Notebooks to separate the CV and amperometry methods
        self.notebook = ttk.Notebook(self)
        self.sensor = sensor_frame.SensorFrame(self, self.notebook, graph_props)
        self.cv = cv_frame.CVFrame(self, self.notebook, graph_props)

        self.notebook.add(self.sensor, text="Settings")
        self.notebook.add(self.cv, text="Application")

        self.notebook.pack(side='top', expand=True, fill=tk.BOTH)
        tk.Label(self.frames[2], textvariable=self.voltage_source_label, font=("Bookman", 10)).pack(side='top')
        tk.Label(self.frames[2], textvariable=self.electrode_config_label, font=("Bookman", 10)).pack(side='top')
        
        # make a button to display connection settings and allow user to try to reconnect
        self.make_connect_button(self.frames[1])
        option_menu.OptionMenu(self)

    def make_connect_button(self, _frame):
        """ Make a button that will allow the user to connect to the amperometry device if it is
        available. This checks if a device is already connected (in which case it does nothing) and
         attempts to connect if a device is not already attached [see method connect for more
        details].
        The button will be red if no device is connected and green if it is connected, except on
        mac devices as there tcl (or something) does not allow the buttons to be colored
        :param _frame: tk frame to put the button in
        """
        self.connect_button = tk.Button(_frame, command=lambda: self.connect(self.connect_button))
        if not hasattr(self, "device"):  # if the device is not there just pass
            return

        if hasattr(self.device, "found"):
            if self.device.found and self.device.connected:
                self.connect_button.config(text="Connected", bg='green')
                # need to update later
            # if self.device.found and self.device.working:
            #     self.connect_button.config(text="Connected", bg='green')
            elif self.device.found:  # device i
                self.connect_button.config(text="Not Connected", bg='red')
            else:
                self.connect_button.config(text="Device Not Found", bg='red')
        else:
            self.connect_button.config(text="No Device", bg='red')
        self.connect_button.pack(side='bottom')

    def change_data_labels(self):
        """ Call a toplevel to allow the user to change data labels in the legend
        """
        change_top.ChangeDataLegend(self)

    def update_current_range(self, _value, current_limit):
        self.cv.set_tia_current_lim(_value, current_limit)

    def open_data(self):
        """ Open a csv file that has the data saved in it, in the same format as this program
        saves the data.  Check what type of
        NOTE:
        _data_hold - holds the data as its being pulled from the file with the structure
        _data_hold = [ [x-data-array], [y1-data-array], [y2-data-array], .., [yn-data] ]
        """
        logging.debug("opening data")
        _file_name = cv_frame.open_file('open')  # get a filename
        # Confirm that the user supplied a file
        if _file_name:

            logging.debug("a file named %s opened", _file_name)
            with open(_file_name, 'rb') as _file:
                _reader = csv.reader(_file)  # create reader from file

                first_array = _reader.next()  # get the first line that has the data labels
                first_element = first_array[0].split(":") if len(first_array) != 0 else ''
                # figure out what type of data was opened
                if len(first_array) > 0 and len(first_element) == 3:
                    # this is a cyclic voltammetry data
                    self.cv.open_data(_reader, first_array)
            _file.close()

    def user_select_delete_some_data(self):
        change_top.UserSelectDataDelete(self)

    def delete_all_data_user_prompt(self):
        change_top.UserDeleteDataWarning(self)

    def delete_all_data(self):
        """ Delete all the data collected so far and clear the lines from the plot area
        :return:
        """
        logging.debug("deletinga all data")
        # Delete all displayed lines
        self.cv.delete_all_data()

    def quit(self):
        """  Destroy the master """
        # self.destroy()
        destroyer()

    def connect(self, button=None):
        """ Function the connect button is attached to, to try to connect a amperometry PSoC device
        and display if the device is connected or not
        :param button: button the user clicks to try to connect the device
        """
        logging.debug("trying connecting")
        self.serialsettings = change_top.SerialSettingChanges(self.parent,self, None, None)
        if self.device.connected:
            logging.info("device is connected")
            if self.device.working:
                # If a device was just found then change the button's appearance
                if button:
                    button["text"] = 'Connected'
                    button.config(bg='green')
        else:
            logging.debug("attempting to connect")
            self.device = usb_comm.AmpUsb(self, self.device_params, self.serialsettings.port, self.serialsettings.speed)
            # If no device then try to connect
            if self.device.working:
                # If a device was just found then change the button's appearance
                if button:
                    button["text"] = 'Connected'
                    button.config(bg='green')
            else:
                logging.info("No Device detected")  # If still no device detected, warn the user

    def failed_connection(self):  # this is not working now
        logging.info("failed connection")

        # usb.util.dispose_resources()
        if hasattr(self, "device"):
            # self.device.destroy()
            pass
        if hasattr(self, "connect_button"):
            self.connect_button.config(text="Not Connected", bg='red')

    def make_bottom_frames(self):
        """ To pack the matplotlib toolbar and connect button in a nice layout make a frame along
        the bottom of the GUI and fill it with 3 'evenly' spaced frames
         :return: list of 3 frames to put toolbar, button, and VDAC label
        """
        # make frame to line the bottom of the GUI
        main_bottom = tk.Frame(self)
        main_bottom.pack(side='bottom', fill=tk.X)
        # make a list to fill with the 3 frames and pack them
        bottom_frame = []
        for i in range(3):
            bottom_frame.append(tk.Frame(main_bottom, width=220, height=35))
            bottom_frame[i].pack(side='left', fill=tk.X, expand=1)
        return bottom_frame


def destroyer():
    # app.quit()
    app.destroy()
    sys.exit()


def get_data_from_csv_file(_filename):
    with open(_filename, 'rb') as _file:
        _reader = csv.reader(_file)  # create reader from file

        first_array = _reader.next()  # get the first line that has the data labels
        _data_hold = []  # create a list to hold the data
        # Make lists to hold the voltage and data arrays
        for i in range(len(first_array)):  # make as many list as there columns in the csv file
            _data_hold.append([])

        for row in _reader:
            for i, data in enumerate(row):
                # _data_hold[i].append(float(data))
                _data_hold[i].append(data)
    _file.close()
    return _data_hold


def check_display_type():
    """ Check if matplotlib graph can be used,
    :return: type that can be used to make display graph, matplotlib or canvas as a string
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        return "matplotlib"
    except ImportError as e:
        return "canvas"

if __name__ == '__main__':
    app = ElectroChemGUI()
    app.protocol("WM_DELETE_WINDOW", destroyer)
    app.title("E-Nose Application")
    app.iconbitmap(r'favicon.ico')
    app.geometry("850x400")
    app.mainloop()