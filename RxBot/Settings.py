import os
import time
import argparse

try:
    import xlrd
    import xlsxwriter
except ImportError as e:
    print(e)
    raise ImportError(">>> One or more required packages are not properly installed! Run INSTALL_REQUIREMENTS.bat to fix!")

parser = argparse.ArgumentParser(description='Generate Settings File')
parser.add_argument('--g', dest="GenSettings", action="store_true")
parser.set_defaults(GenSettings=False)

GenSettings = (vars(parser.parse_args())["GenSettings"])


'''----------------------SETTINGS----------------------'''

'''FORMAT ---->   ("Option", "Default", "This is a description"), '''

defaultSettings = [
    ("TRIGGER MESSAGE", "", "The message from another bot that will trigger this bot's main function.,"),
    ("TRIGGER USER", "CreatisBot", "Only this user can send the TRIGGER MESSAGE and trigger the bot."),
]


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


class settingsConfig:
    def __init__(self):
        self.defaultSettings = defaultSettings

    def formatSettingsXlsx(self):
        try:
            with xlsxwriter.Workbook('../Config/Settings.xlsx') as workbook:
                worksheet = workbook.add_worksheet('Settings')
                format = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
                boldformat = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'black'})
                lightformat = workbook.add_format({'bold': True, 'center_across': True, 'font_color': 'black', 'bg_color': '#DCDCDC', 'border': True})
                worksheet.set_column(0, 0, 25)
                worksheet.set_column(1, 1, 50)
                worksheet.set_column(2, 2, 130)
                worksheet.write(0, 0, "Option", format)
                worksheet.write(0, 1, "Your Setting", boldformat)
                worksheet.write(0, 2, "Description", format)
                worksheet.set_column('B:B', 50, lightformat)  # END FORMATTING

                writeSettings(worksheet, self.defaultSettings)

        except PermissionError:
            stopBot("Can't open the Settings file. Please close it and make sure it's not set to Read Only.")
        except:
            stopBot("Can't open the Settings file. Please close it and make sure it's not set to Read Only. [0]")



    def reloadSettings(self, tmpSettings):
        for item in tmpSettings:
            for i in enumerate(defaultSettings):
                if (i[1][0]) == item:  # Remove all 'list' elements from the string to feed it back into the speadsheet
                    defaultSettings[i[0]] = (item, deformatEntry(tmpSettings[item]), defaultSettings[i[0]][2])

        self.formatSettingsXlsx()

    def readSettings(self, wb):
        settings = {}
        worksheet = wb.sheet_by_name("Settings")

        for item in range(worksheet.nrows):
            if item == 0:
                pass
            else:
                option = worksheet.cell_value(item, 0)
                try:
                    setting = int(worksheet.cell_value(item, 1))
                except ValueError:
                    setting = str(worksheet.cell_value(item, 1))
                    # Change "Yes" and "No" into bools, only for strings
                    if setting.lower() == "yes":
                        setting = True
                    elif setting.lower() == "no":
                        setting = False

                settings[option] = setting

        if worksheet.nrows != (len(defaultSettings) + 1):
            self.reloadSettings(settings)
            stopBot("The settings have been changed with an update! Please check your Settings.xlsx file then restart the bot.")
        return settings

    def settingsSetup(self):
        global settings

        if not os.path.exists('../Config'):
            print("Creating a Config folder, check it out!")
            os.mkdir("../Config")

        if not os.path.exists('../Config/Settings.xlsx'):
            print("Creating Settings.xlsx")
            self.formatSettingsXlsx()
            stopBot("Please open Config / Settings.xlsx and configure the bot, then run it again.")

        wb = xlrd.open_workbook('../Config/Settings.xlsx')
        # Read the settings file

        settings = self.readSettings(wb)

        if not os.path.exists("../Config/token.txt"):
            stopBot("No auth token exists, run INSTALL_REQUIREMENTS in the Setup folder and authenticate!")

        print(">> Initial Checkup Complete! Connecting to Chat...")
        return settings

    def formatCommandsxlsx(self):
        try:
            with xlsxwriter.Workbook('../Config/Commands.xlsx') as workbook:  # FORMATTING

                format = workbook.add_format(
                    {'bold': True, 'center_across': True, 'font_color': 'white', 'bg_color': 'gray'})
                lightformat = workbook.add_format(
                    {'center_across': True, 'font_color': 'black', 'bg_color': '#DCDCDC', 'border': True})
                evenlighterformat = workbook.add_format(
                    {'font_color': 'black', 'bg_color': '#f0f0f0', 'border': True})
                redformat = workbook.add_format({'font_color': 'black', 'bg_color': '#ffdede', 'border': True})

                worksheet = workbook.add_worksheet("Commands")  # FORMAT GLOBAL
                worksheet.set_column(0, 0, 30)
                worksheet.set_column(1, 1, 110)
                worksheet.write(0, 0, "Command", format)
                worksheet.write(0, 1, "Response", format)
                worksheet.set_column('B:B', 110, evenlighterformat)

            print("Commands.xlsx has been updated successfully.")
        except PermissionError:
            stopBot("Can't open the settings file. Please close it and make sure it's not set to Read Only")

    def readCommands(self):
        wb = xlrd.open_workbook('../Config/Commands.xlsx')
        commandsFromFile = {}
        worksheet = wb.sheet_by_name("Commands")

        for item in range(worksheet.nrows):
            if item == 0:
                pass
            else:
                command = worksheet.cell_value(item, 0)
                response = str(worksheet.cell_value(item, 1))
                commandsFromFile[command] = response

        return commandsFromFile


def buildConfig():
    if not os.path.exists('../Config'):
        os.mkdir("../Config")

    if not os.path.exists('../Config/Settings.xlsx'):
        print("Creating Settings.xlsx")
        settingsConfig.formatSettingsXlsx(settingsConfig())
        print("\nPlease open Config / Settings.xlsx and configure the bot, then run it again.")
        print("Please follow the setup guide to everything set up! https://rxbots.net/rxbot-setup.html")
        time.sleep(3)
        quit()

    if not os.path.exists('../Config/Commands.xlsx'):
        settingsConfig.formatCommandsxlsx(settingsConfig())
        print("\nCommands file has been created.")
    else:
        print("Everything is already set up!")


if GenSettings:
    buildConfig()