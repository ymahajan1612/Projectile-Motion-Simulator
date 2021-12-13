# importing modules required
import pygame, math
from abc import ABC,abstractmethod
pygame.init()
# Defining constants
PPM = 30  # Setting a scale (Pixels per metre)
G = 9.81 * PPM
SCREEN_W = 1430  # Screen width
SCREEN_H = 700  # Screen height
SCREEN_CENTRE = (SCREEN_W / 2, SCREEN_H / 2)  # Defining screen centre
clock = pygame.time.Clock()
# constants for air resistance
MASS = 1
RADIUS = 0.1
DRAG_COEFF = 0.47
DENSITY_AIR = 1.225  # density of air in kg/m^3
SURFACE_AREA = math.pi * RADIUS ** 2
K = 1 / 2 * DENSITY_AIR * DRAG_COEFF

# defining colours
white = (255, 255, 255)
green = (0, 255, 0)
maroon = (128, 0, 0)
navy = (0, 0, 128)
orange = (255, 165, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
purple = (128, 0, 128)
grey = (128, 128, 128)
black = (0, 0, 0)


# --------------------------------------Parent classes-----------------------------------------------------------
class Window:
    def __init__(self, width, height, caption=None, icon=None, background_img=None, background_colour=None):
        self.width = width  # window's width
        self.height = height  # height
        self.caption = caption
        self.icon = icon
        self.background_img = background_img
        self.background_colour = background_colour

    def create_window(self):
        display = pygame.display.set_mode((self.width, self.height))  # setting up display dimensions
        self.display = display  # Creates new attribute: display
        if self.caption:
            pygame.display.set_caption(self.caption)  # setting caption
        if self.icon:
            img = pygame.image.load(self.icon)  # setting window icon
            pygame.display.set_icon(img)
        if self.background_img:  # setting background image
            img = pygame.image.load(self.background_img)  # loading background image
            display.blit(img, (0, -200))  # Drawing image to window
        elif self.background_colour:  # if there is a background colour
            display.fill(self.background_colour)
        return display  # returns the display

    # method to refresh window
    def update_window(self, colour=None, background=None):
        if background:
            self.display.blit(background, (0, 0))
            background.set_alpha(200)
        elif self.background_img:
            image = pygame.image.load(self.background_img)
            self.display.blit(image, (0, -200))
        elif colour:
            self.display.fill(colour)
        elif self.background_colour:
            self.display.fill(self.background_colour)


class Tools(ABC):  # Parent class: Tools
    def __init__(self, x, y, font, font_size, font_colour, colour=black, text="", width=0,
                 height=0):
        self.x = x
        self.y = y
        self.font = font
        self.font_colour = font_colour
        self.font_size = font_size
        self.colour = colour
        self.text = text
        self.width = width
        self.height = height
        self.active = False

    def isClicked(self, pos):
        if self.x < pos[0] < self.x + self.width and pos[1] > self.y and pos[1] < self.y + self.height:
            if pygame.mouse.get_pressed()[0]:
                self.active = True
        else:
            self.active = False

        return self.active

    def get_text(self):
        return self.text

    @abstractmethod
    def draw(self):
        pass

class Sprite(pygame.sprite.Sprite):  # Sprite class-creating an interface
    def __init__(self, x_pos, y_pos, image):
        super(Sprite, self).__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = pygame.image.load(image)
        self.image_size = self.image.get_size()
        self.rect = self.image.get_rect()  # creating a rectangle for sprite
        self.rect.width = self.image_size[0]
        self.rect.height = self.image_size[1]
        # setting rectangle x and y positions
        self.rect.x = self.x_pos
        self.rect.y = self.y_pos
        # setting rectangle's width and height
        self.rect_width = self.rect.width
        self.rect_height = self.rect.height
        self.active = False

    def set_image(self, new_image):
        self.image = new_image

    def get_image(self):
        return self.image

    def get_pos(self):
        return self.rect.center

    def set_pos(self, new_pos):
        self.rect.center = new_pos

    def get_top(self):
        return self.rect.top


# --------------------------------Sprite sub-classes-----------------------------------
class Projectile(Sprite):
    dt = 0.05  # class variable (defining time step)

    def __init__(self, x_pos, y_pos):
        super(Projectile, self).__init__(x_pos, y_pos, image="projectile.png")
        self.rect.bottom = 540  # setting the position
        # getting initial x and y values
        self.initial_x = self.rect.centerx
        self.initial_y = self.rect.centery
        # setting all initial values to 0
        self.launch_angle = 0
        self.initial_velocity = 0
        self.initial_vel_x = 0
        self.initial_vel_y = 0
        self.time = 0
        self.vel_y = 0
        self.positions = []
        self.max_px = 0
        self.first_check = True  # first check for max height
        # a boolean to check if projectile is above the ground
        self.above_ground =  False
        # setting initial height
        self.initial_height = (540 - self.rect.bottom) / PPM
        self.off_screen = [False, False]
        self.drag = False
        self.dp = 2

    def setInitialValues(self, velocity=None, angle=None, v_x=None, v_y=None):
        if velocity and angle is not None:
            self.launch_angle = angle
            self.initial_velocity = velocity * PPM  # converts from m/s to px/s
            self.initial_vel_x = self.initial_velocity * math.cos(math.radians(self.launch_angle))
            self.initial_vel_y = self.initial_velocity * math.sin(math.radians(self.launch_angle))
            self.vel_y = self.initial_vel_y
        elif v_x and v_y is not None:
            try:
                self.launch_angle = math.degrees(math.atan(v_y/v_x))
            except ZeroDivisionError:
                self.launch_angle = 90
            self.initial_velocity = math.sqrt(v_x ** 2 + v_y ** 2) * PPM  # Vi = sqrt(Vx**2 + Vy**2)
            self.initial_vel_x = v_x * PPM
            self.initial_vel_y = v_y * PPM
            self.vel_y = v_y * PPM

    def set_height(self, height):
        if height != 0:
            self.rect.bottom -= (height * 45)
            # new initial x and y values
            self.initial_x = self.rect.centerx
            self.initial_y = self.rect.centery
            self.above_ground = True if self.rect.bottom != 540 else False
        else:
            self.rect.bottom = 540

    def get_initial_pos(self):
        return self.initial_x, self.initial_y

    def update_pos(self):
        self.time += self.dt  # incrementing time by dt

        if self.time >= -self.initial_vel_y / -G and self.first_check:  # Getting the max height  using v-u/G = time
            self.max_px = self.rect.center
            self.vel_y = 0
            self.first_check = False  # ensures check only occurs once
        if self.time >= (self.initial_vel_y * 2) / G:  # if time is exceeded due to dt
            if self.above_ground:
                # quadratic formula to calculate value for time using the SUVAT: s = ut + 1/2at^2
                discriminant = ((self.initial_vel_y / PPM) ** 2) - 4 * (G / PPM / 2 * -self.initial_height)
                # two values for the extra time taken for projectile to hit floor
                extra_time_1 = (-(self.initial_vel_y / PPM) - math.sqrt(discriminant)) / (G / PPM)
                extra_time_2 = (-(self.initial_vel_y / PPM) + math.sqrt(discriminant)) / (G / PPM)
                # discarding negative value of time
                extra_time = extra_time_1 if extra_time_2 < 0 else extra_time_2
                self.time += extra_time
            else:
                self.time = (self.initial_vel_y * 2) / G  # A method of fixing the truncation error caused by time step
        if self.drag:
            self.rect.centerx = (self.initial_x + (self.Vx_drag() * self.time))
            self.rect.centery = (self.initial_y + (self.Vy_drag() * self.time))
        else:
            self.rect.centerx = (self.initial_x + (self.initial_vel_x * self.time))  # Using the equation s = Vt
        if self.initial_vel_y != 0 or self.rect.bottom < 540:
            # total resistive forces using F_total = mass * acceleration
            if self.drag:
                # total force = force due to gravity + drag force
                F_total = (G) + (K * self.vel_y) # drag force = 1/2 * density * velocity * dragcoeff * surface area
            else:
                F_total = G
            self.rect.centery = (self.initial_y - (
                    (self.initial_vel_y * self.time) - (F_total / 2 * self.time ** 2)))  # s = ut + 1/2at^2
        if self.get_displacement() >= 0:
            self.vel_y = math.sqrt(
                (self.initial_vel_y / PPM) ** 2 + (2 * (-G / PPM) * (self.get_displacement() / PPM)))  # v^2 = u^2 + 2as
        else:
            self.vel_y = 0
        self.positions.append(self.rect.center)
        self.is_off_screen()

    def is_off_screen(self):
        for coordinate in self.positions:
            if coordinate[0] > SCREEN_W:
                self.off_screen[0] = True
            if coordinate[1] < 0:
                self.off_screen[1] = True
        return self.off_screen

    def draw_trail(self, display):
        for position in self.positions:
            if position == self.max_px:
                pygame.draw.circle(display, red, self.max_px, 5)
            else:
                pygame.draw.circle(display, white, position, 5)

    def get_displacement(self):
        vertical_displacement = (self.initial_vel_y * self.time) + ((-G / 2) * (self.time ** 2))
        return vertical_displacement

    def get_velocity(self):
        return round(math.sqrt((self.initial_vel_x / PPM) ** 2 + (self.vel_y / PPM) ** 2), 1)

    def get_max_height(self, initial_height):
        max_height = (0 - (self.initial_vel_y / PPM) ** 2) / (2 * -G / PPM)
        if self.above_ground:
            max_height += initial_height
        return round(max_height, self.dp)

    def get_angle(self):
        return self.launch_angle

    def is_above_ground(self):
        return self.above_ground

    def get_velocities(self):
        return self.initial_vel_x, self.vel_y

    def get_time(self):
        return self.time

    def get_pos_list(self, direction=None):
        #Returns a list containing the (x,y) coordinates of the projectile
        if direction:
            if direction.lower() == "x":
                return [position[0] for position in self.positions]
            elif direction.lower() == "y":
                return [position[1] for position in self.positions]
        return self.positions

    def set_pos_list(self, new_positions):
        # replace the list of (x,y) coordinates of the projectile with new_positions
        self.positions = new_positions

    def Vx_drag(self):
        Vx = self.initial_vel_x * math.pow(math.e, (-K * self.time) / MASS)
        return Vx

    def Vy_drag(self):
        Vy = ((MASS * G) / K) * (math.pow(math.e, (-K * self.time)/MASS)-1)
        return Vy

    def toggle_drag(self):
        self.drag = not self.drag

# --------------------------------Tools sub-classes------------------------------------
class Text(Tools):
    def __init__(self, x, y, font, width, height, colour, text, font_size):
        super(Text, self).__init__(x, y, font, width, height, colour, text)  # inheriting from Tools
        self.font_size = font_size

    def update_text(self, new_text):
        self.text = new_text

    def get_y(self):
        return self.y

    def set_y(self, pixels):
        if self.y:
            self.y += pixels
        else:
            self.y = pixels

    def draw(self, display):  # method to display text to screen
        font = pygame.font.SysFont(self.font, self.font_size)  # setting font
        text_surface = font.render(str(self.text),True, self.colour)  # rendering text surface
        display.blit(text_surface, (self.x, self.y))  # displaying text to screen


class Button(Tools):
    def __init__(self, x, y, font, font_size, font_colour, colour, text, width, height,image=None):
        super().__init__(x, y, font, font_size, font_colour, colour, text, width, height)
        self.image = image

    def draw(self, display, outline=True):  # Option for outline on button
        if outline:
            pygame.draw.rect(display, outline,
                             (self.x - 2, self.y - 2, self.width + 4, self.height + 4))  # larger rect.
        pygame.draw.rect(display, self.colour, (self.x, self.y, self.width, self.height))  # Create button rectangle

        if self.text != "" and self.font != "":
            font = pygame.font.SysFont(self.font, self.font_size)  # initialising Pygame font
            text = font.render(self.text, True, self.font_colour)  # Rendering font
            display.blit(text, (self.x + (self.width / 2 - text.get_width() / 2),
                                self.y + (self.height / 2 - text.get_height() / 2)))  # Drawing text to screen


        if self.image:
            image_rect = self.image.get_rect(center=(self.x+self.width/2,self.y+self.height/2))
            display.blit(self.image,image_rect)

    def deactivate(self):
        self.active = False


class Text_box(Tools):
    def __init__(self, x, y, width, height, input_type, font_size, mask=False):
        super(Text_box, self).__init__(x, y, width, height, font_size)
        self.rect = pygame.Rect(x, y, width, height)  # Creates the textbox using rect.
        self.font = pygame.font.SysFont(None, self.font_size)  # setting the font to pygame default (None)
        self.colour = black  # colour of the box
        self.font_colour = black  # colour of the font
        self.text_rect = self.font.render(self.text, True, self.font_colour)  # creating the text surface
        self.active = False  # setting to False
        self.input_type = input_type  # expected data type of input (could be str, int or float)
        self.mask = mask  # characters replaced by *
        try:
            self.variable = self.input_type(self.text)  # setting input to correct type
        except:
            self.variable = None

    def add_chars(self, event):  # A method which adds user's input to the textbox
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):  # checks if textbox clicked
                self.active = True  # sets to True
                self.colour = white  # changes colour to white
            else:
                self.active = False  # if mouse clicks off the textbox
                self.colour = black
        if event.type == pygame.KEYDOWN:  # adding characters
            if self.active:
                # Refreshing text
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif self.text_rect.get_width() + 10 < self.rect.width:
                    self.text += event.unicode
            if self.mask:
                self.text_rect = self.font.render("*" * len(self.text), True,
                                                  self.font_colour)  # renders the text (masked)
            else:
                self.text_rect = self.font.render(self.text, True, self.font_colour)  # renders the text

    def draw(self, display):  # a method to draw the textbox to the screen
        display.blit(self.text_rect, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(display, self.colour, self.rect, 2)


class Slider(Tools):
    def __init__(self, x, y, max_val, min_val, default_val, colour, width, height, dp=1):
        super(Slider, self).__init__(x, y, colour, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_val = max_val
        self.min_val = min_val
        self.default_val = default_val
        self.scale = self.get_scale()
        self.slider_square = pygame.Rect((self.default_val * self.scale + self.x - 25, self.y), (50, self.height))
        self.slider_rect = pygame.Rect(x - 25, self.y, self.width + 50, self.height)
        self.colour = colour
        self.square_colour = black
        self.max_x = self.slider_rect.x + self.slider_rect.width
        self.active = False
        self.dp = dp  # dp: decimal places

    def get_scale(self):  # returns slider's scale
        scale = self.width / (self.max_val - self.min_val)
        return scale

    def draw(self, display):
        pygame.draw.rect(display, self.colour, self.slider_rect)  # draws slider rectangle
        pygame.draw.rect(display, self.square_colour, self.slider_square)  # draws slider's square

    def set_colour(self, hover_colour):  # changing the colour when slider is clicked
        self.square_colour = hover_colour

    def get_value(self):  # returns the value of the slider
        value = (self.slider_square.left + 25 - self.x) / self.scale
        return round(value, self.dp)  # returns value rounded to specified dp

    def set_value(self, num):
        self.value = num

    def get_dimensions(self):  # gets slider dimensions
        return self.slider_rect.x, self.y, self.slider_rect.width

    def update(self, new_pos):
        if new_pos < self.x:
            new_pos = self.x
        elif new_pos > self.x + self.width:
            new_pos = self.x + self.width
        self.slider_square.left = new_pos - 25


class Toggle(Tools):
    def __init__(self, x, y, width, height, colour_on, colour_off, default_state):
        super(Toggle, self).__init__(x, y, width, height, None)
        self.width = width
        self.height = height
        self.x = x - self.width/2
        self.y = y - self.height/2
        self.colour_on = colour_on
        self.colour_off = colour_off
        self.switch_colour = white
        self.default_state = default_state
        self.state = self.default_state

    def draw(self, screen):
        if not self.state:
            colour = self.colour_off  # sets colour
            switch_x = self.x  # switch x position = toggle x position
        else:
            colour = self.colour_on
            switch_x = self.x + (self.width / 2)  # switch moved to right half
        pygame.draw.rect(screen, black, (self.x - 2, self.y - 2, self.width + 4, self.height + 4))  # drawing outline
        pygame.draw.rect(screen, colour, (self.x, self.y, self.width, self.height))
        switch_rect = pygame.Rect((switch_x, self.y, self.width / 2, self.height))
        pygame.draw.rect(screen, self.switch_colour, switch_rect)

    def switch(self):
        self.state = not self.state

    def get_state(self):
        return self.state
