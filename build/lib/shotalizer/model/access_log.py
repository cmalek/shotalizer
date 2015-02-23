import logging

import apache_log_parser

from apacheviz.commands.db import Db
import re

class AccessLogImporter(Db):
    """
    CustomLog logs/access_log "%h %{X-Forwarded-For}i %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""
    """
    
    log = logging.getLogger(__name__)
    
    def split_url(self, url):
        bare_url = url
        query_string = ""
        if url.find('?') != -1:
            bare_url, query_string = url.split("?", 1)
        # Strip trailing slashes
        if bare_url.endswith("/"):
            bare_url = bare_url[:-1]
        return(bare_url, query_string)

    def load(self, filename, tag="default"):
        line_parser = apache_log_parser.make_parser( "%h %{X-Forwarded-For}i %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" )
        count = 0
        with open(filename) as f:
            content = f.readlines()
            for line in content:
                # some lines in our access_log are missing the remote_user column
                # because there are apparently two different CustomLog lines on some
                # of our servers
                line = re.sub("- [[]", '- "" [', line)
                try:
                    data = line_parser(line)
                except ValueError:
                    self.log.error("Couldn't parse this line: {0}".format(line))
                else:
                    (bare_url, query_string) = self.split_url(data['request_url'])
                    self.cursor.execute("""
INSERT INTO access_log (
    tag,
    timestamp,
    remote_ip,
    x_forwarded_for,
    remote_user,
    method,
    url,
    bare_url,
    query_string,
    status,
    bytes,
    referrer,
    user_agent,
    is_mobile)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", [
    tag,
    data['time_received_datetimeobj'].strftime('%s'),
    data['remote_host'],
    data['request_header_x_forwarded_for'],
    data['remote_user'],
    data['request_method'],
    data['request_url'],
    bare_url,
    query_string,
    data['status'],
    data['response_bytes_clf'],
    data['request_header_referer'],
    data['request_header_user_agent'],
    data['request_header_user_agent__is_mobile']
    ]
) 
                    count +=1
                    if count % 1000 == 0:
                        self.log.info("Processed {0} lines ({1}%)".format(count, float(count)/float(len(content)) * 100))
            self.db.commit()
            self.db.close()
        return(len(content))


