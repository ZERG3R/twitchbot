import sqlite3
import datetime
import requests

from twitchbot import (encryption_key,
                       current_game,
                       twitchchat,
                       )

fkey = encryption_key.fkey
channel_name = encryption_key.decrypted_chan


def sql_file():
    sqlite_file = r'MyFiles\ViewerData_' + encryption_key.decrypted_chan + '.sqlite'
    return sqlite_file


def hours_file():
    hrs_file = r'MyFiles\hours_' + encryption_key.decrypted_chan + '.sqlite'
    return hrs_file


def create_viewer_tables():
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()

    table2 = 'ViewerData'
    column1 = 'UID'
    column2 = 'User_Name'
    column3 = 'User_Type'
    column4 = 'Level'
    column5 = 'Points'
    column14 = 'Join_Message'
    column15 = 'Join_Date'
    column16 = 'Join_Date_Check'
    column17 = 'Last_Seen'
    column18 = 'Join_Game'
    column19 = 'Invited_By'
    str_type = 'STRING'
    int_type = 'INTEGER'

    c.execute(
        'CREATE TABLE {table2}( '
        '{nf1} {ft1} PRIMARY KEY,'
        '{nf2} {ft2} UNIQUE,'
        '{nf3} {ft3},'
        '{nf4} {ft4},'
        '{nf5} {ft5},'

        '{nf14} {ft14},'
        '{nf15} {ft15},'
        '{nf16} {ft16},'
        '{nf17} {ft17},'
        '{nf18} {ft18},'
        '{nf19} {ft19})'
        .format(table2=table2,
                nf1=column1, ft1=int_type,
                nf2=column2, ft2=str_type,
                nf3=column3, ft3=str_type,
                nf4=column4, ft4=str_type,
                nf5=column5, ft5=int_type,

                nf14=column14, ft14=str_type,
                nf15=column15, ft15=str_type,
                nf16=column16, ft16=str_type,
                nf17=column17, ft17=str_type,
                nf18=column18, ft18=str_type,
                nf19=column19, ft19=str_type))
    conn.commit()
    conn.close()

    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    c.execute('INSERT INTO ViewerData(UID, User_Name, User_Type, Level, Points, Join_Date) '
              'VALUES(12358132, "zerg3rr", "Creator", "Larvae", "0", "2014-06-01")')
    conn.commit()
    conn.close()


def insert_user(User_Name, User_Type, Join_Date, game):
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    if type(User_Name) is list or User_Name is None:
        pass
    elif str(User_Name).isdigit():
        if User_Name[0] == 0:
            pass
    else:
        c.execute('INSERT INTO ViewerData(UID, "User_Name", User_Type, Join_Date, Points, Join_Game) Values'
                  '(?, LOWER(?), ?, ?, ?, ?)', (UID_generator(), str(User_Name), User_Type, Join_Date, 0, game))
    conn.commit()
    conn.close()


def get_table_columns():  # startup
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    sql_column_list = c.execute("PRAGMA table_info(ViewerData)")
    string_column_list = sql_column_list.fetchall()
    columns = []
    for i in string_column_list:
        columns.append(i[1])
    if "Points" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Points INTEGER")
    if "Last_Seen" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Last_Seen STRING")
    if "Invited_By" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Invited_By STRING")
    if "Join_Game" not in columns:
        c.execute("ALTER TABLE ViewerData ADD COLUMN Join_Game STRING")
    conn.commit()
    conn.close()


def check_table_names():  # startup
    table_list = []

    conn = sqlite3.connect(hours_file())
    c = conn.cursor()
    sql_table_names = c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    string_table_names = sql_table_names.fetchall()
    for i in string_table_names:
        table_list.append(i[0])

    if "viewer_chat" not in table_list:
        c.execute("CREATE TABLE viewer_chat (MessageNum INTEGER PRIMARY KEY, UID INTEGER, Date STRING, "
                  "Time STRING, Message STRING, Game STRING)")
    if "Hours" not in table_list:
        insert_hours_table()
    conn.commit()
    conn.close()


