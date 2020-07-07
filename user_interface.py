
#THIS PROGRAM WAS WRITTEN WITH PYTHON 3.7

#Importing modules and setting the options for pandas that will allow user to see full results of a read
from sqlalchemy import create_engine, exc
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

#Prompting for username/password
username = input('Please input your username: ')
password = input('Please input your password: ')
dbName = input('Please input the name of the database you wish to interact with: ')

while True:
    try:
        #Sets the connection settings with the username & password
        settings = {
            'userName': username,
            'password': password,
            'serverName': "localhost",
            'portNumber': 3306,
            'dbName': dbName}
        db = create_engine('mysql://{0[userName]}:{0[password]}@{0[serverName]}:{0[portNumber]}/{0[dbName]}'.format(settings))
        #Attempts to connect to the database, and if successful create a list of all of the database's table names
        conn = db.connect()
        select_table_names = "SHOW TABLES"
        tables=[]
        for (name) in conn.execute(select_table_names):
            tables.append((name[0]).lower())
        print("\nSuccessfully connected to database\n")
        break
    #If there was an error in establishing the connection, the below statement prints, and prompts user to restart the program
    except exc.SQLAlchemyError:
        print("\nUnable to connect with the database. \nPlease retry your username/password and try again.")
        quit()
        break

#Creates a dictionary, where keys are integers, and values are the database's table names
table_dict = {}
count = 0
for tab in tables:
    table_dict[count] = tab
    count += 1

#Function to check if a value is a key within a dictionary
def dict_check(dict, key):
    boo = False
    try:
        key = int(key)
    except ValueError:
        return boo
    if key in dict.keys():
        boo = True
    return boo

#Given a datatype and a value, this function checks if the value fits into the datatype
def datatype_check(datatype, data):
    bool = False
    if datatype[:3] == 'int':
        try:
            data = int(data)
            bool = True
        except ValueError:
            pass
    elif datatype[:7] == 'decimal':
        if len(datatype) == 7:
            try:
                data = float(data)
                bool = True
            except ValueError:
                pass
        elif len(datatype) > 7:
            decimal_reqs = datatype[8:-1]
            first = decimal_reqs.split(',')[0]
            if len(data) + 1 == first:
                bool = True
    elif datatype[:7] == 'varchar':
        if type(data) == str:
            if len(data) <= int(datatype[8:-1]):
                bool = True
    elif datatype[:4] == 'date':
        try:
            if int(data[0:4]) < 2010 and int(data[0:4]) > 1900:
                if int(data[5:7]) < 13:
                    if int(data[8:]) < 32:
                        bool = True
        except ValueError:
            bool = False
    elif datatype[:4] == 'year':
        try:
            if len(data) == 4:
                int(data)
                bool = True
        except ValueError:
            bool = False
    elif datatype[:4] == 'enum':
        choices = datatype[4:].replace('(', '').replace(')', '').replace('\'', '').split(',')
        if data in choices:
            bool = True
    return bool

#This function creates a SQL select statement and executes it, returning the results as a DataFrame
def read_records(select_statement, table_s, condition):
    query = select_statement + table_s + condition
    df = pd.read_sql(query, con=conn)
    return df

#Function to create a conditional statement based on the chosen operator and the column
def create_condition(operator, col_name):
    #If BETWEEN is chosen, gets the high and low end of the statement
    if operator =='BETWEEN':
        while True:
            value1 = input('Please enter the low end of the between condition: ')
            try:
                low_end = int(value1)
                break
            except ValueError:
                print('\nPlease enter an integer.\n')
        while True:
            value2 = input('Please enter the high end of the between condition: ')
            try:
                high_end = int(value2)
                break
            except ValueError:
                print('\nPlease enter an integer.\n')
        cond = f'{col_name} {operator} {low_end} AND {high_end}'
        return cond
    else:
        if operator == '=' or operator == '<>':
            #Tries to use an integer first, but if it doesnt work, uses a string
            value = input('Which value would you like to base the condition on? ')
            try:
                int(value)
                cond = f'{col_name} {operator} {value}'
            except ValueError:
                cond = f'{col_name} {operator} \'{value}\''
            return cond
        else:
            while True:
                #Since the rest of operators only apply to integers, it attempts to
                #convert value to int, and if it doesnt work, prompts the user to retry
                value = input('Which value would you like to base the condition on? ')
                try:
                    con_value = int(value)
                    break
                except ValueError:
                    print('\nPlease enter an integer.\n')
            cond = f'{col_name} {operator} {con_value}'
            return cond

