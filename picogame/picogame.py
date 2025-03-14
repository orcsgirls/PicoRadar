import board
import busio
import displayio
import terminalio
import adafruit_imageload
import time
from adafruit_display_text import label
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
from fourwire import FourWire
from adafruit_st7789 import ST7789
from digitalio import DigitalInOut, Direction, Pull

#-----------------------------------------------------------------------------------------------------------
# Game Classes for Platformer
#-----------------------------------------------------------------------------------------------------------

class Picogame():
    def __init__(self):
        displayio.release_displays()
        spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=None)
        tft_cs = board.GP9
        tft_dc = board.GP8
        tft_rst = board.GP12
        display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)

        self.display = ST7789(display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53)

        self.joystickUp = Button(board.GP2)
        self.joystickDown = Button(board.GP18)
        self.joystickLeft = Button(board.GP16)
        self.joystickRight = Button(board.GP20)
        self.joystickCenter = Button(board.GP3)
        self.buttonA = Button(board.GP15)
        self.buttonB = Button(board.GP17)

        self.game = displayio.Group()
        self.display.root_group = self.game

    def append(self, obj):
        self.game.append(obj)

    def remove(self, obj):
        self.game.remove(obj)

#-----------------------------------------------------------------------------------------------------------
class GameObject():

    def __init__(self):
        pass

    def reset(self):
        pass

    @property
    def x(self):
        return self.group.x

    @x.setter
    def x(self, value):
        self.group.x = value

    @property
    def y(self):
        return self.group.y

    @y.setter
    def y(self, value):
        self.group.y = value

    @property
    def height(self):
        return self.group.height

    @property
    def width(self):
        return self.group.width

    @property
    def visible(self):
        return not self.group.hidden

    @visible.setter
    def visible(self, visible):
        self.group.hidden = not visible

#-----------------------------------------------------------------------------------------------------------
class Wall(GameObject):
    def __init__(self, game, gap=30, thickness=10, wall_color=0x0000FF, gap_color=0x000000):
        self.game = game
        self.gap = gap
        self.wall_color = wall_color
        self.gap_color = gap_color
        self.thickness = thickness
        self.group = displayio.Group()
        self.solid = Rect(0, 0, self.thickness, self.game.display.height, fill=wall_color)
        self.hole = Rect(0, 0, self.thickness, self.gap, fill=gap_color)
        self.group.append(self.solid)
        self.group.append(self.hole)
        self.game.append(self.group)
        self.reset()

    def reset(self):
        self.solid.x = self.game.display.width
        self.solid.y = 0
        self.solid.fill = self.wall_color
        self.hole.x = self.game.display.width
        self.hole.y = int((self.game.display.height-self.gap)/2)
        self.hole.fill = self.gap_color

    @property
    def x(self):
        return self.hole.x

    @x.setter
    def x(self, value):
        self.solid.x = value
        self.hole.x = value

    @property
    def y(self):
        return int(self.hole.y+int(self.gap/2))

    @y.setter
    def y(self, value):
        self.hole.y = int(value-int(self.gap/2))

    @property
    def height(self):
        return self.gap

    @property
    def width(self):
        return self.thickness

    @property
    def color(self):
        return self.solid.fill

    @color.setter
    def color(self, color):
        self.solid.fill = color

#-----------------------------------------------------------------------------------------------------------
class Ball(GameObject):
    def __init__(self, game, radius=10, color=0x00FF00):
        self.game = game
        self.radius = radius
        self.group = Circle(0, 0, radius, fill=color)
        self.game.append(self.group)
        self.reset()

    def reset(self):
        self.group.x = 10
        self.group.y = int(self.game.display.height/2)-self.radius

    @property
    def y(self):
        return int(self.group.y+self.radius)

    @y.setter
    def y(self, value):
        if(value >=0 and value <= self.game.display.height):
            self.group.y = int(value-self.radius)

    @property
    def height(self):
        return 2*self.radius

    @property
    def width(self):
        return 2*self.radius

#-----------------------------------------------------------------------------------------------------------
class Box(GameObject):
    def __init__(self, game, x=0, y=0, width=100, height=20, color=0x00FF00):
        self.game = game
        self.color = color
        self.group = Rect(x, y, width, height, fill=color)
        self.game.append(self.group)

#-----------------------------------------------------------------------------------------------------------
class Text(GameObject):
    def __init__(self, game, font_size=3, x=0, y=0, color=0xFFFF00, anchor=(0.0,0.0)):
        self.game = game
        self.group = label.Label(terminalio.FONT, color=color, scale=font_size,
                                 anchor_point=anchor, anchored_position=(x,y))
        self.group.x = x
        self.group.y = y
        self.game.append(self.group)
        self.reset()

    def reset(self):
        self.group.text = ""

    @property
    def text(self):
        return self.group.text

    @text.setter
    def text(self, string):
        self.group.text = string

    @property
    def textColor(self):
        return self.group.color

    @textColor.setter
    def textColor(self, color):
        self.group.color = color

#-----------------------------------------------------------------------------------------------------------
class Score(Text):
    def __init__(self, game, font_size=3, x=190, y=20, color=0xFFFF00, anchor=(0.0,0.0)):
        super(Score, self).__init__(game, font_size=font_size, x=x, y=y, color=color, anchor=anchor)
        self.score_value = 0
        self.reset()

    def reset(self):
        self.score_value = 0
        self.group.text = str(self.score_value)

    def add(self, points):
        self.score_value = self.score_value + points
        self.group.text = str(self.score_value)

    @property
    def value(self):
        return self.score_value

    @value.setter
    def value(self, value):
        self.score_value = value
        self.group.text = str(self.score_value)

