import webbrowser
from tkinter import filedialog

import customtkinter
from PIL import Image


def center_window(window, width, height):
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate center position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    # Set window geometry
    window.geometry(f"{width}x{height}+{x}+{y}")

class MainWindow(customtkinter.CTk):
    @property
    def required_conditions_met(self):
        all_bool = [x.required_condition_met for x in self.required_widgets]
        return all(all_bool)


    @staticmethod
    def open_link(url):
        """Opens the given URL in a new browser tab."""
        webbrowser.open_new_tab(url)
        print(f"Opening {url}...")


    @staticmethod
    def select_dir_dialog(target_entry_widget):
        path = filedialog.askdirectory()
        if path:
            target_entry_widget.delete(0, "end")
            target_entry_widget.insert(0, path)

    @staticmethod
    def select_file_dialog(target_entry_widget):
        path = filedialog.askopenfilename()
        if path:
            target_entry_widget.delete(0, "end")
            target_entry_widget.insert(0, path)


    def add_logo(self):
        gh_image_data = Image.open(f"{self.media_path}{self.github_logo}")
        gh_image = customtkinter.CTkImage(gh_image_data, gh_image_data, (50, 50))

        gh_label = customtkinter.CTkLabel(self.logo_frame, image=gh_image, text="")
        gh_label.grid(row=0, column=0, sticky="e", padx=15)

        # Make the label clickable
        gh_label.bind("<Button-1>", lambda e: self.open_link(self.GITHUB_URL))
        # Change cursor to a hand when hovering over the icon
        gh_label.configure(cursor="hand2")

        # Open the image using Pillow
        logo_image_data = Image.open(f"{self.media_path}{self.app_logo}")
        # Create a CTkImage object
        logo_image = customtkinter.CTkImage(
            dark_image=logo_image_data,
            light_image=logo_image_data,
            size=(112, 112)  # Adjust size as needed
        )
        # Create a label to display the image.
        # columnspan=3 makes it span all columns, allowing it to be centered.
        logo_label = customtkinter.CTkLabel(self.logo_frame, image=logo_image, text="")
        logo_label.grid(row=0, column=1)

        kofi_image_data = Image.open(f"{self.media_path}{self.kofi_logo}")
        kofi_image = customtkinter.CTkImage(kofi_image_data, kofi_image_data, (80, 50))

        kofi_label = customtkinter.CTkLabel(self.logo_frame, image=kofi_image, text="")
        kofi_label.grid(row=0, column=2, sticky="w")

        # Make the label clickable
        kofi_label.bind("<Button-1>", lambda e: self.open_link(self.KOFI_URL))
        # Change cursor to a hand when hovering over the icon
        kofi_label.configure(cursor="hand2")

    def on_close(self):
        self.destroy()

    def reset_required_fields(self):
        for required_widget in self.required_widgets:
            required_widget.required_condition_met = False
            required_widget.configure(border_color="green")

            required_widget.configure(validate='key',
                                  validatecommand=self.register_validation(required_widget))

    # noinspection PyProtectedMember
    def validate_input(self, action, new_value):
        print(action[0])
        print(new_value._placeholder_text)
        val = action[0]
        placeholder_text = new_value._placeholder_text

        if val != placeholder_text:
            new_value.configure(border_color="black")
            new_value.insert(0, val)
            new_value.required_condition_met = True
            if self.required_conditions_met:
                self.run_when_required_conditions_met()
            return None

        return True


    def register_validation(self, entry):
        return (self.register(
            lambda *args: self.validate_input(
                args,
                entry)), "%S")

    # function to run when all required widgets are succesfully validated
    def run_when_required_conditions_met(self):
        pass



    def __init__(self, title, width, height, app_logo="metabooster_logo_rounded.png"):
        super().__init__()
        self.title(title)
        center_window(self, width, height)

        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("dark-blue")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # default logo/media path
        self.media_path = "media/"
        self.app_logo = app_logo
        self.GITHUB_URL = "https://github.com/A-Temur"
        self.github_logo = "github-mark-white.png"
        self.KOFI_URL = "https://ko-fi.com/your-username"
        self.kofi_logo = "support_me_on_kofi_badge_blue.png"


        # create logo frame
        self.logo_frame = customtkinter.CTkFrame(self.main_frame)
        # self.logo_frame.grid_rowconfigure(0, weight=1)
        self.logo_frame.grid_columnconfigure(0, weight=1)
        self.logo_frame.grid_columnconfigure(1, weight=1)
        self.logo_frame.grid_columnconfigure(2, weight=1)
        self.logo_frame.pack(fill="both", pady=(0, 10))

        self.add_logo()

        # simply append CTKEntry's which are required
        self.required_widgets = []

        # holds all widgets
        self.widgets = []
        self.protocol("WM_DELETE_WINDOW", self.on_close)