#List of operators for conditional statements
operators = ['=', '>', '<', '>=', '<=', '<>', 'BETWEEN']

list_of_ops = ("""
1: Read data from one table
2: Read data from two or more tables
3: Insert data into a table
4: Update data in a table
5: Delete data from a table
""")

#Prompts the user to enter the corresponding number for the desired operation, and re-prompts them until their entry is valid
while True:
    try:
        print(list_of_ops)
        input_operation = input('Please choose an operation from the above list by entering its number: ')
        if int(input_operation) in range(1, 6):
            break
        else:
            raise ValueError
    except ValueError:
        print("\nThat choice is invalid, please try again.\n")
        continue

#READ SINGLE TABLE
if input_operation == '1':
    #Prompts the user to enter the corresponding number for the desired table, and re-prompts them until their entry is valid
    while True:
        print('\nWhich table\'s records do you wish to read? Enter the corresponding number. \n')
        for key, value in table_dict.items():
            print(f'{key}: {value}\n')
        table_key = input('Please enter the corresponding number: ')
        if dict_check(table_dict, table_key):
            table_key = int(table_key)
            break
        else:
            print('\n\nThat is not a valid entry, please try again.')
            continue
    table_of_records = table_dict[table_key] #Uses the inputted number as a key to retrieve the table name
    table_s = f' FROM {table_of_records}' #Creates the FROM part of the statement
    #Asks the user if they want to select all columns or just some, repeating until the input is valid
    all_or_some = input('\nWould you like to view all of the table\'s columns?\nEnter \'yes\'/\'no\': ').lower()
    while True:
     if all_or_some == 'yes' or all_or_some == 'no':
         break
     else:
         all_or_some = input('\nPlease enter \'yes\' or \'no\': ').lower()
    if all_or_some == 'yes':
        select = 'SELECT *' #Creates the SELECT part of the statement if the user wishes to see all columns
    elif all_or_some == 'no':
        #Collects the names of the columns in the table, and creates a dictionary, with the names as values and ascending integers as keys
        col_list = [column[0] for column in conn.execute('SHOW COLUMNS FROM ' + table_of_records)]
        col_dict = {}
        count = 1
        for col in col_list:
            col_dict[count] = col
            count += 1
        while True:
            #Asks the user to input the comma-separated numbers(dictionary keys) of the columns they would like to use.
            #It checks each value, and if any of them are invalid, it prompts the user to re-enter the list
            print('\nWhich columns do you wish to view?\n')
            #Prints the dictionary in a easy-to-read form so the user can choose their columns
            for key, value in col_dict.items():
                print(f'{key}: {value}\n')
            col_input = input('Please enter the corresponding numbers, separated by a comma: ')
            #Splits the inputted list and removes any trailing whitespace
            col_input_split = [col.strip() for col in col_input.split(',')]
            count = 0
            try:
                #For each column key, calls the dict_check function to make sure that it is indeed a valid key for the col_dict,
                #and if not, restarts the while loop to prompt the user to re-enter the column values
                for col in col_input_split:
                    if dict_check(col_dict, col):
                        count += 1
                    else:
                        raise ValueError
            except ValueError:
                print('\n\nSome or all of those values were invalid, please try again.')
            #Stops the loop once each column has been validated
            if count == len(col_input_split):
                break
        #Once the input has been validated, we use the numbers as dictionary keys
        col_names = [col_dict[int(colu)] for colu in col_input_split]
        #Creates the SELECT part of the statement, joining each column name with a column (e.g. SELECT x, y, z)
        select = 'SELECT ' + ', '.join(col_names)
    #Asks user if they wish to retrieve all records or filter them, and re-prompts the user if their entry was invalid
    condition_yes_no = input('\nWould you like to retrieve all records or filter based on conditions?\nEnter \'all\' or \'filter\': ').lower()
    while True:
        if condition_yes_no == 'all' or condition_yes_no == 'filter':
            break
        else:
            condition_yes_no = input('\nPlease enter \'all\' or \'filter\': ').lower()
    #If the user did not wish to apply a condition, the conditon will be added to the statement as a blank
    condition = ''
    where = ' WHERE '
    if condition_yes_no == 'filter':
        #If the user would like their result to be filtered, the program prompts the user to enter the number of
        #different conditions they would like to apply, and keeps asking until a valid integer is entered
        while True:
            num_con = input('Please enter the number of different condtions you wish to apply: ')
            try:
                num_con = int(num_con)
                break
            except ValueError:
                print('\nPlease enter an integer.\n')
        condition = ''
        #Collects the names of the columns in the table, and creates a dictionary, with the names as values and ascending integers as keys
        col_list = [column[0] for column in conn.execute('SHOW COLUMNS FROM ' + table_of_records)]
        col_dict = {}
        count = 1
        for col in col_list:
            col_dict[count] = col
            count += 1
        for n in range(1, num_con +1):
            while True:
                #Prints the dictionary in a easy-to-read form so the user can choose their columns
                for key, value in col_dict.items():
                    print(f'\n{key}: {value}')
                #Prompts the user to enter the number of their desired column, then validates it with the dict_check function
                #If input is invalid, the user will have to try again
                condition_col = input('\nEnter the number of the above column you would like to base the condition on: ')
                try:
                    if dict_check(col_dict, condition_col):
                        condition_col = int(condition_col)
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print('\n\nThat input is invalid, please choose one of the columns from the list.\n')
            #Prints the list of operators and asks the user to enter their desired operator, the input is then validated
            #If the inputted operation is not in the list of operators, the user has to try again
            print(operators)
            while True:
                operator = input('Which operator would you like to use for this condition? Please enter it now: ')
                try:
                    if operator in operators:
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print('\n')
                    print(operators)
                    print('\nThat input is invalid, please choose one of the operators from the above list.')
            #Retrieves the mySQL datatype for the chosen column, and prints it for the user to see what to enter
            for column, datatype, null, key, default, extra in conn.execute('SHOW COLUMNS FROM ' + table_of_records):
                if column == col_dict[condition_col]:
                    dtype = datatype
            print('\nThe correct datatype for that column is ' + dtype)
            #Calls the create_condition function to create the string to be used in the condional statement.
            #Datatype validation takes place within the function
            condition_var = create_condition(operator, col_dict[condition_col])
            #If it's the first part of the conditional, we concatenate it to the where string
            if n == 1:
                condition = where + condition_var
            #If not the first part, we show what the condtional currently looks likes, then ask the user whether
            #they would like the newest part to be introduced by 'and' or 'or'
            #This part is then added to the ongoing condition string
            else:
                print('The conditional statement is currently composed as such:')
                print(condition)
                and_or = input('Would you like this newest part of the conditional statement to be preceded by \'or\' or \'and\'? ').lower()
                while True:
                    if and_or == 'or' or and_or == 'and':
                        break
                    and_or = input('Please enter \'or\' or \'and\': ')
                condition += ' ' + and_or + ' ' + condition_var
    #Attempts to call the read_records function to view the results of the select, if there is
    #an error, we print the error and prompt the user to start over
    try:
        print(read_records(select, table_s, condition))
    except exc.SQLAlchemyError as e:
        print('\n' + e.orig.args[1])
        print('\nPlease retry, making sure your inputs are correct.\n')

