import os
import time
import random

try:
    import xlrd
    import xlsxwriter
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")



def stopBot(err):
    print(">>>>>---------------------------------------------------------------------------<<<<<")
    print(err)
    print(">>>>>----------------------------------------------------------------------------<<<<<")
    time.sleep(3)
    quit()


def deformatEntry(inp):
    if isinstance(inp, list):
        toRemove = ["'", '"', "[", "]", "\\", "/"]
        return ''.join(c for c in str(inp) if not c in toRemove)

    elif isinstance(inp, bool):
        if inp:
            return "Yes"
        else:
            return "No"

    else:
        return inp


def writeSettings(sheet, toWrite):

    row = 1  # WRITE SETTINGS
    col = 0
    for col0, col1, col2 in toWrite:
        sheet.write(row, col, col0)
        sheet.write(row, col + 1, col1)
        sheet.write(row, col + 2, col2)
        row += 1


class worldConfig:
    def __init__(self):
        self.world = {
            "areas": {

            }

        }
        self.readWorld()

    def formatWorldXlsx(self):
        print("Formatting world xlsx")
        try:
            with xlsxwriter.Workbook('../Config/World.xlsx') as workbook:
                for area in range(10):
                    worksheet = workbook.add_worksheet('Area%s' % area)
                    format_graybkg = workbook.add_format({'bold': True, 'center_across': False, 'font_color': 'white', 'bg_color': 'gray'})
                    format_bold = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'black'})
                    format_light = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'black', 'bg_color': '#DCDCDC', 'border': True})
                    format_black = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'black', 'bg_color': 'black'})
                    materialColorCodes = ["#FFCDD2", "#E1BEE7", "#D1C4E9", "#BBDEFB", "#B2EBF2", "#B2DFDB", "#C8E6C9", "#DCEDC8", "#F0F4C3", "#FFECB3"]
                    random.shuffle(materialColorCodes)
                    worksheet.set_column(0, 0, 30)
                    worksheet.set_column(1, 1, 100)
                    for i in range(20):
                        x = i + 2
                        worksheet.set_column(x, x, 30)
                    worksheet.set_row(1, 40)
                    worksheet.set_row(2, 15, format_black)
                    for i in range(500):
                        x = i + 5
                        worksheet.set_row(x, 40)
                    worksheet.write(0, 0, "Area Name", format_light)
                    worksheet.write(1, 0, "Area Description", format_light)
                    worksheet.write(4, 0, "Room ID", format_light)
                    worksheet.write(4, 1, "Room Description", format_light)
                    column = 2
                    for option in range(1, 11):
                        format_option = workbook.add_format({'border': True, 'bg_color': materialColorCodes[option-1]})
                        row = 4
                        # Write Option column
                        worksheet.write(row, column, "Option %s" % option, format_option)
                        for y in range(500):
                            x = y + 5
                            worksheet.write(x, column, "", format_option)
                        column += 1
                        # Go over a column then write ID column
                        worksheet.write(row, column, "Room ID for Option %s" % option, format_option)
                        for y in range(500):
                            x = y + 5
                            worksheet.write(x, column, "", format_option)
                        column += 1

        except PermissionError:
            stopBot("Can't open the World file. Please close it and make sure it's not set to Read Only.")



    def readWorld(self):
        workbook = xlrd.open_workbook("../Config/World.xlsx")
        for sheet in workbook.sheets():
            area = {
                "ID": sheet.name,
                "name": sheet.cell_value(0, 1),
                "description": sheet.cell_value(1, 1),
                "roomCount": sheet.nrows - 5,
                "rooms": {

                }
            }
            for row in range(0, area["roomCount"]):
                row = row + 5
                room = {
                    "ID": sheet.cell_value(row, 0),
                    "description": sheet.cell_value(row, 1),
                    }
                allRooms = {
                        "Option1": {
                            "Phrase": sheet.cell_value(row, 2),
                            "ID": sheet.cell_value(row, 3),
                        },
                        "Option2": {
                            "Phrase": sheet.cell_value(row, 4),
                            "ID": sheet.cell_value(row, 5),
                        },
                        "Option3": {
                            "Phrase": sheet.cell_value(row, 6),
                            "ID": sheet.cell_value(row, 7),
                        },
                        "Option4": {
                            "Phrase": sheet.cell_value(row, 8),
                            "ID": sheet.cell_value(row, 9),
                        },
                        "Option5": {
                            "Phrase": sheet.cell_value(row, 10),
                            "ID": sheet.cell_value(row, 11),
                        },
                        "Option6": {
                            "Phrase": sheet.cell_value(row, 12),
                            "ID": sheet.cell_value(row, 13),
                        },
                        "Option7": {
                            "Phrase": sheet.cell_value(row, 14),
                            "ID": sheet.cell_value(row, 15),
                        },
                        "Option8": {
                            "Phrase": sheet.cell_value(row, 16),
                            "ID": sheet.cell_value(row, 17),
                        },
                        "Option9": {
                            "Phrase": sheet.cell_value(row, 18),
                            "ID": sheet.cell_value(row, 19),
                        },
                        "Option10": {
                            "Phrase": sheet.cell_value(row, 20),
                            "ID": sheet.cell_value(row, 21),
                        }
                }
                dictToReturn = {}
                for option in allRooms:
                    if allRooms[option]["Phrase"]:
                        dictToReturn[option] = allRooms[option]

                room["options"] = dictToReturn
                area["rooms"][room["ID"]] = room
            if area["roomCount"]:
                self.world["areas"][area["ID"]] = area



    def settingsSetup(self):
        global settings

        if not os.path.exists('../Config'):
            print("Creating a Config folder, check it out!")
            os.mkdir("../Config")

        if not os.path.exists('../Config/World.xlsx'):
            print("Creating World.xlsx")
            self.formatWorldXlsx()
            stopBot("Config/World.xlsx has been generated!")

        wb = xlrd.open_workbook('../Config/World.xlsx')
        # Read the settings file

        #settings = self.readSettings(wb)

        if not os.path.exists("../Config/token.txt"):
            stopBot("No auth token exists, run INSTALL_REQUIREMENTS in the Setup folder and authenticate!")

        print(">> Initial Checkup Complete! Connecting to Chat...")
        return settings



world = worldConfig()