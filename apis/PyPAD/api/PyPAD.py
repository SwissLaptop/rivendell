# PyPAD.py
#
# PAD processor for Rivendell
#
#   (C) Copyright 2018 Fred Gleason <fredg@paravelsystems.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License version 2 as
#   published by the Free Software Foundation.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import configparser
import datetime
import MySQLdb
import signal
import socket
import sys
import json

#
# Enumerated Constants (sort of)
#
# Escape types
#
ESCAPE_NONE=0
ESCAPE_XML=1
ESCAPE_URL=2
ESCAPE_JSON=3

#
# PAD Types
#
TYPE_NOW='now'
TYPE_NEXT='next'

#
# Field Names
#
FIELD_START_DATETIME='startDateTime'
FIELD_CART_NUMBER='cartNumber'
FIELD_CART_TYPE='cartType'
FIELD_CUT_NUMBER='cutNumber'
FIELD_LENGTH='length'
FIELD_YEAR='year'
FIELD_GROUP_NAME='groupName'
FIELD_TITLE='title'
FIELD_ARTIST='artist'
FIELD_PUBLISHER='publisher'
FIELD_COMPOSER='composer'
FIELD_ALBUM='album'
FIELD_LABEL='label'
FIELD_CLIENT='client'
FIELD_AGENCY='agency'
FIELD_CONDUCTOR='conductor'
FIELD_USER_DEFINED='userDefined'
FIELD_SONG_ID='songId'
FIELD_OUTCUE='outcue'
FIELD_DESCRIPTION='description'
FIELD_ISRC='isrc'
FIELD_ISCI='isci'
FIELD_EXTERNAL_EVENT_ID='externalEventId'
FIELD_EXTERNAL_DATA='externalData'
FIELD_EXTERNAL_ANNC_TYPE='externalAnncType'

#
# Default TCP port for connecting to Rivendell's PAD service
#
PAD_TCP_PORT=34289