#READ JOINED TABLES
elif input_operation == '2':
    #Prompts the user to enter the number of tables they want in the join, and re-prompts them until their entry is valid
    while True:
        num_tables = input('\nPlease enter the number of tables you would like to read data from: ')
        try:
            num_tables = int(num_tables)
            if num_tables < 2:
                print('\nYou must enter more than 1 table in order to read data from a join.\n')
                continue
            if num_tables > len(tables):
                print('\nThat number is larger than the amount of tables in the database.\nThere are only {len(tables)} in the database. Please try again.\n')
                continue
            break
        except ValueError:
            print('\nPlease enter an integer.\n')
    for n in range(1, num_tables + 1):
        #For the first table, we join it with another to create join #1
        if n == 1:
            #Prompts the user to enter the corresponding number of the first table in the
            #join, and will re-prompt if the given number is invalid
            while True:
                #Print the table names in an easy-to-read format for the user
                for key, value in table_dict.items():
                    print(f'\n{key}: {value}')
                #Receives the number for the first table. If valid, the name of the table is
                #retrieved from the dictionary and stored as table_1
                table_1_key = input('\nPlease enter the number for the first table in the join: ')
                if dict_check(table_dict, table_1_key):
                    table_1_key = int(table_1_key)
                    table_1 = table_dict[table_1_key]
                    #Once a table is part of the join, we want to remove it from the list of possible
                    #choices since there's no point to joining a table with itself, so we delete that
                    #table from the dictionary
                    del table_dict[table_1_key]
                    break
                else:
                    print('\n\nThat is not a valid entry, please try again.')
                    continue
            while True:
                #Print the table names in an easy-to-read format for the user
                for key, value in table_dict.items():
                    print(f'{key}: {value}\n')
                #Receives the number for the second table. If valid, the name of the table is
                #retrieved from the dictionary and stored as table_2
                table_2_key = input('\nPlease enter the number for the second table in the join: ')
                if dict_check(table_dict, table_2_key):
                    table_2_key = int(table_2_key)
                    table_2 = table_dict[table_2_key]
                    #Once a table is part of the join, we want to remove it from the list of possible
                    #choices since there's no point to joining a table with itself, so we delete that
                    #table from the dictionary
                    del table_dict[table_2_key]
                    break
                else:
                    print('\n\nThat is not a valid entry, please try again.')
                    continue
            #We concatenate the two tables with a double underscore in the middle as the name for the joined table
            table_name = table_1 + '__' + table_2
            #We call a stored procedure that performs a natural join and creates a temporary table in the database
            join_statement = f'CALL jointables(\'{table_name}\', \'{table_1}\', \'{table_2}\');'
            #We execute the join and store the joins name as prev_tab for use if there are more tables to be joined
            conn.execute(join_statement)
            prev_tab = table_name
        #Since we already did table 2 in the first join, we skip n = 2
        elif n > 2:
            #For every table after the first two, we are joining a new table to the result of
            #the previous join, which is why the previous join's table name is saved as prev_tab
            #Prev_tab is now stored as table_1 so that we can keep the same code of formaing the
            #statement to call the stored procedure
            table_1 = prev_tab
            while True:
                #Print the table names in an easy-to-read format for the user
                for key, value in table_dict.items():
                    print(f'{key}: {value}\n')
                #Receives the number for the second table in this join. If valid, the name of the table is
                #retrieved from the dictionary and stored as table_2
                table_2_key = input(f'\nPlease enter the number for table {n} in the join: ')
                if dict_check(table_dict, table_2_key):
                    table_2_key = int(table_2_key)
                    table_2 = table_dict[table_2_key]
                    #Once a table is part of the join, we want to remove it from the list of possible
                    #choices since there's no point to joining a table with itself, so we delete that
                    #table from the dictionary
                    del table_dict[table_2_key]
                    break
                else:
                    print('\n\nThat is not a valid entry, please try again.')
                    continue
            #We concatenate the two tables with a double underscore in the middle as the name for the joined table
            table_name = table_1 + '__' + table_2
            #We call a stored procedure that performs a natural join and creates a temporary table in the database
            join_statement = f'CALL jointables(\'{table_name}\', \'{table_1}\', \'{table_2}\');'
            #We execute the join and store the joins name as prev_tab for use if there are more tables to be joined
            conn.execute(join_statement)
            prev_tab = table_name
    table_s = f' FROM {table_name}' #Creates the FROM part of the statement
    #Asks the user if they want to select all columns or just some, repeating until the input is valid
    all_or_some = input('\nWould you like to view all of the table\'s columns?\nEnter \'yes\'/\'no\': ').lower()
    while True:
        if all_or_some == 'yes' or all_or_some == 'no':
            break
        else:
            all_or_some = input('\nPlease enter \'yes\' or \'no\': ').lower()
    if all_or_some == 'yes':
        select = 'SELECT *'
    elif all_or_some == 'no':
        #Collects the names of the columns in the table, and creates a dictionary, with the names as values and ascending integers as keys
        col_list = [column[0] for column in conn.execute('SHOW COLUMNS FROM ' + table_name)]
        col_dict = {}
        count = 1
        for col in col_list:
            col_dict[count] = col
            count += 1
        while True:
            #Asks the user to input the comma-separated numbers(dictionary keys) of the columns they would like to use.
            #It checks each value, and if any of them are invalid, it prompts the user to re-enter the list
            print('\nWhich columns do you wish to view?\n')
            #Prints the dictionary in a easy-to-read form so the user can choose their columns
            for key, value in col_dict.items():
                print(f'{key}: {value}\n')
            col_input = input('Please enter the corresponding numbers, separated by a comma: ')
            #Splits the inputted list and removes any trailing whitespace
            col_input_split = [col.strip() for col in col_input.split(',')]
            count = 0
            try:
                #For each column key, calls the dict_check function to make sure that it is indeed a valid key for the col_dict,
                #and if not, restarts the while loop to prompt the user to re-enter the column values
                for col in col_input_split:
                    if dict_check(col_dict, col):
                        count += 1
                    else:
                        raise ValueError
            except ValueError:
                print('\n\nSome or all of those values were invalid, please try again.')
            #Stops the loop once each column has been validated
            if count == len(col_input_split):
                break
        #Once the input has been validated, we use the numbers as dictionary keys
        col_names = [col_dict[int(colu)] for colu in col_input_split]
        #Creates the SELECT part of the statement, joining each column name with a column (e.g. SELECT x, y, z)
        select = 'SELECT ' + ', '.join(col_names)
    #Asks user if they wish to retrieve all records or filter them, and re-prompts the user if their entry was invalid
    condition_yes_no = input('\nWould you like to retrieve all records or filter based on conditions?\nEnter \'all\' or \'filter\': ').lower()
    while True:
        if condition_yes_no == 'all' or condition_yes_no == 'filter':
            break
        else:
            condition_yes_no = input('\nPlease enter \'all\' or \'filter\': ').lower()
    #If the user did not wish to apply a condition, the conditon will be added to the statement as a blank
    condition = ''
    where = ' WHERE '
    if condition_yes_no == 'filter':
        #If the user would like their result to be filtered, the program prompts the user to enter the number of
        #different conditions they would like to apply, and keeps asking until a valid integer is entered
        while True:
            num_con = input('Please enter the number of different condtions you wish to apply: ')
            try:
                num_con = int(num_con)
                break
            except ValueError:
                print('\nPlease enter an integer.\n')
        condition = ''
        #Collects the names of the columns in the table, and creates a dictionary, with the names as values and ascending integers as keys
        col_list = [column[0] for column in conn.execute('SHOW COLUMNS FROM ' + table_name)]
        col_dict = {}
        count = 1
        for col in col_list:
            col_dict[count] = col
            count += 1
        for n in range(1, num_con +1):
            while True:
                #Prints the dictionary in a easy-to-read form so the user can choose their columns
                for key, value in col_dict.items():
                    print(f'\n{key}: {value}')
                #Prompts the user to enter the number of their desired column, then validates it with the dict_check function
                #If input is invalid, the user will have to try again
                condition_col = input('\nEnter the number of the above column you would like to base the condition on: ')
                try:
                    if dict_check(col_dict, condition_col):
                        condition_col = int(condition_col)
                        break
                except ValueError:
                    print('\n\nThat input is invalid, please choose one of the columns from the list.\n')
            #Prints the list of operators and asks the user to enter their desired operator, the input is then validated
            #If the inputted operation is not in the list of operators, the user has to try again
            print(operators)
            while True:
                operator = input('Which operator would you like to use for this condition? Please enter it now: ')
                try:
                    if operator in operators:
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print('\n')
                    print(operators)
                    print('\nThat input is invalid, please choose one of the operators from the above list.')
            #Retrieves the mySQL datatype for the chosen column, and prints it for the user to see what to enter
            for column, datatype, null, key, default, extra in conn.execute('SHOW COLUMNS FROM ' + table_name):
                if column == col_dict[condition_col]:
                    dtype = datatype
            print('\nThe correct datatype for that column is ' + dtype)
            #Calls the create_condition function to create the string to be used in the condional statement.
            #Datatype validation takes place within the function
            condition_var = create_condition(operator, col_dict[condition_col])
            #If it's the first part of the conditional, we concatenate it to the where string
            if n == 1:
                condition = where + condition_var
            #If not the first part, we show what the condtional currently looks likes, then ask the user whether
            #they would like the newest part to be introduced by 'and' or 'or'
            #This part is then added to the ongoing condition string
            else:
                print('The conditional statement is currently composed as such:')
                print(condition)
                and_or = input('Would you like this newest part of the conditional statement to be preceded by \'or\' or \'and\'? ').lower()
                while True:
                    if and_or == 'or' or and_or == 'and':
                        break
                    and_or = input('Please enter \'or\' or \'and\': ')
                condition += ' ' + and_or + ' ' + condition_var
    #Attempts to call the read_records function to view the results of the select, if there is
    #an error, we print the error and prompt the user to start over
    try:
        print(pd.read_sql_query(f'{select}{table_s}{condition}', con=conn))
    except exc.SQLAlchemyError as e:
        print('\n' + e.orig.args[1])
        print('\nPlease retry, making sure your inputs are correct.\n')

