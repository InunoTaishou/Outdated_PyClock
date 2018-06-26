import pygame
import time
from PIL import Image, ImageDraw, ImageFont

ALIGNMENT_NEAR = 0
ALIGNMENT_FAR = 2
ALIGNMENT_CENTER = 1

ALIGNMENT_LEFT = ALIGNMENT_NEAR
ALIGNMENT_TOP = ALIGNMENT_NEAR
ALIGNMENT_RIGHT = ALIGNMENT_FAR
ALIGNMENT_BOTTOM = ALIGNMENT_FAR

controls = []

SS_LEFT = 0x0000
SS_RIGHT = 0x0002
BS_BOTTOM = 0x0800
BS_CENTER = 0x0300
BS_DEFPUSHBUTTON = 0x0001
BS_MULTILINE = 0x2000
BS_TOP = 0x0400
BS_VCENTER = 0x0C00
BS_ICON = 0x0040
BS_BITMAP = 0x0080
BS_FLAT = 0x8000
BS_NOTIFY = 0x4000

DEFAULT_BUTTON_PROPERTIES = {'bk_color_normal': (51, 51, 51, 255), 'border_color_normal': (51, 51, 51, 255), 'text_color_normal': (241, 241, 241, 255),
                             'bk_color_hot': (16, 16, 16, 255), 'border_color_hot': (16, 16, 16), 'text_color_hot': (241, 241, 241, 255),
                             'bk_color_pressed': (0, 122, 204, 255), 'border_color_pressed': (0, 122, 204, 255), 'text_color_pressed': (241, 241, 241, 255),
                             'bk_color_disabled': (82, 82, 82, 255), 'border_color_disabled': (118, 118, 118, 255), 'text_color_disabled': (124, 124, 124, 255),
                             'px_border': 3}
DEFAULT_FONT_PROPERTIES = {'family': 'Segoe UI',
                           'size': 12,
                           'path': 'C:\\WINDOWS\\Fonts\\segoeui.ttf',
                           'bold': False,
                           'semi_bold': False,
                           'italic': False,
                           'light': False,
                           'semi_light': False,
                           'black': False}


def valid_control(control_id):
    if 1 >= control_id <= len(controls) and controls[control_id]['state'] != 'deleted':
        return True
    return False


def control_delete(control_id):
    if valid_control(control_id):
        controls[control_id]['draw'] = False
        controls[control_id]['state'] = 'deleted'
        return True


def control_set_text(control_id, text):
    if valid_control(control_id):
        return True


def control_set_event(control_id, func):
    if valid_control(control_id):
        controls[control_id]['on_event'] = func
        return True
    return False


def control_set_dbl_click(control_id, func):
    if valid_control(control_id):
        controls[control_id]['on_dbl_click'] = func


def mouse_events(mouse_pos, event_type):
    for button in controls:
        state = button['state']

        if button['rect'].collidepoint(mouse_pos):
            if event_type == pygame.MOUSEBUTTONUP and state != 'disabled' and state == 'pressed':
                button['state'] = 'hot'

                # time from the last time double click was trigger is > 1 second
                if int(time.clock() - button['dbl_timer']):
                    # initialize a timer for checking double clicks
                    button['timer'] = time.clock()
                elif button['timer']:
                    button['timer'] = 0

                if button['on_event']:
                    button['on_event']()

            elif event_type == pygame.MOUSEBUTTONDOWN and state != 'disabled':
                if button['timer'] and time.clock() - button['timer'] <= 0.6:
                    print('Double click')
                    button['dbl_timer'] = time.clock()

                button['state'] = 'pressed'
            elif state != 'pressed' and state != 'disabled':
                button['state'] = 'hot'
        else:
            if state != 'normal' or state != 'disabled':
                button['state'] = 'normal'
    return True


def draw_buttons(surface):
    for button in controls:
        surface.blit(button[button['state']], button['rect'])


def _create_button(text, width, height, button_properties, style):

    return True


