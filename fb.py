from flask import Flask, request, jsonify
import requests, re, json

app = Flask(__name__)

class Facebook:
    def __init__(self, cookie):
        try:
            self.fb_dtsg = ''
            self.jazoest = ''
            self.cookie = cookie
            self.session = requests.Session()
            self.id = self.cookie.split('c_user=')[1].split(';')[0]
            self.headers = {
                'authority': 'www.facebook.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'vi',
                'sec-ch-prefers-color-scheme': 'light',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                'viewport-width': '1366',
                'Cookie': self.cookie
            }
            url = self.session.get(f'https://www.facebook.com/{self.id}', headers=self.headers).url
            response = self.session.get(url, headers=self.headers).text
            matches = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
            if len(matches) > 0:
                self.fb_dtsg += matches[0]
                self.jazoest += re.findall(r'jazoest=(.*?)\"', response)[0]
        except:
            pass

    def info(self):
        try:
            get = self.session.get('https://www.facebook.com/me', headers=self.headers).url
            url = 'https://www.facebook.com/' + get.split('%2F')[-2] + '/' if 'next=' in get else get
            response = self.session.get(url, headers=self.headers, params={"locale": "vi_VN"})
            data_split = response.text.split('"CurrentUserInitialData",[],{')
            json_data = '{' + data_split[1].split('},')[0] + '}'
            parsed_data = json.loads(json_data)
            id = parsed_data.get('USER_ID', '0')
            name = parsed_data.get('NAME', '')
            if id == '0' and name == '':
                return {'status': 'error', 'message': 'cookieout'}
            elif '828281030927956' in response.text:
                return {'status': 'error', 'message': '956'}
            elif '1501092823525282' in response.text:
                return {'status': 'error', 'message': '282'}
            elif '601051028565049' in response.text:
                return {'status': 'error', 'message': 'spam'}
            else:
                id, name = parsed_data.get('USER_ID'), parsed_data.get('NAME')
            return {
                'status': 'success',
                'id': id,
                'name': name,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest
            }
        except:
            return {'status': 'error', 'message': 'Lỗi khi phân tích thông tin'}

@app.route('/facebook-info', methods=['GET', 'POST'])
def facebook_info():
    cookie = None

    if request.method == 'POST':
        # Ưu tiên lấy từ form (x-www-form-urlencoded)
        cookie = request.form.get('cookie')
        # Nếu không có, thử lấy từ JSON
        if not cookie:
            data = request.get_json(silent=True)
            cookie = data.get('cookie') if data else None
    elif request.method == 'GET':
        cookie = request.args.get('cookie')

    if not cookie:
        print("== COOKIE NHẬN VỀ:", cookie)
        return jsonify({'status': 'error', 'message': 'Thiếu hoặc sai cookie'}), 400
    

    api = Facebook(cookie)
    info = api.info()
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