def insert_hours_table():
    conn = sqlite3.connect(hours_file())
    c = conn.cursor()

    table = 'Hours'
    col1 = 'UID'
    col2 = 'Game'
    col3 = 'Day'
    col4 = 'Hours'
    col5 = 'Chat'
    str_type = 'STRING'
    int_type = 'INTEGER'
    c.execute("CREATE TABLE {table_name}("
              "{nf1} {ft1},"
              "{nf2} {ft2},"
              "{nf3} {ft3},"
              "{nf4} {ft4},"
              "{nf5} {ft5})".format(table_name=table,
                                    nf1=col1, ft1=int_type,
                                    nf2=col2, ft2=str_type,
                                    nf3=col3, ft3=str_type,
                                    nf4=col4, ft4=int_type,
                                    nf5=col5, ft5=int_type))
    conn.commit()
    conn.close()


def get_last_uid():
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    last_uid = c.execute('SELECT MAX(UID) FROM ViewerData')
    largest_uid = last_uid.fetchone()
    largest_uid = largest_uid[0]
    conn.close()
    return largest_uid


def base_UID():
    base_first = 1
    base_second = base_first + base_first
    base_third = base_first + base_second
    base_fourth = base_second + base_third
    base_fifth = base_third + base_fourth
    base_sixth = base_fourth + base_fifth
    base_seventh = base_fifth + base_sixth
    fullalgorithm = str(base_first) + str(base_second) + str(base_third) + str(base_fourth) + str(base_fifth) + \
                    str(base_sixth) + str(base_seventh)
    algorithm = fullalgorithm[0:8]
    return algorithm


def UID_generator():  # this needs to read the last uid from the database and use the algorithm on
    # it to get the next number then add the next number to the file when a new user is entered
    algorithm = str(get_last_uid())
    base_algo = 0
    # convert the above to a string so it can be iterated over
    secondtolast_char = str(algorithm[-2:-1:]).strip()  # take second to last character of algorithm
    # add our algorithm number plus the second to last character together to get our new number
    secondtolast_char = int(secondtolast_char)
    if int(secondtolast_char) != 0:
        base_algo = int(algorithm) + int(secondtolast_char)
    elif int(secondtolast_char) == 0:
        secondtolast_char = int(secondtolast_char) + 1
        base_algo = int(algorithm) + int(secondtolast_char)
    # overwrite the algorithm number with the base number to prepare for the next loop
    return base_algo


def update_all_users_hours(general, todaydate):
    conn1 = sqlite3.connect(hours_file())
    c1 = conn1.cursor()
    for viewer in general.viewer_objects:
        uid = general.viewer_objects[viewer].uid
        if uid is None or uid == 'None':
            pass
        else:
            for game in general.viewer_objects[viewer].seconds:

                # game = 0 day = 1 seconds = 2
                seconds = general.viewer_objects[viewer].seconds.get(game)

                sql_gameuid = c1.execute("SELECT UID FROM Hours WHERE UID=? AND Game=? AND Day=?", (uid,
                                                                                                    game,
                                                                                                    todaydate))
                string_gameuid = sql_gameuid.fetchone()
                if string_gameuid is None:

                    c1.execute('INSERT INTO HOURS(UID, Game, Day, Hours) Values(?, ?, ?, ?)',
                               (uid, game, todaydate, seconds))
                else:

                    sql_oldtime = c1.execute("SELECT Hours FROM Hours WHERE UID=? AND Game=? AND Day=?", (uid,
                                                                                                          game,
                                                                                                          todaydate))
                    string_oldtime = sql_oldtime.fetchone()

                    c1.execute("UPDATE Hours SET Hours=?+? WHERE UID=? AND Game=? AND Day=?", (string_oldtime[0],
                                                                                               seconds, uid,
                                                                                               game,
                                                                                               todaydate))
                    general.viewer_objects[viewer].seconds[game] = 0
    conn1.commit()
    conn1.close()


