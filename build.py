from distutils.core import setup

import py2exe, glob

opts = { 
 "py2exe": { 
   # if you import .py files from subfolders of your project, then those are
   # submodules.  You'll want to declare those in the "includes"
   'includes':['Team_1_board', 'Team_1_box_and_button', 'Team_1_chat', 'Team_1_connection', 'Team_1_constants', 'Team_1_dice', 'Team_1_form',
               'Team_1_piece', 'Team_1_player', 'Team_1_server', 'Team_1_setup'
              ],
   "dist_dir": "Ludo",
 } 
} 

setup(

  #this is the file that is run when you start the game from the command line.  
  console=['Team_1_client.py'],

  #options as defined above
  options=opts,

  #data files - these are the non-python files, like images and sounds
  #the glob module comes in handy here.
  data_files = [
    ("images", glob.glob("images\\*.*")),
    ("sound", glob.glob("sound\\*.*"))
  ],

  #this will pack up a zipfile instead of having a glut of files sitting
  #in a folder.
  zipfile="_build.zip"
)
