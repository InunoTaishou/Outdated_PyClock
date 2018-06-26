IMS_ANIMATION = -1

# PyGameControl events
PGCE_MOUSEMOVE = 0x0200
PGCE_MOUSEENTER = 0x02A2
PGCE_MOUSELEAVE = 0x02A3
PGCE_MOUSEHOVER = 0x02A1
PGCE_LBUTTONDOWN = 0x0201
PGCE_LBUTTONUP = 0x0202
PGCE_LBUTTONDBLCLK = 0x0203
PGCE_RBUTTONDOWN = 0x0204
PGCE_RBUTTONUP = 0x0205
PGCE_RBUTTONDBLCLK = 0x0206
PGCE_MBUTTONDOWN = 0x0207
PGCE_MBUTTONUP = 0x0208
PGCE_MBUTTONDBLCLK = 0x0209
STATE_HIDDEN = 0
STATE_NORMAL = 1
STATE_HOT = 2
STATE_PRESSED = 3
STATE_FOCUSED = 4
STATE_DISABLED = 5

# PyGameControls Styles
# Control that can receive the keyboard focus when the user presses the TAB key. Pressing the TAB key changes the keyboard focus to the next control with the WS_TABSTOP style.
PGCS_TABSTOP = 1

# Static Control Styles
# Draws the top and bottom edges of the static control using the EDGE_ETCHED edge style. For more information, see the DrawEdge function.
SS_ETCHEDHORZ = 2
# Draws the left and right edges of the static control using the EDGE_ETCHED edge style. For more information, see the DrawEdge function.
SS_ETCHEDVERT = 3
# Draws the frame of the static control using the EDGE_ETCHED edge style. For more information, see the DrawEdge function.
SS_ETCHEDFRAME = 4
# Draws a half-sunken border around a static control.
SS_SUNKEN = 5

# Styles used with any control that has text
# Specifies a simple rectangle and left-aligns the text in the rectangle. The text is formatted before it is displayed. Words that extend past the end of a line are automatically wrapped to the beginning of the next left-aligned line. Words that are longer than the width of the control are truncated.
TS_LEFT = 0
# A simple rectangle and centers the text in the rectangle (horizontally). The text is formatted before it is displayed. Words that extend past the end of a line are automatically wrapped to the beginning of the next centered line. Words that are longer than the width of the control are truncated.
TS_HCENTER = 6
# A simple rectangle and right-aligns the text in the rectangle. The text is formatted before it is displayed. Words that extend past the end of a line are automatically wrapped to the beginning of the next right-aligned line. Words that are longer than the width of the control are truncated.
TS_RIGHT = 7
# Places text at the top of the rectangle.
TS_TOP = 0
# Places text in the middle (vertically) of the rectangle.
TS_VCENTER = 8
# Places text at the bottom of the rectangle.
TS_BOTTOM = 9
# Wraps the text to multiple lines if the text string is too long to fit on a single line in the rectangle.
TS_MULTILINE = 10
# A simple rectangle and left-aligns the text in the rectangle. Tabs are expanded, but words are not wrapped. Text that extends past the end of a line is clipped.
TS_LEFTNOWORDWRAP = 11
# Combined with the IMS_ICON, BS_CHECKBOX (BS_AUTOCHECKBOX), BS_RADIOBUTTON (BS_AUTORADIOBUTTON), BS_COMMANDLINK, and BS_SPLITBUTTON. Places text on the left side of the icon (radio, check, split, etc), and draws the icon on the right side of the rectangle
TS_LEFTTEXT = 12
TS_RIGHTICON = TS_LEFTTEXT
# Prevents interpretation of any ampersand (&) characters in the control's text as accelerator prefix characters. These are displayed with the ampersand removed and the next character in the string underlined. This static control style may be included with any of the defined static controls. You can combine SS_NOPREFIX with other styles. This can be useful when filenames or other strings that may contain an ampersand (&) must be displayed in a static control in a dialog box.
TS_NOPREFIX = 13
# The static control duplicates the text-displaying characteristics of a multiline edit control. Specifically, the average character width is calculated in the same manner as with an edit control, and the function does not display a partially visible last line.
TS_EDITCONTROL = 14
# If the end of a string does not fit in the rectangle, it is truncated and ellipses are added. If a word that is not at the end of the string goes beyond the limits of the rectangle, it is truncated without ellipses. Using this style will force the control’s text to be on one line with no word wrap. Compare with SS_PATHELLIPSIS and SS_WORDELLIPSIS.
TS_ENDELLIPSIS = 15
# Replaces characters in the middle of the string with ellipses so that the result fits in the specified rectangle. If the string contains backslash (\) characters, SS_PATHELLIPSIS preserves as much as possible of the text after the last backslash. Using this style will force the control’s text to be on one line with no word wrap. Compare with SS_ENDELLIPSIS and SS_WORDELLIPSIS.
TS_PATHELLIPSIS = 16
# Truncates any word that does not fit in the rectangle and adds ellipses. Using this style will force the control’s text to be on one line with no word wrap.
# Compare with SS_ENDELLIPSIS and SS_PATHELLIPSIS.
TS_WORDELLIPSIS = 17

