from appdirs import user_config_dir
import os


app_name = "SpaceGame"
app_author = "Sandeep"

config_path = user_config_dir(app_name, app_author)
os.makedirs(config_path, exist_ok=True)

highscore_file_path = os.path.join(config_path, "spacegame.sav")