# this cant write to DB because it's already open from where this function is called from
# will need to save everything in a class nested dict viewer_name{game:chat number}
def update_user_chat_lines(date, general):  # this should grab an item from viewerclass and add that to game for day
    conn1 = sqlite3.connect(hours_file())
    c1 = conn1.cursor()
    # can use this same concept for trivia questions answered correctly

    for viewer in general.viewer_objects:
        uid = general.viewer_objects[viewer].uid
        for game in general.viewer_objects[viewer].chat_line_dict:

            sql_old_chatlines = c1.execute("SELECT Chat FROM Hours WHERE UID=? AND Game=? AND Day=?",
                                           (uid, game, date))
            string_old_chatlines = sql_old_chatlines.fetchone()
            if string_old_chatlines[0] is None or string_old_chatlines[0] == 'None':
                string_old_chatlines = 0
            else:
                string_old_chatlines = string_old_chatlines[0]

            c1.execute("UPDATE Hours SET Chat=?+? WHERE UID=? AND Game=? AND Day=?",
                       (string_old_chatlines,
                        general.viewer_objects[viewer].chat_line_dict.get(game),
                        uid,
                        game,
                        date))
            general.viewer_objects[viewer].chat_line_dict[game] = 0
    conn1.commit()
    conn1.close()
    # print(e, "line 286")  # this doesnt need to be printed anymore, user just hadnt been added to DB yet


def update_user_points(general):
    try:
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()

        c.execute("UPDATE ViewerData SET Points='0' WHERE Points IS NULL")
        for viewer in general.viewer_objects:
            for game in general.viewer_objects[viewer].seconds:
                # game = 0, day = 1, time = 2, username = 3
                if game == "Offline":
                    points = 0.0001 * general.viewer_objects[viewer].seconds.get(game)
                else:
                    points = 0.00016 * general.viewer_objects[viewer].seconds.get(game)
                sql_oldpoints = c.execute("SELECT Points FROM ViewerData WHERE User_Name=?", (viewer,))
                string_oldpoints = sql_oldpoints.fetchone()[0]
                total_points = float(string_oldpoints) + float(points)
                c.execute("UPDATE ViewerData SET Points=? WHERE User_Name=?",
                          (str(total_points), viewer))
        conn.commit()
        conn.close()
    except (TypeError, sqlite3.OperationalError) as e:
        pass


def update_bots():  # time based
    conn1 = sqlite3.connect(hours_file())
    c1 = conn1.cursor()
    conn2 = sqlite3.connect(sql_file())
    c2 = conn2.cursor()

    sql_bots = c1.execute("SELECT DISTINCT UID FROM Hours WHERE Game NOT IN ('Offline') "
                          "GROUP BY UID HAVING COALESCE (SUM(HOURS), 0) > 180000 "
                          "AND COALESCE (SUM(Chat), 0) < 100")

    string_bots = sql_bots.fetchall()
    for i in string_bots:
        i = i[0]
        c2.execute("UPDATE ViewerData SET User_Type = 'Botter' WHERE UID = ?", (i,))
    other_bots = ["nightbot", "moobot", encryption_key.decrypted_nick, "zerg3rrbot", "giphertius"]
    for i in other_bots:
        c2.execute("UPDATE ViewerData Set User_Type = 'Botter' WHERE User_Name = ?", (i,))

    conn1.commit()
    conn2.commit()
    conn1.close()
    conn2.close()


def get_bot_list():  # time based
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    sql_uid_list = c.execute("SELECT UID FROM ViewerData WHERE User_Type = 'Botter'")
    string_uid_list = sql_uid_list.fetchall()
    bot_list = []
    for i in string_uid_list:
        bot_list.append(i[0])

    bot_list.append(encryption_key.decrypted_chan.strip())

    conn.close()
    return bot_list


def update_last_seen(username):  # time based
    try:
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        today = str(datetime.datetime.today())
        today = today[0:10]

        c.execute("UPDATE ViewerData SET Last_Seen = ? WHERE User_Name = ?", (today, username,))

        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        pass
    # print(e, 366)


# chat sometimes saves without the uid if the user isn't in DB yet
# need to save both the username{game:chatcount}
def save_chat(general):  # chat based
    conn = sqlite3.connect(hours_file())
    c = conn.cursor()
    # message=sublist[2], game=sublist[3], formatted_time=sublist[1], date=sublist[0]

    for viewer in general.viewer_objects:
        if general.viewer_objects[viewer].chat is not None:
            uid = get_uid_from_username(viewer)
            for chat_item in general.viewer_objects[viewer].chat:
                sql_currnum = c.execute('SELECT MAX(MessageNum) from viewer_chat')
                string_currnum = sql_currnum.fetchone()[0]
                if string_currnum is None:
                    int_currnum = 1
                else:
                    int_currnum = int(string_currnum) + 1
                c.execute('INSERT INTO viewer_chat(MessageNum, Date, Time, UID, Message, Game) Values(?,?,?,?,?,?)',
                          (int_currnum,
                           chat_item[0],
                           chat_item[1],
                           uid,
                           chat_item[2],
                           chat_item[3]))
                general.viewer_objects[viewer].chat.remove(chat_item)
    conn.commit()
    conn.close()


