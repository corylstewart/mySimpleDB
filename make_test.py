import random
import string

print 'SET a 10'
print 'SET b 20'
print 'SET c 30'
print 'BEGIN'
choices = ['SET ', 'GET ', 'UNSET ' 'SET ', 'SET ']
letter = ['a ', 'b ', 'c ']
number = ['10', '20', '30']
for i in xrange(100000):
    if i%100 == 0:
        print 'BEGIN'
    if i%100 == 50:
        print 'ROLLBACK'
    command = random.choice(choices)
    if i%30 == 0:
        command = ''.join(random.choice(string.lowercase) for x in range(5)) + ' '
    l = random.choice(letter)
    if command == 'SET ':
        n = random.choice(number)
    else:
        n = ''
    print command + l + n
print 'ROLLBACK'
print 'NUMEQUALTO 10'
print 'NUMEQUALTO 20'
print 'NUMEQUALTO 30'