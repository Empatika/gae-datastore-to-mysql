import webapp2
import json
import logging
from datetime import datetime
from google.appengine.api import memcache
from google.appengine.api import mail


class RecentDataHandler(webapp2.RequestHandler):

    def __init__(self):
        self.TIMESTAMP_PROP_NAME = 'created'    # TODO: Define the name of the 'timestamp' property that will be used to
                                                #       fetch only recent entitites from the Datastore.
        self.KINDS = {
                                                # TODO: Provide a mapping from kind names (that will come through requests)
                                                #       to GAE Datastore model classes.
                                                
                                                # NOTE: All model classes are required to have a property named
                                                #       self.TIMESTAMP_PROP_NAME of type db.DateTimeProperty.
        }
        self.SECRET_KEY = ''                    # TODO: Provide a secret key to protect the data.

    def get(self):
    
        datetime_format = '%Y-%m-%d %H:%M:%S'
    
        kind = self.request.get('kind').lower()
        batch_size = int(self.request.get('batch_size', '100'))
        time_from = datetime.strptime(self.request.get('from', ''), datetime_format)
        time_to = datetime.strptime(self.request.get('to', datetime.now().strftime(datetime_format)), datetime_format)
        time_to_str = self.request.get('to', 'now') # used for caching
        session_id = int(self.request.get('session_id', 0))
        repeat_previous = self.request.get('repeat_previous', 'false').lower()
        secret_key = self.request.get('secret_key', '')
        
        # Overall ersponse structure
        resp = {'kind': kind, 'data': [], 'count': 0, 'error': None}
        
        if secret_key != self.SECRET_KEY:
            resp['error'] = 'Invalid secret key'
            self.response.out.write(json.dumps(resp, separators=(',',':')))
            return
        
        query = self.KINDS[kind].all().filter(self.TIMESTAMP_PROP_NAME + ' >', time_from)
            
        if not query:
            resp['error'] = 'Could not retrieve entities of kind %s' % kind
            self.response.out.write(json.dumps(resp, separators=(',',':')))
            return
            
        cursor_key = 'cursor_%s_recent_data_%s_%s_session_%i' % (kind, time_from.strftime(datetime_format),
                                                                 time_to_str, session_id)
        cursor = memcache.get(cursor_key) if repeat_previous != 'true' else memcache.get(cursor_key + '_prev')
        if cursor:
            query.with_cursor(start_cursor=cursor)
            
        try:
            results = query.fetch(batch_size)
        except:
            # Optional: send an e-mail to indicate that replication failed
            mail.send_mail(sender="TODO: <your@email.com>",
                           to="TODO: <recipient@email.com>",
                           subject="Replication failure",
                           body="Fix the issue.")

        for entity in results:
            resp['count'] += 1
            try:
                entity_timestamp = getattr(entity, self.TIMESTAMP_PROP_NAME)
                entity_properties = [prop for prop in dir(entity)
                                     if not prop.startswith('__') and
                                        prop != 'key' and prop != self.TIMESTAMP_PROP_NAME and
                                        not hasattr(getattr(entity, prop), '__call__')]
                if entity_timestamp < time_to:
                    entity_dict = {}
                    entity_dict['id'] = entity.key().id()
                    entity_dict[self.TIMESTAMP_PROP_NAME] = entity_timestamp.strftime(datetime_format)
                    for prop in entity_properties:
                        entity_dict[prop] = getattr(entity, prop)
                else:
                    resp['count'] -= 1 # Nothing was added; cancel counter increment
            
            except Exception as ex:
                logging.info('Exception in kind %s: %s' % (kind, ex.message))
                resp['count'] -= 1 # Simply ignore 'corrupt' entities, no error output
                

        memcache.set(cursor_key + '_prev', cursor, 60*60)
        cursor = query.cursor()
        memcache.set(cursor_key, cursor, 60*60)
                        
        self.response.headers.add_header('Content-Type', 'application/json')
        self.response.out.write(json.dumps(resp, separators=(',',':')))
