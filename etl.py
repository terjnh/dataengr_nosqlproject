# Import Python packages 
import pandas as pd
import cassandra
import re
import os
import glob
import numpy as np
import json
import csv

## Creating list of filepaths to process original event csv data files
# checking your current working directory
print(os.getcwd())

# Get your current folder and subfolder event data
filepath = os.getcwd() + '/event_data'

# Create a for loop to create a list of files and collect each filepath
for root, dirs, files in os.walk(filepath):
    
# join the file path and roots with the subdirectories using glob
    file_path_list = glob.glob(os.path.join(root,'*'))
    #print(file_path_list)


## Processing the files to create the data file csv that will be used for Apache Casssandra tables
# initiating an empty list of rows that will be generated from each file
full_data_rows_list = [] 
    
# for every filepath in the file path list 
for f in file_path_list:

# reading csv file 
    with open(f, 'r', encoding = 'utf8', newline='') as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
        next(csvreader)
        
 # extracting each data row one by one and append it        
        for line in csvreader:
            #print(line)
            full_data_rows_list.append(line) 
            
# uncomment the code below if you would like to get total number of rows 
#print(len(full_data_rows_list))
# uncomment the code below if you would like to check to see what the list of event data rows will look like
#print(full_data_rows_list)

# creating a smaller event data csv file called event_datafile_full csv that will be used to insert data into the \
# Apache Cassandra tables
csv.register_dialect('myDialect', quoting=csv.QUOTE_ALL, skipinitialspace=True)

with open('event_datafile_new.csv', 'w', encoding = 'utf8', newline='') as f:
    writer = csv.writer(f, dialect='myDialect')
    writer.writerow(['artist','firstName','gender','itemInSession','lastName','length',\
                'level','location','sessionId','song','userId'])
    for row in full_data_rows_list:
        if (row[0] == ''):
            continue
        writer.writerow((row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[12], row[13], row[16]))


# check the number of rows in your csv file
with open('event_datafile_new.csv', 'r', encoding = 'utf8') as f:
    print(sum(1 for line in f))




"""
Part II. Complete the Apache Cassandra coding portion of your project
Now you are ready to work with the CSV file titled event_datafile_new.csv, located within the Workspace directory.
"""

# Creating a cluster
# This should make a connection to a Cassandra instance your local machine 
# (127.0.0.1)
from cassandra.cluster import Cluster
cluster = Cluster()

# To establish connection and begin executing queries, need a session
session = cluster.connect()


# TO-DO: Create a Keyspace
try:
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS udacity 
    WITH REPLICATION = 
    { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }"""
)
except Exception as e:
    print(e)


# TO-DO: Set KEYSPACE to the keyspace specified above
try:
    session.set_keyspace('udacity')
except Exception as e:
    print(e)


"""
Now we need to create tables to run the following queries. 
Remember, with Apache Cassandra you model the database tables on the queries you want to run.

Create queries to ask the following three questions of the data
1. Give me the artist, song title and song's length in the music app history that was heard during sessionId = 338, and itemInSession = 4
2. Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name) for userid = 10, sessionid = 182
3. Give me every user name (first and last) in my music app history who listened to the song 'All Hands Against His Own'
"""




## TO-DO: Query 1:  Give me the artist, song title and song's length in the music app history that was heard during \
## sessionId = 338, and itemInSession = 4
query = "CREATE TABLE IF NOT EXISTS song_library "
query = query + "(session_id int, item_in_session int, artist text, song_title text, length text, PRIMARY KEY (session_id, item_in_session))"
try:
    session.execute(query)
except Exception as e:
    print(e)

# We have provided part of the code to set up the CSV file. Please complete the Apache Cassandra code below#
file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
## TO-DO: Assign the INSERT statements into the `query` variable
        query = "INSERT INTO song_library (session_id, item_in_session, artist, song_title, length)"
        query = query + "VALUES (%s, %s, %s, %s, %s)"
        ## TO-DO: Assign which column element should be assigned for each column in the INSERT statement.
        ## For e.g., to INSERT artist_name and user first_name, you would change the code below to `line[0], line[1]`
        session.execute(query, (int(line[8]), int(line[3]), line[0], line[9], line[5]))

## TO-DO: Add in the SELECT statement to verify the data was entered into the table
### 1. Give me the artist, song title and song's length in the music app history that was heard during  sessionId = 338, and itemInSession  = 4
print("\nQuery 1: Provide artist, song title and song's length where sessionId=338 and itemInSession=4 ----->")
query = "select artist, song_title, length from song_library WHERE SESSION_ID=338 AND ITEM_IN_SESSION=4"
try:
    rows = session.execute(query)
except Exception as e:
    print(e)
    
for row in rows:
    print (row.artist, row.song_title, row.length)




### 2. Query 2: Give me only the following: name of artist, song (sorted by itemInSession) and user (first and last name)\
## for userid = 10, sessionid = 182
query = "CREATE TABLE IF NOT EXISTS table2 "
query = query + "(user_id int, session_id int, artist text, song_title text, first_name text, last_name text, item_in_session int, PRIMARY KEY (user_id, session_id, item_in_session))"
try:
    session.execute(query)
except Exception as e:
    print(e)

file = 'event_datafile_new.csv'

with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
        query = "INSERT INTO table2 (user_id, session_id, artist, song_title, first_name, last_name, item_in_session)"
        query = query + "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        session.execute(query, (int(line[10]), int(line[8]), line[0], line[9], line[1], line[4], int(line[3])))

print("\nQuery 2: Provide name of artist, song (sorted by itemInSession) and user (first and last name)\
 for userid = 10, sessionid = 182 ----->")
query = "SELECT *\
        FROM table2\
        WHERE user_id=10 AND session_id=182\
        ORDER BY session_id, item_in_session;"
try:
    rows = session.execute(query)
except Exception as e:
    print(e)
    
for row in rows:
    print (row.artist, row.song_title, row.first_name, row.last_name)




## TO-DO: Query 3: Give me every user name (first and last) in 
#                  my music app history who listened to the song 'All Hands Against His Own'
query = "CREATE TABLE IF NOT EXISTS user_table "
query = query + "(song_title text, first_name text, last_name text, PRIMARY KEY (song_title, first_name, last_name))"
try:
    session.execute(query)
except Exception as e:
    print(e)

file = 'event_datafile_new.csv'
with open(file, encoding = 'utf8') as f:
    csvreader = csv.reader(f)
    next(csvreader) # skip header
    for line in csvreader:
        query = "INSERT INTO user_table (song_title, first_name, last_name)"
        query = query + "VALUES (%s, %s, %s)"
        # if(line[9] == 'All Hands Against His Own'):
        #     print(line[1], line[4])
        session.execute(query, (line[9], line[1], line[4]))

print("\nQuery 3: Give me every user name (first and last) in my music app history who listened to the song 'All Hands Against His Own' ----->")
query = "SELECT first_name, last_name\
        FROM user_table\
        WHERE song_title='All Hands Against His Own'\
        ORDER BY first_name;"
try:
    rows = session.execute(query)
except Exception as e:
    print(e)
    
for row in rows:
    print (row.first_name, row.last_name)





### Drop tables
## TO-DO: Drop the table before closing out the sessions
query = "drop table song_library"
try:
    rows = session.execute(query)
except Exception as e:
    print(e)

query = "drop table table2"
try:
    rows = session.execute(query)
except Exception as e:
    print(e)

query = "drop table user_table"
try:
    rows = session.execute(query)
except Exception as e:
    print(e)  


session.shutdown()
cluster.shutdown()