#INSERT RECORDS INTO TABLE
elif input_operation == '3':
    #Prompts the user to enter the corresponding number for the desired table, and re-prompts them until their entry is valid
    while True:
        print('\nWhich table do you wish to insert records into? Enter the corresponding number. \n')
        for key, value in table_dict.items():
            print(f'{key}: {value}\n')
        table_key = input('Please enter the corresponding number: ')
        if dict_check(table_dict, table_key):
            table_key = int(table_key)
            break
        else:
            print('\n\nThat is not a valid entry, please try again.')
            continue
    table_of_records = table_dict[table_key] #Uses the inputted number as a key to retrieve the table name
    #Prompts the user to enter the number of records they will be inserting, and re-prompts them until their entry is valid
    while True:
        input_records_num = input('\nPlease enter the number of records you are creating: ')
        try:
            records_num = int(input_records_num)
            break
        except ValueError:
            print('\nPlease enter an integer.\n')
    for n in range(1, records_num+1): #'For each record that will be inserted'
        while True:
            try:
                #Retrieves and stores the result of SHOW COLUMNS, then creates an empty dictionary will hold each record
                columns = conn.execute('SHOW COLUMNS FROM ' + table_of_records)
                data = {}
                #Print the number of the record the user is currently writing
                if records_num > 1:
                    print(f'\nCreating record {n}: ')
                for column, datatype, null, key, default, extra in columns:
                    #Shows the user what the correct datatype is for
                    print(f'\nThe accepted datatype for {column} is {datatype}.\n')
                    #Gets user input for the new value for each column
                    data[column] = input(f"Please input value for {column}: ")
                    while True:
                        try:
                            #Calls the datatype_check function to validate that the new value matches the column's datatype
                            #If it does not match, the user will have to redo that column's new value
                            boo = datatype_check(datatype, data[column])
                            if boo == False:
                                raise ValueError
                            else:
                                break
                        except ValueError:
                            print(f'\nThat value is invalid, please try again.\nThe accepted datatype for {column} is {datatype}.\n')
                            data[column] = input(f"Please input value for {column}: ")
                #Creates the insert statement, uses the keys of the dataframe 'data' as the table's column names, and the values
                #as the values to be inserted
                insert_string = 'INSERT INTO {} ({}) VALUES {}'.format(table_of_records, ', '.join(data.keys()), tuple(data.values()))
                #Executes the insert statement. If there was an error executing the insert, the error will print
                #and the user will be prompted to retry inserting that particular record which caused the fail
                conn.execute(insert_string)
                print('\nRow added.')
                break
            except exc.SQLAlchemyError as e:
                print('\n' + e.orig.args[1])
                print('\nPlease re-enter your data.\n')