class Update(object):
    def __init__(self,pad_data,config):
        self.__fields=pad_data
        self.__config=config

    def __fromIso8601(self,string):
        try:
            return datetime.datetime.strptime(string.strip()[:19],'%Y-%m-%dT%H:%M:%S')
        except AttributeError:
            return ''

    def __escapeXml(self,string):
        string=string.replace("&","&amp;")
        string=string.replace("<","&lt;")
        string=string.replace(">","&gt;")
        string=string.replace("'","&apos;")
        string=string.replace("\"","&quot;")
        return string

    def __escapeWeb(self,string):
        string=string.replace("%","%25")
        string=string.replace(" ","%20")
        string=string.replace("<","%3C")
        string=string.replace(">","%3E")
        string=string.replace("#","%23")
        string=string.replace("\"","%22")
        string=string.replace("{","%7B")
        string=string.replace("}","%7D")
        string=string.replace("|","%7C")
        string=string.replace("\\","%5C")
        string=string.replace("^","%5E")
        string=string.replace("[","%5B")
        string=string.replace("]","%5D")
        string=string.replace("`","%60")
        string=string.replace("\a","%07")
        string=string.replace("\b","%08")
        string=string.replace("\f","%0C")
        string=string.replace("\n","%0A")
        string=string.replace("\r","%0D")
        string=string.replace("\t","%09")
        string=string.replace("\v","%0B")
        return string

    def __escapeJson(self,string):
        string=string.replace("\\","\\\\")
        string=string.replace("\"","\\\"")
        string=string.replace("/","\\/")
        string=string.replace("\b","\\b")
        string=string.replace("\f","\\f")
        string=string.replace("\n","\\n")
        string=string.replace("\r","\\r")
        string=string.replace("\t","\\t")
        return string

    def __replaceWildcard(self,wildcard,sfield,stype,string,esc):
        try:
            if isinstance(self.__fields['padUpdate'][stype][sfield],str):
                string=string.replace('%'+wildcard,self.escape(self.__fields['padUpdate'][stype][sfield],esc))
            else:
                string=string.replace('%'+wildcard,str(self.__fields['padUpdate'][stype][sfield]))
        except TypeError:
            string=string.replace('%'+wildcard,'')
        except KeyError:
            string=string.replace('%'+wildcard,'')
        return string

    def __replaceWildcardPair(self,wildcard,sfield,string,esc):
        string=self.__replaceWildcard(wildcard,sfield,'now',string,esc);
        string=self.__replaceWildcard(wildcard.upper(),sfield,'next',string,esc);
        return string;

    def __findDatetimePattern(self,pos,wildcard,string):
        start=string.find('%'+wildcard+'(',pos)
        if start>=0:
            end=string.find(")",start+3)
            if end>0:
                return (end+2,string[start:end+1])
        return None

    def __replaceDatetimePattern(self,string,pattern):
        stype='now'
        if pattern[1]=='D':
            stype='next'
        try:
            dt=self.__fromIso8601(self.__fields['padUpdate'][stype]['startDateTime'])
        except TypeError:
            string=string.replace(pattern,'')
            return string

        dt_pattern=pattern[3:-1]

        try:
            #
            # Process Times
            #
            miltime=(dt_pattern.find('ap')<0)and(dt_pattern.find('AP')<0)
            if not miltime:
                if dt.hour<13:
                    dt_pattern=dt_pattern.replace('ap','am')
                    dt_pattern=dt_pattern.replace('AP','AM')
                else:
                    dt_pattern=dt_pattern.replace('ap','pm')
                    dt_pattern=dt_pattern.replace('AP','PM')
            if miltime:
                dt_pattern=dt_pattern.replace('hh',dt.strftime('%H'))
                dt_pattern=dt_pattern.replace('h',str(dt.hour))
            else:
                dt_pattern=dt_pattern.replace('hh',dt.strftime('%I'))
                hour=dt.hour
                if hour==0:
                    hour=12
                dt_pattern=dt_pattern.replace('h',str(hour))

            dt_pattern=dt_pattern.replace('mm',dt.strftime('%M'))
            dt_pattern=dt_pattern.replace('m',str(dt.minute))

            dt_pattern=dt_pattern.replace('ss',dt.strftime('%S'))
            dt_pattern=dt_pattern.replace('s',str(dt.second))

            #
            # Process Dates
            #
            dt_pattern=dt_pattern.replace('MMMM',dt.strftime('%B'))
            dt_pattern=dt_pattern.replace('MMM',dt.strftime('%b'))
            dt_pattern=dt_pattern.replace('MM',dt.strftime('%m'))
            dt_pattern=dt_pattern.replace('M',str(dt.month))

            dt_pattern=dt_pattern.replace('dddd',dt.strftime('%A'))
            dt_pattern=dt_pattern.replace('ddd',dt.strftime('%a'))
            dt_pattern=dt_pattern.replace('dd',dt.strftime('%d'))
            dt_pattern=dt_pattern.replace('d',str(dt.day))

            dt_pattern=dt_pattern.replace('yyyy',dt.strftime('%Y'))
            dt_pattern=dt_pattern.replace('yy',dt.strftime('%y'))

        except AttributeError:
            string=string.replace(pattern,'')
            return string

        string=string.replace(pattern,dt_pattern)
        return string

    def __replaceDatetimePair(self,string,wildcard):
        pos=0
        pattern=(0,'')
        while(pattern!=None):
            pattern=self.__findDatetimePattern(pattern[0],wildcard,string)
            if pattern!=None:
                string=self.__replaceDatetimePattern(string,pattern[1])
        return string

    def config(self):
        """
           If a valid configuration file was set in
           'PyPAD.Receiver::setConfigFile()', this will return a
           parserconfig object created from it. If no configuration file
           was specified, returns None.
        """
        return self.__config

    def dateTimeString(self):
        """
           Returns the date-time of the update in ISO 8601 format (string).
        """
        return self.__fields['padUpdate']['dateTime']

    def dateTime(self):
        """
           Returns the date-time of the PAD update (datetime)
        """
        return self.__fromIso8601(self.__fields['padUpdate']['dateTime'])

    def escape(self,string,esc):
        """
           Returns an 'escaped' version of the specified string.

           Takes two arguments:

           string - The string to be processed.

           esc - The type of escaping to be applied. The following values
                 are valid:
                 PyPAD.ESCAPE_JSON - Escape for use in JSON string values
                                     (as per ECMA-404)
                 PyPAD.ESCAPE_NONE - String is passed through unchanged
                 PyPAD.ESCAPE_URL - Escape for use in URLs
                                    (as per RFC 2396)
                 PyPAD.ESCAPE_XML - Escape for use in XML
                                    (as per XML-v1.0)
        """
        if(esc==0):
            return string
        if(esc==1):
            return self.__escapeXml(string)
        if(esc==2):
            return self.__escapeWeb(string)
        if(esc==3):
            return self.__escapeJson(string)
        raise ValueError('invalid esc value')

    def hostName(self):
        """
           Returns the host name of the machine whence this PAD update
           originated (string).
        """
        return self.__fields['padUpdate']['hostName']

    def shortHostName(self):
        """
           Returns the short host name of the machine whence this PAD update
           originated (string).
        """
        return self.__fields['padUpdate']['shortHostName']

    def machine(self):
        """
           Returns the log machine number to which this update pertains
           (integer).
        """
        return self.__fields['padUpdate']['machine']

    def mode(self):
        """
           Returns the operating mode of the host log machine to which
           this update pertains (string).
        """
        return self.__fields['padUpdate']['mode']

    def onairFlag(self):
        """
           Returns the state of the on-air flag (boolean).
        """
        return self.__fields['padUpdate']['onairFlag']

    def hasService(self):
        """
           Indicates if service information is included with this update
           (boolean).
        """
        try:
            return self.__fields['padUpdate']['service']!=None
        except TypeError:
           return False;
        
    def serviceName(self):
        """
           Returns the name of the service associated with this update (string).
        """
        return self.__fields['padUpdate']['service']['name']

    def serviceDescription(self):
        """
           Returns the description of the service associated with this update
           (string).
        """
        return self.__fields['padUpdate']['service']['description']

    def serviceProgramCode(self):
        """
           Returns the Program Code of the service associated with this update
           (string).
        """
        return self.__fields['padUpdate']['service']['programCode']

    def hasLog(self):
        """
           Indicates if log information is included with this update
           (boolean).
        """
        try:
            return self.__fields['padUpdate']['log']!=None
        except TypeError:
            return False;
        
    def logName(self):
        """
           Returns the name of the log associated with this update (string).
        """
        return self.__fields['padUpdate']['log']['name']

    def resolvePadFields(self,string,esc):
        """
           Takes two arguments:

           string - A string containing one or more PAD wildcards, which it
                    will resolve into the appropriate values. See the
                    'Metadata Wildcards' section of the Rivendell Operations
                    Guide for a list of recognized wildcards.

           esc - Character escaping to be applied to the PAD fields.
                 See the documentation for the 'escape()' method for valid
                 field values.
        """
        string=self.__replaceWildcardPair('a','artist',string,esc)
        string=self.__replaceWildcardPair('b','label',string,esc)
        string=self.__replaceWildcardPair('c','client',string,esc)
        string=self.__replaceDatetimePair(string,'d') # %d(<dt>) Handler
        string=self.__replaceDatetimePair(string,'D') # %D(<dt>) Handler
        string=self.__replaceWildcardPair('e','agency',string,esc)
        #string=self.__replaceWildcardPair('f',sfield,string,esc) # Unassigned
        string=self.__replaceWildcardPair('g','groupName',string,esc)
        string=self.__replaceWildcardPair('h','length',string,esc)
        string=self.__replaceWildcardPair('i','description',string,esc)
        string=self.__replaceWildcardPair('j','cutNumber',string,esc)
        #string=self.__replaceWildcardPair('k',sfield,string,esc) # Start time for rdimport
        string=self.__replaceWildcardPair('l','album',string,esc)
        string=self.__replaceWildcardPair('m','composer',string,esc)
        string=self.__replaceWildcardPair('n','cartNumber',string,esc)
        string=self.__replaceWildcardPair('o','outcue',string,esc)
        string=self.__replaceWildcardPair('p','publisher',string,esc)
        #string=self.__replaceWildcardPair('q',sfield,string,esc) # Start date for rdimport
        string=self.__replaceWildcardPair('r','conductor',string,esc)
        string=self.__replaceWildcardPair('s','songId',string,esc)
        string=self.__replaceWildcardPair('t','title',string,esc)
        string=self.__replaceWildcardPair('u','userDefined',string,esc)
        #string=self.__replaceWildcardPair('v',sfield,string,esc) # Length, rounded down
        #string=self.__replaceWildcardPair('w',sfield,string,esc) # Unassigned
        #string=self.__replaceWildcardPair('x',sfield,string,esc) # Unassigned
        string=self.__replaceWildcardPair('y','year',string,esc)
        #string=self.__replaceWildcardPair('z',sfield,string,esc) # Unassigned
        string=string.replace('\\b','\b')
        string=string.replace('\\f','\f')
        string=string.replace('\\n','\n')
        string=string.replace('\\r','\r')
        string=string.replace('\\t','\t')
        return string

    def hasPadType(self,pad_type):
        """
           Indicates if this update includes the specified PAD type

           Takes one argument:

           pad_type - The type of PAD value. Valid values are:
                      PyPAD.TYPE_NOW - Now playing data
                      PyPAD.TYPE_NEXT - Next to play data
        """
        try:
            return self.__fields['padUpdate'][pad_type]!=None
        except TypeError:
            return False;

    def startDateTime(self,pad_type):
        """
           Returns the start datetime of the specified PAD type

           Takes one argument:

           pad_type - The type of PAD value. Valid values are:
                      PyPAD.TYPE_NOW - Now playing data
                      PyPAD.TYPE_NEXT - Next to play data
        """
        try:
            return self.__fromIso8601(self.__fields['padUpdate'][pad_type]['startDateTime'])
        except AttributeError:
            return None

    def padField(self,pad_type,pad_field):
        """
           Returns the raw value of the specified PAD field.

           Takes two arguments:

           pad_type - The type of PAD value. Valid values are:
                      PyPAD.TYPE_NOW - Now playing data
                      PyPAD.TYPE_NEXT - Next to play data

           pad_field - The specific field. Valid values are:
                       PyPAD.FIELD_AGENCY - The 'Agency' field (string)
                       PyPAD.FIELD_ALBUM - The 'Album' field (string)
                       PyPAD.FIELD_ARTIST - The 'Artist' field (string)
                       PyPAD.FIELD_CART_NUMBER - The 'Cart Number' field
                                                 (integer)
                       PyPAD.FIELD_CART_TYPE - 'The 'Cart Type' field (string)
                       PyPAD.FIELD_CLIENT - The 'Client' field (string)
                       PyPAD.FIELD_COMPOSER - The 'Composer' field (string)
                       PyPAD.FIELD_CONDUCTOR - The 'Conductor' field (string)
                       PyPAD.FIELD_CUT_NUMER - The 'Cut Number' field (integer)
                       PyPAD.FIELD_DESCRIPTION - The 'Description' field
                                                 (string)
                       PyPAD.FIELD_EXTERNAL_ANNC_TYPE - The 'EXT_ANNC_TYPE'
                                                        field (string)
                       PyPAD.FIELD_EXTERNAL_DATA - The 'EXT_DATA' field
                                                   (string)
                       PyPAD.FIELD_EXTERNAL_EVENT_ID - The 'EXT_EVENT_ID'
                                                       field (string)
                       PyPAD.FIELD_GROUP_NAME - The 'GROUP_NAME' field (string)
                       PyPAD.FIELD_ISRC - The 'ISRC' field (string)
                       PyPAD.FIELD_ISCI - The 'ISCI' field (string)
                       PyPAD.FIELD_LABEL - The 'Label' field (string)
                       PyPAD.FIELD_LENGTH - The 'Length' field (integer)
                       PyPAD.FIELD_OUTCUE - The 'Outcue' field (string)
                       PyPAD.FIELD_PUBLISHER - The 'Publisher' field (string)
                       PyPAD.FIELD_SONG_ID - The 'Song ID' field (string)
                       PyPAD.FIELD_START_DATETIME - The 'Start DateTime field
                                                    (string)
                       PyPAD.FIELD_TITLE - The 'Title' field (string)
                       PyPAD.FIELD_USER_DEFINED - 'The 'User Defined' field
                                                   (string)
                       PyPAD.FIELD_YEAR - The 'Year' field (integer)
        """
        return self.__fields['padUpdate'][pad_type][pad_field]

    def resolveFilepath(self,string,dt):
        """
           Returns a string with any Rivendell Filepath wildcards resolved
           (See Appdendix C of the Rivendell Operations Guide for a list).

           Takes two arguments:
 
           string - The string to resolve.

           dt - A Python 'datetime' object to use for the resolution.
        """
        ret=''
        upper_case=False
        initial_case=False
        offset=0
        i=0

        while i<len(string):
            field=''
            offset=0;
            if string[i]!='%':
                ret+=string[i]
            else:
                i=i+1
                offset=offset+1
                if string[i]=='^':
                    upper_case=True
                    i=i+1
                    offset=offset+1
                else:
                    upper_case=False

                if string[i]=='$':
                    initial_case=True
                    i=i+1
                    offset=offset+1
                else:
                    initial_case=False

                found=False
                if string[i]=='a':   # Abbreviated weekday name
                    field=dt.strftime('%a').lower()
                    found=True

                if string[i]=='A':   # Full weekday name
                    field=dt.strftime('%A').lower()
                    found=True

                if (string[i]=='b') or (string[i]=='h'): # Abrev. month Name
                    field=dt.strftime('%b').lower()
                    found=True

                if string[i]=='B':  # Full month name
                    field=dt.strftime('%B').lower()
                    found=True

                if string[i]=='C':  # Century
                    field=dt.strftime('%C').lower()
                    found=True

                if string[i]=='d':  # Day (01 - 31)
                    field='%02d' % dt.day
                    found=True

                if string[i]=='D':  # Date (mm-dd-yy)
                    field=dt.strftime('%m-%d-%y')
                    found=True

                if string[i]=='e':  # Day, padded ( 1 - 31)
                    field='%2d' % dt.day
                    found=True

                if string[i]=='E':  # Day, unpadded (1 - 31)
                    field='%d' % dt.day
                    found=True

                if string[i]=='F':  # Date (yyyy-mm-dd)
                    field=dt.strftime('%F')
                    found=True
                    
                if string[i]=='g':  # Two digit year number (as per ISO 8601)
                    field=dt.strftime('%g').lower()
                    found=True

                if string[i]=='G':  # Four digit year number (as per ISO 8601)
                    field=dt.strftime('%G').lower()
                    found=True

                if string[i]=='H':  # Hour, zero padded, 24 hour
                    field=dt.strftime('%H').lower()
                    found=True

                if string[i]=='I':  # Hour, zero padded, 12 hour
                    field=dt.strftime('%I').lower()
                    found=True

                if string[i]=='i':  # Hour, space padded, 12 hour
                    hour=dt.hour
                    if hour>12:
                        hour=hour-12
                    if hour==0:
                        hour=12
                    field='%2d' % hour
                    found=True

                if string[i]=='J':  # Hour, unpadded, 12 hour
                    hour=dt.hour
                    if hour>12:
                        hour=hour-12
                    if hour==0:
                        hour=12
                    field=str(hour)
                    found=True

                if string[i]=='j':  # Day of year
                    field=dt.strftime('%j')
                    found=True
                
                if string[i]=='k':  # Hour, space padded, 24 hour
                    field=dt.strftime('%k')
                    found=True

                if string[i]=='M':  # Minute, zero padded
                    field=dt.strftime('%M')
                    found=True

                if string[i]=='m':  # Month (01 - 12)
                    field=dt.strftime('%m')
                    found=True

                if string[i]=='p':  # AM/PM string
                    field=dt.strftime('%p')
                    found=True

                if string[i]=='r':  # Rivendell host name
                    field=self.hostName()
                    found=True

                if string[i]=='R':  # Rivendell short host name
                    field=self.shortHostName()
                    found=True

                if string[i]=='S':  # Second (SS)
                    field=dt.strftime('%S')
                    found=True

                if string[i]=='s':  # Rivendell service name
                    if self.hasService():
                        field=self.serviceName()
                    else:
                        field=''
                    found=True

                if string[i]=='u':  # Day of week (numeric, 1..7, 1=Monday)
                    field=dt.strftime('%u')
                    found=True

                if (string[i]=='V') or (string[i]=='W'): # Week # (as per ISO 8601)
                    field=dt.strftime('%V')
                    found=True
    
                if string[i]=='w':  # Day of week (numeric, 0..6, 0=Sunday)
                    field=dt.strftime('%w')
                    found=True

                if string[i]=='y':  # Year (yy)
                    field=dt.strftime('%y')
                    found=True

                if string[i]=='Y':  # Year (yyyy)
                    field=dt.strftime('%Y')
                    found=True

                if string[i]=='%':
                    field='%'
                    found=True

                if not found:  # No recognized wildcard, rollback!
                    i=-offset
                    field=string[i]

            if upper_case:
                field=field.upper();
            if initial_case:
                field=field[0].upper()+field[1::]
            ret+=field
            upper_case=False
            initial_case=False
            i=i+1

        return ret

    def shouldBeProcessed(self,section):
        """
           Reads the Log Selection and SendNullUpdate parameters of the
           config and returns a boolean to indicate whether or not this
           update should be processed (boolean).

           Takes one argument:

           section - The '[<section>]' of the INI configuration from which
                     to take the parameters.
        """
        try:
            if self.__config.get(section,'ProcessNullUpdates')=='0':
                return True
            if self.__config.get(section,'ProcessNullUpdates')=='1':
                return self.hasPadType(PyPAD.TYPE_NOW)
            if self.__config.get(section,'ProcessNullUpdates')=='2':
                return self.hasPadType(PyPAD.TYPE_NEXT)
            if self.__config.get(section,'ProcessNullUpdates')=='3':
                return self.hasPadType(PyPAD.TYPE_NOW) and self.hasPadType(PyPAD.TYPE_NEXT)
        except configparser.NoOptionError:
            return True

        log_dict={1: 'MasterLog',2: 'Aux1Log',3: 'Aux2Log',
                  101: 'VLog101',102: 'VLog102',103: 'VLog103',104: 'VLog104',
                  105: 'VLog105',106: 'VLog106',107: 'VLog107',108: 'VLog108',
                  109: 'VLog109',110: 'VLog110',111: 'VLog111',112: 'VLog112',
                  113: 'VLog113',114: 'VLog114',115: 'VLog115',116: 'VLog116',
                  117: 'VLog117',118: 'VLog118',119: 'VLog119',120: 'VLog120'}
        if self.__config.get(section,log_dict[self.machine()]).lower()=='yes':
            return True
        if self.__config.get(section,log_dict[self.machine()]).lower()=='no':
            return False
        if self.__config.get(section,log_dict[self.machine()]).lower()=='onair':
            return self.onairFlag()


        