#-----------------------------------------------------------------------------------------------------------
class Sign(GameObject):
    def __init__(self, game, string="ORCSGirls", border_width=20, text_scale=3,
                             outer_color=0x3333FF, inner_color=0xAA0088, text_color=0xFFFF00):
        self.game = game
        self.string = string
        self.border_width = border_width
        self.text_scale = text_scale
        self.outer_color = outer_color
        self.inner_color = inner_color
        self.text_color = text_color
        self.group = displayio.Group()

        # Big rectangle
        self.color_bitmap = displayio.Bitmap(self.game.display.width, self.game.display.height, 1)
        self.color_palette = displayio.Palette(1)
        self.color_palette[0] = self.outer_color
        self.bg_sprite = displayio.TileGrid(self.color_bitmap, pixel_shader=self.color_palette, x=0, y=0)
        self.group.append(self.bg_sprite)

        # Draw a smaller inner rectangle
        self.inner_bitmap = displayio.Bitmap(self.game.display.width-(self.border_width*2),
                                        self.game.display.height-(self.border_width*2), 1)
        self.inner_palette = displayio.Palette(1)
        self.inner_palette[0] = self.inner_color
        self.inner_sprite = displayio.TileGrid(self.inner_bitmap, pixel_shader=self.inner_palette,
                                               x=self.border_width, y=self.border_width)
        self.group.append(self.inner_sprite)

        # Draw a label
        self.text_area = label.Label(terminalio.FONT, text=self.string, color=self.text_color,
                                     scale=self.text_scale, anchor_point=(0.5, 0.5),
                                     anchored_position=(self.game.display.width//2, self.game.display.height//2))
        self.group.append(self.text_area)
        self.game.append(self.group)

    def switch(self):
        outer_color=self.color_palette[0]
        inner_color=self.inner_palette[0]
        self.color_palette[0] = inner_color
        self.inner_palette[0] = outer_color

    def reset(self):
        self.text_area.text = "ORCSGirls"

    @property
    def text(self):
        return self.text_area.text

    @text.setter
    def text(self, string):
        self.text_area.text = string

    @property
    def textColor(self):
        return self.text_area.color

    @textColor.setter
    def textColor(self, color):
        self.text_area.color = color

    @property
    def innerColor(self):
        return self.inner_palette[0]

    @innerColor.setter
    def innerColor(self, color):
        self.inner_palette[0] = color

    @property
    def outerColor(self):
        return self.color_palette[0]

    @outerColor.setter
    def outerColor(self, color):
        self.color_palette[0] = color

    @property
    def outerColor(self):
        return self.color_palette[0]

#-----------------------------------------------------------------------------------------------------------
class Sprite(GameObject):

    def __init__(self, game, index=1, scale=1):
        sprite_file = "/sprites/cp_sprite_sheet.bmp"
        self.game = game
        self.scale = scale
        self.index = index
        sprite_sheet, palette = adafruit_imageload.load(sprite_file, bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(19)  # Transparent background
        self.sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette, width=1, height=1, tile_width=16, tile_height=16)
        self.group = displayio.Group(scale=self.scale)
        self.group.append(self.sprite)
        self.game.append(self.group)
        self.reset()

    def reset(self):
        self.sprite[0] = self.index
        self.group.x = 10
        self.group.y = int(self.game.display.height/2)-self.scale*8

    @property
    def y(self):
        return int(self.group.y+self.scale*8)

    @y.setter
    def y(self, value):
        if(value >=0 and value <= self.game.display.height):
            self.group.y = int(value-self.scale*8)

    @property
    def height(self):
        return self.scale*16

    @property
    def width(self):
        return self.scale*16

    @property
    def type(self):
        return self.index

    @type.setter
    def type(self, value):
        if (value >= 1 and value <= 6):
            self.index = int(value)
        else:
            print('Invalid index')

#-----------------------------------------------------------------------------------------------------------
class Timer():

    def __init__(self):
        self.current_status = 'stopped'
        self.start_time = 0
        self.stop_time = 0

    def start(self):
        if(self.current_status == 'stopped'):
            self.start_time = time.monotonic()
        self.current_status = 'running'

    def stop(self):
        if(self.current_status == 'running'):
            self.stop_time = time.monotonic() - self.start_time
        self.current_status = 'stopped'

    def reset(self):
        self.current_status = 'stopped'
        self.start_time = 0
        self.stop_time = 0

    @property
    def status(self):
        return self.current_status

    @property
    def value(self):
        if(self.current_status == 'running'):
            return (time.monotonic() - self.start_time)
        else:
            return self.stop_time

#-----------------------------------------------------------------------------------------------------------
class Button():
    def __init__(self, pin):
        self.btn = DigitalInOut(pin)
        self.btn.direction = Direction.INPUT
        self.btn.pull = Pull.UP
        self.lastState = self.btn.value

    def isPressed(self):
        currentState = self.btn.value
        if currentState != self.lastState:
            self.lastState=currentState
            return currentState
        else:
            return False

    @property
    def value(self):
        return self.btn.value

