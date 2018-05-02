


debugs = [] # list of printed debug messages
infos = []  # list of printed info strings
warnings = []  # list of printed warning strings
errors = []  # list of printed error strings
fatals = [] # list of printd fatal messages

dt_level = 3  # 0 = no output, 1 = fatal, 2 = error, 3 = warning, 4 = info, 5 = debug

def debug(text):
    if dt_level >= 5:
        print('Debug: ' + text)
    global debugs
    debugs.append(text)

def info(text):
    if dt_level >= 4:
        print('Info: ' + text)
    global infos
    infos.append(text)

def warning(text):
    if dt_level >= 3:
        print('Warning: ' + text)
    global warnings
    warnings.append(text)

def error(text):
    if dt_level >= 2:
        print('Error: ' + text)
    global errors
    errors.append(text)

def fatal(text):
    if dt_level >= 1:
        print('Fatal: ' + text)
    global fatals
    fatals.append(text)


def setLevel(_level):
    global dt_level
    dt_level = _level

def clear():
    global debugs
    debugs = []
    global infos
    infos = []
    global warnings
    warnings = []
    global errors
    errors = []
    global fatals
    fatals = []


def summary():
    if dt_level >= 5:
        print(str(len(debugs)) + " Debug Messages")
    if dt_level >= 4:
        print(str(len(infos)) + " Info Messages")
    if dt_level >= 3:
        print(str(len(warnings)) + " Warnings")
    if dt_level >= 2:
        print(str(len(errors)) + " Errors")
    if dt_level >= 1:
        print(str(len(fatals)) + " Fatal Messages")

    print("") # empty line after summary