# Styles used with any control that supports bitmaps/icons
# An icon to be displayed in the dialog box. If the control is created as part of a dialog box, the text is the name of an icon (not a filename) defined elsewhere in the resource file. If the control is created via CreateWindow or a related function, the text is the name of an icon (not a filename) defined in the resource file associated with the module specified by the hInstance parameter to CreateWindow.
# The icon can be an animated cursor.
# The style ignores the CreateWindow parameters nWidth and nHeight; the control automatically sizes itself to accommodate the icon. As it uses the LoadIcon function, the SS_ICON style can load only icons of dimensions SM_CXICON and SM_CYICON. This restriction can be bypassed by using the SS_REALSIZEIMAGE style in addition to SS_ICON.
# If an icon cannot be loaded through LoadIcon, an attempt is made to load the specified resource as a cursor using LoadCursor. If that too fails, an attempt is made to load from the device driver using LoadImage.
IMS_ICON = 18   # Not implemented
# A bitmap is to be displayed in the static control.
IMS_BITMAP = 19
# The lower right corner of a static control with the SS_BITMAP or SS_ICON style is to remain fixed when the control is resized. Only the top and left sides are adjusted to accommodate a new bitmap or icon.
IMS_RIGHTJUST = 20
# A bitmap is centered in the static control that contains it. The control is not resized, so that a bitmap too large for the control will be clipped. If the static control contains a single line of text, the text is centered vertically in the client area of the control.
IMS_HCENTERIMAGE = 21
IMS_VCENTERIMAGE = 38
# Specifies that the actual resource width is used and the icon is loaded using LoadImage. SS_REALSIZEIMAGE is always used in conjunction with SS_ICON.
# SS_REALSIZEIMAGE uses LoadImage, overriding the process normally followed under SS_ICON. It does not load cursors; if LoadImage fails, no further attempts to load are made. It uses the actual resource width. The static control is resized accordingly, but the icon remains aligned to the originally specified left and top edges of the control.
# Note that if SS_CENTERIMAGE is also specified, the icon is centered within the control's space, which was specified using the CreateWindow parameters nWidth and nHeight.
# Compare with SS_REALSIZECONTROL.
IMS_REALSIZEIMAGE = 22
# Adjusts the bitmap to fit the size of the static control. For example, changing the locale can change the system font, and thus controls might be resized. If a static control had a bitmap, the bitmap would no longer fit the control. This style bit dictates automatic redimensioning of bitmaps to fit their controls.
# If SS_CENTERIMAGE is specified, the bitmap or icon is centered (and clipped if needed). If SS_CENTERIMAGE is not specified, the bitmap or icon is stretched or shrunk.
# Note that the redimensioning in the two axes are independent, and the result may have a changed aspect ratio.
# Compare with SS_REALSIZEIMAGE.
IMS_REALSIZECONTROL = 23

# Styles specific to buttons
# Creates a push button that posts a WM_COMMAND message to the owner window when the user selects the button.
BS_PUSHBUTTON = 24
# Creates a push button that behaves like a BS_PUSHBUTTON style button, but has a distinct appearance. If the button is in a dialog box, the user can select the button by pressing the ENTER key, even when the button does not have the input focus. This style is useful for enabling the user to quickly select the most likely (default) option.
BS_DEFPUSHBUTTON = 25
# Creates a small, empty check box with text. By default, the text is displayed to the right of the check box. To display the text to the left of the check box, combine this flag with the BS_LEFTTEXT style (or with the equivalent BS_RIGHTBUTTON style).
BS_CHECKBOX = 26
# Creates a button that is the same as a check box, except that the check state automatically toggles between checked and cleared each time the user selects the check box.
BS_AUTOCHECKBOX = 27
# Creates a small circle with text. By default, the text is displayed to the right of the circle. To display the text to the left of the circle, combine this flag with the BS_LEFTTEXT style (or with the equivalent BS_RIGHTBUTTON style). Use radio buttons for groups of related, but mutually exclusive choices.
BS_RADIOBUTTON = 28
# Creates a button that is the same as a radio button, except that when the user selects it, the system automatically sets the button's check state to checked and automatically sets the check state for all other buttons in the same group to cleared.
BS_AUTORADIOBUTTON = 29
# Creates a rectangle in which other controls can be grouped. Any text associated with this style is displayed in the rectangle's upper left corner.
BS_GROUPBOX = 30
# Creates a button that is the same as a check box, except that the box can be grayed as well as checked or cleared. Use the grayed state to show that the state of the check box is not determined.
BS_3STATE = 31
# Creates a button that is the same as a three-state check box, except that the box changes its state when the user selects it. The state cycles through checked, indeterminate, and cleared.
BS_AUTO3STATE = 32
# Creates a command link button that behaves like a BS_PUSHBUTTON style button, but the command link button has a green arrow on the left pointing to the button text. A caption for the button text can be set by sending the BCM_SETNOTE message to the button.
BS_COMMANDLINK = 33
# Creates a command link button that behaves like a BS_PUSHBUTTON style button. If the button is in a dialog box, the user can select the command link button by pressing the ENTER key, even when the command link button does not have the input focus. This style is useful for enabling the user to quickly select the most likely (default) option.
BS_DEFCOMMANDLINK = 34
# Creates a split button. A split button has a drop down arrow.
BS_SPLITBUTTON = 35
# Creates a split button that behaves like a BS_PUSHBUTTON style button, but also has a distinctive appearance. If the split button is in a dialog box, the user can select the split button by pressing the ENTER key, even when the split button does not have the input focus. This style is useful for enabling the user to quickly select the most likely (default) option.
BS_DEFSPLITBUTTON = 36
# Makes a button (such as a check box, three-state check box, or radio button) look and act like a push button. The button looks raised when it isn't pushed or checked, and sunken when it is pushed or checked.
BS_PUSHLIKE = 37
