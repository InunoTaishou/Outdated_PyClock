import pygame
import datetime
import os
import copy
import glob
from constants import *
from PIL import ImageFont

if os.name != 'nt':
    import subprocess

OpenType_extensions = frozenset(('.ttf', '.ttc', '.otf'))
SUPPORTED_CONTROLS = frozenset(('label', 'button', 'picture', 'animation'))
SUPPORTED_CONTROL_STYLES = frozenset(('flat', 'gradient'))
SUPPORTED_ATTRIBUTES = frozenset(('oblique', 'condensed', 'extralight',
                                  'semibold', 'semilight', 'italic', 'bold',
                                  'light', 'black', 'book', 'condensed bold',
                                  'semibold italic', 'semilight italic',
                                  'bold italic', 'black italic', 'light italic'))


class PyGameControls(object):
    def __init__(self):
        self._default_font = ''
        self._default_font_key = ''
        self._default_attribute = ['regular']
        self._default_font_file = ''
        self._font_files = self.__font_list()
        self._fonts = self.__init_fonts()

    def create_label(self, surface, text, x, y, width=None, height=None, style=None, properties=None, font=None):
        return Label(self, surface, text, x, y, width, height, style, properties, font)

    def create_pic(self, surface, file, x, y, width=None, height=None, style=None, properties=None):
        return Picture(self, surface, file, x, y, width, height, style, properties)

    def create_font(self, family_name, size, attribute):
        return Font(self, family_name, size, attribute)

    def add_font(self, font_file):
        if font_file not in self._font_files:
            self._font_files.append(font_file)
            f = ImageFont.truetype(font_file)
            family_lower = f.font.family.lower()
            style_lower = f.font.style.lower()

            if family_lower in self._fonts:
                self._fonts[family_lower].update({style_lower: font_file})
            else:
                self._fonts[family_lower] = {'family': f.font.family, style_lower: font_file}
            del f
            return True
        return False

    @property
    def default_font(self):
        return self._default_font

    @property
    def default_font_key(self):
        return self._default_font_key

    @property
    def default_attribute(self):
        return self._default_attribute[0]

    @property
    def default_font_file(self):
        return self._default_font_file

    @default_font.setter
    def default_font(self, family_name, attribute='regular'):
        attribute = self._proper_attribute(attribute)
        if not attribute:
            attribute = ['regular']

        font_file = self.find_font(family_name, attribute)

        if font_file != self._default_font_file:
            self._default_font = family_name
            self._default_font_key = family_name.lower()
            self._default_attribute = attribute
            self._default_font_file = font_file

    @default_attribute.setter
    def default_attribute(self, attribute):
        attribute = self._proper_attribute(attribute)
        if attribute:
            self._default_attribute = attribute

    @staticmethod
    def _proper_attribute(attribute):
        if isinstance(attribute, tuple):
            attribute = list(attribute)
        elif isinstance(attribute, str):
            attribute = [attribute]
        if not isinstance(attribute, list):
            attribute = ['regular']
        else:
            attribute[0] = attribute[0].lower()

        if attribute[0] in SUPPORTED_ATTRIBUTES:
            return attribute
        return False

    @staticmethod
    def toascii(raw):
        """return ASCII characters of a given unicode or 8-bit string"""
        return raw.decode('ascii', 'ignore')

    def find_font(self, family_name, attribute):
        attribute = self._proper_attribute(attribute)
        if not attribute:
            attribute = self._default_attribute

        if family_name in self._fonts:
            if attribute[0] in self._fonts[family_name]:
                return self._fonts[family_name][attribute[0]]

            if 'regular' not in attribute[0]:
                if 'bold' in attribute[0] \
                        and 'condensed' in attribute[0] \
                        and 'condensed bold' in self._fonts[family_name]:
                    attribute[0] = 'condensed bold'
                    return self._fonts[family_name][attribute[0]]

                for attrib in ('semibold', 'semilight', 'bold', 'black', 'light'):
                    if attrib + ' italic' in self._fonts[family_name]:
                        attribute[0] = attrib + ' italic'
                        return self._fonts[family_name][attribute[0]]

                for attrib in ('oblique', 'condensed', 'extralight', 'semibold',
                               'semilight', 'italic', 'bold', 'light', 'black', 'book'):
                    if attrib in self._fonts[family_name]:
                        attribute[0] = attrib
                        return self._fonts[family_name][attrib]

            elif 'regular' in self._fonts[family_name]:
                attribute[0] = 'regular'
                return self._fonts[family_name]['regular']

        return self._fonts[self._default_font_key]['regular']

    def add_font(self, font):
        if not isinstance(font, str) or not os.path.isfile(font):
            return False

        if font in self._font_files:
            return True

        f = ImageFont.truetype(font)
        family_lower = f.font.family.lower()
        style_lower = f.font.style.lower()

        if family_lower in self._fonts:
            if style_lower in self._fonts[family_lower] and not os.path.isfile(self._fonts[family_lower][style_lower]):
                self._fonts[family_lower].update({style_lower: font})
        else:
            self._fonts[family_lower] = {'family': f.font.family, style_lower: font}
        del f
        return True

    def __font_list(self):
        font_files = []

        # get fonts in the current directory
        for extension in OpenType_extensions:
            for font in glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), '*' + extension)):
                if font not in font_files:
                    font_files.append(font)

        # if the OS is windows
        if os.name == 'nt':
            self._default_font = 'Segoe UI'
            self._default_font_key = 'segoe ui'
            self._default_attribute = ['regular']

            for extension in OpenType_extensions:
                for font in glob.glob('C:\\Windows\\Fonts\\*' + extension):
                    if font not in font_files:
                        font_files.append(font)
        # OS is Linux
        else:
            try:
                flout, flerr = subprocess.Popen('%s : file family style' % 'fc-list', shell=True,
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                close_fds=True).communicate()
            except Exception:
                pass

            try:
                for line in self.toascii(flout).splitlines():
                    try:
                        font, family, style = line.split(':', 2)
                        if font[font.rfind('.'):].lower() in OpenType_extensions:
                            if font not in font_files:
                                font_files.append(font)

                    except Exception:
                        # try the next one.
                        pass

            except Exception:
                pass

        return font_files

    def __init_fonts(self):
        fonts = dict()

        for font in self._font_files:
            f = ImageFont.truetype(font)
            family_lower = f.font.family.lower()
            style_lower = f.font.style.lower()

            if family_lower in fonts:
                fonts[family_lower].update({style_lower: font})
            else:
                fonts[family_lower] = {'family': f.font.family, style_lower: font}
            del f

        if not self._default_font_key or self._default_font_key not in fonts:
            if 'freesans' in fonts:
                if 'regular' in fonts['freesans']:
                    self._default_font = fonts['freesans']['family']
                    self._default_font_key = 'freesans'
                    self._default_attribute = ['regular']
                    self._default_font_file = fonts['freesans']['regular']

        if not self._default_font_key or self._default_font_key not in fonts:
            print('Windows Segoe UI and backup FreeSans font not in system, selecting a random font')
            for font in fonts:
                if 'regular' in fonts[font]:
                    self._default_font = fonts[font]['family']
                    self._default_font_key = font
                    self._default_attribute = ['regular']
                    self._default_font_file = fonts[self._default_font_key]['regular']
                    break
        else:
            self._default_font_file = fonts[self._default_font_key][self._default_attribute[0]]

        return fonts

    @staticmethod
    def _check_style(style, default, forced_styles):
        if not style or len(style) == 0:
            return default
        elif not isinstance(style, list):
            if isinstance(style, int):
                style = [style]
            elif isinstance(style, str):
                style = [int(style)]
        else:
            for i in range(len(style)):
                if isinstance(style[i], str):
                    style[i] = int(style[i])
        if forced_styles and isinstance(forced_styles, list):
            style += forced_styles

        seen = set()
        return [x for x in style if not (x in seen or seen.add(x))]

    @staticmethod
    def _format_text(text_to_format, pygame_font, rect, style, wrap_at_letter=True):
        if not isinstance(text_to_format, str):
            text_to_format = str(text_to_format)

        if not text_to_format:
            return ''

        text_to_format = text_to_format.replace('\t', '')

        lines_of_string = text_to_format.splitlines()

        # text_to_format that will hold the newly formatted text_to_format
        new_string = ''

        for line in lines_of_string:
            if line == '':
                new_string += '\n'
            else:
                while line:
                    amps = []

                    if TS_NOPREFIX not in style:
                        while line.find('&') != -1:
                            index = line.find('&')
                            amps.append(index)
                            line = line[:index] + line[index + 1:]

                    if TS_LEFTNOWORDWRAP not in style:
                        char_index = 0
                        line_size = pygame_font.size(line[:char_index])[0]
                        # start building this line
                        while line_size <= rect.width and char_index < len(line):
                            char_index += 1
                            line_size = pygame_font.size(line[:char_index])[0]

                        if len(amps):
                            for amp in reversed(amps):
                                if amp < char_index:
                                    char_index += 1
                                line = line[:amp] + '&' + line[amp:]

                        # whole string does not fit on this line
                        if char_index < len(line) or line_size > rect.width:
                            # find the last word in this line up until the char_index position
                            j = line.rfind(' ', 0, char_index) + 1

                            # no words found (no space), this string is way long to be drawn in this area
                            if j == 0:
                                if TS_MULTILINE in style or wrap_at_letter:
                                    # if the string in line[:char_index] == the rect.width, it can be drawn on this line
                                    # but if it's > rect.width, shift char_index over to the left 1
                                    if line_size > rect.width:
                                        char_index -= 1
                                # can't wrap at the letter, text outside the rect will be clipped
                                else:
                                    char_index = len(line)
                            # a word was found, cut back to it
                            else:
                                if TS_WORDELLIPSIS not in style:
                                    # print('TS_WORDELLPISIS is not in style')
                                    char_index = j
                                else:
                                    char_index = j - 1
                                    line = line[:char_index] + line[char_index + 1:]
                        # whole string fits on this line
                        else:
                            if TS_MULTILINE in style or wrap_at_letter:
                                # if the string in line[:char_index] == the rect.width, it can be drawn on this line
                                # but if it's > rect.width, shift char_index over to the left 1
                                if line_size > rect.width:
                                    char_index -= 1
                            else:
                                char_index = line.find(' ', char_index)
                                if char_index == -1:
                                    char_index = len(line)
                    # TS_LEFTNOWORDWRAP is in the style, leave this line alone and let it be cut off
                    else:
                        char_index = len(line)

                    new_string += line[:char_index] + '\n'
                    # trim the string we took out of this line
                    line = line[char_index:]
        # return the properly formatted string, complete with newlines
        return new_string[:-1]

    @staticmethod
    def draw_style(surface, properties, style, bk_color, border_color, rect):
        if properties.px_border and bk_color != border_color:
            pygame.draw.rect(surface, border_color,
                             pygame.Rect(0, 0, rect.width, rect.height), properties.px_border)
        if SS_ETCHEDFRAME in style:
            pygame.draw.lines(surface, (255, 255, 255, 255), False,
                              [(0, 0),
                               (0, rect.height),
                               (rect.width, rect.height),
                               (rect.width, 0),
                               (0, 0)], 2)
            pygame.draw.lines(surface, (160, 160, 160, 255), False,
                              [(0, 0),
                               (0, rect.height - 1),
                               (rect.width - 1, rect.height - 1),
                               (rect.width - 1, 0),
                               (0, 0)], 1)
        elif SS_ETCHEDHORZ in style:
            pygame.draw.line(surface, (255, 255, 255, 255),
                             (0, 0),
                             (rect.width, 0),
                             2)
            pygame.draw.line(surface, (160, 160, 160, 255),
                             (0, 0),
                             (rect.width - 2, 0),
                             1)
        elif SS_ETCHEDVERT in style:
            pygame.draw.line(surface, (255, 255, 255, 255),
                             (0, 0),
                             (0, rect.height),
                             2)
            pygame.draw.line(surface, (160, 160, 160, 255),
                             (0, 0),
                             (0, rect.height - 2),
                             1)
        elif SS_SUNKEN in style:
            pygame.draw.lines(surface, (160, 160, 160, 255), False,
                              [(0, rect.height - 2),
                               (0, 0),
                               (rect.width - 2, 0)],
                              1)
            pygame.draw.lines(surface, (255, 255, 255, 255), False,
                              [(0, rect.height - 1),
                               (rect.width - 1, rect.height - 1),
                               (rect.width - 1, 0)],
                              1)