def create_button(text, x, y, width, height,
                  button_properties=DEFAULT_BUTTON_PROPERTIES,
                  style=BS_CENTER | BS_VCENTER | BS_MULTILINE,
                  font_properties=DEFAULT_FONT_PROPERTIES):
    rect = pygame.Rect(button_properties['px_border'], button_properties['px_border'], width - (button_properties['px_border'] * 2), height - (button_properties['px_border'] * 2))
    tmp_font = ImageFont.truetype(font_properties['path'], font_properties['size'])
    lines_of_string = format_string(text, tmp_font, rect).splitlines()

    bk_normal = Image.new('RGBA', size=(width, height), color=button_properties['border_color_normal'])
    bk_hot = Image.new('RGBA', size=(width, height), color=button_properties['border_color_hot'])
    bk_pressed = Image.new('RGBA', size=(width, height), color=button_properties['border_color_pressed'])
    bk_disabled = Image.new('RGBA', size=(width, height), color=button_properties['border_color_disabled'])

    image_normal = ImageDraw.Draw(bk_normal)
    image_hot = ImageDraw.Draw(bk_hot)
    image_pressed = ImageDraw.Draw(bk_pressed)
    image_disabled = ImageDraw.Draw(bk_disabled)

    image_normal.rectangle([(button_properties['px_border'], button_properties['px_border']),
                            (width - button_properties['px_border'] - 1, height - button_properties['px_border'] - 1)],
                           button_properties['bk_color_normal'])
    image_hot.rectangle([(button_properties['px_border'], button_properties['px_border']),
                         (width - button_properties['px_border'] - 1, height - button_properties['px_border'] - 1)],
                        button_properties['bk_color_hot'])
    image_pressed.rectangle([(button_properties['px_border'], button_properties['px_border']),
                             (width - button_properties['px_border'] - 1, height - button_properties['px_border'] - 1)],
                            button_properties['bk_color_pressed'])
    image_disabled.rectangle([(button_properties['px_border'], button_properties['px_border']),
                              (width - button_properties['px_border'] - 1, height - button_properties['px_border'] - 1)],
                             button_properties['bk_color_disabled'])

    if lines_of_string:
        i = 0
        text_y = 0
        font_height = tmp_font.getsize(text)[1] + 3

        # Get vertical alignment
        if style & BS_VCENTER == BS_VCENTER:
            if style & BS_MULTILINE == BS_MULTILINE:
                # get the number of lines that will fit in the area
                while i < len(lines_of_string):
                    if i * font_height < rect.height:
                        i += 1
                    else:
                        break
                # calculate the starting position of y
                # will center the number of lines it can draw
                text_y = int(rect.y + int(rect.height / 2) - ((i * font_height) / 2))
                # text_y is going to start above the actual start position of y, re-adjust
                if text_y < rect.y:
                    text_y = rect.y
            else:
                lines_of_string = lines_of_string[:1]
                text_y = rect[1] + (rect[3] / 2) - (font_height / 2)
        elif style & BS_BOTTOM == BS_BOTTOM:
            lines_of_string = reversed(lines_of_string)
            text_y = rect[3] - font_height
            font_height *= -1
        elif style & BS_TOP == BS_TOP:
            text_y = rect.y

        for line in lines_of_string:
            #
            if style & SS_RIGHT == SS_RIGHT:
                # check that the text_y value is not above the top of the rect
                if text_y < rect.top:
                    break
            # if the text_y value + the current height needed to draw this line goes below the bottom
            elif text_y + font_height > rect.bottom:
                break

            # get the width of this line
            line_width = tmp_font.getsize(line)[0]

            # draw in the center
            if style & BS_CENTER == BS_CENTER:
                row_x = rect.left + ((rect.width / 2) - (line_width / 2))
                row_y = text_y
            # draw on the right side
            elif style & SS_RIGHT == SS_RIGHT:
                row_x = rect.right - line_width
                row_y = text_y
            # draw on the left side
            else:
                row_x = rect.left
                row_y = text_y

            image_normal.text((row_x, row_y), line, font=tmp_font, fill=button_properties['text_color_normal'])
            image_hot.text((row_x, row_y), line, font=tmp_font, fill=button_properties['text_color_hot'])
            image_pressed.text((row_x, row_y), line, font=tmp_font, fill=button_properties['text_color_pressed'])
            image_disabled.text((row_x, row_y), line, font=tmp_font, fill=button_properties['text_color_disabled'])
            # adjust the text_y position
            text_y += font_height

    controls.append({'draw': True,
                     'state': 'normal',
                     'control_type': 'button',
                     'on_event': None,
                     'on_right_event': None,
                     'on_middle_event': None,
                     'on_dbl_click': None,
                     'on_dbl_right_click': None,
                     'on_dbl_middle_click': None,
                     'on_left_down': None,
                     'on_right_down': None,
                     'on_middle_down': None,
                     'on_scroll_up': None,
                     'on_scroll_down': None,
                     'timer': 0,
                     'timer_right': 0,
                     'timer_middle': 0,
                     'dbl_timer': time.clock(),
                     'dbl_right_timer': time.clock(),
                     'dbl_middle_timer': time.clock(),
                     'text': text,
                     'style': style,
                     'tooltip': None,
                     'timer_tooltip': 0,
                     'on_hover': 'tooltip',
                     'mouse_pos': None,
                     'button_properties': button_properties,
                     'font_properties': font_properties,
                     'rect': pygame.Rect(x, y, width, height),
                     'normal': pygame.image.fromstring(bk_normal.tobytes(), bk_normal.size, bk_normal.mode),
                     'hot': pygame.image.fromstring(bk_hot.tobytes(), bk_hot.size, bk_hot.mode),
                     'pressed': pygame.image.fromstring(bk_pressed.tobytes(), bk_pressed.size, bk_pressed.mode),
                     'disabled': pygame.image.fromstring(bk_disabled.tobytes(), bk_disabled.size, bk_disabled.mode)})
    return len(controls)