#UPDATE RECORDS IN A TABLE
elif input_operation == '4':
    #Prompts the user to enter the corresponding number for the desired table, and re-prompts them until their entry is valid
    while True:
        print('\nWhich table\'s records do you wish to update? Enter the corresponding number. \n')
        for key, value in table_dict.items():
            print(f'{key}: {value}\n')
        table_key = input('Please enter the corresponding number: ')
        if dict_check(table_dict, table_key):
            table_key = int(table_key)
            break
        else:
            print('\n\nThat is not a valid entry, please try again.')
            continue
    table_of_records = table_dict[table_key] #Uses the inputted number as a key to retrieve the table name
    #Collects the names of the columns in the table, and creates a dictionary, with the names as values and ascending integers as keys
    col_list = [column[0] for column in conn.execute('SHOW COLUMNS FROM ' + table_of_records)]
    col_dict = {}
    c_count = 1
    for col in col_list:
        col_dict[c_count] = col
        c_count += 1
    while True:
        #Asks the user to input the comma-separated numbers(dictionary keys) of the columns they would like to use.
        #It checks each value, and if any of them are invalid, it prompts the user to re-enter the list
        print('\nWhich columns do you wish to update?\n')
        #Prints the dictionary in a easy-to-read form so the user can choose their columns
        for key, value in col_dict.items():
            print(f'{key}: {value}\n')
        col_input = input('Please enter the corresponding numbers, separated by a comma: ')
        #Splits the inputted list and removes any trailing whitespace
        col_input_split = [col.strip() for col in col_input.split(',')]
        count = 0
        try:
            #For each column key, calls the dict_check function to make sure that it is indeed a valid key for the col_dict,
            #and if not, restarts the while loop to prompt the user to re-enter the column values
            for col in col_input_split:
                if dict_check(col_dict, col):
                    count += 1
                    col = int(col)
                else:
                    raise ValueError
        except ValueError:
            print('\n\nSome or all of those values were invalid, please try again.')
        #Stops the loop once each column has been validated
        if count == len(col_input_split):
            break
    col_names = [col_dict[int(colu)] for colu in col_input_split]
    data_list = [column[1] for column in conn.execute('SHOW COLUMNS FROM ' + table_of_records)]
    update_st = 'UPDATE ' + table_of_records
    set_str = ' SET '
    #Goes through each of the columns selected by the user
    for colum in col_names:
        #Goes through each of the columns in the table
        for column, datatype, null, key, default, extra in conn.execute('SHOW COLUMNS FROM ' + table_of_records):
            #Finds and prints the correct datatype for the column so that the user knows what type will be accepted
            if colum == column:
                print(f'\nThe correct datatype for {colum} is {datatype}')
                while True:
                    try:
                        #Receives and validates an input from the user until the value is found to be valid
                        new_value = input(f'Please input the new value for {colum}: ')
                        stri = ''
                        #If the new value matches the column's datatype, we then create a different string for the update string based on the datatype
                            #e.g. integers would just be numbers (4) while VARCHAR would be a string ('baseball')
                        if datatype_check(datatype, new_value):
                            if datatype[0:3] =='int' or datatype[:7] == 'decimal':
                                new_value = str(new_value)
                                stri += f'{colum} = {new_value}'
                            else:
                                stri += f'{colum} = \'{new_value}\''
                            if count + 1 == len(col_input_split):
                                stri += ' '
                            else:
                                stri +=', '
                            count += 1
                            set_str += stri
                            break
                        else:
                            raise ValueError
                    except ValueError:
                        print(f'\nThat value is invalid, the correct datatype for {col} is {datatype}.\nPlease try again. ')
                        continue
    #Removing extra whitespace from the end of the string
    set_str = set_str[:-2]
    #For delete, users have to input at least one condition
    condition = ''
    where = ' WHERE '
    while True:
        #The program prompts the user to enter the number of different conditions they would
        #like to apply, and keeps asking until a valid integer is entered
        num_con = input('Please enter the number of different condtions you wish to apply: ')
        try:
            num_con = int(num_con)
            break
        except ValueError:
            print('\nPlease enter an integer.\n')
    for n in range(1, num_con +1):
        while True:
            #Prints the dictionary in a easy-to-read form so the user can choose their column
            for key, value in col_dict.items():
                print(f'\n{key}: {value}')
            #Prompts the user to enter the number of their desired column, then validates it with the dict_check function
            #If input is invalid, the user will have to try again
            condition_col = input('\nEnter the number of the above column you would like to base the condition on: ')
            try:
                if dict_check(col_dict, condition_col):
                    condition_col = int(condition_col)
                    break
                else:
                    raise ValueError
            except ValueError:
                print('\n\nThat input is invalid, please choose one of the columns from the list.\n')
        #Prints the list of operators and asks the user to enter their desired operator, the input is then validated
        #If the inputted operation is not in the list of operators, the user has to try again
        print(operators)
        while True:
            operator = input('Which operator would you like to use for this condition? Please enter it now: ')
            try:
                if operator in operators:
                    break
                else:
                    raise ValueError
            except ValueError:
                print('\n')
                print(operators)
                print('\nThat input is invalid, please choose one of the operators from the above list.')
        #Retrieves the mySQL datatype for the chosen column, and prints it for the user to see what to enter
        for column, datatype, null, key, default, extra in conn.execute('SHOW COLUMNS FROM ' + table_of_records):
            if column == col_dict[condition_col]:
                dtype = datatype
        print('\nThe correct datatype for that column is ' + dtype)
        #Calls the create_condition function to create the string to be used in the condional statement.
        #Datatype validation takes place within the function
        condition_var = create_condition(operator, col_dict[condition_col])
        #If it's the first part of the conditional, the condtion is set equal to this first part
        if n == 1:
            condition = condition_var
        else:
            #If not the first part, we show what the condtional currently looks likes, then ask the user whether
            #they would like the newest part to be introduced by 'and' or 'or'
            #This part is then added to the ongoing condition string
            print('The conditional statement is currently composed as such:')
            print(condition)
            and_or = input('Would you like this newest part of the conditional statement to be preceded by \'or\' or \'and\'? ').lower()
            while True:
                if and_or == 'or' or and_or == 'and':
                    break
                and_or = input('Please enter \'or\' or \'and\': ')
            condition += ' ' + and_or + ' ' + condition_var
    #Creates the update string by concatenating the update, set, and condition strings
    update_string = update_st + set_str + where + condition
    #Attempts to execute the update, if it fails, we print the error and ask the user to retry
    try:
        conn.execute(update_string)
        print('\nThe indicated rows have been updated')
    except exc.SQLAlchemyError as e:
        print('\n' + e.orig.args[1])
        print('\nPlease retry, making sure your inputs are correct.\n')