class DirectoryInputTemplate:
    def __init__(self, parent:customtkinter.CTkFrame, select_dir_dialog, row_number:int, text_label:str, directory_label:str, directory_button_label:str):
        self.dir1_label = customtkinter.CTkLabel(parent, text=text_label)
        self.dir1_label.grid(row=row_number, column=0, padx=10, pady=10, sticky="w")

        self.target_dir = customtkinter.CTkEntry(parent, placeholder_text=directory_label)
        self.target_dir.grid(row=row_number, column=1, padx=10, pady=10, sticky="ew")
        self.dir1_button = customtkinter.CTkButton(parent, text=directory_button_label,
                                                   command=lambda: select_dir_dialog(self.target_dir))
        self.dir1_button.grid(row=row_number, column=2, padx=10, pady=10, sticky="e")


class TextInputTemplate:
    def __init__(self, parent:customtkinter.CTkFrame, row_number, text_label, placeholder_text):
        self.label = customtkinter.CTkLabel(parent, text=text_label)
        self.label.grid(row=row_number, column=0, padx=10, pady=10, sticky="w")
        self.entry = customtkinter.CTkEntry(parent, placeholder_text=placeholder_text)
        self.entry.grid(row=row_number, column=1, padx=10, pady=10, sticky="ew")



class PopupProgressBarWindow:
    def __init__(self, mainwindow:customtkinter.CTk, title, text):
        self.main_window = mainwindow
        self.window = customtkinter.CTkToplevel(mainwindow)
        # remove default title bar
        self.window.overrideredirect(True)

        self.window.title(title)
        center_window(self.window, 500, 70)

        self.progress_bar = customtkinter.CTkProgressBar(self.window, mode="indeterminate", width=300)
        self.progress_bar.pack(pady=10)
        self.progress_label = customtkinter.CTkLabel(self.window, text=text, font=("Arial", 12))
        self.progress_label.pack()

        self.progress_bar.start()

        self.window.transient(mainwindow)
        self.window.wait_visibility()
        # grab_set and focus force must be invoked from parent window when using focus_force on child
        self.window.focus_force()

        self.window.grab_set()

    def update(self, text=""):
        if bool(text):
            self.progress_label.configure(text=text)
        self.progress_bar.update()

    def destroy(self):
        self.progress_bar.stop()
        self.window.destroy()
        self.window = None
        self.main_window.focus_force()
        self.main_window.grab_set()


class PopupDialogWindow:
    def __init__(self, mainwindow:customtkinter.CTk, title, text_, button_text="OK"):
        self.window = customtkinter.CTkToplevel(mainwindow)
        self.window.title(title)
        center_window(self.window, 300, 100)

        dialog_label_ = customtkinter.CTkLabel(self.window, text=text_)
        dialog_label_.pack(pady=20)

        ok_button = customtkinter.CTkButton(self.window, text=button_text, command=self.destroy)
        ok_button.pack()

        self.window.transient(mainwindow)
        self.window.wait_visibility()
        self.window.grab_set()
        mainwindow.wait_window(self.window)

    def destroy(self):
        self.window.destroy()
        self.window = None






# Example
# class Sub(MainWindow):
#
#     def __init__(self):
#         super().__init__("PyPortable", 757, 474)
#
#         self.program_name_frame = customtkinter.CTkFrame(self.main_frame)
#         self.program_name_frame.grid_columnconfigure(1, weight=1)
#         self.program_name_frame.pack(fill="both")
#
#         self.directory_frame = customtkinter.CTkFrame(self.main_frame)
#         self.directory_frame.grid_columnconfigure(1, weight=1)
#         self.directory_frame.pack(fill="both")
#
#         self.python_version_dropdown_frame = customtkinter.CTkFrame(self.main_frame)
#         self.python_version_dropdown_frame.grid_columnconfigure(0, weight=1)
#         self.python_version_dropdown_frame.grid_columnconfigure(1, weight=1)
#         self.python_version_dropdown_frame.pack(fill="both")
#
#
#         self.program_name_widget = TextInputTemplate(self.program_name_frame, 0, "Program Name", "MyApp")
#         self.required_widgets.append(self.program_name_widget.entry)
#
#         self.main_project_dir = DirectoryInputTemplate(self.directory_frame, self.select_dir_dialog, 1,
#                             "Select your Projects directory", "Enter Path or select Browse Button", "Browse")
#         self.required_widgets.append(self.main_project_dir.target_dir)
#
#         self.output_project_dir = DirectoryInputTemplate(self.directory_frame, self.select_dir_dialog,
#                                                      2,
#                                                      "Select output location", "Where your Portable App will be saved", "Browse")
#         self.required_widgets.append(self.output_project_dir.target_dir)
#
#         self.python_file_location = DirectoryInputTemplate(self.directory_frame, self.select_file_dialog,
#                                              3,
#                                              "Select the main python file to execute", "Path to your main python file", "Browse")
#         self.required_widgets.append(self.python_file_location.target_dir)
#
#
#
#         self.python_version_label = customtkinter.CTkLabel(self.python_version_dropdown_frame, text="Python Version:")
#         self.python_version_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
#         self.python_version_var = customtkinter.StringVar()
#         self.python_version = customtkinter.CTkComboBox(self.python_version_dropdown_frame,
#                                                         values=["TMP", "TMP2"],
#                                                         variable=self.python_version_var)
#         self.python_version.grid(row=0, column=1, padx=10, pady=5, sticky="w")
#
#
#         self.reset_required_fields()