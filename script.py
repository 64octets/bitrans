import re
import os
import copy

import ops
import bytestream
import machine

url_regex  = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
    r'localhost|' # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class script:
    def __init__(self, s):
        if isinstance(s, str):
            self.bstream = bytestream.bytestream(s)
        else:
            self.bstream = s
        self.original_bstream = copy.deepcopy(self.bstream)

    def __add__(self, other):
        return script(self.bstream + other.bstream)

    def __len__(self):
        return len(self.original_bstream)

    def stream(self):
        return copy.deepcopy(self.original_bstream)

    def interpret(self, stack_machine = None, transaction = None, index = None, animate = False):
        if stack_machine is None:
            stack_machine = machine.machine()  # create a clean machine if none provided
        if animate:
            stack_machine.draw()
        while not self.bstream.isempty():
            code = self.bstream.read(1).unsigned(endian="big")
            op = ops.code[code]
            print op
            if op.word == 'OP_CHECKSIG':  #checksig is a special case
                if transaction is None or index is None:
                    print "OP_CHECKSIG called but transaction or index missing; script invalid"
                    return False
                op(self.bstream, stack_machine, transaction, index, self)
            else:
                op(self.bstream, stack_machine)
            if animate:
                stack_machine.draw()
        self.bstream = self.stream()
        if stack_machine.peek().unsigned() == 0:
            return False
        return True
            
            
