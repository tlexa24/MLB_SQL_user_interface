# Introduction
As a final project in my Database Design course in the Fall of 2019, I was tasked with creating an SQL database, retrieving data to be stored in the database, and finally creating an interface allowing users to create and exectute SQL queries.

# Data Retrieval
I decided to base this project around Major League Baseball. Not only am I a fan of the sport, but there is also an incredible amount of statistics to be found in the sport, making this the ideal choice for a database. In order to retrieve this data, I decided to scrape both baseball-reference.com and wikipedia.com. I utilized the beautifulsoup library for the scraping, and once all data was retrieved, I catalogued the data with unique identifiers so that the data would work within a SQL database and could be easily retrieved. The scraper I built will retrieve team info, stadium info, league/division info, player personal info, and statistics for both pitchers and batters over the years indicated by the user.

# Backend
The backend is a relational database created within MySQLWorkbench. All of the unique identifiers created during the scraping phase are used as primary keys, and each table has a foreign key pointing to at least one other table. Once the scheme was created, the data was imported from csv.

# User Interface
My goal for the interface was to allow those with little SQL experience to create and execute queries through a series of questions posed to them through their command line. The interface enables all four of the CRUD (Create, Read, Update, Delete) operations. A secondary goal was to create a interface that would work with any SQL database, and to an extent this was accomplished (see Future Improvements for more detail).

Every step of the way, the user will be prompted with a question and given either a list or format that is acceptable (ex. the program may give a list of options and prompt the user to enter the number that corresponds to their choice, or may say that only a number will be accepted). Should the user still enter an unacceptable answer, the program will catch the error and re-prompt the user to try again. 

Through a series of these questions, the program will craft a query, and utilizing the sqlalchemy library, will then execute this query once complete.

# Future Improvements
-Adding security features. Right now, any user can perform any operation, but for example, this can be changed so that only certain users can delete records

-Right now, the program only supports full joins of tables. In the future, I'd like to add functionality allowing users to have left/right/outer joins, along with unions.

-Add further support for more SQL datatypes. Right now, the program only accounts for datatypes present in the MLB schema, and in order to be effective in all databases, more datatypes will need to be supported. 
