import json
import os
import glob


class Helper:
    VERSION = "beta"

    def __init__(self, argv):
        self.argv = argv
        self.banner()
        self.validate_args()
        self.config = {}

    def validate_args(self):
        if "-l" in self.argv or "--list" in self.argv:
            self.list_modules()
            self.exit()

        if "-h" in self.argv or "--help" in self.argv:
            self.menu()
            self.exit()

        elif len(self.argv) < 3:
            self.menu()
            self.exit_show_error("Missing arguments.")

    def menu(self):
        print("Usage: %s [config] [output] (optional parameters)\n")
        print("\n")
        print("\t[config]\t\t\t\tConfig file that contain generator information")
        print("\n\t[output]\t\t\t\tOutput filename for the macro\n")
        print("\n\t-l\t--list\t\t\t\tList of all available payloads and evasion techniques")
        print("\n\t-s\t--split_strings\t\t\tRandomly split strings at parts")
        print("\n\t-x\t--strings_to_hex\t\tEncode strings to hex" % self.argv[0])

    @staticmethod
    def banner():
        print("MaliciousMacroGenerator.Malicious Macro Generator v%s \nAuthor: T0x1cEnv31ope toxicenvelope@protonmail.com\n" % Helper.VERSION)

    def process_completed(self):
        self.print_success("Generation completed.")

    @staticmethod
    def exit_show_error(error):
        print("\n[-] Error: %s" % error)
        exit(0)

    @staticmethod
    def exit():
        exit(0)

    @staticmethod
    def print_success(message):
        print("[+] %s" % message)

    def parse_config(self):
        buffer = self.load_file(self.argv[1])
        try:
            self.config = json.loads(buffer)
        except:
            self.exit_show_error("\"%s\" is not a valid config file." % self.argv[1])
        return self

    def get_config(self, key):
        if key in self.config:
            return self.config[key]
        else:
            self.exit_show_error("\"%s\" key not found in the config file." % key)

    def show_config_description(self):
        buffer = self.get_config("description")
        self.print_success("Loading the following payload:\n\n%s\n" % buffer)
        return self

    def load_file(self, filename):
        if os.path.exists(filename):
            buffer = open(filename, "rb").read()
            return buffer
        else:
            self.exit_show_error("\"%s\" file not found." % filename)

    def save_file(self, filename, buffer):
        try:
            open(f"outputs/{filename}", "wb").write(buffer)
        except:
            self.exit_show_error("Failed to save \"%s\"." % filename)
        self.print_success("\"%s\" successfully saved to the disk." % filename)
        return self

    def list_modules(self):
        path = os.path.dirname(os.path.realpath(__file__))
        payloadPath = path + "/../templates/payloads/"
        evasionPath = path + "/../templates/evasions/"
        self.print_success("List of available payloads")
        self.glob_folder(payloadPath)
        print("\n")
        self.print_success("List of available evasion techniques")
        self.glob_folder(evasionPath)

    @staticmethod
    def glob_folder(path):
        for file in glob.glob(path + "*"):
            print("\t" + file.replace(path, ""))