class Picture:
    def __init__(self, pygamecontrol, surface, file, x, y, width=None, height=None, style=None, properties=None):
        if not isinstance(surface, pygame.Surface):
            print('second argument, surface, not a valid pygame.Surface')
            raise ValueError
        if not isinstance(pygamecontrol, PyGameControls):
            print('first argument, pygamecontrol, not a valid PyGameControls')
            raise ValueError

        if isinstance(x, str) or isinstance(x, float):
            x = int(x)
        if isinstance(y, str) or isinstance(y, float):
            y = int(y)
        if isinstance(width, str) or isinstance(width, float):
            width = int(width)
        if isinstance(height, str) or isinstance(height, float):
            height = int(height)
        if x is None:
            print('x value cannot be none')
            raise ValueError
        if y is None:
            print('y value cannot be none')
            raise ValueError
        if width is None or width < 0:
            width = 0
        if height is None or height < 0:
            height = 0
        if isinstance(file, tuple):
            file = list(file)
        if isinstance(file, list):
            if len(file) == 0:
                file = ''

        self.__state = STATE_NORMAL
        self.__state_copy = STATE_NORMAL
        self.__surface_normal = None
        self.__surface_hot = None
        self.__surface_pressed = None
        self.__surface_focused = None
        self.__surface_disabled = None
        self.__surface_to_draw = None
        self.__surface_files = []
        self.__rect_normal = pygame.Rect(x, y, width, height)
        self.__x = x
        self.__y = y
        self.__rect_hot = None
        self.__rect_pressed = None
        self.__rect_focused = None
        self.__rect_disabled = None
        self.__pygamecontrol = pygamecontrol
        self.__surface = surface
        self.__forced_styles = [IMS_BITMAP]
        self.__style = self.__pygamecontrol._check_style(style, [IMS_BITMAP, IMS_REALSIZEIMAGE], self.__forced_styles)
        self.__properties = properties \
            if isinstance(properties, ControlProperties) \
            else ControlProperties('picture', 'flat')
        self.__properties_copy = self.__properties
        self.__style_copy = self.__style
        self.__rect = None
        self.__rect_copy = None
        self.__check_rect = False
        self.__check_properties = False
        self.__check_style = False

        if isinstance(file, dict):
            file = [v for k, v in file.items()]

        if isinstance(file, str):
            self.__surface_normal = self.__load_image(file, self.__rect_normal)
            if self.__surface_normal:
                self.__surface_hot = self.__surface_normal
                self.__surface_pressed = self.__surface_normal
                self.__surface_focused = self.__surface_normal
                self.__surface_disabled = self.__surface_normal

                for i in range(5):
                    self.__surface_files.append(file)

            self.__rect_normal = pygame.Rect(x, y, self.__rect_normal.width, self.__rect_normal.height)
            self.__rect_hot = pygame.Rect(x, y, self.__rect_normal.width, self.__rect_normal.height)
            self.__rect_pressed = pygame.Rect(x, y, self.__rect_normal.width, self.__rect_normal.height)
            self.__rect_focused = pygame.Rect(x, y, self.__rect_normal.width, self.__rect_normal.height)
            self.__rect_disabled = pygame.Rect(x, y, self.__rect_normal.width, self.__rect_normal.height)
        elif isinstance(file, list):
            surfaces = [None, None, None, None, None]

            for i in range(5 - len(file)):
                file.append(None)

            for i in range(min(len(surfaces), len(file))):
                if isinstance(file[i], str) and os.path.isfile(file[i]):
                    surfaces[i] = pygame.image.load(file[i])

                    if not surfaces[i] and surfaces[0]:
                        surfaces[i] = surfaces[0]
                elif surfaces[0]:
                    surfaces[i] = surfaces[0]

            if surfaces[0]:
                get_width = not width
                get_height = not height
                if get_width or get_height:
                    for surface in surfaces:
                        if surface:
                            if get_width:
                                width = max(width, surface.get_width())
                            if get_height:
                                height = max(height, surface.get_height())

                self.__rect_normal = pygame.Rect(x, y, width, height)
                self.__rect_hot = pygame.Rect(x, y, width, height)
                self.__rect_pressed = pygame.Rect(x, y, width, height)
                self.__rect_focused = pygame.Rect(x, y, width, height)
                self.__rect_disabled = pygame.Rect(x, y, width, height)
                self.__surface_normal = self.__proper_surface(surfaces[0], self.__rect_normal)
                self.__surface_hot = self.__proper_surface(surfaces[1], self.__rect_hot)
                self.__surface_pressed = self.__proper_surface(surfaces[2], self.__rect_pressed)
                self.__surface_focused = self.__proper_surface(surfaces[3], self.__rect_focused)
                self.__surface_disabled = self.__proper_surface(surfaces[4], self.__rect_disabled)
            elif not (width or height):
                print('cannot supply an empty array of images with no default width, height')
                raise ValueError

    def draw(self):
        if self.__state == STATE_HIDDEN:
            return

        if self.__check_properties or self.__check_rect or self.__check_style:
            if self.__properties != self.__properties_copy \
                    or self.__rect != self.__rect_copy \
                    or self.__style != self.__style_copy \
                    or self.__state != self.__state_copy:
                self.__surface_to_draw = self.__rect = self.__rect_copy = None
            self.__state_copy = self.__state
            self.__check_properties = self.__check_rect = self.__check_style = False

        if self.__surface_to_draw:
            self.__surface.blit(self.__surface_to_draw, self.__rect)
            return

        if self.__state == STATE_NORMAL:
            if self.__surface_normal:
                self.__rect = self.__rect_normal
                surface = self.__surface_normal
                bk_color = self.__properties.bk_color_normal
                border_color = self.__properties.border_color_normal
        elif self.__state == STATE_HOT:
            if self.__surface_hot:
                self.__rect = self.__rect_hot
                surface = self.__surface_hot
                bk_color = self.__properties.bk_color_hot
                border_color = self.__properties.border_color_hot
        elif self.__state == STATE_PRESSED:
            if self.__surface_pressed:
                self.__rect = self.__rect_pressed
                surface = self.__surface_pressed
                bk_color = self.__properties.bk_color_pressed
                border_color = self.__properties.border_color_pressed
        elif self.__state == STATE_FOCUSED:
            if self.__surface_focused:
                self.__rect = self.__rect_focused
                surface = self.__surface_focused
                bk_color = self.__properties.bk_color_focused
                border_color = self.__properties.border_color_focused
        elif self.__state == STATE_DISABLED:
            if self.__surface_disabled:
                self.__rect = self.__rect_disabled
                surface = self.__surface_disabled
                bk_color = self.__properties.bk_color_disabled
                border_color = self.__properties.border_color_disabled
        else:
            print('invalid state for Picture')
            raise ValueError

        self.__surface_to_draw = pygame.Surface((self.__rect.width, self.__rect.height), pygame.SRCALPHA)

        if bk_color[3]:
            bg = pygame.Surface((self.__rect.width, self.__rect.height), pygame.SRCALPHA)
            bg.fill(bk_color)
            bg.set_alpha(bk_color[3], pygame.RLEACCEL)
            self.__surface_to_draw.blit(bg, (0, 0))
            del bg

        self.__surface_to_draw.blit(surface,
                                    pygame.Rect(self.__rect.x - self.__x, self.__rect.y - self.__y, self.__rect.width,
                                                self.__rect.height))

        self.__rect_copy = self.__rect

        self.__pygamecontrol.draw_style(self.__surface_to_draw, self.__properties, self.__style,
                                        bk_color, border_color, self.__rect)
        self.__surface.blit(self.__surface_to_draw, self.__rect)

    def __load_image(self, file, rect):
        if isinstance(file, str):
            if os.path.isfile(file):
                surface = pygame.image.load(file)
            else:
                print('error loading image:', file, '\nfile does not exist')
                return None
        elif isinstance(file, pygame.Surface):
            surface = file
        else:
            return None

        if not rect.width:
            rect.width = surface.get_width()
        if not rect.height:
            rect.height = surface.get_height()

        return self.__proper_surface(surface, rect)

    def __proper_surface(self, surface, rect):
        if IMS_REALSIZECONTROL in self.__style:
            if rect.width and rect.height:
                surface = pygame.transform.scale(surface, (rect.width, rect.height))
            else:
                return surface
        elif IMS_REALSIZEIMAGE in self.__style:
            rect.width = surface.get_width()
            rect.height = surface.get_height()

        if IMS_RIGHTJUST in self.__style:
            rect.x = rect.width - surface.get_width()
            rect.y = rect.height - surface.get_height()
        else:
            if IMS_HCENTERIMAGE in self.__style:
                rect.x = int((rect.width / 2) - (surface.get_width() / 2))
            if IMS_VCENTERIMAGE in self.__style:
                rect.y = int((rect.height / 2) - (surface.get_height() / 2))

        return surface

    def move_surface(self, x=None, y=None, width=None, height=None):
        if isinstance(x, str) or isinstance(x, float):
            x = int(x)
        if isinstance(y, str) or isinstance(y, float):
            y = int(y)
        if isinstance(width, str) or isinstance(width, float):
            width = int(width)
        if isinstance(height, str) or isinstance(height, float):
            height = int(height)
        if x is not None:
            self.__rect_normal.x = x
            self.__rect_hot.x = x
            self.__rect_pressed.x = x
            self.__rect_focused.x = x
            self.__rect_disabled.x = x
        if y is not None:
            self.__rect_normal.y = y
            self.__rect_hot.y = y
            self.__rect_pressed.y = y
            self.__rect_focused.y = y
            self.__rect_disabled.y = y
        if width is not None:
            self.__rect_normal.width = width
            self.__rect_hot.width = width
            self.__rect_pressed.width = width
            self.__rect_focused.width = width
            self.__rect_disabled.width = width
        if height is not None:
            self.__rect_normal.height = height
            self.__rect_hot.height = height
            self.__rect_pressed.height = height
            self.__rect_focused.height = height
            self.__rect_disabled.height = height
        if not (x is None or y is None or width is None or height is None):
            self.__surface_normal = self.__proper_surface(self.__surface_normal, self.__rect_normal)
            self.__surface_hot = self.__proper_surface(self.__surface_hot, self.__rect_hot)
            self.__surface_pressed = self.__proper_surface(self.__surface_pressed, self.__rect_pressed)
            self.__surface_focused = self.__proper_surface(self.__surface_focused, self.__rect_focused)
            self.__surface_disabled = self.__proper_surface(self.__surface_disabled, self.__rect_disabled)

    @property
    def surface_normal(self):
        return self.__surface_normal

    @property
    def surface_hot(self):
        return self.__surface_hot

    @property
    def surface_pressed(self):
        return self.__surface_pressed

    @property
    def surface_focused(self):
        return self.__surface_focused

    @property
    def surface_disabled(self):
        return self.__surface_disabled

    @property
    def file_normal(self):
        return self.__surface_files[0]

    @property
    def file_hot(self):
        return self.__surface_files[1]

    @property
    def file_pressed(self):
        return self.__surface_files[2]

    @property
    def file_focused(self):
        return self.__surface_files[3]

    @property
    def file_disabled(self):
        return self.__surface_files[4]

    @property
    def style(self):
        self.__check_style = True
        return self.__style

    @property
    def properties(self):
        self.__check_properties = True
        return self.__properties

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        if self.__state != state:
            self.__state = state

    @surface_normal.setter
    def surface_normal(self, file):
        self.__surface_normal = self.__load_image(file, self.__rect_normal)
        if self.__state_copy == STATE_NORMAL:
            self.__surface_to_draw = None

    @surface_hot.setter
    def surface_hot(self, file):
        self.__surface_hot = self.__load_image(file, self.__rect_hot)
        if self.__state_copy == STATE_HOT:
            self.__surface_to_draw = None

    @surface_pressed.setter
    def surface_pressed(self, file):
        self.__surface_pressed = self.__load_image(file, self.__rect_pressed)
        if self.__state_copy == STATE_PRESSED:
            self.__surface_to_draw = None

    @surface_focused.setter
    def surface_focused(self, file):
        self.__surface_focused = self.__load_image(file, self.__rect_focused)
        if self.__state_copy == STATE_FOCUSED:
            self.__surface_to_draw = None

    @surface_disabled.setter
    def surface_disabled(self, file):
        self.__surface_disabled = self.__load_image(file, self.__rect_disabled)
        if self.__state_copy == STATE_DISABLED:
            self.__surface_to_draw = None


