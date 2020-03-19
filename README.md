# SeqtaSDSBridge
 
This script will connect to a SEQTA database and extract data from an approved_classes.csv file. Then the data is formatted for Microsoft SDS compliant csv files. 

### Prerequisites

What do you need to get this working

```
Read only access to the SEQTA server. You will need to contact SEQTA support for this.
Python 3.8
	- psycopg2
	- configparser
Microsoft Education licensing
A configured SDS profile - sds.microsoft.com
```

### Installing

```
The approved_classes.csv file needs to include the names of each class that you want to extract data for. 
The class name is checked against the 'name' value in the 'classunit' table. It will generally be something like 2020.09DRA#1
If you check a teacher timetable and look at the class name in the top left of the timetable view you will see the class name.

You need to rename the example.config.ini file to config.ini and put in the correct database credentials

I wanted to have one admin account on all of the Teams so that I could easily manage them. 
To do this I created an account on Office365 (or local AD if syncing) called teamsadmin. The script adds this user to all Teams.
You can change this username in the config.ini file to whatever account you create. The user id for this admin account is set to 9999
It MUST be unique and not a code used by your teachers. I doubt many schools have 9998 teachers, or have had that many. But be mindful of this.

```

## Versioning

I use [SemVer](http://semver.org/) for versioning.

## Authors

* **Jacob Curulli** - *Author* - [website](https://www.jacobcurulli.com)

## License

This project is licensed under the CC 4.0 - see the [License.md](License.md) file for details

## Acknowledgments

*
