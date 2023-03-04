from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
#import os
from aws_xray_sdk.core.models.subsegment import Subsegment
from aws_xray_sdk.core.utils.sqs_message_helper import SqsMessageHelper

# X-Ray
#xray_url = os.getenv("AWS_XRAY_URL")
#xray_recorder.configure(service='notifications_activities', dynamic_naming=xray_url)

class NotificationsActivities:
  def run():
    # xray 
    subsegment = xray_recorder.begin_subsegment('notifications_activities')

    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Lloyd',
      'message': 'I am a Ninja',
      'created_at': (now - timedelta(days=2)).isoformat(),
      'expires_at': (now + timedelta(days=5)).isoformat(),
      'likes_count': 5,
      'replies_count': 1,
      'reposts_count': 0,
      'replies': [{
        'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
        'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
        'handle':  'Worf',
        'message': 'This post has no honor!',
        'likes_count': 0,
        'replies_count': 0,
        'reposts_count': 0,
        'created_at': (now - timedelta(days=2)).isoformat()
      }],
    }
    
    ]
    #subsegment = xray_recorder.begin_subsegment('mock-data')
    dict = {
      "now": now.isoformat(),
      "results-size": len(results)
    
    }
    subsegment.put_metadata('key', dict, 'namespace')
    
    return results