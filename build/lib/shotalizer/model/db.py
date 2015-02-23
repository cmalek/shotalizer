import os
import sqlite3

class Stream(list):
    def __str__(self):
        return ";".join(["{0}:{1}:{2}".format(x[0],x[1],x[2]) for x in self])

def convert_stream(s):
    stream = Stream()
    for r in s.split(";"):
        (timestamp, status, url_code) = r.split(":")
        stream.append((int(timestamp), int(status), int(url_code)))
    return(stream)

sqlite3.register_converter("stream", convert_stream)

class Db(object):
    
    def __init__(self, filename):
        self.filename = filename
        self.db = sqlite3.connect(self.filename, detect_types=sqlite3.PARSE_DECLTYPES)
        # Make sqlite3 return our results as a dict-like rather than as a tuple
        self.db.row_factory = sqlite3.Row
        self.cursor = self.db.cursor()

    @property
    def description(self):
        self.cursor.execute("""
SELECT description FROM meta  
LIMIT 1
""")
        return self.cursor.fetchone()[0]

    @property
    def rows(self):
        self.cursor.execute("""
SELECT count(*) FROM access_log  
""")
        return self.cursor.fetchone()[0]

    def initdb(self, description=None):
        self.cursor.execute("""
CREATE TABLE access_log (
    tag text,
    timestamp integer,
    remote_ip text,
    x_forwarded_for text,
    remote_user text,
    method text,
    url text,
    bare_url text,
    query_string text,
    status integer,
    bytes integer,
    referrer text,
    user_agent text,
    is_mobile boolean
)
""")
        self.cursor.execute("""
CREATE TABLE meta (
    description text
)
""")
        self.db.commit()
        self.cursor.execute("""
INSERT INTO meta (description) values (?)
""", [description]
)

    def create_streams_table(self):
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS streams (
    username text,
    clickstream text
)
""")
        self.db.commit()

    def create(self, description=None):
        self.initdb(description)
        self.db.commit()
        self.db.close()

    def delete(self):
        self.db.commit()
        self.db.close()
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def _get_extra(self, where=[], uri_filter=None, start_time=None, end_time=None):
        if uri_filter:
            if uri_filter.startswith("!"):
                where.append("url not like '%{0}%'".format(uri_filter[1:]))
            else:
                where.append("url like '%{0}%'".format(uri_filter[1:]))
        if start_time:
            where.append("timestamp >= '{0}'".format(start_time))
        if end_time:
            where.append("timestamp < '{0}'".format(end_time))
        if where:
            extra = "where " + " and ".join(where)
        else:
            extra = ""
        return extra
    
class HitsAnalyzer(Db):
    
    def all(self, uri_filter=None, start_time=None):
        extra = self._get_extra(uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
            SELECT timestamp, status from access_log
            {0}
            """.format(extra)
            )
        return self.cursor.fetchall()
    
class UserAnalyzer(Db):
    
    def unique_urls(self, uri_filter=None, start_time=None):
        extra = self._get_extra(uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
            SELECT distinct(bare_url) from access_log 
            {0}
            order by bare_url asc
            """.format(extra)
        )
        return self.cursor.fetchall()
        

    def unique_users(self, uri_filter=None, start_time=None):
        extra = self._get_extra(uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
            SELECT distinct(remote_user) from access_log 
            {0}
            order by remote_user asc
            """.format(extra)
        )
        return self.cursor.fetchall()
    
    
    def user_hits(self, uri_filter=None, start_time=None):
        extra = self._get_extra(uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
                SELECT remote_user, count(remote_user) from access_log
                {0}
                group by remote_user
                order by count(remote_user) desc
            """.format(extra)
        )
        return self.cursor.fetchall()

    def user_errors(self, uri_filter=None, start_time=None):
        extra = self._get_extra(["status in (502, 503)"], uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
                SELECT remote_user, count(remote_user) from access_log
                {0}
                group by remote_user
                order by count(remote_user) desc
            """.format(extra)
        )
        return self.cursor.fetchall()

    def user_no_errors(self, uri_filter=None, start_time=None, end_time=None):
        extra = self._get_extra(["remote_user not in (select distinct remote_user from access_log where status in (502,503) group by remote_user)"], uri_filter=uri_filter, start_time=start_time, end_time=end_time)
        self.cursor.execute("""
                SELECT distinct remote_user from access_log
                {0}
                group by remote_user
                order by remote_user asc
            """.format(extra)
        )
        return self.cursor.fetchall()
    
    def user_stream(self, username, uri_filter=None, start_time=None):
        extra = self._get_extra(["remote_user = '{0}'".format(username)], uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
            SELECT timestamp, status, url from access_log
            {0}
            order by timestamp asc
            """.format(extra)
        )
        return self.cursor.fetchall()
    
    def user_base_stream(self, username, uri_filter=None, start_time=None):
        extra = self._get_extra(["remote_user = '{0}'".format(username)], uri_filter=uri_filter, start_time=start_time)
        self.cursor.execute("""
            SELECT timestamp, status, bare_url from access_log
            {0}
            order by timestamp asc
            """.format(extra)
        )
        return self.cursor.fetchall()
    
    def add_stream(self, username, stream):
        self.create_streams_table()
        self.cursor.execute("""
            INSERT INTO streams (username, clickstream) values (?,?)
        """, (username, str(stream))
        )
        self.db.commit()
        
    def get_stream(self, username):
        self.create_streams_table()
        self.cursor.execute("""
            SELECT clickstream from streams where username = ?
        """, (username,)
        )
        row = self.cursor.fetchone()
        return convert_stream(row['clickstream'])