#DELETE RECORDS FROM A TABLE
elif input_operation == '5':
    #Prompts the user to enter the corresponding number for the desired table, and re-prompts them until their entry is valid
    while True:
        print('\nWhich table\'s records do you wish to delete? Enter the corresponding number. \n')
        for key, value in table_dict.items():
            print(f'{key}: {value}\n')
        table_key = input('Please enter the corresponding number: ')
        if dict_check(table_dict, table_key):
            table_key = int(table_key)
            break
        else:
            print('\n\nThat is not a valid entry, please try again.')
            continue
    table_of_records = table_dict[table_key] #Uses the inputted number as a key to retrieve the table name
    #Collects the names of the columns in the table, and creates a dictionary, with the names as values and ascending integers as keys
    col_list = [column[0] for column in conn.execute('SHOW COLUMNS FROM ' + table_of_records)]
    col_dict = {}
    c_count = 1
    for col in col_list:
        col_dict[c_count] = col
        c_count += 1
    delete_statement = f'DELETE FROM {table_of_records} '
    condition = ''
    #For delete, users have to input at least one condition
    while True:
        #The program prompts the user to enter the number of different conditions they would
        #like to apply, and keeps asking until a valid integer is entered
        num_con = input('Please enter the number of different condtions you wish to apply: ')
        try:
            num_con = int(num_con)
            break
        except ValueError:
            print('\nPlease enter an integer.\n')
    condition = ''
    for n in range(1, num_con +1):
        while True:
            #Prints the dictionary in a easy-to-read form so the user can choose their column
            for key, value in col_dict.items():
                print(f'\n{key}: {value}')
            #Prompts the user to enter the number of their desired column, then validates it with the dict_check function
            #If input is invalid, the user will have to try again
            condition_col = input('\nEnter the number of the above column you would like to base the condition on: ')
            try:
                if dict_check(col_dict, condition_col):
                    condition_col = int(condition_col)
                    break
                else:
                    raise ValueError
            except ValueError:
                print('\n\nThat input is invalid, please choose one of the columns from the list.\n')
        #Prints the list of operators and asks the user to enter their desired operator, the input is then validated
        #If the inputted operation is not in the list of operators, the user has to try again
        print(operators)
        while True:
            operator = input('Which operator would you like to use for this condition? Please enter it now: ')
            try:
                if operator in operators:
                    break
                else:
                    raise ValueError
            except ValueError:
                print('\n')
                print(operators)
                print('\nThat input is invalid, please choose one of the operators from the above list.')
        #Retrieves the mySQL datatype for the chosen column, and prints it for the user to see what to enter
        for column, datatype, null, key, default, extra in conn.execute('SHOW COLUMNS FROM ' + table_of_records):
            if column == col_dict[condition_col]:
                dtype = datatype
        print('\nThe correct datatype for that column is ' + dtype)
        #Calls the create_condition function to create the string to be used in the condional statement.
        #Datatype validation takes place within the function
        condition_var = create_condition(operator, col_dict[condition_col])
        #If it's the first part of the conditional, the condtion is set equal to this first part
        if n == 1:
            condition = condition_var
        #If not the first part, we show what the condtional currently looks likes, then ask the user whether
        #they would like the newest part to be introduced by 'and' or 'or'
        #This part is then added to the ongoing condition string
        else:
            print('The conditional statement is currently composed as such:')
            print(condition)
            and_or = input('Would you like this newest part of the conditional statement to be preceded by \'or\' or \'and\'? ').lower()
            while True:
                if and_or == 'or' or and_or == 'and':
                    break
                and_or = input('Please enter \'or\' or \'and\': ')
            condition += ' ' + and_or + ' ' + condition_var
        #Creates the update string by concatenating the delete, where, and condition strings
        delete_string = delete_statement + ' WHERE ' + condition
        #Attempts to execute the delete, if there is an error, we print the error and prompt the user to start over
        try:
            conn.execute(delete_string)
            print('\nThe indicated rows have been deleted')
        except exc.SQLAlchemyError as e:
            print('\n' + e.orig.args[1])
            print('\nPlease retry, making sure your inputs are correct.\n')

#Closes out the database connection
conn.close()
db.dispose()
print("\nConnection to database closed")
