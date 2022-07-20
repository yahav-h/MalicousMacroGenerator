from lib.helper import Helper
from lib.encoder import Encoder
import sys

if __name__ == "__main__":
    helper = Helper(sys.argv)
    helper.parse_config().show_config_description()

    encoder = Encoder(helper)
    encoder.append_vars(helper.get_config("vars"))

    template = helper.load_file(helper.get_config("template"))
    data = template

    for evasion in helper.get_config("evasion"):
        data += helper.load_file("templates/evasions/" + evasion + ".vba")

    data = encoder.replace_var(data, "offset", encoder.get_encoding_offset())
    data = encoder.encode_user_vars(data)
    data = encoder.append_def_use_tag(data)
    data = encoder.rand_vars(data)
    data = encoder.rand_int(data)
    data = encoder.rand_smallint(data)

    encodedvars = helper.get_config("encodedvars")
    for var in encodedvars:
        data = encoder.replace_var(data, var, encodedvars[var], True)

    if "-s" in sys.argv or "--split_strings" in sys.argv:
        data = encoder.split_strings(data)
    if "-x" in sys.argv or "--strings_to_hex" in sys.argv:
        decoder = helper.load_file("templates/evasions/hex-decode.vba")
        data = encoder.strings_to_hex(data, decoder)

    data = encoder.chunk_payload(data, helper.get_config("payload"))

    helper.save_file(sys.argv[2], data).process_completed()