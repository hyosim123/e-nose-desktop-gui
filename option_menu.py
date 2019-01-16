""" Option menu for electrochemical device
"""
# standard libraries
import logging
import Tkinter as tk
# local files
import change_toplevel

__author__ = 'Kyle Vitatuas Lopin'


class OptionMenu(tk.Menu):
    """
    Make the option menu for the electrochemical device
    """
    def __init__(self, master):
        """ Make the options menu for the application
        :param master: root
        """
        tk.Menu.__init__(self, master=master)
        # Make the main menu to put all the submenus on
        menubar = tk.Menu(master)
        # Make a menus along the top of the gui
        file_menu = tk.Menu(menubar, tearoff=0)
        data_menu = tk.Menu(menubar, tearoff=0)
        about_menu = tk.Menu(menubar, tearoff=0)
        # Different options the user can change
        make_file_option_menu(file_menu, master)
        make_data_menu(data_menu, master)
        make_about_menu(about_menu, master)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Data", menu=data_menu)
        menubar.add_cascade(label="About", menu=about_menu)

        master.config(menu=menubar)


def make_data_menu(data_menu, master):
    """ Make command to add to the "Data" option in the menu, to modify the data
    :param data_menu: tk.Menu to add the commands to
    :param master: master menu
    """
    data_menu.add_command(label="Save All Data",
                          command=master.cv.save_all_data)
    data_menu.add_command(label="Delete all data traces",
                          command=master.delete_all_data_user_prompt)


def make_file_option_menu(file_menu, master):
    """ Make command to add to the "File" option in the menu
    :param file_menu: tk.Menu to add the commands to
    :param master: menu master
    """
    file_menu.add_command(label="Open",
                          command=master.open_data)

    # file_menu.add_command(label="Select Data to Save",
    #                       command=master.save_selected_data)
    file_menu.add_separator()
    file_menu.add_command(label="Quit",
                          command=master.quit)

def set_smoothing_value(master, value):
    logging.info("setting smoothing value: {0}".format(value))
    master.device.samples_to_smooth = value


# def set_voltage_source(master, value):
#     """ Set the user selection to the device, device class handles this so just
#     pass the selection along
#     TODO: confirm this works
#     :param master: root tk.TK
#     :param value: value user selected
#     """
#     print 'option menu 112: ', value
#     master.device.select_voltage_source(value)


def set_user_label_option(master, value):
    """ Set the labe the user entered
    :param master: root master
    :param value: value user entered
    """
    master.graph.user_sets_labels_after_run = value

def make_about_menu(about_menu, master):
    about_menu.add_cascade(label="About", command=lambda: change_toplevel.About(master))