class Receiver(object):
    def __init__(self):
        self.__callback=None
        self.__config_parser=None

    def __PyPAD_Process(self,pad):
        self.__callback(pad)

    def __getDbCredentials(self):
        config=configparser.ConfigParser()
        config.readfp(open('/etc/rd.conf'))
        return (config.get('mySQL','Loginname'),config.get('mySQL','Password'),
                config.get('mySQL','Hostname'),config.get('mySQL','Database'))

    def __openDb(self):
        creds=self.__getDbCredentials()
        return MySQLdb.connect(creds[2],creds[0],creds[1],creds[3])

    def setCallback(self,cb):
        """
           Set the processing callback.
        """
        self.__callback=cb

    def setConfigFile(self,filename):
        """
           Set a file whence to get configuration information. If set,
           the 'PyPAD.Update::config()' method will return a parserconfig
           object created from the specified file. The file must be in INI
           format.

           A special case is if the supplied filename string begins with
           the '$' character. If so, the remainder of the string is assumed
           to be an unsigned integer ID that is used to retrieve the
           configuration from the 'PYPAD_INSTANCES' table in the database
           pointed to by '/etc/rd.conf'.
        """
        if filename[0]=='$':  # Get the config from the DB
            db=self.__openDb()
            cursor=db.cursor()
            cursor.execute('select CONFIG from PYPAD_INSTANCES where ID='+
                           filename[1::])
            config=cursor.fetchone()
            self.__config_parser=configparser.ConfigParser(interpolation=None)
            self.__config_parser.read_string(config[0])
            db.close()

        else:   # Get the config from a file
            fp=open(filename)
            self.__config_parser=configparser.ConfigParser(interpolation=None)
            self.__config_parser.readfp(fp)
            fp.close()

    def start(self,hostname,port):
        """
           Connect to a Rivendell system and begin processing PAD events.
           Once started, a PyPAD object can be interacted with
           only within its callback method.

           Takes the following arguments:

           hostname - The hostname or IP address of the Rivendell system.

           port - The TCP port to connect to. For most cases, just use
                  'PyPAD.PAD_TCP_PORT'.
        """
        # So we exit cleanly when shutdown by rdpadengined(8)
        signal.signal(signal.SIGTERM,SigHandler)

        sock=socket.socket(socket.AF_INET)
        conn=sock.connect((hostname,port))
        c=bytes()
        line=bytes()
        msg=""

        while 1<2:
            c=sock.recv(1)
            line+=c
            if c[0]==10:
                msg+=line.decode('utf-8')
                if line.decode('utf-8')=="\r\n":
                    self.__PyPAD_Process(Update(json.loads(msg),self.__config_parser))
                    msg=""
                line=bytes()


def SigHandler(signo,stack):
    sys.exit(0)
