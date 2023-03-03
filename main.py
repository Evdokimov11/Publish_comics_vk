import requests
import os
import random

from dotenv import load_dotenv

VK_API_VERSION = 5.131


def get_rand_comics():

    last_comics_url = "https://xkcd.com/info.0.json"
    
    last_comics_response = requests.get(last_comics_url)
    last_comics_response.raise_for_status()
    last_comics = last_comics_response.json()
    comics_number = last_comics['num']
    
    rand_comics_number = random.randint(1,comics_number)
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


def get_upload_url(vk_headers,vk_group_id):

        request_url = 'https://api.vk.com/method/photos.getWallUploadServer'
        params = {
                    'group_id': vk_group_id,
                    'v': VK_API_VERSION
                    }
  
        response = requests.post(request_url,params=params,headers=vk_headers)
        response.raise_for_status()
        formatted_response = response.json()

        return formatted_response['response']['upload_url']


def upload_photo(vk_headers, upload_photo_url):

    with open('comics.png', 'rb') as file:
      
        files = {
            'photo': file, 
        }
      
        upload_photo_response = requests.post(upload_photo_url,files=files,headers=vk_headers)
        upload_photo_response.raise_for_status()
        upload_photo_formatted_response = upload_photo_response.json()

    return upload_photo_formatted_response


def save_photo(vk_headers,upload_photo_response,vk_group_id):

    saved_request_url = 'https://api.vk.com/method/photos.saveWallPhoto'
  
    save_vk_params = {
            'group_id': vk_group_id,
            'v': VK_API_VERSION,
            'photo':upload_photo_response['photo'],
            'hash':upload_photo_response['hash'],
            'server':upload_photo_response['server']
            }
    save_vk_response = requests.post(saved_request_url, params=save_vk_params,headers=vk_headers)
    save_vk_response.raise_for_status()
    save_formatted_vk_response = vk_response_save.json()
    
    person_id = save_formatted_vk_response['response'][0]['owner_id']
    photo_id = save_formatted_vk_response['response'][0]['id']

    return person_id, photo_id


def publish_photo(vk_headers,person_id,photo_id,vk_group_id, comics_comment):

    publish_url = 'https://api.vk.com/method/wall.post'
    publish_params = {
                'owner_id': -int(vk_group_id),
                'from_group': 1,
                'message':comics_comment,
                'attachments':f'photo{person_id}_{photo_id}',
                'v': VK_API_VERSION
                }
  
    publish_response = requests.post(publish_url, params=publish_params,  headers=vk_headers)
    publish_response.raise_for_status()


if __name__ == '__main__':

    load_dotenv()
  
    vk_access_token = os.environ['VK_ACCESS_TOKEN']
    vk_group_id = os.environ['VK_GROUP_ID']
  
    vk_headers = {'Authorization': 'Bearer {}'.format(vk_access_token)}
  
    comics_comment = get_rand_comics()
    upload_photo_url = get_upload_url(vk_headers,vk_group_id)
    upload_photo_response = upload_photo(vk_headers, upload_photo_url)
    person_id, photo_id =  save_photo(vk_headers,upload_photo_response,vk_group_id)
    publish_photo(vk_headers,person_id,photo_id,vk_group_id,comics_comment)
  
    os.remove('comics.png')
  

