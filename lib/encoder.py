import random
import string
import re
import codecs


class Encoder:

    def __init__(self, helper):
        self.helper = helper
        self.default = ["var", "func", "data", "bool"]
        self.default_size = len(self.default)
        try:
            self.offset = int(helper.GetConfig("encodingoffset"))
        except:
            helper.ExitShowError("\"%s\" is not a valid encodingoffset value." % self.offset)

    def get_encoding_offset(self):
        return self.offset

    def append_vars(self, vars):
        self.default += vars
        return self

    def encode_buffer(self, buffer, reverse=False):
        output = ""
        for c in buffer:
            if reverse:
                output += chr(ord(c) + int(self.offset))
            else:
                output += chr(ord(chr(c)) + int(self.offset))
        return output.encode()

    def encode_user_vars(self, buffer):
        for var in re.findall(b"{\[.*?\]}", buffer):
            buffer = buffer.replace(var, self.encode_buffer(self.remove_encode_tag(var)))
        return buffer

    def append_def_use_tag(self, buffer):
        for var in re.findall(b"\[use:.*?\]", buffer):
            buffer = buffer.replace(var, b"")
            self.default.append(self.remove_def_use_tag(var))
        return buffer

    def remove_encode_tag(self, buffer):
        return buffer.replace(b"{[", b"").replace(b"]}", b"")

    def remove_def_use_tag(self, buffer):
        return buffer.replace(b"[use:", b"").replace(b"]", b"")

    def rand_vars(self, buffer):
        iterator = self.helper.GetConfig("varcount")
        count = 0
        for var in self.default:
            count += 1

            for i in reversed(range(1, iterator)):
                if not isinstance(var, bytes):
                    var = var.encode()
                buffer = buffer.replace(var + str(i).encode(), self.gen_str(random.randrange(5, 25)).encode())

            if count > self.default_size:
                buffer = buffer.replace(var, self.gen_str(random.randrange(5, 25)).encode())

        return buffer

    def rand_smallint(self, buffer):
        return self.__rand_int(buffer, "smallint", 1, 2)

    def rand_int(self, buffer):
        current = self.__rand_int(buffer, "int", 2, 5)
        if len(current) < 100:
            self.rand_int(self, buffer)
        return current

    def __rand_int(self, buffer, var, min, max):
        iterator = self.helper.GetConfig("varcount")
        for i in reversed(range(1, iterator)):
            buffer = buffer.replace(("[" + var + str(i) + "]").encode(), self.gen_int(random.randrange(min, max)))
        return buffer

    def gen_str(self, size):
        return ''.join(
            random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(size))

    def gen_int(self, size):
        return (''.join(random.SystemRandom().choice(string.digits) for _ in range(size))).encode()

    def replace_var(self, buffer, var, data, encode=False):
        if encode:
            data = self.encode_buffer(data)
        return buffer.replace(("[" + var + "]").encode(), str(data).encode())

    def chunk_payload(self, buffer, payload):
        payload = self.encode_buffer(payload, reverse=True)
        chunksize = int(self.helper.GetConfig("chunksize"))
        vars = ("Dim " + self.gen_str(random.randrange(5, 20)) + " As String\r\n").encode()
        args = ""
        size = 0

        for chunk in re.findall(b"." * chunksize, payload):
            current_var = self.gen_str(random.randrange(5, 20))
            vars += "\tDim " + current_var + " As String\r\n"
            vars += "\t" + current_var + " = \"" + chunk + "\"\r\n"

            args += current_var + " & "
            size += chunksize

        if len(payload) > size:
            current_var = self.gen_str(random.randrange(5, 20)).encode()
            vars += b"\tDim " + current_var + b" As String\r\n"
            vars += b"\t" + current_var + b" = \"" + payload[(len(payload) - size) * -1:] + b"\"\r\n"
            args += current_var.decode()
        else:
            args = args[:-3]

        return buffer.replace(b"[payload]", vars).replace(b"[payload_args]", args.encode())

    def split_strings(self, buffer):
        for detected_str in re.findall(r'"(.+?)"', buffer):
            if len(detected_str) > 5:
                random_number = random.randint(1, len(detected_str) // 2)
                st = 0
                new_str = ''
                for i in range(random_number):
                    random_value = random.randint(1, (len(detected_str) - st) // (random_number - i))
                    if random_value > 3:
                        new_str += detected_str[st:st + random_value] + "\" & \""
                        st += random_value
                new_str += detected_str[st:]
                buffer = buffer.replace(detected_str, new_str)
        return buffer

    def strings_to_hex(self, buffer, vba_decoder):
        encoded_function_name = self.gen_str(random.randrange(5, 15))
        encoded_var_name1 = self.gen_str(random.randrange(5, 15))
        encoded_var_name2 = self.gen_str(random.randrange(5, 15))
        for detected_str in re.findall(r'"(.+?)"', buffer):
            r = random.randint(1, 10)
            if r > 7:
                encoded_bytes = codecs.encode(bytes(detected_str), 'hex_codec')
                new_str = encoded_function_name + "(\"" + str(encoded_bytes.decode("ascii")) + "\")"
                word_to_replace = "\"" + detected_str + "\""
                buffer = str(buffer.replace(word_to_replace, new_str))

        vba_decoder = vba_decoder.replace("HexToStr", encoded_function_name)
        vba_decoder = vba_decoder.replace("counter", encoded_var_name1)
        vba_decoder = vba_decoder.replace("hexString", encoded_var_name2)

        buffer += "\n\n" + vba_decoder
        return buffer
