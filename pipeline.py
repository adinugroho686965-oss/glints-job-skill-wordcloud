from payload import get_payload
from analyze import get_skill,count_frequency_word



def run_pipeline(
            device_id,
            session,
            url,
            max_data
        ): 

    raw_cookies = f"""device_id={device_id.strip()}; session={session.strip()}"""

    payload =  get_payload(raw_cookies,url)
    list_skill =  get_skill(payload,raw_cookies,max_data)
    counted_word = count_frequency_word(list_skill)

    return counted_word
