#! /usr/bin/python

try:
    import parse
except:
    print "bad parse module"
    exit()

def asm():
    adr = 0
    sloc, dloc = raw_input('source: '), raw_input('output: ')
    source = open(sloc).read()
    while source.count('include') > 0:
        source = parse.include (source)
    source = parse.pushcalls (source)
    source = parse.findvars (source)
    source = parse.assem (source)
    source = parse.link (source)
    for i in source.split():
        if i.count(';') > 0:
            print '*********************************************'
            print 'Link Error: ' + i + ' in address ' + hex(adr)
            print '*********************************************'
        adr += 1
    
    open(dloc, 'w').write(('v2.0 raw\n' + source))
    
    return source

def help():
    print """
point *pointname*            - declare a point
var *varname*                - declare a variable
include *file*.mds           - include a remote file (subroutine)
print *text*                 - print a string of chars
printl *text*                - print with a new line
# *comments*                 - write comments
mov r* r*                    - move data between registers
call *pointname*(*, ...)     - call a specific subroutine
return                       - return to main function after subroutine
put r*, *value*              - place a 32 bit literal value in a register
output r*                    - output the contents of a register
out32 *value*                - output a 32 bit literal value (bigger)
out16 *value*                - output a 16 bit literal value (faster)
alu op r* r* r*              - do math on to src regs and place into dst reg
jump *pointname* 	     - jump to a point in the program
     equals r* r* *point*    - if ra and ra are equal
     lesser  ...
     greater ...
     notequals ...
ram write r* *var|indirect   - write the value of src reg to ram with a var or indirectly
    read r* *var|indirect)   - read the value of ram to dst reg, var or indirectly
mar increment                - increment the memory location
    decrement                - decrement the meory location
reset                        - perform a hardware reset
halt                         - halt the program

operators: +, -, *, /, <<, >>, and, or, xor, not, random, mask, select

all operations are in prefix notation:

alu + r*A r*B r*C is r*A + r*B = r*C
"""
print "type help() for information, or asm() to run Zanita ASM"
try:
    asm()
except IOError:
    pass


while 1:
    try:
        keyword = raw_input('zan: ')
        if keyword == 'exit()':
            break
        exec (keyword)
    except TypeError:
        print 'Invalid command. Try help(), asm(), or exit()'
exit()
