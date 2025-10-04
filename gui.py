import os
import re
import runpy
import sys

import customtkinter
import requests

import gui_context
import gui_template


class Sub(gui_template.MainWindow):

    def fetch_python_versions(self):
        try:
            url = "https://www.python.org/ftp/python/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # Regex to find version numbers like 3.9.13, ignoring release candidates etc.
            versions = re.findall(r'href="(\d+\.\d+\.\d+)/"', response.text)
            # Remove duplicates and sort descending
            unique_versions = sorted(list(set(versions)), key=lambda v: list(map(int, v.split('.'))), reverse=True)
            self.python_versions_list = unique_versions
            self.python_versions_dropdown.configure(values=unique_versions)
            print(unique_versions)

            self.init_progressbar.destroy()
            self.init_progressbar = None


        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            print(f"Error fetching Python versions: {e}")
            # Fallback to a list of common versions if the fetch fails
            return self.python_versions_list

    # noinspection PyUnusedLocal
    def validate_python_version(self, *args):
        current_value = self.python_version_var.get()
        if current_value in self.python_versions_list:
            self.python_versions_dropdown.configure(border_color=self.original_border_color)
            self.python_version_error_label.configure(text="Python Version matches FTP directory.", text_color="green")
            self.python_version_var.required_condition_met = True
            if self.required_conditions_met:
                self.run_when_required_conditions_met()

        else:
            self.python_versions_dropdown.configure(border_color="red")
            self.python_version_error_label.configure(
                text="Invalid version. Please select a valid version from the list or look at https://www.python.org/ftp/python/", text_color="red")
            self.python_version_var.required_condition_met = False



    def submit(self):
        submit_progress = gui_template.PopupProgressBarWindow(self.main_frame, "Making your application PyPortable", "...")

        gui_context.GuiContext.set_gui_ref(submit_progress.update)

        # Save original argv
        original_argv = sys.argv.copy()

        args = [self.program_name_entry.get(), self.main_project_dir.target_dir.get(), self.output_project_dir.target_dir.get(), self.python_file_location.target_dir.get(), self.python_version_var.get()]

        # Set custom arguments
        sys.argv = ['main.py', args, "gui"]

        runpy.run_module('main', run_name="__main__", alter_sys=True)

        # Restore original sys.argv
        sys.argv = original_argv

        submit_progress.destroy()
        # noinspection PyUnusedLocal
        submit_progress = None

        # noinspection PyUnusedLocal
        success = gui_template.PopupDialogWindow(self, "Finished", "PyPortable application created successfully!", "Open Folder")

        # open containing folder
        os.startfile(self.output_project_dir.target_dir.get())


    def run_when_required_conditions_met(self):
        self.submit_button.configure(fg_color="green")



    def __init__(self):
        super().__init__("PyPortable", 883, 485, app_logo="PyPortableLogo.png")

        self.program_name_frame = customtkinter.CTkFrame(self.main_frame)
        self.program_name_frame.grid_columnconfigure(0, weight=1)
        self.program_name_frame.grid_columnconfigure(1, weight=1)
        self.program_name_frame.pack(fill="both")

        self.directory_frame = customtkinter.CTkFrame(self.main_frame)
        self.directory_frame.grid_columnconfigure(1, weight=1)
        self.directory_frame.pack(fill="both")

        self.python_version_dropdown_frame = customtkinter.CTkFrame(self.main_frame)
        self.python_version_dropdown_frame.grid_columnconfigure(0, weight=1)
        self.python_version_dropdown_frame.grid_columnconfigure(1, weight=1)
        self.python_version_dropdown_frame.pack(fill="both")

        self.submit_button_frame = customtkinter.CTkFrame(self.main_frame)
        self.submit_button_frame.grid_columnconfigure(0, weight=1)
        self.submit_button_frame.pack(fill="both")

        #  --------------------------------------------------------------------------------------
        self.python_versions_list = ["3.12.4", "3.12.3", "3.12.2", "3.12.1", "3.12.0", "3.11.9", "3.11.8", "3.11.7", "3.11.6", "3.11.5",
                        "3.11.4", "3.11.3", "3.11.2", "3.11.1", "3.11.0", "3.10.14", "3.10.13", "3.10.12", "3.10.11",
                        "3.10.10", "3.10.9", "3.10.8", "3.10.7", "3.10.6", "3.10.5", "3.10.4", "3.10.3", "3.10.2",
                        "3.10.1", "3.10.0", "3.9.19", "3.9.18", "3.9.17", "3.9.16", "3.9.15", "3.9.14", "3.9.13"]


        # Program Frame WIDGETS --------------------------------------------------------------------------------------

        self.program_name_label = customtkinter.CTkLabel(self.program_name_frame, text="Program Name")
        self.program_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.program_name_entry = customtkinter.CTkEntry(self.program_name_frame, placeholder_text="MyApp", width=300)
        self.program_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.required_widgets.append(self.program_name_entry)

        # Directory Frame WIDGETS --------------------------------------------------------------------------------------

        self.main_project_dir = gui_template.DirectoryInputTemplate(self.directory_frame, self.select_dir_dialog, 1,
                            "Select your Projects directory", "Enter Path or select Browse Button", "Browse")
        self.required_widgets.append(self.main_project_dir.target_dir)

        self.output_project_dir = gui_template.DirectoryInputTemplate(self.directory_frame, self.select_dir_dialog,
                                                     2,
                                                     "Select output location", "Where your Portable App will be saved", "Browse")
        self.required_widgets.append(self.output_project_dir.target_dir)

        self.python_file_location = gui_template.DirectoryInputTemplate(self.directory_frame, self.select_file_dialog,
                                             3,
                                             "Select the main python file to execute", "Path to your main python file", "Browse")
        self.required_widgets.append(self.python_file_location.target_dir)


        # PYTHON VERSION WIDGETS --------------------------------------------------------------------------------------

        self.python_version_label = customtkinter.CTkLabel(self.python_version_dropdown_frame, text="Select or Enter Python Version:")
        self.python_version_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.python_version_var = customtkinter.StringVar()
        self.python_version_var.set(self.python_versions_list[0])

        self.python_versions_dropdown = customtkinter.CTkComboBox(self.python_version_dropdown_frame,
                                                                  values=self.python_versions_list,
                                                                  variable=self.python_version_var)
        self.python_versions_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.original_border_color = self.python_versions_dropdown.cget("border_color")
        self.python_version_var.trace_add("write", self.validate_python_version)

        self.python_version_error_label = customtkinter.CTkLabel(self.python_version_dropdown_frame,
                                                                 text="The version must be available on https://www.python.org/ftp/python/")
        self.python_version_error_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        self.reset_required_fields()

        # Reset required fields exception --------------------------------------------------------------------------------------
        self.python_version_var.required_condition_met = True
        self.required_widgets.append(self.python_version_var)

        # Submit Frame WIDGETS --------------------------------------------------------------------------------------
        self.submit_button = customtkinter.CTkButton(self.submit_button_frame, text="Create PyPortable Application", command=self.submit)
        self.submit_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.init_progressbar = gui_template.PopupProgressBarWindow(self.main_frame, "Loadin", "Fetching available Python versions...")
        # noinspection PyTypeChecker
        self.after(1000, self.fetch_python_versions)



if __name__ == '__main__':
    app = Sub()
    app.mainloop()