def button_update_button_properties(button_id, new_button_properties):
    return True


def button_update_font(button_id, new_font):
    return True


# string format class, used to set the alignment of the draw_string function
class StringFormat:
    def __init__(self, _align=ALIGNMENT_NEAR, _line_align=ALIGNMENT_NEAR):
        self._align = _align
        self._line_align = _line_align

    @property
    def align(self):
        return self._align

    @property
    def line_align(self):
        return self._line_align

    @align.setter
    def align(self, _align):
        self._align = _align

    @line_align.setter
    def line_align(self, _line_align):
        self._line_align = _line_align


def draw_string(surface, string, rect, font, font_format, color):
    if rect.width == -1 or rect.height == -1:
        display_info = pygame.display.Info()
        if rect.width == -1:
            rect.width = display_info.current_w - rect.x
        if rect.height == -1:
            rect.height = display_info.current_h - rect.y

    font_height = font.get_height()
    lines_of_string = format_string(string, font, rect).splitlines()
    i = 0
    y = 0

    if not lines_of_string:
        return False

    if font_format.line_align == ALIGNMENT_NEAR:
        y = rect.y
    elif font_format.line_align == ALIGNMENT_CENTER:
        # get the number of lines that will fit in the area
        while i < len(lines_of_string):
            if i * font_height < rect.height:
                i += 1
            else:
                break
        # calculate the starting position of y
        # will center the number of lines it can draw
        y = rect.y + (rect.height / 2) - ((i * font_height) / 2)
        # y is going to start above the actual start position of y, re-adjust
        if y < rect.y:
            y = rect.y
    elif font_format.line_align == ALIGNMENT_FAR:
        lines_of_string = reversed(lines_of_string)
        y = rect.bottom - font_height
        font_height *= -1

    for line in lines_of_string:
        # if the line alignment is far
        if font_format.line_align == ALIGNMENT_FAR:
            # check that the y value is not above the top of the rect
            if y < rect.top:
                break
        # if the y value + the current height needed to draw this line goes below the bottom
        elif y + font_height > rect.bottom:
            break

        # create a new surface with the drawn string of this line
        string_surface = font.render(line, True, color)

        # get the width of this line
        width = font.size(line)[0]

        # draw on the left side
        if font_format.align == ALIGNMENT_NEAR:
            surface.blit(string_surface, (rect.left, y))
        # draw in the center
        elif font_format.align == ALIGNMENT_CENTER:
            surface.blit(string_surface, (rect.left + ((rect.width / 2) - (width / 2)), y))
        # draw on the right side
        elif font_format.align == ALIGNMENT_FAR:
            surface.blit(string_surface, (rect.right - width, y))
        # adjust the y position
        y += font_height
    return True


# returns a list formatted to fit the rect provided
# font needed to measure each line
def format_string(string, font, rect):
    if not isinstance(string, str):
        string = str(string)

    if str(type(font)).find('pygame') > -1:
        size_func = font.size
    else:
        size_func = font.getsize

    lines_of_string = string.splitlines()

    # string that will hold the newly formatted string
    new_string = ''

    for line in lines_of_string:
        if line == '':
            new_string += "\n"
        else:
            while line:
                i = 0

                # start building this line
                while size_func(line[:i])[0] < rect.width and i < len(line):
                    i += 1

                # i is less than the length of this line
                if i < len(line):
                    # find the last word in this line up until the i position
                    i = line.rfind(' ', 0, i) + 1

                    # no words found, this string is way too long to be drawn in this area
                    if i == 0:
                        return ''
                    else:
                        # append the fitted line to new_string, trimming the trailing ' ' character and add the linefeed
                        new_string += line[:i - 1] + '\n'
                # this whole line fits
                else:
                    i = len(line)
                    new_string += line[:i] + '\n'

                # trim the string we took out of this line
                line = line[i:]
    # return the properly formatted string, complete with newlines
    return new_string
