# Weekminder

## Features

This allows you to give your beeminder yellow brick road different slopes depending on the day of the week. Useful if you want to spend more time doing the activity you are beemining on the weekends or during certain days of the week.

This project requires Python and should otherwise work on any system.

These installation steps should work for Mac OS X, Linux, or any other Unix system with python. For Windows, you will need to find a way to run the python script repeatedly.

### Configuration

For each goal you need to create a road configuration file. Road config files should be located in roads/<your goal>.road.

An example road config file is provided (roads/test.road.example). They are all in a JSON format.

`cp roads/test.road.example roads/test.road`

Then edit your road config file. For each road config file you will be asked to specify your beeminder username, your beeminder authentication token and the goal name. Then you can specify the rates that you want to have for each day in one of the following ways:
- By using `"daily_rates": [0, 1, 2, 3, 4, 5, 6]` (with different numbers). In this case, your beeminder goal will have a rate of 0 on Monday, 1 on Tuesday, 2 on Wednesday and so on.
- By using `"weekdays": 1` and `"weekends": 2` (with different numbers). THIS IS THE RECOMMENDED WAY. In this case your goal will have a rate of 1 on weekdays and 2 on weekends.
- By using `"mon": 0, "tue": 1, "wed": 2`... and so on (with different numbers). This is how you set specific days. If you are using the "weekend" and "weekdays" method you can still override a specific day of the week this way.

Note that all these rates are DAILY rates, so when you set these numbers, ask yourself "how much of this do I want to do PER DAY" not per week as you would when using the web version of beeminder.

Also note that the beeminder goals should NOT be the user friendly goal names but should be the goal URL name. For example, if your goal is called "Be More Productive", but when you navigate to it you see `https://www.beeminder.com/<your_username>/goals/prod` in your browser's URL bar, you should use "prod" as your goal name here.

Your beeminder_token can be found at https://www.beeminder.com/settings/advanced_settings

Your beeminder user name is whatever you use to log into beeminder (obviously). Write it in lowercase.

### How do I take a break?

DO NOT use the beeminder "take a break" feature if you're using this script. Instead, if you want to take a break on a given day, add an entry in the `"day_overrides"` section of the format `"YYYY-MM-DD": <rate on that specific day>`.

### Making the script run repeatedly

If you run `python update_all_roads.py`, all the roads that you created in your roads/ directory will be updated in beeminder for the next month. Running this manually isn't very convient however, so let's make it run every day.

Add your script as a cron by using (in shell):

`EDITOR=nano crontab -e`

This will open an editor with a cron configuration file. Add the following line in the file:

`0 16 * * * python <PATH_TO_THE_SCRIPT>/update_all_roads.py`

Of course, replace <PATH_TO_THE_SCRIPT> with the path to the directory that contains update_all_roads.py (For example: `/User/yourname/weekminder/`).

Then save and exit.

You're all set. The script will run every day at 4 pm (if you don't like 4 pm, replace the 16 in the cron line by the time you'd like the program to run in 24h notation). Feel free to still run it manually as needed.
