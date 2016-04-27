# A script to install all requirements from all plugins
import glob
import os

requirements_base = os.path.join(os.path.dirname(__file__), 'base_requirements.txt')
local_txt_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(local_txt_file, 'w+') as output_file:
    for filename in glob.iglob('lessons/**/requirements.txt'):
        with open(filename, 'r') as input_file:
            plugin_name = os.path.basename(os.path.dirname(filename))
            output_file.write("######## {} requirements #########\n".format(plugin_name))
            output_file.write(input_file.read())
            output_file.write("\n\n###### end {} requirements #######\n\n".format(plugin_name))

    with open(requirements_base, 'r') as input_file:
        output_file.write(input_file.read())

# os.system("easy_install install pip")
os.system("pip install -r {}".format(local_txt_file))
