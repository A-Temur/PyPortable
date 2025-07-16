"""
Copyright 2025 github.com/A-Temur, Abdullah Temur. All rights reserved.
"""

import io
import os
import re
import shutil
import subprocess
import webbrowser
import zipfile
from tkinter import filedialog

import customtkinter
import requests
from PIL import Image


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("PyPortable")
        # Increased height to make space for the logo
        self.geometry("757x474")

        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.grid_columnconfigure(1, weight=1)
        # # Configure column 0 to have equal weight for centering the logo
        # self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.GITHUB_URL = "https://github.com/A-Temur"
        self.KOFI_URL = "https://ko-fi.com/your-username"

        # --- 2. Load and Add Logo ---
        try:
            gh_image_data = Image.open("media/github-mark-white.png")
            gh_image = customtkinter.CTkImage(gh_image_data, gh_image_data, (50, 50))

            gh_label = customtkinter.CTkLabel(self, image=gh_image, text="")
            gh_label.grid(row=0, column=0, pady=(20, 10), sticky="e")

            # Make the label clickable
            gh_label.bind("<Button-1>", lambda e: self.open_link(self.GITHUB_URL))
            # Change cursor to a hand when hovering over the icon
            gh_label.configure(cursor="hand2")

            # Open the image using Pillow
            logo_image_data = Image.open("media/PyPortableLogo.png")
            # Create a CTkImage object
            logo_image = customtkinter.CTkImage(
                dark_image=logo_image_data,
                light_image=logo_image_data,
                size=(112, 112)  # Adjust size as needed
            )
            # Create a label to display the image. 
            # columnspan=3 makes it span all columns, allowing it to be centered.
            logo_label = customtkinter.CTkLabel(self, image=logo_image, text="")
            logo_label.grid(row=0, column=1, pady=(20, 10))

            kofi_image_data = Image.open("media/support_me_on_kofi_badge_blue.png")
            kofi_image = customtkinter.CTkImage(kofi_image_data, kofi_image_data, (80, 50))

            kofi_label = customtkinter.CTkLabel(self, image=kofi_image, text="")
            kofi_label.grid(row=0, column=2, pady=(20, 10), sticky="w")

            # Make the label clickable
            kofi_label.bind("<Button-1>", lambda e: self.open_link(self.KOFI_URL))
            # Change cursor to a hand when hovering over the icon
            kofi_label.configure(cursor="hand2")


        except FileNotFoundError:
            # Fallback if logo.png is not found
            logo_label = customtkinter.CTkLabel(self, text="My Application", font=("Arial", 24))
            logo_label.grid(row=0, column=1, olumnspan=3, pady=(20, 10))


        # 3. Select your Projects directory:
        self.dir1_label = customtkinter.CTkLabel(self, text="Select your Projects directory:")
        self.dir1_label.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="w")
        # ... (rest of the widgets)
        self.original_project_dir = customtkinter.CTkEntry(self, placeholder_text="Select directory...")
        self.original_project_dir.grid(row=1, column=1, padx=10, pady=(10, 5), sticky="ew")
        self.dir1_button = customtkinter.CTkButton(self, text="Browse...", command=self.select_first_directory)
        self.dir1_button.grid(row=1, column=2, padx=10, pady=(10, 5))

        # 4. Select output directory location
        self.dir2_label = customtkinter.CTkLabel(self, text="Select output directory location:")
        self.dir2_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.out_dir = customtkinter.CTkEntry(self,
                                              placeholder_text="Select the location of the resulting PyPortable output...")
        self.out_dir.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.dir2_button = customtkinter.CTkButton(self, text="Browse...", command=self.select_second_directory)
        self.dir2_button.grid(row=2, column=2, padx=10, pady=5)

        # 5. Select the main python file to execute
        self.desired_python_file_label = customtkinter.CTkLabel(self, text="Select the main python file to execute:")
        self.desired_python_file_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.desired_python_file = customtkinter.CTkEntry(self, placeholder_text="Select python file...")
        self.desired_python_file.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.desired_python_file_browser = customtkinter.CTkButton(self, text="Browse...",
                                                    command=lambda: self.select_file(self.desired_python_file,
                                                                                     [("Python Files", "*.py")]))
        self.desired_python_file_browser.grid(row=3, column=2, padx=10, pady=5)

        # 6. String Inputs
        # self.desired_program_name_label = customtkinter.CTkLabel(self, text="Name of your Program/Project:")
        # self.desired_program_name_label.grid(row=4, column=0, padx=10, pady=(20, 5), sticky="w")
        # self.desired_program_name = customtkinter.CTkEntry(self, placeholder_text="SampleProject")
        # self.desired_program_name.grid(row=4, column=1, columnspan=2, padx=10, pady=(20, 5), sticky="ew")

        self.python_version_label = customtkinter.CTkLabel(self, text="Python Version:")
        self.python_version_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.python_versions_list = self.get_python_versions()
        self.python_version_var = customtkinter.StringVar()

        self.python_version = customtkinter.CTkComboBox(self,
                                                        values=self.python_versions_list,
                                                        variable=self.python_version_var)  # Make dropdown scrollable
        self.python_version.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        if self.python_versions_list:
            self.python_version.set(self.python_versions_list[0])

        self.original_border_color = self.python_version.cget("border_color")
        self.python_version_var.trace_add("write", self.validate_python_version)

        self.python_version_error_label = customtkinter.CTkLabel(self,
                                                                 text="The version must be available on https://www.python.org/ftp/python/")
        self.python_version_error_label.grid(row=5, column=1, columnspan=2, padx=10, sticky="w")

        # 7. Custom Python Path Toggle and Input
        self.custom_path_switch = customtkinter.CTkSwitch(self, text="Custom embeddable Python ZIP",
                                                          command=self.toggle_custom_path_entry)
        self.custom_path_switch.grid(row=6, column=0, padx=10, sticky="w")
        self.custom_path_entry = customtkinter.CTkEntry(self,
                                                        placeholder_text="Path to your python-x.x.x-embed-amd64.zip",
                                                        state="disabled")
        self.custom_path_entry.grid(row=6, column=1, padx=10, sticky="ew")

        # 8. Submit Button
        self.submit_button = customtkinter.CTkButton(self, text="Create PyPortable Application", command=self.submit)
        self.submit_button.grid(row=7, column=1, columnspan=2, padx=10, pady=(20, 10), sticky="e")

    def validate_python_version(self, *args):
        current_value = self.python_version_var.get()
        if current_value in self.python_versions_list:
            self.python_version.configure(border_color=self.original_border_color)
            self.python_version_error_label.configure(text="Version matches FTP directory.", text_color="green")

        else:
            self.python_version.configure(border_color="red")
            self.python_version_error_label.configure(
                text="Invalid version. Please select a valid version from the list.", text_color="red")

    def get_python_versions(self):
        try:
            url = "https://www.python.org/ftp/python/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            # Regex to find version numbers like 3.9.13, ignoring release candidates etc.
            versions = re.findall(r'href="(\d+\.\d+\.\d+)/"', response.text)
            # Remove duplicates and sort descending
            unique_versions = sorted(list(set(versions)), key=lambda v: list(map(int, v.split('.'))), reverse=True)
            return unique_versions
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            print(f"Error fetching Python versions: {e}")
            # Fallback to a list of common versions if the fetch fails
            return ["3.12.4", "3.12.3", "3.12.2", "3.12.1", "3.12.0", "3.11.9", "3.11.8", "3.11.7", "3.11.6", "3.11.5",
                    "3.11.4", "3.11.3", "3.11.2", "3.11.1", "3.11.0", "3.10.14", "3.10.13", "3.10.12", "3.10.11",
                    "3.10.10", "3.10.9", "3.10.8", "3.10.7", "3.10.6", "3.10.5", "3.10.4", "3.10.3", "3.10.2",
                    "3.10.1", "3.10.0", "3.9.19", "3.9.18", "3.9.17", "3.9.16", "3.9.15", "3.9.14", "3.9.13"]

    def toggle_custom_path_entry(self):
        if self.custom_path_switch.get() == 1:
            self.custom_path_entry.configure(state="normal")
        else:
            self.custom_path_entry.configure(state="disabled")

    def select_file(self, target_entry_widget, file_types=None):
        initial_dir = self.original_project_dir.get()
        if not initial_dir:
            initial_dir = "/"
        filepath = filedialog.askopenfilename(initialdir=initial_dir, filetypes=file_types)
        if filepath:
            target_entry_widget.delete(0, "end")
            target_entry_widget.insert(0, filepath)

    def select_first_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.original_project_dir.delete(0, "end")
            self.original_project_dir.insert(0, path)

    def select_second_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.out_dir.delete(0, "end")
            self.out_dir.insert(0, path)

    def submit(self):
        print("Submit button clicked")
        desired_program_name = os.path.basename(self.original_project_dir.get())
        out_dir = self.out_dir.get() + f"/{desired_program_name}"
        pyportable_dir = out_dir + "/PyPortable"

        os.mkdir(out_dir)
        os.mkdir(pyportable_dir)

        # copy original_project_dir contents to pyportable dir
        shutil.copytree(self.original_project_dir.get(), pyportable_dir + f"/{desired_program_name}", dirs_exist_ok=True)

        # extract local zip or download and extract (py embeddable)
        if self.custom_path_switch.get() == 1:
            with zipfile.ZipFile(self.custom_path_entry.get()) as custom_zip_file:
                custom_zip_file.extractall(pyportable_dir)
        else:
            zip_url = f"https://www.python.org/ftp/python/{self.python_version.get()}/python-{self.python_version.get()}-embed-amd64.zip"
            response = requests.get(zip_url)
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(pyportable_dir)  # Set your path here

        # copy get-pip.py to the pyportable_dir
        shutil.copy("sources/get-pip.py", pyportable_dir)
        # uncomment the import site statement found on the ._pth file
        # search for the file, which ends with ._pth
        for file in os.listdir(pyportable_dir):
            if file.endswith("._pth"):
                with open(pyportable_dir + "/" + file, 'r') as pth_reader:
                    pth_content = pth_reader.read()
                with open(pyportable_dir + "/" + file, 'w') as pth_writer:
                    modified_pth = re.sub(r"^(\s*)#\s*(import\s+site)", r"\1\2", pth_content, flags=re.MULTILINE)
                    pth_writer.write(modified_pth)
                break

        requirementstxt_path = pyportable_dir + f"/{desired_program_name}/requirements.txt"
        # install pip via get-pip
        subprocess.Popen(f"{pyportable_dir}/python.exe {pyportable_dir}/get-pip.py", shell=True).wait()

        # # Install pip-tools
        # subprocess.Popen(
        #     f"{pyportable_dir}/python.exe -m {pyportable_dir}/Scripts/pip.exe install pip-tools",
        #     shell=True).wait()
        # # Generate requirements with all dependencies
        # subprocess.Popen(
        #     f"{pyportable_dir}/python.exe -m pip-tools compile {requirementstxt_path} --output-file {pyportable_dir}/requirements_compiled.txt",
        #     shell=True).wait()
        # # Install everything
        # subprocess.Popen(f"{pyportable_dir}/python.exe -m {pyportable_dir}/Scripts/pip.exe install -r {pyportable_dir}/requirements_compiled.txt",
        #                  shell=True).wait()

        # install requirements
        subprocess.Popen(
            f"{pyportable_dir}/python.exe {pyportable_dir}/Scripts/pip.exe install -r {pyportable_dir}/{desired_program_name}/requirements.txt",
            shell=True).wait()

        # create vbs script inside new dir (name of vbs filename same as python_file)
        python_filename = os.path.splitext(os.path.basename(self.desired_python_file.get()))[0]
        source_vbs_path = pyportable_dir + f"/{desired_program_name}/{python_filename}.vbs"
        with open("sources/runner.vbs", 'r') as runner_reader:
            runner_content = runner_reader.read()
        with open(source_vbs_path, 'w') as vbs_writer:
            # the vbs script just needs to execute the desired_python_file via the pyportable/pythonw.exe
            modified_runner = runner_content.replace('{desired_python_file}', python_filename + '.py')
            vbs_writer.write(modified_runner)

        # create shortcut of vbs script on root dir (out_dir)
        with open("sources/create_shortcut.vbs", 'r') as vbs_reader:
            vbs_content = vbs_reader.read()

        vbs_script_dir = pyportable_dir + f"/{desired_program_name}"

        modified_content = vbs_content.replace('{vbs_script_dir}', vbs_script_dir)
        modified_content = modified_content.replace('{out_dir}', out_dir)
        modified_content = modified_content.replace('{shortcut_source}', source_vbs_path)
        modified_content = modified_content.replace('{shortcut_destination}', f'{out_dir}/{python_filename}.vbs')
        modified_content = modified_content.replace('{shortcut_name}', f'{desired_program_name}')

        # replace the slashes with backslash
        modified_content = modified_content.replace('/', '\\')

        # open file (create file when it doesn't exists)
        with open("sources/create_shortcut_custom.vbs", 'w') as vbs_writer:
            vbs_writer.write(modified_content)

        # get full path of the create_shortcut.vbs
        path_to_create_shortcut_vbs = os.path.abspath("sources/create_shortcut_custom.vbs")

        subprocess.Popen(f"cscript {path_to_create_shortcut_vbs}", shell=True).wait()

        # inform the user about operations completed

        success_dialog = customtkinter.CTkToplevel(self)
        success_dialog.title("Success")
        success_dialog.geometry("300x100")

        success_label = customtkinter.CTkLabel(success_dialog, text="PyPortable application created successfully!")
        success_label.pack(pady=20)

        ok_button = customtkinter.CTkButton(success_dialog, text="OK", command=self.destroy)
        ok_button.pack()

        success_dialog.transient(self)
        success_dialog.grab_set()
        self.wait_window(success_dialog)

    # --- 4. Add a method to open links ---
    def open_link(self, url):
        """Opens the given URL in a new browser tab."""
        webbrowser.open_new_tab(url)
        print(f"Opening {url}...")


if __name__ == '__main__':
    app = App()
    app.mainloop()
