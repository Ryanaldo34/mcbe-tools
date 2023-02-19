# Minecraft Bedrock Edition Tools

CLI Developer Tools For Minecraft Bedrock Edition Developers to speed up our development time

# Installation

- First off, start by downloading the latest version of [python](https://www.python.org/downloads/)
- Next, download the latest release of mcbe-tools from this repository. It should be a zip archive. You will then unzip it in the desired location. Make sure that this is somewhere you will remember or is easy to get to, as you will need the location to run the script.
- Next, you will want to copy the path to the requirements.txt file in the mcbe-tools/src folder. You will then paste that path and run this command in a terminal or windows powershell `pip install -r path/to/mcbe-tools/src/requirements.txt`. This installs are dependencies so that the script can properly run.
- Finally, go into the config.json file which is in mcbe-tools/src folder and copy and paste an absolute path to where you want mcbe-tools to generate new projects for you. This should go as the value of the `project_paths` property. An absolute path looks something like this `C:\\Users\\ryan\\OneDrive\\Documents\\projects`

# Running the program

Make sure you know where the save path for this! You will then run it by opening up the windows powershell or any other terminal and running the command `python path/to/where/you/downloaded/mcbe-tools/src/main.py entity define --help`
- Here you will paste the absolute path to the main.py file in src folder after the python command.
- The commands after the main.py path are commands I have added to the script. Using certain ones will do certain things such as defining an entity, item, or block for example.
- The help flag (a flag, aka option, is anything preceded by --) is a flag that will tell you how to use the command. It will print out syntax and the list of flags and arguments in the terminal for you.
- The python command invokes the python interpreter and starts the python runtime which will be running our script environment
- Run `python path/to/where/you/downloaded/mcbe-tools/src/main.py --help` to see a list of all commands the script has to offer and how to use them

# Using the entity define command
