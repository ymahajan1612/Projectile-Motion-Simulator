import Classes as cls  # importing classes file
import pygame, math  # importing modules
from tkinter import *
from tkinter import messagebox  # importing message box from tkinter
import db_interaction  # importing file for database interaction
import sys
import re  # regex module for pattern matching

pygame.init()  # initialsing pygame

# Defining colours
white = (255, 255, 255)
green = (71, 120, 62)
bright_green = (0, 255, 0)
maroon = (128, 0, 0)
navy = (65, 67, 118)
orange = (255, 165, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
purple = (128, 0, 128)
grey = (128, 128, 128)
black = (0, 0, 0)
sky_blue = (0, 193, 247)
teal = (55, 103, 123)

# Defining constants and global variable
G = 9.81  # gravitational field strength
SCREEN_W = 1430  # Screen width
SCREEN_H = 700  # Screen height
SCREEN_CENTRE = (SCREEN_W / 2, SCREEN_H / 2)  # Defining screen centre
large_font = "Impact"
small_font = "arial"
clock = pygame.time.Clock()  # creating pygame clock object
FPS = 60  # Frame rate has been capped to ensure consistency across devices
current_user = None # will later store the current user id, necessary for querying database
calculations = []  # A list will hold each of the calculations carried out

# Loading any images required
frame_img = pygame.image.load("rect_frame.png")
title = pygame.image.load("title.png")
exit_icon = pygame.image.load("Exit icon.png")
home_icon = pygame.image.load("home_icon.png")
retry_icon = pygame.image.load("retry_icon.png")
home_button = cls.Button(10,10,"",None,None,red,"",100,100,home_icon)


def close():  # close function will run when X button pressed
    pygame.quit()
    sys.exit()


# ======================================Functions for pop-ups and windows==============================================
def pause(screen, objects_list):  # function that runs when game is pause (esc-key pressed)
    is_paused = True
    # creating a translucent overlay
    background = pygame.Surface((SCREEN_W, SCREEN_H))
    background.set_alpha(200)
    background.fill(sky_blue)
    screen.blit(background, (0, 0))
    paused_title = cls.Text(500, 10, large_font, 100, 100, white, "Paused", 140)
    play = cls.Text(10,10,small_font,100,100,white,"Press ESC to resume",50)
    texts = [paused_title,play]
    while is_paused:
        for text in texts:
            text.draw(screen)
        pos = pygame.mouse.get_pos()
        for graphic in objects_list:
            graphic.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                close()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for graphic in objects_list:
                    if isinstance(graphic, cls.Toggle):  # if a toggle is clicked
                        if graphic.isClicked(pos):
                            graphic.switch()

            if event.type == pygame.KEYDOWN:  # To leave pause menu
                if event.key == pygame.K_ESCAPE:
                    is_paused = False
        clock.tick(5)
        pygame.display.update()


def save_projectile(screen, window, projectile_details):  # projectile_details = [max_height, range]
    objects = []
    background = pygame.Surface((SCREEN_W, SCREEN_H))
    background.fill(blue)
    screen.blit(background, (0, 0))
    projectile_name_box = cls.Text_box(SCREEN_CENTRE[0] - 300, SCREEN_CENTRE[1] - 50, 600, 100, str, 70)
    ok_button = cls.Button(SCREEN_CENTRE[0] - 75, SCREEN_CENTRE[1] + 55, large_font, 70, white, orange, "Save", 150, 75)
    name_box_title = cls.Text(200, SCREEN_CENTRE[1] - 200, large_font, 80, 30, white,
                              "Enter a name (10 characters max):", 80)
    objects.extend([projectile_name_box, ok_button, name_box_title])
    save = True
    while save:
        window.update_window(grey)
        pos = pygame.mouse.get_pos()
        for graphic in objects:
            graphic.draw(screen)
        for event in pygame.event.get():
            for graphic in objects:
                if isinstance(graphic, cls.Text_box):
                    graphic.add_chars(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button.isClicked(pos):
                    if len(projectile_name_box.get_text()) > 10:
                        popup_window("The name should be less than 10 characters", "Error", "error")
                    elif not projectile_name_box.get_text():
                        popup_window("Name field left blank", "Error", "error")
                    else:
                        db_interaction.store_values(projectile_details, current_user, projectile_name_box.get_text())
                        save = False

            if event.type == pygame.KEYDOWN:  # To leave pause menu
                if event.key == pygame.K_ESCAPE:
                    save = False
        pygame.display.update()


def inputs_menu(screen, window, objects_list):  # a function that runs when the ctrl+ i keys pressed
    adjust_inputs = True
    background = pygame.Surface((SCREEN_W, SCREEN_H))
    background.fill(navy)
    screen.blit(background, (0, 0))
    inputs_title = cls.Text(500, 10, large_font, 100, 100, white, "Inputs", 140)
    esc_instruction = cls.Text(900,10,small_font,100,100,white,"Press ESC to resume",60)
    while adjust_inputs:
        window.update_window(None, background)  # updating the window
        inputs_title.draw(screen)
        esc_instruction.draw(screen)
        pos = pygame.mouse.get_pos()
        for graphic in objects_list:
            if isinstance(graphic, cls.Slider):
                slider_values = cls.Text(graphic.get_dimensions()[0] + graphic.get_dimensions()[2] + 10,
                                         graphic.get_dimensions()[1] - 20, large_font, 100, 100, white,
                                         graphic.get_value(),
                                         70)  # creating text for each slider
                slider_values.draw(screen)

        for graphic in objects_list:
            graphic.draw(screen)  # drawing all objects

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                close()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    adjust_inputs = False

            for graphic in objects_list:
                if isinstance(graphic, cls.Slider):  # Slider is clicked
                    if graphic.slider_square.collidepoint(pos[0], pos[1]):
                        graphic.set_colour(sky_blue)  # changes colour
                        if pygame.mouse.get_pressed()[0]:
                            graphic.update(pygame.mouse.get_pos()[0])  # updates slider square's position
                    else:
                        graphic.set_colour(black)  # Resets colour to black

        clock.tick(30)
        pygame.display.update()


def calculations_tab(screen, calculations_file_name, window):
    view_calculations = True
    background = pygame.Surface((SCREEN_W, SCREEN_H))
    background.fill(sky_blue)
    screen.blit(background, (0, 0))
    text_bitmaps = []
    esc_control = cls.Text(1000,10,small_font,100,150,black,"Press ESC to close",50)
    text_bitmaps.append(esc_control)
    y_pos = 5
    with open(calculations_file_name, "r") as calculations_file:
        all_calculations = calculations_file.readlines()  # returns a list of all contents
    for calculation in all_calculations:
        if len(calculation.split(".")[0]) > 1:  # checking if counter is double digit and adjusting x position
            x_pos = 5
        else:
            x_pos = 10
        calculation_text = cls.Text(x_pos, y_pos, small_font, 100, 50, black, calculation, 30)
        text_bitmaps.append(calculation_text)
        y_pos += 45
    while view_calculations:
        window.update_window(white)
        for text in text_bitmaps:
            text.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                view_calculations = False
                pygame.quit()
                close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    view_calculations = False
                # code for scrolling calculations table
                if event.key == pygame.K_DOWN:
                    for text in text_bitmaps:
                        if text_bitmaps[-1].get_y() > SCREEN_H:
                            text.set_y(-10)
                if event.key == pygame.K_UP:
                    for text in text_bitmaps:
                        if text_bitmaps[0].get_y() < 0:
                            text.set_y(10)
        clock.tick(FPS)
        pygame.display.update()


def popup_window(message, title, msg_type="yes/no"):  # a function to display pop-up window -
    window = Tk()
    window.eval("tk::PlaceWindow {} center".format(window.winfo_toplevel()))  # ensures that pop-up is top-most
    window.withdraw()  # removes main window that appears behind pop-up

    if msg_type == "yes/no":
        return messagebox.askyesno(title, message)
    elif msg_type == "retry/cancel":
        return messagebox.askretrycancel(title, message)
    elif msg_type == "info":
        return messagebox.showinfo(title, message)
    elif msg_type == "error":
        return messagebox.showerror(title, message)

    window.deiconify()
    window.destroy()
    window.quit()


def validate(username, password):  # A function to validate user inputs -
    if " " in username:  # checks for space in  username
        return popup_window("Your username should not contain a space", "Error", "error")
    if len(password) < 8:  # length check
        return popup_window("Your password should be longer than 8 characters", "Error", "error")
    elif not re.search("[0-9]", password):  # Checks if password contains at least 1 digit
        return popup_window("Your password should contain at least 1 digit", "Error", "error")
    elif not re.search("[A-Z]", password):  # Checks if password contains at least 1 capital letter
        return popup_window("Your password should contain at least 1 capital letter", "Error", "error")
    return True


# ========================================Functions for projectile======================================================

def set_arrow(velocity, angle, projectile):
    x = ((math.cos(math.radians(angle)) * velocity) * 25) + projectile.get_pos()[0]
    y = projectile.get_pos()[1] - ((math.sin(math.radians(angle)) * velocity) * 25)
    return x, y


def launch(sprite_list, launched, landed, screen):
    projectile, floor = sprite_list[0], sprite_list[1]
    if launched and not landed:
        projectile.update_pos()
    projectile.draw_trail(screen)


def pan_screen(object_list, key, original_positions_list,pan_vel):  # [projectile,floor,positions]
    projectile, floor, positions = object_list[0], object_list[1], object_list[2]
    new_positions = []
    scroll = [False, False]  # For checking if projectile if scrolling (particle out of bounds in x,y)
    if key:
        # Horizontal scrolling
        if key == pygame.K_RIGHT and projectile.is_off_screen()[0]:
            if projectile.get_pos()[0] >= SCREEN_W/2:
                scroll[0] = True
        elif key == pygame.K_LEFT and projectile.get_pos_list("x") != [pos[0] for pos in original_positions_list]:
                scroll[0] = True
        if scroll[0]:
            for coordinate in projectile.get_pos_list():
                new_coordinate = coordinate[0] + pan_vel, coordinate[1]
                new_positions.append(new_coordinate)
                if len(original_positions_list) != 0: # dequeue old position from projectile positions list
                    original_positions_list.pop(0)
            original_positions_list = [position for position in new_positions] # enqueuing new positions to the positions list
            projectile.set_pos_list(original_positions_list) # setting the positions list to the new list created above
            projectile.set_pos((projectile.get_pos()[0] + pan_vel, projectile.get_pos()[1]))
        # vertical scrolling
        if key == pygame.K_UP:
            max_y = min(projectile.get_pos_list("y"))
            if max_y < 5:
                scroll[1] = True
        elif key == pygame.K_DOWN and floor.get_top() > 540:
            scroll[1] = True

        if scroll[1]:
            for coordinate in projectile.get_pos_list():
                new_coordinate = coordinate[0], coordinate[1] + pan_vel
                new_positions.append(new_coordinate)
            projectile.set_pos_list(new_positions)
            projectile.set_pos((projectile.get_pos()[0], projectile.get_pos()[1] + pan_vel))
            floor.set_pos((floor.get_pos()[0], floor.get_pos()[1] + pan_vel))


def component_velocities(velocity, angle):
    x_velocity = round(velocity * math.cos(math.radians(angle)), 2)
    y_velocity = round(velocity * math.sin(math.radians(angle)), 2)
    return x_velocity, y_velocity


# =========================================Functions for screens========================================================
def main_menu():
    main_window = cls.Window(SCREEN_W, SCREEN_H, "Projectile Motion Simulator (Yash Mahajan)", "", "background_1.png")
    main_screen = main_window.create_window()
    # Creating buttons on this screen

    # Not added to developement log
    login_button = cls.Button(491, 288, large_font, 118, white, navy, "Login", 452, 116)  # login button
    sign_up_button = cls.Button(491, 424, large_font, 115, white, navy, "Sign-up", 452, 116)
    quit_button = cls.Button(491, 560, large_font, 115, white, navy, "Quit", 452, 116)
    buttons_dict = {login_button: "login", sign_up_button: "sign_up",
                    quit_button: "close"}  # dict of buttons and functions
    # getting list of buttons
    buttons = list(buttons_dict.keys())

    for button in buttons:  # drawing each button
        button.draw(main_screen, True)

    main_screen.blit(title, (58, 29))

    # main loop for main menu
    run_main = True
    while run_main:
        pos = pygame.mouse.get_pos()  # gets mouse position
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # X button is pressed
                run_main = False
                close()
            if quit_button.isClicked(pos):
                run_main = False
                close()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.isClicked(pos):
                        if button == quit_button:
                            run_main = False
                        eval(buttons_dict.get(button))()  # evaluates string value from dict and runs as function
        pygame.display.update()


def login():  # function for user login -
    global current_user
    objects = []
    login_window = cls.Window(SCREEN_W, SCREEN_H, "Login", None, "background_1.png")
    login_screen = login_window.create_window()

    # setting width and height of textboxes
    box_width = 500
    box_height = 70

    # setting labels for each of the textboxes
    username_label = cls.Text(400, 100, large_font, 100, 100, white, "Username:", 70)
    password_label = cls.Text(400, 300, large_font, 100, 100, white, "Password:", 70)
    login_text = [username_label, password_label]

    # creating two textbox objects and appending them to a list
    username_box = cls.Text_box(SCREEN_CENTRE[0] - box_width / 2, 200, box_width, box_height, str, 60)
    password_box = cls.Text_box(SCREEN_CENTRE[0] - box_width / 2, 400, box_width, box_height, str, 60, True)
    input_boxes = [username_box, password_box]
    objects.append(username_box)
    objects.append(password_box)

    # creating button to login
    login_button = cls.Button(SCREEN_CENTRE[0] - 226, 500, large_font, 115, white, navy, "Login", 452, 116)
    objects.append(login_button)
    objects.append(home_button)

    run_login = True
    while run_login:
        login_window.update_window()
        login_screen.blit(frame_img, (343, 43))
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                close()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
            if home_button.isClicked(pos):
                main_menu()
            elif login_button.isClicked(pos):
                
                user_details = []  # creates a list to which all user's inputs will be added
                for box in input_boxes:
                    if box.get_text() == "":  # checks if any fields has been left blank
                        if popup_window("You left a field blank, would you like to retry?", "Error", "yes/no"):
                            login()
                        else:
                            main_menu()
                    else:
                        user_details.append(box.get_text())  # appends user's inputs of: username and password
                if db_interaction.login_validation(user_details):  # validates user's input (returns boolean value)
                    popup_window("Login successful", "Success",
                                 "info")  # if True is returned from the login_validation function
                    current_user = db_interaction.get_id(
                        user_details[0])  # sets the global variable current user to username
                    mode_menu()  # loads the menu where user selects desired modes
                else:  # if login_validation function returns False/ user's details were incorrect
                    # displaying pop_up
                    if popup_window("Incorrect username or password, would you like to try again?", "Error", "yes/no"):
                        login()  # calling the login function again if user clicks "yes"
                    main_menu()
            for box in input_boxes:
                box.add_chars(event)
        for text in login_text:
            text.draw(login_screen)
        for object in objects:
            object.draw(login_screen)
        pygame.display.update()


def sign_up():  # sign up function -
    objects = []
    signUp = cls.Window(SCREEN_W, SCREEN_H, "Sign up", None,
                        "background_1.png")
    signUp_screen = signUp.create_window()  # creating sign-up window

    box_width = 500
    box_height = 70

    # creating the textboxes
    name_box = cls.Text_box(SCREEN_CENTRE[0] - box_width / 2, 200, box_width, box_height, str, 60)
    username_box = cls.Text_box(SCREEN_CENTRE[0] - box_width / 2, 325, box_width, box_height, str, 60)
    password_box = cls.Text_box(SCREEN_CENTRE[0] - box_width / 2, 450, box_width, box_height, str, 60, True)
    input_boxes = [name_box, username_box, password_box]

    # sign-up button object
    signUp_button = cls.Button(SCREEN_CENTRE[0] - 226, 540, large_font, 115, white, navy, "Sign-up", 452, 116)


    # labels for each textbox
    name_label = cls.Text(SCREEN_CENTRE[0] - box_width / 2, 145, large_font, 100, 100, white,
                          "Enter your name: ", 50)
    username_label = cls.Text(SCREEN_CENTRE[0] - box_width / 2, 270, large_font, 100, 100, white,
                              "Enter a username:", 50)
    password_label = cls.Text(SCREEN_CENTRE[0] - box_width / 2, 395, large_font, 100, 100, white,
                              "Enter a password:", 50)
    objects.extend([name_label, username_label, password_label,signUp_button,home_button])

    run_signUp = True
    add_user = True  # A boolean to ensure that user is only added once to the database
    while run_signUp:
        signUp.update_window()
        signUp_screen.blit(frame_img, (343, 50))  # displaying the frame to the screen
        for graphic in objects:
            graphic.draw(signUp_screen)
        pos = pygame.mouse.get_pos()
        for box in input_boxes:
            box.draw(signUp_screen)  # draws each textbox to the screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                close()
            for box in input_boxes:
                box.add_chars(event)  # continuously checking for events on each text-box
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
        if home_button.isClicked(pos):
            main_menu()
        elif signUp_button.isClicked(pos):
            user_details = []
            for box in input_boxes:
                if box.get_text() == "":  # checking if any textbox is empty
                    # pop-up to notify user of blank field
                    if popup_window("You left a field blank, would you like to retry?", "Error", "retry/cancel"):
                        main_menu()  # if the user clicks cancel on the pop-up box
                    else:
                        sign_up()
                else:  # If no fields are empty
                    user_details.append(box.get_text())
            if not validate(user_details[1], user_details[2]):  # if the validate function returns false
                sign_up()
            else:
                while add_user:
                    if db_interaction.signUp_validation(user_details):
                        add_user = False  # add user becomes false
                        popup_window("Sign-up successful!", "Success",
                                     "info")
                        login()
                    else:  # If user enters details of an existing user
                        popup_window("This user already exists, try again", "Error", "error")
                        sign_up()
        pygame.display.update()


def mode_menu():
    simulation_menu = cls.Window(SCREEN_W, SCREEN_H, "Select simulation mode", None, "background_1.png").create_window()

    # creating the buttons

    science_button = cls.Button((SCREEN_W / 2) - 226, SCREEN_CENTRE[1] - 100, large_font, 95, white, orange,
                                "Simulation", 452,
                                116)  # a button that will take the user to science mode
    projectile_button = cls.Button((SCREEN_W / 2) - 245, SCREEN_CENTRE[1] + 40, large_font, 85, white, purple,
                                   "My projectiles", 490, 116)
    home_button.deactivate()
    buttons_dict = {science_button: "level", projectile_button: "saved_projectiles"}
    buttons = buttons_dict.keys()

    done = False
    while not done:
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                close()
        for button in buttons:
            button.draw(simulation_menu)
            if button.isClicked(pos):
                if buttons_dict.get(button) == "level":
                    popup_window("-To pause the simulation and adjust settings press ESC\n\n"
                                 "-If the projectile has not been launched you can press I to bring up the inputs menu\n\n"
                                 "-Once the projectile has landed,if it is out of bounds, you can pan the screen using the arrow keys\n\n"
                                 "-Press the exit button to leave the simulation\n\n"
                                 "-You can view saved projectiles in the My Projectiles window", "Controls", "info")
                eval(buttons_dict.get(button))()
        pygame.display.update()


def saved_projectiles():
    saved_screen = cls.Window(SCREEN_W, SCREEN_H, "Saved projectiles", None,
                              "background_1.png")
    saved_window = saved_screen.create_window()

    names_list, ranges, max_heights = db_interaction.get_values(current_user)

    name_heading = cls.Text(120, 9, large_font, 100, 10, navy, "Name", 64)
    max_height_heading = cls.Text(388, 9, large_font, 100, 20, navy, "Maximum height (m)", 63)
    range_heading = cls.Text(1080, 9, large_font, 100, 40, navy, "Range (m)", 64)

    all_text = []
    all_text.extend([name_heading,range_heading,max_height_heading])
    # creating text from data fetched from database
    y_pos = 80
    for name in names_list:
        name_text = cls.Text(120,y_pos,large_font,100,100,black,name,50) # creates text bitmap
        y_pos += 70
        all_text.append(name_text)
    y_pos = 80
    for height in max_heights:
        height_text = cls.Text(600,y_pos,large_font,100,50,black,height,50)
        y_pos += 70
        all_text.append(height_text)
    y_pos = 80
    for distance in ranges:
        distance_text = cls.Text(1150,y_pos,large_font,100,40,black,distance,50)
        y_pos += 70
        all_text.append(distance_text)
    done = False
    while not done:
        home_button.draw(saved_window)
        for text in all_text:
            text.draw(saved_window)
        home_button.draw(saved_window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                close()
            elif home_button.isClicked(pygame.mouse.get_pos()):
                mode_menu()
            #for scrolling
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    for text in all_text:
                        if all_text[-1].get_y() > SCREEN_H:
                            text.set_y(-10)
                if event.button == 4:
                    for text in all_text:
                        if all_text[0].get_y() < 0:
                            text.set_y(10)
                if home_button.isClicked(pygame.mouse.get_pos()):
                    mode_menu()
        pygame.display.update()


def level():
    all_sprites = pygame.sprite.Group()  # a list of all sprites in my program
    launched = False  # When the launch button is clicked
    landed = False  # When projectile has hit the ground
    moving = False  # When the projectile is in motion
    objects = []  # creates an empty list for all the objects (may create separate list for all texts)
    all_sprites.empty()
    pan_velocity = 0
    key_pressed = None
    with open("calculations.txt", "w") as f:  # clears the text file
        f.close()

    simulation = cls.Window(SCREEN_W, SCREEN_H, "Projectile Simulator", None, None, sky_blue)
    simulation_screen = simulation.create_window()

    # Items for initial inputs menu
    text_pos = SCREEN_W / 2 - 550
    velocity_slider = cls.Slider(text_pos, 270, 50, 0, 15, white, 1000, 40)
    velocity_label = cls.Text(text_pos, 200, large_font, 100, 100, white, "Initial Velocity (m/s)", 60)
    angle_slider = cls.Slider(text_pos, 400, 90, 0, 45, white, 1000, 40)
    angle_label = cls.Text(text_pos, 330, large_font, 100, 100, white, "Angle ({})".format(chr(176)), 60)
    initial_height_slider = cls.Slider(text_pos, 530, 10, 0, 0, white, 1000, 40)
    initial_height_label = cls.Text(text_pos, 460, large_font, 100, 100, white, "Initial Height (m)", 60)
    x_velocity_slider = cls.Slider(text_pos, 270, 20, 0, 12, white, 1000, 40)
    x_vel_label = cls.Text(text_pos, 200, large_font, 100, 100, white, "Horizontal velocity (m/s) ", 60)
    y_velocity_slider = cls.Slider(text_pos, 400, 20, 0, 12, white, 1000, 40)
    y_vel_label = cls.Text(text_pos, 330, large_font, 12, 100, white, "Vertical velocity (m/s) ", 60)

    # Items  for pause menu
    velocity_input_title = cls.Text(SCREEN_CENTRE[0] - 500, 200, large_font, 100, 100, white,
                                    "Select a velocity input method: ", 70)
    magnitude_title = cls.Text(60, 300, small_font, 100, 100, white, "magnitude and angle", 70)
    components_title = cls.Text(850, 300, small_font, 100, 100, white, "components", 70)
    velocity_input_switch = cls.Toggle(SCREEN_CENTRE[0], 350, 150, 70, green, navy, False)
    drag_title = cls.Text(SCREEN_CENTRE[0] - 200, 400, large_font, 100, 50, white, "Air resistance", 70)
    drag_switch = cls.Toggle(SCREEN_CENTRE[0], 550, 150, 70, bright_green, red, False)
    drag_on_text = cls.Text(SCREEN_CENTRE[0] + 100, 510, small_font, 100, 130, white, "On", 70)
    drag_off_text = cls.Text(SCREEN_CENTRE[0] - 200, 510, small_font, 100, 130, white, "Off", 70)

    # Items for simulation screen
    launch_button = cls.Button(SCREEN_W / 2 - 125, 585, large_font, 80, white, bright_green, "Launch!", 300, 100)
    calculations_button = cls.Button(SCREEN_W / 2 - 125, 585, large_font, 75, white, navy, "Calculations", 400, 100)
    exit_button = cls.Button(SCREEN_W - 100, 10, large_font, 70, white, red, "", 90, 86, exit_icon)
    retry_button = cls.Button(10, 10, large_font, 70, white, red, "", 90, 86, retry_icon)
    save_button = cls.Button(50, 585, large_font, 70, white, orange, "Save projectile", 450, 100)
    info_button = cls.Button(SCREEN_W - 150, 585, small_font, 70, black, grey, "i", 70, 70)
    inputs_button = cls.Button(50,585,large_font,70,black,orange,"Inputs menu",360,90)
    initial_height_text = cls.Text(10, 90, large_font, 100, 50, white,
                                   "Initial height: {} m".format(initial_height_slider.get_value()), 40)
    initial_velocity_text = cls.Text(10, 10, large_font, 100, 50, white,
                                     "Initial velocity: {} m/s".format(velocity_slider.get_value()), 40)
    x_velocity_text = cls.Text(10, 130, large_font, 100, 50, white, "Horizontal velocity: {} m/s".format(
        component_velocities(velocity_slider.get_value(), angle_slider.get_value())[0]), 40)
    y_velocity_text = cls.Text(10, 170, large_font, 100, 50, white, "Vertical velocity: {} m/s".format(
        component_velocities(velocity_slider.get_value(), angle_slider.get_value())[1]), 40)
    initial_angle_text = cls.Text(10, 50, large_font, 100, 50, white,
                                  "Angle above horizontal: {}{}".format(angle_slider.get_value(), chr(176)), 40)
    magnitude_text = [initial_velocity_text, x_velocity_text, y_velocity_text, initial_angle_text]
    objects = [text for text in magnitude_text]
    objects.extend([launch_button, initial_height_text, info_button, exit_button,inputs_button])

    # creating all sprites and adding to all_sprites list
    floor = cls.Sprite(0, 540, "floor.png")  # floor sprite
    projectile = cls.Projectile(25, 437)  # creating projectile sprite
    velocity_arrow = cls.Sprite(100, 100, "arrow.png")
    velocity_arrow.rect.center = set_arrow(velocity_slider.get_value(), angle_slider.get_value(), projectile)
    velocity_arrow_image = velocity_arrow.get_image()
    velocity_arrow.set_image(pygame.transform.rotate(velocity_arrow_image, 45))
    all_sprites.add(floor, projectile, velocity_arrow)

    done = False
    while not done:
        simulation.update_window()  # updates window with each iteration
        if not launched and not landed:
            pygame.draw.aaline(simulation_screen, black, projectile.get_pos(), velocity_arrow.get_pos(), 10)
        else:
            all_sprites.remove(velocity_arrow)
        all_sprites.draw(simulation_screen)
        for graphic in objects:
            graphic.draw(simulation_screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                close()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if landed:
                    if keys[pygame.K_LEFT] or keys[pygame.K_UP]:
                        pan_velocity = 30
                    if keys[pygame.K_RIGHT] or keys[pygame.K_DOWN]:
                        pan_velocity = -30
                    key_pressed = event.key
                if event.key == pygame.K_r:  # pressing r resets simulation
                    level()
                elif event.key == pygame.K_ESCAPE:  # pause menu opened
                    current_state_velocity, current_state_drag = velocity_input_switch.get_state(), drag_switch.get_state()
                    objects.clear()
                    objects.extend([velocity_input_title,
                                    magnitude_title,
                                    components_title,
                                    velocity_input_switch,
                                    drag_title,
                                    drag_switch,
                                    drag_on_text,
                                    drag_off_text
                                    ])
                    pause(simulation_screen, objects)
                    if current_state_velocity != velocity_input_switch.get_state():
                        input_method = "components" if velocity_input_switch.get_state() else "Magnitude and Angle"
                        calculations.append("Velocity input method switched to {}\n".format(input_method))
                    if current_state_drag != drag_switch.get_state() and not launched:
                        projectile.toggle_drag()
                        if drag_switch.get_state():
                            calculations.append("Air resistance switched on\n")
                        else:
                            calculations.append("Air resistance switched off\n")
                    if not velocity_input_switch.get_state() and not launched:  # if magnitude + angle option selected
                        objects = [text for text in magnitude_text]
                    # if component velocities selected, update velocities
                    else:
                        x_velocity_text = cls.Text(10, 130, large_font, 100, 50, white,
                                                   "Horizontal velocity: {} m/s".format(
                                                       x_velocity_slider.get_value()), 40)
                        y_velocity_text = cls.Text(10, 170, large_font, 100, 50, white,
                                                   "Vertical velocity: {} m/s".format(
                                                       y_velocity_slider.get_value()), 40)
                        try:
                            angle = math.degrees(math.atan(float(y_velocity_slider.get_value()/x_velocity_slider.get_value())))
                        except:
                            angle = 90
                        initial_angle_text.update_text("Angle above horizontal: {}{}".format(angle, chr(176)))
                        total_velocity = round(
                            math.sqrt(x_velocity_slider.get_value() ** 2 + y_velocity_slider.get_value() ** 2),
                            2)  # Vi = sqrt(Vx^2 + Vy^2)
                        initial_velocity_text = cls.Text(10, 10, large_font, 100, 50, white,
                                                         "Initial velocity: {} m/s".format(total_velocity), 40)
                        # A separate list if components option selected
                        components_text = [x_velocity_text, y_velocity_text, initial_angle_text, initial_velocity_text]
                        if not launched:
                            objects = [text for text in components_text]
                    objects.append(info_button)
                    if not launched:
                        objects.extend([launch_button, initial_height_text, exit_button,inputs_button])
                    elif landed:
                        objects.clear()
                        objects.extend([calculations_button, exit_button,retry_button])
                        if not drag_switch.get_state():
                            objects.append(save_button)
                    else:
                        objects.clear()
            if event.type == pygame.KEYUP:
                if landed:
                    pan_velocity = 0
            if inputs_button.isClicked(pygame.mouse.get_pos()) and not launched:
                objects.clear()
                # appending all required objects to objects list
                if not velocity_input_switch.get_state():
                    objects.extend([velocity_label,
                                    angle_label,
                                    initial_height_label,
                                    velocity_slider,
                                    angle_slider,
                                    initial_height_slider,
                                    ])
                else:
                    objects.extend([x_velocity_slider, x_vel_label, y_velocity_slider, y_vel_label,
                                    initial_height_slider, initial_height_label])
                inputs_menu(simulation_screen, simulation, objects)
                inputs_button.deactivate()
                projectile.set_height(initial_height_slider.get_value())
                if initial_height_slider.get_value() != 0:
                    calculations.append("Initial height set to {} m\n".format(initial_height_slider.get_value()))

                # updating all text
                initial_height_text.update_text("Initial height: {} m".format(initial_height_slider.get_value()))

                if not velocity_input_switch.get_state():  # if magnitude + angle option selected
                    initial_velocity_text.update_text(
                        "Initial Velocity: {} m/s".format(velocity_slider.get_value()))
                    initial_angle_text.update_text(
                        "Angle above horizontal: {}{}".format(angle_slider.get_value(), chr(176)))
                    x_velocity_text.update_text("Horizontal velocity: {} m/s".format(
                        component_velocities(velocity_slider.get_value(), angle_slider.get_value())[0]))
                    y_velocity_text.update_text("Vertical Velocity: {} m/s".format(
                        component_velocities(velocity_slider.get_value(), angle_slider.get_value())[1]))
                    magnitude_text = [initial_velocity_text, initial_angle_text, x_velocity_text, y_velocity_text]
                    objects = [text for text in magnitude_text]

                    calculations.extend(["{} \n".format(initial_velocity_text.get_text()),
                                         "{} \n".format(initial_angle_text.get_text()),
                                         "{} calculated by sin({}) * {} \n".format(x_velocity_text.get_text(),
                                                                                   angle_slider.get_value(),
                                                                                   velocity_slider.get_value()),
                                         "{} calculated by cos({}) * {} \n".format(y_velocity_text.get_text(),
                                                                                   angle_slider.get_value(),
                                                                                   velocity_slider.get_value())])

                else:  # If component option selected
                    x_velocity_text.update_text("Horizontal velocity: {} m/s".format(x_velocity_slider.get_value()))
                    y_velocity_text.update_text("Vertical velocity: {} m/s".format(y_velocity_slider.get_value()))
                    try:
                        angle = round(
                            math.degrees(math.atan(y_velocity_slider.get_value()/x_velocity_slider.get_value())), 2)
                    except ZeroDivisionError:
                        angle = 90
                    initial_angle_text.update_text("Angle above horizontal: {}{}".format(angle, chr(176)))
                    total_velocity = round(
                        math.sqrt(x_velocity_slider.get_value() ** 2 + y_velocity_slider.get_value() ** 2),
                        1)  # Vi = sqrt(Vx^2 + Vy^2)
                    initial_velocity_text.update_text("Initial velocity: {} m/s".format(total_velocity))
                    components_text = [x_velocity_text, y_velocity_text, initial_angle_text, initial_velocity_text]
                    objects = [text for text in components_text]

                    calculations.extend(["{}\n".format(x_velocity_text.get_text()),
                                         "{}\n".format(y_velocity_text.get_text()),
                                         "{} calculated by: ({}^2 + {}^2)^1/2\n".format(
                                             initial_velocity_text.get_text(), x_velocity_text.get_text(),
                                             y_velocity_text.get_text()),
                                         "{} calculated by tan^-1({}/{})\n".format(initial_angle_text.get_text(),
                                                                                   y_velocity_text.get_text(),
                                                                                   x_velocity_text.get_text())])
                objects.extend([initial_height_text, launch_button, info_button,inputs_button])
                # Setting arrow's position and length
                if not velocity_input_switch.get_state():
                    velocity = velocity_slider.get_value()
                    angle = angle_slider.get_value()
                else:
                    velocity = math.sqrt(x_velocity_slider.get_value() ** 2 + y_velocity_slider.get_value() ** 2)
                    try:
                        angle = math.degrees(math.atan(y_velocity_slider.get_value()/x_velocity_slider.get_value()))
                    except ZeroDivisionError:
                        angle = 90

                newArrowposition = set_arrow(velocity, angle, projectile)
                velocity_arrow.set_pos(newArrowposition)
                velocity_arrow.set_image(pygame.transform.rotate(velocity_arrow_image, angle))

        if info_button.isClicked(pygame.mouse.get_pos()):
            popup_window("-To pause the simulation and adjust settings press ESC\n\n"
                         "-If the projectile has not been launched you can press I to bring up the inputs menu\n\n"
                         "-Once the projectile has landed,if it is out of bounds, you can pan the screen using the arrow keys\n\n"
                         "-Press the exit button to leave the simulation\n\n"
                         "-You can view saved projectiles in the My Projectiles window", "Controls", "info")

            info_button.deactivate()

        if exit_button.isClicked(pygame.mouse.get_pos()):
            mode_menu()

        if launch_button.isClicked(pygame.mouse.get_pos()) and not launched:
            objects = [graphic for graphic in objects if
                       graphic not in (initial_velocity_text, initial_height_text, initial_angle_text, x_velocity_text,
                                       y_velocity_text, launch_button)]
            launched = True
            moving = True
            if not velocity_input_switch.get_state():
                projectile.setInitialValues(velocity_slider.get_value(), angle_slider.get_value())
            else:
                projectile.setInitialValues(None, None, x_velocity_slider.get_value(), y_velocity_slider.get_value())

        if launched and moving:
            landed = getattr(projectile, "rect").bottom >= getattr(floor, "rect").top and projectile.get_initial_pos()[
                0] < getattr(projectile, "rect").center[0] and projectile.get_angle() != 90 or projectile.rect.colliderect(floor.rect)
            # checking for collision between floor and projectile

            if landed:
                projectile.set_height(0)
                moving = False
                objects.append(exit_button)
                objects.append(calculations_button)
                objects.append(retry_button)
                original_positions = [position for position in projectile.get_pos_list()]
                if not drag_switch.get_state():
                    objects.append(save_button)
                horizontal_velocity = projectile.get_velocities()[0] / cls.PPM
                total_time = projectile.get_time()
                max_height = projectile.get_max_height(initial_height_slider.get_value())
                horizontal_displacement = round(horizontal_velocity * total_time, 2)
                if not drag_switch.get_state():
                    calculations.extend(
                        ["Maximum height reached: {} m above the ground \n".format(
                            max_height),
                            "Flight time: {}s \n".format(round(total_time,2)),
                            "Horizontal displacement calculated by: {} m/s * {} s = {} m\n\n".format(
                                round(horizontal_velocity, 2),
                                round(total_time, 2),
                                horizontal_displacement)])

                with open("calculations.txt", "r") as calculations_file:
                    lines = sum(1 for _ in calculations_file)  # gets total number of lines in file
                with open("calculations.txt", "a") as calculations_file: #Appending calculations to text file
                    for calculation_num in range(lines, len(calculations)):
                        calculations_file.write("{}. {}".format(calculation_num + 1, calculations[calculation_num]))

        if landed:
            if calculations_button.isClicked(pygame.mouse.get_pos()):
                calculations_tab(simulation_screen, "calculations.txt", simulation)
                calculations_button.deactivate()
            if save_button.isClicked(pygame.mouse.get_pos()) and not drag_switch.get_state():
                save_projectile(simulation_screen, simulation, [max_height, horizontal_displacement])
                save_button.deactivate()
            if retry_button.isClicked(pygame.mouse.get_pos()):
                level()
            pan_screen([projectile, floor, projectile.positions],key_pressed,original_positions,pan_velocity)

        launch([projectile, floor], launched, landed, simulation_screen)
        clock.tick(FPS)
        pygame.display.update()


if __name__ == '__main__':
    main_menu()