def welcome_viewers(s, general, getviewers):  # welcomes all new viewers with a joinmessage # time based
    conn = sqlite3.connect(sql_file())
    c = conn.cursor()
    for viewer in getviewers:
        if viewer not in general.viewer_objects:
            pass
        elif general.viewer_objects[viewer].join_message_check is None:
            sql_check_for_joinmessage = c.execute("SELECT Join_Message FROM ViewerData WHERE User_Name=?",
                                                  (viewer,))
            str_check_for_joinmessage = sql_check_for_joinmessage.fetchone()
            if str_check_for_joinmessage is not None:

                if str(str_check_for_joinmessage[0]).strip() == "None":
                    general.viewer_objects[viewer].join_message_check = False
                else:
                    if abs(general.viewer_objects[viewer].last_seen -
                       general.viewer_objects[viewer].time_before_last_seen) > 2400:
                            twitchchat.chat(s, str(str_check_for_joinmessage[0]))
            else:
                general.viewer_objects[viewer].join_message_check = False
    conn.close()


def check_if_user_exists(get_viewers):
        if get_viewers is not None:
            conn = sqlite3.connect(sql_file())
            c = conn.cursor()
            all_users = c.execute('SELECT User_Name FROM ViewerData')
            user_list = all_users.fetchall()
            user_list = list(user_list)

            untupled_user_list = []
            for j in user_list:
                untupled_user_list.append(str(j[0]).lower())

            for i in get_viewers:
                if i not in untupled_user_list:
                    year_month_day = datetime.datetime.now().strftime('%Y-%m-%d')
                    year_month_day = str(year_month_day)
                    insert_user(User_Name=i, User_Type='Viewer',
                                Join_Date=year_month_day, game=current_game.game_name())
                    # can change this ^^ to be saved in viewer object
            conn.close()


def check_users_joindate(get_viewers):  # time based
    def get_user_id(username, client_id):
        try:
            # Construct headers for HTTP request
            headers = {"Client-ID": client_id}

            # Need user id for request
            personal_user_info = requests.get("https://api.twitch.tv/helix/users?login={}".format(username),
                                              headers=headers).json()

            # extract user id
            user_id = personal_user_info['data'][0]['id']
            return user_id
        except KeyError as e:
            #print(e, 470)
            pass

    def initial_follow_date_for(username, client_id):

        # Construct headers for HTTP request
        headers = {"Client-ID": client_id}

        user_id = get_user_id(username, client_id)

        # Find follower data for user by id
        try:
            follow_data = requests.get("https://api.twitch.tv/helix/users/follows?from_id={}&to_id={}"
                                       .format(user_id, get_user_id(encryption_key.decrypted_chan,
                                                                    client_id)), headers=headers).json()['data'][0]

            # extract the follow date
            date = follow_data['followed_at'].split("T")[0]

            # return dict of format name: follow date in form year-month-day
            return [str(e) for e in date.split('-')]

        except (IndexError, KeyError) as e:
            #print(e, 492)
            return False

    try:
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        if get_viewers is not None:
            viewer_list = get_viewers
            if viewer_list is not None:
                for i in viewer_list:
                    sql_jdc = c.execute('SELECT Join_Date_Check FROM ViewerData WHERE User_Name = ?', (i.strip(),))
                    string_jdc = sql_jdc.fetchone()
                    if string_jdc[0] != 'x':
                        web_date = initial_follow_date_for(i.strip(), client_id=str('j82z1o73ha4tauoxb8y462udh8t4i2'))
                        if web_date is False:
                            c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                      'WHERE User_Name = ?', (i,))
                            conn.commit()
                        if web_date:
                            year_month_day = ['']

                            sql_users_joindate = c.execute("SELECT Join_Date FROM ViewerData WHERE User_Name = ?", (i,))
                            users_joindate = sql_users_joindate.fetchone()
                            if users_joindate is not None:
                                users_joindate = users_joindate[0]
                                str_yearnow = str(users_joindate)[0:4]
                                str_monthnow = str(users_joindate)[5:7]
                                str_daynow = str(users_joindate)[8:]
                                full_strnow = str(str_yearnow + '-' + str_monthnow + '-' + str_daynow)
                                full_webdate = str(web_date[0]) + '-' + str(web_date[1]) + '-' + str(web_date[2])

                                if full_strnow == full_webdate:
                                    c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                              'WHERE User_Name = ?', (i,))

                                else:
                                    yearnow = int(str_yearnow)
                                    monthnow = int(str_monthnow)
                                    daynow = int(str_daynow)

                                    if int(web_date[0]) < yearnow:
                                        year_month_day[0] = str(web_date[0]) + '-' + str(web_date[1]) + '-' + \
                                                            str(web_date[2])

                                    elif int(web_date[0]) == yearnow:
                                        if int(web_date[1]) < monthnow:
                                            year_month_day[0] = str(web_date[0]) + '-' + str(web_date[1]) + '-' + \
                                                                str(web_date[2])

                                    elif int(web_date[0]) == yearnow:
                                        if (web_date[1]) == monthnow:
                                            if int(web_date[2]) < daynow:
                                                year_month_day[0] = str(web_date[0]) + '-' + str(web_date[1]) \
                                                                    + '-' + str(web_date[2])

                                    else:
                                        year_month_day[0] = users_joindate

                                if users_joindate != year_month_day[0]:
                                    if year_month_day[0] != '':
                                        c.execute('UPDATE ViewerData SET Join_Date = ? WHERE User_Name = ?'
                                                  , (year_month_day[0], i))
                                        c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                                  'WHERE User_Name = ?', (i,))

                                elif users_joindate == year_month_day[0]:
                                    c.execute('UPDATE ViewerData SET Join_Date_Check = "x" WHERE User_Name=?', (i,))

                                elif web_date is None:
                                    c.execute('UPDATE ViewerData SET Join_Date_Check = "x" '
                                              'WHERE User_Name = ?', (i,))
        conn.commit()
        conn.close()
    except (sqlite3.OperationalError, TypeError) as e:
        pass
        #print(e, 566)


