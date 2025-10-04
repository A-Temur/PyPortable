import io
import os
import re
import shutil
import subprocess
import sys
import zipfile

import requests

from gui_context import GuiContext


def user_feedback(text_=""):
    if gui_mode:
        GuiContext.user_feedback(text_)
    elif cli_mode:
        # used for cli feedback
        print(text_)
    else:
        # for context menu feedback
        pass

if __name__ == "__main__":

    try:
        if sys.argv[2] == "gui":
            gui_mode = True
            cli_mode = False
    except IndexError:
        gui_mode = False
        cli_mode = True

    desired_program_name = sys.argv[1][0]
    main_project_dir = sys.argv[1][1]
    output_project_dir = sys.argv[1][2]
    python_file_location = sys.argv[1][3]
    desired_python_version = sys.argv[1][4]

    pyportable_dir = output_project_dir + f"/{desired_program_name}_PyPortable"
    requirementstxt_path = pyportable_dir + f"/{desired_program_name}/requirements.txt"
    python_ftp_url = "https://www.python.org/ftp/python/"

    os.mkdir(output_project_dir)
    os.mkdir(pyportable_dir)

    # copy original_project_dir contents to pyportable dir
    user_feedback("Copying files to new location")
    shutil.copytree(main_project_dir, pyportable_dir + f"/{desired_program_name}", dirs_exist_ok=True)


    # download and extract (py embeddable)
    user_feedback("Downloading and extracting python embeddable zip")
    zip_url = f"{python_ftp_url}{desired_python_version}/python-{desired_python_version}-embed-amd64.zip"
    response = requests.get(zip_url)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(pyportable_dir)  # Set your path here


    # copy get-pip.py to the pyportable_dir
    user_feedback("Copying get-pip and modifying _pth files")
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

    # install pip via get-pip
    user_feedback("Installing pip")
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
    user_feedback("Installing requirements.txt")
    subprocess.Popen(
        f"{pyportable_dir}/python.exe {pyportable_dir}/Scripts/pip.exe install -r {pyportable_dir}/{desired_program_name}/requirements.txt",
        shell=True).wait()

    # create vbs script inside new dir (name of vbs filename same as python_file)
    user_feedback("Creating VBS Script")
    python_filename = os.path.splitext(os.path.basename(python_file_location))[0]
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
    modified_content = modified_content.replace('{out_dir}', output_project_dir)
    modified_content = modified_content.replace('{shortcut_source}', source_vbs_path)
    modified_content = modified_content.replace('{shortcut_destination}', f'{output_project_dir}/{python_filename}.vbs')
    modified_content = modified_content.replace('{shortcut_name}', f'{desired_program_name}')

    # replace the slashes with backslash
    modified_content = modified_content.replace('/', '\\')

    # open file (create file when it doesn't exist)
    with open("sources/create_shortcut_custom.vbs", 'w') as vbs_writer:
        vbs_writer.write(modified_content)

    # get full path of the create_shortcut.vbs
    path_to_create_shortcut_vbs = os.path.abspath("sources/create_shortcut_custom.vbs")

    subprocess.Popen(f"cscript {path_to_create_shortcut_vbs}", shell=True).wait()