class Label:
    def __init__(self, pygamecontrol, surface, text, x, y, width=None, height=None, style=None, properties=None,
                 font=None):
        if not isinstance(surface, pygame.Surface):
            print('second argument, surface, not a valid pygame.Surface')
            raise ValueError
        if not isinstance(pygamecontrol, PyGameControls):
            print('first argument, pygamecontrol, not a valid PyGameControls')
            raise ValueError

        if isinstance(x, str) or isinstance(x, float):
            x = int(x)
        if isinstance(y, str) or isinstance(y, float):
            y = int(y)
        if isinstance(width, str) or isinstance(width, float):
            width = int(width)
        if isinstance(height, str) or isinstance(height, float):
            height = int(height)

        if not width:
            for line in text.splitlines():
                width = max(width, self.__font.pygame_font.size(line)[0]) + 2
        if not height:
            height = self.__font.pygame_font.get_height() + 2

        self.__pygamecontrol = pygamecontrol
        self.__surface = surface
        self.__text = self.__proper_text(text)
        self.__forced_styles = None
        self.__style = self.__pygamecontrol._check_style(style, [TS_LEFT, TS_TOP], self.__forced_styles)
        self.__y_offset = 0
        self.__properties = properties \
            if isinstance(properties, ControlProperties) else \
            ControlProperties('label', 'flat',
                              text_color_normal=(0, 0, 0, 255),
                              text_color_disabled=(150, 150, 150, 255))

        self.__x_offset = 1
        self.__y_offset = 0

        if isinstance(font, Font):
            self.__font = font
        elif isinstance(font, str):
            self.__font = self.__pygamecontrol.create_font(font, 11, 'regular')
        else:
            self.__font = self.__pygamecontrol.create_font(self.__pygamecontrol._default_font, 11, 'regular')

        self.__rect = pygame.Rect(x, y, width, height)
        self.__surface_to_draw = None
        self.__client_rect = self.client_rect()
        self.__text_to_draw = self.__pygamecontrol._format_text(self.__text,
                                                                self.__font.pygame_font,
                                                                self.__client_rect,
                                                                self.__style).splitlines()
        self.__font_copy = copy.copy(self.__font)
        self.__rect_copy = copy.copy(self.__rect)
        self.__style_copy = copy.copy(self.__style)
        self.__properties_copy = copy.copy(self.__properties)
        self.__y_offset_copy = copy.copy(self.__y_offset)
        self.__check_font = False
        self.__check_rect = False
        self.__check_style = False
        self.__check_properties = False
        self.__state = STATE_NORMAL

    @property
    def surface(self):
        return self.__surface

    @property
    def text(self):
        return self.__text

    @property
    def text_to_draw(self):
        return self.__text_to_draw

    @property
    def style(self):
        self.__check_style = True
        return self.__style

    @property
    def font(self):
        self.__check_font = True
        return self.__font

    @property
    def properties(self):
        self.__check_properties = True
        return self.__properties

    @property
    def rect(self):
        self.__check_rect = True
        return self.__rect

    @property
    def state(self):
        return self.__state

    @text.setter
    def text(self, text):
        text = self.__proper_text(text)
        if not text:
            self.__text = ''
            self.__text_to_draw = []
        if isinstance(text, str) and self.__text != text:
            self.__text = text
            self.__text_to_draw = self.__pygamecontrol._format_text(text, self.__font.pygame_font, self.__client_rect,
                                                                    self.__style).splitlines()
        self.__surface_to_draw = None

    @surface.setter
    def surface(self, surface):
        if isinstance(surface, pygame.Surface):
            self.__surface = surface

    @style.setter
    def style(self, style):
        style = self.__pygamecontrol._check_style(style, self.__style, self.__forced_styles)
        if style != self.__style:
            self.__style = style
            self.__check_style = True

    @font.setter
    def font(self, font):
        if isinstance(font, Font) and self.__font != font:
            self.__font = font
            self.__check_font = True

    @properties.setter
    def properties(self, properties):
        if isinstance(property, ControlProperties) and self.__properties != properties:
            self.__properties = properties
            self.__check_properties = True

    @rect.setter
    def rect(self, rect):
        if isinstance(rect, pygame.Rect):
            if rect != self.__rect:
                self.__rect = rect
                self.__check_rect = True

    @state.setter
    def state(self, state):
        if isinstance(state, str) or isinstance(state, float):
            state = int(state)
        if isinstance(state, int) and (STATE_HIDDEN >= state >= STATE_NORMAL):
            if state != self.__state:
                self.__state = state
                self.__surface_to_draw = None

    def __proper_text(self, text):
        if isinstance(text, list) or isinstance(text, tuple):
            text = ''.join(str(s) + '\n' for s in text)
        elif isinstance(text, int) or isinstance(text, float):
            text = str(text)
        elif not isinstance(text, str):
            return ''
        return text

    def client_rect(self):
        if self.__properties.px_border:
            self.__y_offset = self.__properties.px_border + 1
            self.__x_offset = self.__properties.px_border + 1

        if SS_SUNKEN in self.__style:
            self.__y_offset = max(self.__y_offset, 3)
            self.__x_offset = max(self.__x_offset, 3)
        elif SS_ETCHEDFRAME in self.__style or SS_ETCHEDHORZ in self.__style:
            self.__y_offset = max(self.__y_offset, 3)
        elif SS_ETCHEDVERT in self.__style:
            self.__x_offset = max(self.__x_offset, 3)

        return pygame.Rect(self.__rect.x + self.__x_offset, self.__rect.y + self.__y_offset,
                           self.__rect.width - (self.__x_offset * 2), self.__rect.height - (self.__y_offset * 2))

    def draw(self):
        if self.__state == STATE_HIDDEN:
            return

        if self.__check_font or self.__check_properties or self.__check_rect or self.__check_style or self.__y_offset != self.__y_offset_copy:
            if self.__font != self.__font_copy \
                    or self.__properties != self.__properties_copy \
                    or self.__rect != self.__rect_copy \
                    or self.__style != self.__style_copy \
                    or self.__y_offset != self.__y_offset_copy:
                if self.__font != self.__font_copy or self.__rect != self.__rect_copy or self.__style != self.__style_copy:
                    self.__text_to_draw = self.__pygamecontrol._format_text(self.__text,
                                                                            self.__font.pygame_font,
                                                                            self.__client_rect,
                                                                            self.__style).splitlines()

                    if self.__font != self.__font_copy:
                        self.__font_copy = self.__font
                    if self.__rect != self.__rect_copy:
                        self.__rect_copy = self.__rect
                    if self.__style != self.__style_copy:
                        self.__style_copy = self.__style

                if self.__properties != self.__properties_copy:
                    self.__properties_copy = self.__properties
                if self.__y_offset != self.__y_offset_copy:
                    self.__y_offset_copy = self.__y_offset

                self.__surface_to_draw = None
                self.__client_rect = self.client_rect()
            self.__check_font = self.__check_properties = \
                self.__check_rect = self.__check_style = \
                self.__y_offset = self.__y_offset_copy = False

        if not self.__surface_to_draw:
            # If something has changed it will set the last_text_surface to none
            # Only redraw the surface if something has changed
            self.__surface_to_draw = pygame.Surface((self.__rect.width, self.__rect.height), pygame.SRCALPHA)

            if self.__state == STATE_NORMAL:
                text_color = self.__properties.text_color_normal
                bk_color = self.__properties.bk_color_normal
                border_color = self.__properties_copy.border_color_normal
            elif self.__state == STATE_HOT:
                text_color = self.__properties.text_color_hot
                bk_color = self.__properties.bk_color_hot
                border_color = self.__properties_copy.border_color_hot
            elif self.__state == STATE_PRESSED:
                text_color = self.__properties.text_color_pressed
                bk_color = self.__properties.bk_color_pressed
                border_color = self.__properties_copy.border_color_pressed
            elif self.__state == STATE_FOCUSED:
                text_color = self.__properties.text_color_focused
                bk_color = self.__properties.bk_color_focused
                border_color = self.__properties_copy.border_color_focused
            elif self.__state == STATE_DISABLED:
                text_color = self.__properties.text_color_disabled
                bk_color = self.__properties.bk_color_disabled
                border_color = self.__properties_copy.border_color_disabled
            else:
                print('invalid state')
                raise ValueError

            if bk_color[3]:
                bg = pygame.Surface((self.__rect.width, self.__rect.height), pygame.SRCALPHA)
                bg.fill(bk_color)
                bg.set_alpha(bk_color[3], pygame.RLEACCEL)
                self.__surface_to_draw.blit(bg, (0, 0))
                del bg

            if text_color[3]:
                text = self.__text_to_draw
                lines_can_draw = len(text)
                line_count = lines_can_draw
                font_height = self.__font.pygame_font.get_height()

                # get the number of lines that will fit in the area
                # line_count is the number of lines
                while (lines_can_draw * font_height > self.__rect.height) and lines_can_draw:
                    lines_can_draw -= 1

                # Get vertical alignment
                if TS_VCENTER in self.__style:
                    if TS_MULTILINE in self.__style:
                        # calculate the starting position of y
                        # will center the number of lines it can draw
                        # can draw less lines than the total number of lines
                        if lines_can_draw < line_count:
                            mid = int(line_count / 2)
                            start = mid - int(lines_can_draw / 2)
                            y_position = int(start * font_height) - 1

                        else:
                            y_position = int((self.__rect.height / 2) - ((lines_can_draw * font_height) / 2)) - 1
                    # only get the first line of text to draw
                    else:
                        text = text[:1]
                        y_position = int((self.__rect.height / 2) - (font_height / 2))
                # text will be aligned on the bottom
                elif TS_BOTTOM in self.__style:
                    if TS_MULTILINE in self.__style:
                        # calculate the starting position of y
                        # will center the number of lines it can draw
                        # if lines_can_draw < line_count:
                        start = line_count - lines_can_draw
                        y_position = int(start * font_height)
                        # else:
                        #     y_position = int(self.__rect.y + int(self.__rect.height / 2) - int(int(lines_can_draw * font_height) / 2)) - 1
                    # only get the first line of text to draw
                    else:
                        start = line_count - lines_can_draw
                        y_position = int(start * font_height)
                        text = text[:1]
                else:
                    y_position = 0

                y_position += self.__y_offset

                for line in text:
                    amps = []
                    if TS_BOTTOM in self.__style:
                        # check that the y_position value is not above the top of the self.__rect
                        if y_position + font_height < self.__rect.top:
                            y_position += font_height
                            continue
                    # if the y_position value + the current height needed to draw this line goes below the bottom
                    elif y_position + font_height > self.__rect.bottom:
                        break

                    if TS_NOPREFIX not in self.__style:
                        while line.find('&') != -1:
                            index = line.find('&')
                            amps.append(index)
                            line = line[:index] + line[index + 1:]

                    # get the width of this line
                    size = self.__font.pygame_font.size(line)

                    string_surface = self.__font.pygame_font.render(line, True, text_color)

                    for amp in amps:
                        line_size = int(self.__font.font_size * 0.10)
                        chr_width = self.__font.pygame_font.size(line[amp:amp + 1])[0]
                        x_start = self.__font.pygame_font.size(line[:amp])[0]
                        y_start = string_surface.get_height() - line_size
                        pygame.draw.line(string_surface, text_color, (x_start, y_start),
                                         (x_start + chr_width, y_start),
                                         line_size)

                    alpha_img = pygame.Surface(size, pygame.SRCALPHA)
                    alpha_img.fill((255, 255, 255, text_color[3]))
                    string_surface.blit(alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    del alpha_img

                    if TS_HCENTER in self.__style and TS_LEFTNOWORDWRAP not in self.__style:
                        row_x = int((self.__client_rect.width / 2) - (size[0] / 2))
                    # draw on the right side
                    elif TS_RIGHT in self.__style and TS_LEFTNOWORDWRAP not in self.__style:
                        row_x = self.__client_rect.width - size[0]
                    # draw on the left side
                    else:
                        row_x = 0
                    row_x += self.__x_offset

                    self.__surface_to_draw.blit(string_surface, (row_x, y_position))
                    self.__pygamecontrol.draw_style(self.__surface_to_draw, self.__properties, self.__style,
                                                    bk_color, border_color, self.__rect)

                    # adjust the y_position position
                    y_position += font_height

        self.__surface.blit(self.__surface_to_draw, self.__rect)
        return True


class Font:
    def __init__(self, pygamecontrol, family_name=None, font_size=None, attribute=None):
        if not isinstance(pygamecontrol, PyGameControls):
            print('error with first parameter, pygamecontrol, is not a PyGameControls')
            raise ValueError

        self.__font_file = None
        self.__family_name = None
        self.__family_key = None
        self.__font_size = None
        self.__attribute = None
        self.__pygame_font = None
        self.__pygamecontrol = pygamecontrol

        if not family_name:
            family_name = pygamecontrol._default_font
        if isinstance(font_size, str):
            font_size = int(font_size)
        if not font_size or font_size <= 0:
            font_size = 11
        self.__make_font(family_name, font_size, attribute)

    def __make_font(self, family_name, font_size, attribute):
        # attribute has to be a list since strings aren't mutable
        # can't modify them in this function
        if isinstance(attribute, str):
            attribute = [attribute.lower()]
        elif isinstance(attribute, tuple):
            if len(attribute):
                if isinstance(attribute[0], str):
                    attribute = [attribute.lower()]
        elif not isinstance(attribute, list):
            attribute = ['regular']

        # It's all the same
        if family_name == self.__family_name and font_size == self.__font_size and attribute[0] == self.__attribute[0]:
            return

        # family or attribute changed
        # this affects the font file
        if self.__family_name != family_name or attribute[0] != self.__attribute[0]:
            if self.__family_name != family_name:
                self.__family_key = family_name.lower()

            find_file = self.__pygamecontrol.find_font(self.__family_key, attribute)

            if find_file != self.__font_file:
                self.__font_file = find_file
                self.__family_name = self.__pygamecontrol._fonts[self.__family_key]['family']
                self.__attribute = attribute
            else:
                self.__family_key = self.__family_name.lower()
        # size changed, doesn't affect the font file but need to update it
        if self.__font_size != font_size:
            self.__font_size = font_size

        self.__pygame_font = pygame.font.Font(self.__font_file, self.__font_size)

    @property
    def font_file(self):
        return self.__font_file

    @property
    def family_name(self):
        return self.__family_name

    @property
    def font_size(self):
        return self.__font_size

    @property
    def attribute(self):
        return self.__attribute[0]

    @property
    def pygame_font(self):
        return self.__pygame_font

    @family_name.setter
    def family_name(self, family_name):
        self.__make_font(family_name, self.__font_size, self.__attribute)

    @font_size.setter
    def font_size(self, font_size):
        self.__make_font(self.__family_name, font_size, self.__attribute)

    @attribute.setter
    def attribute(self, attribute):

        self.__make_font(self.__family_name, self.__font_size, attribute)

    def set_font(self, family_name, font_size, attribute):
        self.__make_font(family_name, font_size, attribute)


class ControlProperties:
    def __init__(self, control_type, style='flat',
                 bk_color_normal=None, text_color_normal=None,
                 bk_color_hot=None, text_color_hot=None,
                 bk_color_pressed=None, text_color_pressed=None,
                 bk_color_focused=None, text_color_focused=None,
                 bk_color_disabled=None, text_color_disabled=None,
                 px_border=0,
                 border_color_normal=None,
                 border_color_hot=None,
                 border_color_pressed=None,
                 border_color_focused=None,
                 border_color_disabled=None):
        if control_type not in SUPPORTED_CONTROLS:
            print('first argument for ControlProperties, control_type, not a supported control,', control_type)
            raise ValueError

        self.__control_type = control_type

        if not style:
            style = 'flat'
        elif style not in SUPPORTED_CONTROL_STYLES:
            print('second argument for ControlProperties, style, not a supported style,', style)
            raise ValueError

        self.__style = style
        self.__bk_color_normal = self.__proper_rgba(bk_color_normal, (0, 0, 0, 0))
        self.__text_color_normal = self.__proper_rgba(text_color_normal, (0, 0, 0, 255))
        self.__bk_color_hot = self.__proper_rgba(bk_color_hot, self.__bk_color_normal)
        self.__text_color_hot = self.__proper_rgba(text_color_hot, self.__text_color_normal)
        self.__bk_color_pressed = self.__proper_rgba(bk_color_pressed, self.__bk_color_normal)
        self.__text_color_pressed = self.__proper_rgba(text_color_pressed, self.__text_color_normal)
        self.__bk_color_focused = self.__proper_rgba(bk_color_focused, self.__bk_color_normal)
        self.__text_color_focused = self.__proper_rgba(text_color_focused, self.__text_color_normal)
        self.__bk_color_disabled = self.__proper_rgba(bk_color_disabled, self.__bk_color_normal)
        self.__text_color_disabled = self.__proper_rgba(text_color_disabled, self.__text_color_normal)
        self.__border_color_normal = self.__proper_rgba(border_color_normal, (0, 0, 0, 0))
        self.__border_color_hot = self.__proper_rgba(border_color_hot, self.__border_color_normal)
        self.__border_color_pressed = self.__proper_rgba(border_color_pressed, self.__border_color_normal)
        self.__border_color_focused = self.__proper_rgba(border_color_focused, self.__border_color_normal)
        self.__border_color_disabled = self.__proper_rgba(border_color_disabled, self.__border_color_normal)
        self.__px_border = px_border if px_border >= 1 else 0

    def __proper_rgba(self, color, default):
        if not isinstance(color, tuple):
            return default

        count = len(color)

        if count < 4:
            lst = list(color)
            for i in range(4 - count):
                lst.append(default[count - i])
            color = tuple(lst)
        else:
            color = tuple(list(color)[:4])

        for i in range(4):
            if color[i] < 0 or color[i] > 255:
                color[i] = default[i]
        return color

    @property
    def control_type(self):
        return self.__control_type

    @property
    def style(self):
        return self.__style

    @property
    def bk_color_normal(self):
        return self.__bk_color_normal

    @property
    def text_color_normal(self):
        return self.__text_color_normal

    @property
    def bk_color_hot(self):
        return self.__bk_color_hot

    @property
    def text_color_hot(self):
        return self.__text_color_hot

    @property
    def bk_color_pressed(self):
        return self.__bk_color_pressed

    @property
    def text_color_pressed(self):
        return self.__text_color_pressed

    @property
    def bk_color_focused(self):
        return self.__bk_color_focused

    @property
    def text_color_focused(self):
        return self.__text_color_focused

    @property
    def bk_color_disabled(self):
        return self.__bk_color_disabled

    @property
    def text_color_disabled(self):
        return self.__text_color_disabled

    @property
    def px_border(self):
        return self.__px_border

    @property
    def border_color_normal(self):
        return self.__border_color_normal

    @property
    def border_color_hot(self):
        return self.__border_color_hot

    @property
    def border_color_pressed(self):
        return self.__border_color_pressed

    @property
    def border_color_focused(self):
        return self.__border_color_focused

    @property
    def border_color_disabled(self):
        return self.__border_color_disabled

    @style.setter
    def style(self, style):
        if style in SUPPORTED_CONTROL_STYLES:
            self.__style = style

    @bk_color_normal.setter
    def bk_color_normal(self, bk_color_normal):
        self.__bk_color_normal = self.__proper_rgba(bk_color_normal, self.__bk_color_normal)

    @text_color_normal.setter
    def text_color_normal(self, text_color_normal):
        self.__text_color_normal = self.__proper_rgba(text_color_normal, self.__text_color_normal)

    @bk_color_hot.setter
    def bk_color_hot(self, bk_color_hot):
        self.__bk_color_hot = self.__proper_rgba(bk_color_hot, self.__bk_color_hot)

    @text_color_hot.setter
    def text_color_hot(self, text_color_hot):
        self.__text_color_hot = self.__proper_rgba(text_color_hot, self.__text_color_hot)

    @bk_color_pressed.setter
    def bk_color_pressed(self, bk_color_pressed):
        self.__bk_color_pressed = self.__proper_rgba(bk_color_pressed, self.__bk_color_pressed)

    @text_color_pressed.setter
    def text_color_pressed(self, text_color_pressed):
        self.__text_color_pressed = self.__proper_rgba(text_color_pressed, self.__text_color_pressed)

    @bk_color_focused.setter
    def bk_color_focused(self, bk_color_focused):
        self.__bk_color_focused = self.__proper_rgba(bk_color_focused, self.__bk_color_focused)

    @text_color_focused.setter
    def text_color_focused(self, text_color_focused):
        self.__text_color_focused = self.__proper_rgba(text_color_focused, self.__text_color_focused)

    @bk_color_disabled.setter
    def bk_color_disabled(self, bk_color_disabled):
        self.__bk_color_disabled = self.__proper_rgba(bk_color_disabled, self.__bk_color_disabled)

    @text_color_disabled.setter
    def text_color_disabled(self, text_color_disabled):
        self.__text_color_disabled = self.__proper_rgba(text_color_disabled, self.__text_color_disabled)

    @px_border.setter
    def px_border(self, px_border):
        self.__px_border = px_border

    @border_color_normal.setter
    def border_color_normal(self, border_color_normal):
        self.__border_color_normal = self.__proper_rgba(border_color_normal, self.__border_color_normal)

    @border_color_hot.setter
    def border_color_hot(self, border_color_hot):
        self.__border_color_hot = self.__proper_rgba(border_color_hot, self.__border_color_hot)

    @border_color_pressed.setter
    def border_color_pressed(self, border_color_pressed):
        self.__border_color_pressed = self.__proper_rgba(border_color_pressed, self.__border_color_pressed)

    @border_color_focused.setter
    def border_color_focused(self, border_color_focused):
        self.__border_color_focused = self.__proper_rgba(border_color_focused, self.__border_color_focused)

    @border_color_disabled.setter
    def border_color_disabled(self, border_color_disabled):
        self.__border_color_disabled = self.__proper_rgba(border_color_disabled, self.__border_color_disabled)