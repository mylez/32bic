      ##############################
      #####     Zanita ASM      ####
      #####   by Miles Smith    ####
      ##############################

def makehex(msb='', sra='0', srb='0', dr='', alu = '', op='00'):
    token = {'':'', 'and': '5', 'random': '4', 'xor': '7', '-': '1', 'mask': 'a', '<<': 'b', '>>': 'c', '+': '0', 'not': '8', '*': '2', '/': '3', 'or': '6', 'select': '9'}
    sra, srb, dr = sra.replace('r', ''), srb.replace('r', ''), dr.replace('r', '')
    if sra > "f" or srb > "f" or dr > "f":
        print "Error: " + sra, srb, dr
    return msb + token[alu] + dr + srb + sra + op + ' '

def pushcalls(source):
    # Change operations in function calls to lines of assembly
    # using function operand stack with the function regfunc()
    rtn = ''
    for line in source.splitlines():
        splitline = line.split()
        try:
            if splitline[0] == 'call' and line.count('(') > 0:
                line = line.replace('(', ' ')
                line = line.replace(')', ' ')
                line = line.replace(',', ' ')
                functioncall = 'call ' + line.split()[1]
                for operand in range(len(line.split()[2::])):
                    if not operand == len(line.split()[2::]) - 1:
                        rtn += regfunc(line.split()[2::][operand])
                    else:
                        rtn += regfunc(line.split()[2::][operand], True)
                        rtn += functioncall + '\n'
            else:
                rtn += line + '\n'
        except IndexError:
            rtn += line + '\n'
    return rtn


def regfunc(n, last=False):
    if n.count('var:') > 0:
        rtn = 'ram read rE ' + n.replace('var:', '') + '\n'
    elif n.count('r') > 0:
        rtn = 'mov ' + n + ' rE\n'
    else:
        rtn = 'put rE ' + n + '\n'
    if not last:
        rtn += 'call opstack.push\n'
    return rtn

def include(source):
    rtn = ''    
    for line in source.splitlines():
        splitline = line.split()
        try:
            if splitline[0] == 'include':
                rtn += open('lib/'+splitline[1], 'r').read()+'\n'
                print "including file lib/"+splitline[1]
            elif splitline[0][0] == '#':
                pass

            else:
                rtn += line+'\n'
        except IndexError:
            pass
    return rtn

def findvars(source):
    vardic = {}
    wvar = 0
    rtn = ''
    for line in source.splitlines():
        try:
            splitline = line.split()
            if splitline[0] == 'var':
                vardic['v:' + splitline[1] + 'v;'] = wvar
                if len(splitline) > 2:
                    wvar += eval(splitline[2])
                else:
                    wvar += 1
            else:
                rtn += line + '\n'

        except IndexError:
            pass
    vardic['v:type.currentv;'] = (wvar + 1)
    return rtn, vardic

