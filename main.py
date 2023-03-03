import requests
import os
import random

from dotenv import load_dotenv

VK_API_VERSION = 5.131

def check_status(formatted_response):
  
    try :
      error_msg = formatted_response['error']['error_msg']
      error_code = formatted_response['error']['error_code']
      full_error_msg = f'Code error : {error_code}. {error_msg}'

      return True, full_error_msg
      
      exit(full_error_msg)
      
    except KeyError:
      
      return False, 'Ok'


def get_rand_comics():

    last_comics_url = "https://xkcd.com/info.0.json"

    last_comics_response = requests.get(last_comics_url)
    last_comics_response.raise_for_status()
    last_comics = last_comics_response.json()
    comics_number = last_comics['num']

    rand_comics_number = random.randint(1, comics_number)
    comics_url = f"https://xkcd.com/{rand_comics_number}/info.0.json"
    comics_filename = 'comics.png'

    comics_response = requests.get(comics_url)
    comics_response.raise_for_status()
    comics = comics_response.json()
    img_url = comics['img']
    comics_comment = comics['alt']

    comics_image_response = requests.get(img_url)
    comics_image_response.raise_for_status()

    with open(comics_filename, 'wb') as file:
        file.write(comics_image_response.content)

    return comics_comment


def get_upload_url(vk_headers, vk_group_id):

    request_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
      'group_id': vk_group_id,
      'v': VK_API_VERSION,
    }
    
    response = requests.post(request_url, params=params, headers=vk_headers)
    response.raise_for_status()     
    formatted_response = response.json()
    
    error_key, error_message = check_status(formatted_response)
    if error_key : 
      exit(error_message)
    
    upload_photo_url = formatted_response['response']['upload_url']
       
    return upload_photo_url


def upload_photo(vk_headers, upload_photo_url):

    with open('comics.png', 'rb') as file:

        files = {'photo': file}
        upload_photo_response = requests.post(
          upload_photo_url,
          files=files,
          headers=vk_headers,
        )

    upload_photo_response.raise_for_status()
    upload_photo_formatted_response = upload_photo_response.json()
    error_key, error_message = check_status(upload_photo_formatted_response)
    if error_key : 
      exit(error_message)
        
    return upload_photo_formatted_response


def save_photo(vk_headers, upload_photo, upload_hash, 
               upload_server, vk_group_id):

    request_url = 'https://api.vk.com/method/photos.saveWallPhoto'

    vk_params = {
      'group_id': vk_group_id,
      'v': VK_API_VERSION,
      'photo': upload_photo,
      'hash': upload_hash,
      'server': upload_server,
    }

    vk_response = requests.post(
      request_url,
      params=vk_params,
      headers=vk_headers,
    )
    vk_response.raise_for_status()
    formatted_vk_response = vk_response.json()
    
    error_key, error_message = check_status(formatted_vk_response)
    if error_key : 
      exit(error_message)

    person_id = formatted_vk_response['response'][0]['owner_id']
    photo_id =  formatted_vk_response['response'][0]['id']

    return person_id, photo_id


def publish_photo(vk_headers, person_id, photo_id, vk_group_id, comics_coment):

    publish_url = 'https://api.vk.com/method/wall.post'
    attachments = f'photo{person_id}_{photo_id}'
    publish_params = {
        'owner_id': -int(vk_group_id),
        'from_group': 1,
        'message': comics_coment,
        'attachments': attachments,
        'v': VK_API_VERSION,
        }

    publish_response = requests.post(
        publish_url,
        params=publish_params,
        headers=vk_headers,
        )
    publish_response.raise_for_status()


if __name__ == '__main__':

    load_dotenv()

    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']

    vk_headers = {'Authorization': 'Bearer {}'.format(vk_access_token)}

    comics_comment = get_rand_comics()
    upload_photo_url = get_upload_url(vk_headers, vk_group_id)
    upload_photo_response = upload_photo(vk_headers, upload_photo_url)
    upload_photo = upload_photo_response['photo'],
    upload_hash = upload_photo_response['hash'],
    upload_server = upload_photo_response['server'],
    person_id, photo_id = save_photo(
        vk_headers,
        upload_photo,
        upload_hash,
        upload_server,
        vk_group_id,
        )
    publish_photo(vk_headers, person_id, photo_id, vk_group_id, comics_comment)

    os.remove('comics.png')