# noinspection PyUnusedLocal  # time based
def check_mods(get_viewers):  # this needs a way to un-mod a mod as well, not currently implemented
    try:
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        bot_list = get_bot_list()
        bot_username_list = []
        for i in bot_list:
            sql_bot_username = c.execute("SELECT User_Name FROM ViewerData WHERE UID=?", (i,))
            string_bot_username = sql_bot_username.fetchone()
            bot_username_list.append(string_bot_username[0])

        sql_mod_list = c.execute("SELECT User_Name FROM ViewerData WHERE User_Type = 'Moderator'")
        fetchall_mod_list = sql_mod_list.fetchall()
        mod_list = []
        if fetchall_mod_list is None:
            if get_viewers:
                mod_list.append(get_viewers)
        else:
            for i in fetchall_mod_list:
                mod_list.append(i[0])
            if get_viewers:
                for i in get_viewers:
                    if i in mod_list:
                        pass
                    else:
                        mod_list.append(i)
        for i in mod_list:  # if the mod isn't in the mod list from the database
            sql_find_user = c.execute('SELECT User_Name FROM ViewerData WHERE User_Name = ?', (i,))
            user = sql_find_user.fetchall()
            if not user:
                check_if_user_exists(get_viewers)
                    #print('Could not add user, database locked')
            else:
                if i == encryption_key.decrypted_chan.lower():
                    c.execute("UPDATE ViewerData SET User_Type = 'Streamer' WHERE User_Name = ?", (i,))
                else:
                    if i in bot_username_list:
                        pass
                    else:
                        c.execute("UPDATE ViewerData SET User_Type = 'Moderator' WHERE User_Name = ?", (i,))

        conn.commit()
        conn.close()
    except (TypeError, sqlite3.OperationalError) as e:
        pass
        # print(e, 'Typerror or DB lock')


def get_uid_from_username(username):
    try:
        conn = sqlite3.connect(sql_file())
        c = conn.cursor()
        sql_uid = c.execute("SELECT UID FROM ViewerData WHERE User_Name=?", (username,))
        string_uid = sql_uid.fetchone()[0]
        return string_uid
    except TypeError as e:
        return False