def assem(tup):
    source = tup[0]
    vardic = tup[1]
    rtn = ''
    wline = 1
    pointdic = {}
    jumptypes = {'equals':'c1', 'lesser': 'c2', 'greater': 'c3','notequals': 'c4'}

    print "assembling..."
    
    for line in source.splitlines():
        try:
            line = list(line)
            while 1:
                if line[0] == "\t" or line[0] == " ":
                    line.pop(0)
                else:
                    break
        except:
            print "Error removing initial whitespace"
            pass
        
        line = str().join(line)
        splitline = line.split()

        try:
            
            ### Take care of comments/empty lines ###
            if len(splitline) == 0:
                pass
            elif splitline[0][0] == '#':
                
                pass

            ### Build a dictionary of point addresses to link ###
            elif splitline[0] == 'point':
                pointdic['p:' + splitline[1] + 'p;'] = hex(len(rtn.split())).replace('0x', '')


            elif splitline[0] == 'put':
                rtn += makehex(op = '70', dr = splitline[1])
                rtn += hex(signbit(splitline[2])).replace('0x', '') + ' '
                
            elif splitline[0] == 'mov':
                rtn += makehex(op = '60', sra = splitline[1], dr = splitline[2])
                
            elif splitline[0] == 'alu':
                if splitline[1] == 'random':
                    rtn += makehex(op = 'a0', alu = 'random', dr = splitline[2])
                else:
                    rtn += makehex(op = 'a0', alu = splitline[1], sra = splitline[2], srb = splitline[3], dr = splitline[4])
                
            elif splitline[0] == 'jump':
                if len(splitline) == 5:
                    rtn += makehex(op = jumptypes[splitline[1]], sra = splitline[2], srb = splitline[3], msb = 'p:' + splitline[4]+'p;')
                elif len(splitline) == 2:
                    rtn += makehex(op = 'c0', msb = 'p:'+splitline[1]+'p;')
                
            elif splitline[0] == 'ram':
                if len(splitline) == 4:
                    if splitline[1] == 'write':
                        rtn += makehex(op = '51', msb = 'v:' + splitline[3]+'v;', sra = splitline[2])
                    elif splitline[1] == 'read':
                        rtn += makehex(op = '50', msb = 'v:' + splitline[3]+'v;', sra = splitline[2])
                elif len(splitline) == 3:
                    if splitline[1] == 'write':
                        rtn += makehex(op = '52', sra = splitline[2])
                    elif splitline[1] == 'read':
                        rtn += makehex(op = '53', sra = splitline[2])

            elif splitline[0] == 'mar':
                if splitline[1][0] == 'i':
                    rtn += makehex(op = '54')
                elif splitline[1][0] == 'd':
                    rtn += makehex(op = '55')
                elif splitline[1][0] == 'r':
                    rtn += makehex(op = '56', dr = splitline[2])
                elif splitline[1][0] == 'w':
                    rtn += makehex(op = '57', sra = splitline[2]) 

            elif splitline[0] == 'par':
                if splitline[1] == 'read':
                    rtn += makehex(op = '58', dr = splitline[2])
                elif splitline[1] == 'write':
                    rtn += makehex(op = '59', sra = splitline[2])
            
            elif splitline[0] == 'return':
                rtn += 'fb0 '

            elif splitline[0] == 'input':
                rtn += makehex(op = '71', dr = splitline[1])
                
            elif splitline[0] == 'output':
                rtn += makehex(op = '72', sra = splitline[1])

            elif splitline[0] == 'out16':
                rtn += makehex(op = '74', msb = hex(signbit(splitline[1])).replace('0x', ''))
                
            elif splitline[0] == 'out32':
                rtn += makehex(op = '73')
                rtn += hex(eval(signbit(splitline[1]))).replace('0x', '') + ' '
                
            elif splitline[0] == 'halt':
                rtn += 'ff '

            elif splitline[0] == 'reset':
                rtn += '91'

            elif splitline[0] == 'call':
                returnaddress = hex(len(rtn.split()) + 3).replace('0x', '') + ' '
                rtn += 'f0070 '
                rtn += returnaddress
                rtn += makehex(op = 'c0', msb = 'p:' + splitline[1]+'p;')
                
                
            elif splitline[0] == 'print' or splitline[0] == 'printl':
                for char in range(len(splitline[0])+1, len(line)):
                        rtn += hex(ord(line[char])).replace('0x', '') + '0074 '
                if splitline[0] == 'printl':
                    rtn += 'a0074 '
                    
            elif splitline[0] == 'channel':
                if splitline[1] == 'data':
                    rtn += hex(eval(splitline[2])).replace('0x', '') + '0075 '
                if splitline[1]== 'address':
                    if splitline[2] == 'increment':
                        rtn += '0077 '
                    elif splitline[2] == 'decrement':
                        rtn += '0078 '
                    else:
                        rtn += hex(eval(splitline[2])).replace('0x', '') + '0076 '

            elif splitline[0] == 'exec':
                if splitline[1]== 'ram':
                    if splitline[2].count('r') == 0:
                        rtn += makehex(op = '5b', msb = hex(eval(splitline[2])).replace('0x', ''))
                    else:
                        rtn += makehex(sra = splitline[2], op = '5d') + ' '
                elif splitline[1] == 'rom':
                    if splitline[2].count('r') == 0:
                        rtn += makehex(op = '5a', msb = hex(eval(splitline[2])).replace('0x', ''))
                    else:
                        rtn += makehex(sra = splitline[2], op = '5c') + ' '
                        
            elif splitline [0] == 'hex':
                line = line.replace('hex', '')

            elif splitline[0] == 'python':
                #pass
                exec (line[len(splitline[0]) + 1: len(line)])
                    
            else:
                print "**********************************"
                print "Lexical error in line " + str(wline) + ": " + line
                print "**********************************"
            wline += 1

        except IndexError:
            print "**********************************"
            print "Whiney Python IndexError in line " + str(wline) + ": " + line
            print "**********************************"

    return rtn, pointdic, vardic

def link(tup):
    source, pointdic, vardic = tup[0], tup[1], tup[2]
    prgmlen = len(source.split())
    print "linking addresses..."
    for address in pointdic.iterkeys():
        source = source.replace(address, str(pointdic[address]))

    for address in vardic.iterkeys():
        vardic[address] = hex(vardic[address] + prgmlen).replace('0x', '')
        source = source.replace(address, str(vardic[address]))
    return source

def signbit(n):
    n = eval(str(n))
    if n < 0:
        n = abs(n)
        n = bin(n).replace('0b', '')
        n = '0'*(32 - len(n)) + n
        n = n.replace('0', 't')
        n = n.replace('1', '0')
        n = n.replace('t', '1')
        n = '0b' + n
        n = eval(n) + 1
    return n
