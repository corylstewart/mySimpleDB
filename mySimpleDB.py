import sys


class MySimpleDB(object):
    '''
    Simple in memory Database.
    commands for database are as follows

    SET name value : Set the variable name to the value value. 
        Neither variable names nor values will contain spaces.

    GET name : Print out the value of the variable name, 
        or NULL if that variable is not set.

    UNSET name : Unset the variable name, making it just 
        like that variable was never set.

    NUMEQUALTO value : Print out the number of variables 
        that are currently set to value. If no variables 
        equal that value, print 0.

    END : Exit the program.
    '''

    def __init__(self):
        self.db_entries = dict() #hash table containing DB entrie
        self.item_counts = dict() #hash table containing counts of values
        self.sessions = list() #list of current active sessions
        #used to check x previous session entries for duplicates
        self.session_offset = 5 
        #list of valid commands the the appropriate methods for them
        self.valid_inputs = {'SET' : self._set,
                            'GET' : self._print_get,
                            'UNSET' : self._unset,
                            'NUMEQUALTO' : self._num_equal_to,
                            'BEGIN' : self._begin,
                            'ROLLBACK' : self._rollback,
                            'COMMIT' : self._commit
                            }

    def start_listener(self):
        '''
        Start stdin listener.  Process lines until
        EOF or "END" is entered.
        '''
        while True:
            curr_line = sys.stdin.readline().split()
            if curr_line in [[], ["END"]]: #check for break condition
                break
            if curr_line[0] in self.valid_inputs: #validate command
                self.valid_inputs[curr_line[0]](curr_line)

    def set_offset(self, new_offset):
        '''Change the session_offset to a new integer greater than 1'''
        if isinstance(new_offset, int) and new_offset > 1:
            self.session_offset = new_offset

    def get_offset(self):
        '''Return the session_offset'''
        return self.session_offset

    def _set(self, curr_line, add_to_session=True):
        '''Set key, value pair to the hash table.'''
        if len(curr_line) == 3: #confirm input is valid size
            key, value = curr_line[1], curr_line[2]
            #check to see if the command needs to be logged in a session
            if self._session_exists() and add_to_session:
                self._pass_command_to_session(curr_line)
            if self._key_exists(key): #if key exists unset key
                self._unset(curr_line[:2], False) #unset not logged in session
            self.db_entries[key] = value #place key, value pair in hash table
            self._increment_count(value) #increment value count

    def _print_get(self, curr_line):
        '''Use _get to get the value and print to stdout'''
        if len(curr_line) == 2: #confirm input is valid size
            print self._get(curr_line)

    def _get(self, curr_line):
        '''Return value of key or NULL if key did not exist'''
        return self.db_entries.get(curr_line[1], "NULL")

    def _unset(self, curr_line, add_to_session=True):
        '''Remove key, value pair from hash table and decrement count.'''
        #confirm input is valid size and exists
        if len(curr_line) == 2 and self._key_exists(curr_line[1]):
            key = curr_line[1]
            #check to see if the command needs to be logged in a session
            if self._session_exists() and add_to_session:
                self._pass_command_to_session(curr_line)          
            value = self._get(curr_line)
            del self.db_entries[key] #remove key from hash table
            self._decrement_count(value) #decrement value count

    def _num_equal_to(self, curr_line):
        '''Return value count or 0 if value not present'''
        print self.item_counts.get(curr_line[1], 0)

    def _begin(self, curr_line):
        '''Append a new SessionBlock object to the self.sessions list'''
        self.sessions.append(MySimpleDB.SessionBlock(self))

    def _rollback(self, curr_line):
        '''
        Rollback current session.  And remove session from session list
        Print "NO TRANSACTION" if no current session exists
        '''
        if self._session_exists():
            self.sessions[-1]._rollback(curr_line)
            self.sessions.pop()
        else:
            print "NO TRANSACTION"

    def _commit(self, curr_line):
        '''Commit all sessions to the database'''
        self.sessions = list()

    def _session_exists(self):
        '''Return True is a session is alive False if not''' 
        return len(self.sessions) > 0

    def _pass_command_to_session(self, curr_line):
        '''Pass command to current session for logging'''
        self.sessions[-1].parse_command(curr_line)

    def _key_exists(self, key):
        '''Return True if a key is in hash table False if not'''
        return key in self.db_entries

    def _increment_count(self, value):
        '''
        If value is not in item counts add it with and initial
        count of zero.  Then increment the total count by one
        '''
        if value not in self.item_counts:
            self.item_counts[value] = 0
        self.item_counts[value] += 1

    def _decrement_count(self, value):
        '''
        Decrement the count of a value by one.  Remove the value if
        the count of that value is zero
        '''
        if value in self.item_counts:
            self.item_counts[value] -= 1
            if self.item_counts <= 0:
                del self.item_counts[value]


    class SessionBlock(object):
        '''
        Create a log of the current session by reversing each command
        so that if a session needs to be rolled back.
        '''

        def __init__(self, dbObj):
            self.uncommit_log = list()
            self.dbObj = dbObj

        def parse_command(self, curr_line):
            command_dict = {"SET" : self._reverse_set,
                            "UNSET" : self._reverse_set,
                            "ROLLBACK" : self._rollback}
            command_dict[curr_line[0]](curr_line)

        def _reverse_set(self, curr_line):
            '''Create a reversal of SET and UNSET'''
            key = curr_line[1]
            old_value = self.dbObj._get(curr_line) #save old value
            #create new transaction reversing current transaction
            #keeping only key and value removing SET to save memory
            self.uncommit_log.append([key, old_value])
            #check recent entries to see if any are duplicates
            #if so pop that last command from list. adjust the [-x:-1]
            #value to tune it to the inputs.  
            #comment out next two lines if you do not want to remove duplicates
            if self.uncommit_log[-1] in self.uncommit_log[-self.dbObj.session_offset:-1]:
                self.uncommit_log.pop()

        def _rollback(self, curr_line):
            '''Roll back changes made during session'''
            #reverse log to set changes in corret order
            self.uncommit_log.reverse()
            key = ["SET"] #add SET back into the transaction
            for curr_line in self.uncommit_log:
                #reverse all of the transactions from the current session
                self.dbObj._set(key + curr_line, False)


if __name__ == "__main__":
    MySimpleDB().start_listener()