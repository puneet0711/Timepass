testing///ila 


from optparse import OptionParser
from card.USIM import USIM

class hssUser():
	imsi = 0
	ki = 1 
	seq = 1
	amf = None
	opc = None

	def __init__(self, imsi, KI, SEQ=1, AMF=None):
		self.imsi = imsi
		self.ki = KI
		self.seq = SEQ
		self.amf = AMF

	def increment_seq():
		self.seq += 1;

	def set_opc(OPc):
		self.opc = OPc


class AuChss():
    '''
    implements a simple AuC / HSS with no persistant storage
    '''
    _debug = 0

    def __init__(self, OP_hex="00000000000000000000000000000000", debug=0):
    	self.OP_bin = stringToByte(OP_hex) # Operator Key
    	self.OP = byteToString(self.OP_bin)
    	self.users = []
    	#self.users.append = hssUser(imsi="001011234567895", KI="00000000000000000000000000000000")

    def calc_opc_hex(self, K_hex, OP_hex=None):
    	IV = 16 * '\x00'
    	KI = unhexlify(K_hex)

        if not OP_hex == None:
    	   OP = unhexlify(OP_hex)
        else:
            OP = unhexlify(self.OP)
        if self._debug:
            print "[DBG]calc_opc_hex: op(%d) KI(%d) IV(%d)" % (len(OP), len(KI), len(IV))
            print "[DBG]calc_opc_hex: OP", OP, "KI", KI, "IV", IV

    	aesCrypt = AES.new(KI, mode=AES.MODE_CBC, IV=IV)
    	data = OP
    	OPc =  self._xor_str(data, aesCrypt.encrypt(data))
    	return hexlify(OPc)
    	#return b2a_hex(byteToString(OPc))


    def _xor_str(self,s,t):
    	"""xor two strings together"""
    	return "".join(chr(ord(a)^ord(b)) for a,b in zip(s,t))


def xor_strings(s,t):
    """xor two strings together"""
    return "".join(chr(ord(a)^ord(b)) for a,b in zip(s,t))

# Query: SELECT `imsi`,`key`,`OPc` FROM `users` 
# IMSI: 001011234567895 Key: 00.00.00.00.00.00.00.00.00.00.00.00.00.00.00.00.
# OPc: 66.e9.4b.d4.ef.8a.2c.3b.88.4c.fa.59.ca.34.2b.2e.
# RijndaelKeySchedule: K 00000000000000000000000000000000
# Compute opc:
#     K:  00000000000000000000000000000000
#     In: 00000000000000000000000000000000
#     Rinj:   66E94BD4EF8A2C3B884CFA59CA342B2E
#     Out:    66E94BD4EF8A2C3B884CFA59CA342B2E
# Query: UPDATE `users` SET `OPc`=UNHEX('66e94bd4ef8a2c3b884cfa59ca342b2e') WHERE `users`.`imsi`='001011234567895'
# IMSI 001011234567895 Updated OPc 66e94bd4ef8a2c3b884cfa59ca342b2e -> 66e94bd4ef8a2c3b884cfa59ca342b2e
# 0 rows affected


def handle_usim_fakehss(options, rand_bin):
    u = USIM(options.debug)
    if not u:
        print "Error opening USIM"
        exit(1)

    if options.debug:
        u.dbg = 2

    if rand_bin == None:
        rand_bin = stringToByte("00112233445566778899aabbccddeeff")
    IV = 16 * '\x00'
    OP_bin = stringToByte("00000000000000000000000000000000") # Operator Key
    KI_bin = stringToByte("00000000000000000000000000000000") # K
    SQN_bin= stringToByte("000023403500") # SQN 591410432
    # AMF ??
                         #"7D3D6804DB5480003F7A47FB35FA7285"
                         #"808182888485868788898A8B8C8D8E8F" K
                         #"97A167DED889B6DFA92D985D77E5C088" OP
    #calculate OPc
    KI = binascii.unhexlify(byteToString(KI_bin))
    aesCrypt = AES.new(KI, mode=AES.MODE_CBC, IV=IV)
    data = binascii.unhexlify(byteToString(OP_bin))
    ## OCc = encAES(OP) xor OP
    OPc =  xor_strings(data, aesCrypt.encrypt(data)) 
    OPc_bin = stringToByte(OPc)

    print "OP: \t%s" % b2a_hex(OP_bin)
    print "KI: \t%s" % b2a_hex(KI_bin)
    print "OPc:\t%s" % b2a_hex(OPc_bin)

    imsi = u.get_imsi()
    print "USIM card with IMSI %s" % imsi
    print "AUTS:\t%s" % b2a_hex(rand_bin)

def testcode():
    print "use as lib..."
    hss = AuChss("00000000000000000000000000000000")
    
    K = "00000000000000000000000000000000"
    OPc = hss.calc_opc_hex(K)
    print "OP: \t%s" % hss.OP
    print "KI: \t%s" % K
    print "OPc: \t%s" % OPc
    print 16*"--"
    
    K  = "00000000000000000000000000000000"
    OP = "00000000000000000000000000000000"
    OPc= "66E94BD4EF8A2C3B884CFA59CA342B2E"
    print "%s, %s -> %s =? %s" %(K, OP, hss.calc_opc_hex(K, OP),OPc)
    print 16*"--"
    K  = "8BAF473F2F8FD09487CCCBD7097C6862"
    OP = "11111111111111111111111111111111"
    OPc= "8E27B6AF0E692E750F32667A3B14605D"
    print "%s, %s -> %s =? %s" %(K, OP, hss.calc_opc_hex(K, OP),OPc)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-k", "--key", dest="key", help="K from USIM")
    parser.add_option("-o", "--op", dest="op", help="OP operator key")
    (options, args) = parser.parse_args()


    if options.key and options.op:
        hss = AuChss()
        K  = (options.key)
        OP = (options.op)
        print "OP: \t%s" % OP
        print "KI: \t%s" % K
        print "OPc:\t%s" % hss.calc_opc_hex(K, OP)

