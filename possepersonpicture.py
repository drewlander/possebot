"""
plugin to return random meekle image
"""

import plugins
import urllib.request
import os
import hangups
import logging
from fuzzywuzzy import process

logger = logging.getLogger(__name__)
members = ["joey", "meekle", "toomie", "gary", "alex", "miller", "bizic", "drewski", "keener"]

def sanitize_possemember(person):
    return process.extractOne(person, members)[0];

def _initialise(bot):
    plugins.register_user_command(["possepic"])
    
def possepic(bot, event, *args):
    dirty_member = ''.join(args).strip()
    sanitized_member = sanitize_possemember(dirty_member)
    link = "http://funny.drewstud.com/"+sanitized_member+"/"+sanitized_member+"list.txt"
    try:
        response = urllib.request.urlopen(link)
        data = response.read()
        text = data.decode('utf-8')
        images=text.splitlines()
        images = [x for x in images if x]
    except urllib.error.HTTPError as e:
        if e.code==404:
            images=[]
        else:
            yield from bot.coro_send_message(
                event.conv,
                _("Server error %s getting %s" % e.code, dirty_member).format(
                    event.user.full_name, 'yay'))
    from random import randrange
    if len(images) > 0:
        random_index = randrange(0,len(images))
        image_name = images[random_index]
        instanceImageUrl = "http://funny.drewstud.com/"+sanitized_member+"/"+image_name
        image_data = urllib.request.urlopen(instanceImageUrl)
        filename = os.path.basename(instanceImageUrl)
        legacy_segments = [hangups.ChatMessageSegment( instanceImageUrl,
                                                       hangups.SegmentType.LINK,
                                                       link_target = instanceImageUrl )]
        logger.debug("uploading {} from {}".format(filename, instanceImageUrl))

        try:
            photo_id = yield from bot.call_shared('image_upload_single', instanceImageUrl)
        except KeyError:
            logger.warning('image plugin not loaded - using legacy code')
            photo_id = yield from bot._client.upload_image(image_data, filename=filename)
    
        yield from bot.coro_send_message(event.conv.id_, legacy_segments, image_id=photo_id)

    else:
        yield from bot.coro_send_message(
            event.conv,
            _("No images uploaded yet for %s" % dirty_member).format(
                event.user.full_name, 'yay'))



