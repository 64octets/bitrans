import bytestream
import script
import machine
import sys

class transaction:
    def __init__(self, *args):
        if len(args) < 2:
            self.version      = 1
            self.tx_in_count  = 0
            self.tx_in        = []
            self.tx_out_count = 0
            self.tx_out       = []
            self.lock_time    = 0
            if len(args) == 1:
                self.server = args[0]
        elif len(args) == 2:
            txid = args[0]
            server = args[1]
            self.server = server
            tx = server("getrawtransaction", txid, 1)
            self.txid = txid
            try:
                stream = bytestream.bytestream(tx['hex'])
            except TypeError as e:
                print "Server returned error. Probably can't find the transaction key."
                print "\tTypeError error: {0}:".format(e)
                sys.exit(1)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            self.version      = stream.read(4).unsigned()
            self.tx_in_count  = stream.readvarlensize()
            self.tx_in        = [txin(stream) for i in xrange(self.tx_in_count)]
            self.tx_out_count = stream.readvarlensize()
            self.tx_out       = [txout(stream) for i in xrange(self.tx_out_count)]
            self.lock_time    = stream.read(4).unsigned()
        else:
            raise ValueError("Zero or two args")

    def __len__(self):
        return len(self.encode())

    def verify(self, animate=False):
        valid = True
        for tin in self.tx_in:
            # clean machine for each input
            stack_machine = machine.machine()
            # always eval tin
            valid = valid and tin.script.interpret(stack_machine=stack_machine)
            # coinbase transactions do not refer to a previous output, but other transactions do
            if not tin.is_coinbase:
                prev_tran = transaction(tin.prev_hash, self.server)
                tout = prev_tran.tx_out[tin.index]
                valid = valid and tout.script.interpret(stack_machine=stack_machine,  #operate on dirty machine
                                                        transaction=self,
                                                        index=tin.index,
                                                        animate=animate)  
        return valid

    def valid(self):
        """
        Check whether this transaction is valid according to
        https://en.bitcoin.it/wiki/Protocol_rules#.22tx.22_messages

        """
        #Check syntactic correctness
        #  not implemented -james
        
        #Make sure neither in or out lists are empty
        if self.tx_in_count == 0 or self.tx_out_count == 0:
            return False
        
        #Size in bytes < MAX_BLOCK_SIZE
        if len(self.encode()) > parameters.MAX_BLOCK_SIZE:
            return False
        
        #Each output value, as well as the total, must be in legal money range
        total = 0
        for txout in self.tx_out:
            if txout.value < 0 or txout.value > 2.1 * (10**7):
                return False
            total += value
        if total < 0 or total > 2.1 * (10**7):
            return False
        
        #Make sure none of the inputs have hash=0, n=-1 (coinbase transactions)
        for txin in self.tx_in:
            if txin.is_coinbase:
                return False
        
        #Check that nLockTime <= INT_MAX, size in bytes >= 100, and sig opcount <= 2
        if nLockTime > paramters.INT_MAX:
            return False
        if len(self.encode()) < 100:
            return False
        for txin in self.tx_in:
            if txin.script.opcount() > 2:
                return False
        
        #Reject "nonstandard" transactions: scriptSig doing anything other than pushing numbers on the stack, or scriptPubkey not matching the two usual forms[4]
        #  not implemented --james
        
        #Reject if we already have matching tx in the pool, or in a block in the main branch
        #  not implemented --james
        
        #Reject if any other tx in the pool uses the same transaction output as one used by this tx.[5]
        # not implemented --james
        
        #For each input, look in the main branch and the transaction pool to find the referenced output transaction. If the output transaction is missing for any input, this will be an orphan transaction. Add to the orphan transactions, if a matching transaction is not in there already.
        
        #For each input, if the referenced output transaction is coinbase (i.e. only 1 input, with hash=0, n=-1), it must have at least COINBASE_MATURITY (100) confirmations; else reject this transaction
        
        #For each input, if the referenced output does not exist (e.g. never existed or has already been spent), reject this transaction[6]
        
        #Using the referenced output transactions to get input values, check that each input value, as well as the sum, are in legal money range
        
        #Reject if the sum of input values < sum of output values
        
        #Reject if transaction fee (defined as sum of input values minus sum of output values) would be too low to get into an empty block
        
        #Verify the scriptPubKey accepts for each input; reject if any are bad
        
        #Add to transaction pool[7]
        
        #"Add to wallet if mine"
        
        #Relay transaction to peers
        
        #For each orphan transaction that uses this one as one of its inputs, run all these steps (including this one) recursively on that orphan

        return True

    def encode(self):
        stream = bytestream.bytestream('')
        stream += bytestream.fromunsigned(self.version,4)
        stream += bytestream.fromvarlen(self.tx_in_count)
        for tx_in in self.tx_in:
            stream += tx_in.encode()
        stream += bytestream.fromvarlen(self.tx_out_count)
        for tx_out in self.tx_out:
            stream += tx_out.encode()
        stream += bytestream.fromunsigned(self.lock_time,4)
        return stream

    def broadcast(self, clients):
        #raw = self.encode().stream
        #print raw
        #result = self.server("sendrawtransaction", raw)
        #return not result is None
        return clients.sendTransaction(self)

            
class txin:
    def __init__(self, *args):
        if len(args) == 0:
            self.prev_hash     = str(bytestream.fromunsigned(0,32))
            self.index         = 1
            self.script_length = 0
            self.script        = None
            self.sequence      = 0
            self.is_coinbase   = True
        elif len(args) == 1:
            stream = args[0]
            self.prev_hash     = str(stream.read(32).reverse().stream)
            self.index         = stream.read(4).unsigned()
            self.script_length = stream.readvarlensize()
            self.script        = script.script(stream.read(self.script_length))
            self.sequence      = stream.read(4).unsigned()
            
            if int(self.prev_hash,16) == 0:
                self.is_coinbase = True
            else:
                self.is_coinbase = False
        else:
            raise ValueError("Zero or one args")

    def encode(self):
        stream = bytestream.bytestream("")
        stream += bytestream.bytestream(self.prev_hash).reverse()
        stream += bytestream.fromunsigned(self.index,4)
        stream += bytestream.fromvarlen(self.script_length)
        stream += self.script.stream()
        stream += bytestream.fromunsigned(self.sequence,4)
        return stream

class txout:
    def __init__(self, *args):
        if len(args) == 0:
            self.value = 0
            self.script_length = 0
            self.script = None
        elif len(args) == 1:
            stream = args[0]
            self.value         = stream.read(8).unsigned()
            self.script_length = stream.readvarlensize()
            self.script        = script.script(stream.read(self.script_length))
        else:
            raise ValueError("Zero or one args")

    def encode(self):
        stream = bytestream.bytestream("")
        stream += bytestream.fromunsigned(self.value,8)
        stream += bytestream.fromvarlen(self.script_length)
        stream += self.script.stream()
        return stream
