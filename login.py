import requests
from pyquery import PyQuery as pq
from urllib import parse
from sklearn.externals import joblib
from ProcessingImage import *
import time
import re
import json
import warnings


class SCHOOL(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
        }
        self.username = '**********'  # 学号
        self.password = '**********'  # 密码
        self.name = ''
        self.url_base = 'http://***.***.***.***/'  # 这里替换成自己学校的
        self.raw_url = self.url_base + 'default2.aspx'
        self.url_1 = ''
        self.login_url = ''
        self.real_url = ''
        self.session = requests.Session()

        self.get_real_url()
        self.login()

    def get_real_url(self):
        '''
        获取真实的登录url
        :return:
        '''
        response1 = self.session.get(self.raw_url, headers=self.headers)
        self.login_url = response1.url
        self.real_url = re.match('(.*)\/default2.aspx', self.login_url).group(1)
        self.url_1 = self.real_url + '/xs_main.aspx?xh=' + self.username
        # print(self.real_url)
        # print(self.login_url)
        # print(self.url_1)

    def loadModel(self, filename):
        return joblib.load(filename)


    def login(self):
        '''
        登录过程
        :return:
        '''
        response2 = self.session.get(self.login_url, headers=self.headers)
        text = response2.text
        doc = pq(text)
        get_captcha_src = doc.find('#icode').attr("src")
        _VIEWSTATE = doc.find('#form1 input').attr("value")
        _VIEWSTATEGENERATOR = doc.find("#form1 input[name='__VIEWSTATEGENERATOR']").attr('value')

        captcha_url = self.real_url + '/' + get_captcha_src
        captcha = self.session.get(captcha_url).content

        # 保存验证码
        with open('./tmp/captcha.jpg', 'wb') as f:
            f.write(captcha)

        model = self.loadModel('./model/clf1.model')   # 导入模型，model1 准确率较高

        img = Image.open('./tmp/captcha.jpg')
        new_img = SplitImage(GrayscaleAndBinarization(img))

        # 模型预测验证码
        result_pred = []
        i = 0
        for item in new_img:
            tmp = []
            item.save('./tmp/' + str(i) + '.jpg')
            i = i + 1
            img_after_split = item.resize((14, 27))
            tmp.append(featuretransfer(img_after_split))
            result_pred.append(model.predict(tmp)[0])
        captcha = ''.join(result_pred)
        print('此次预测结果为：', captcha)


        # 登录过程
        post_data = {
            '__VIEWSTATE': _VIEWSTATE,
            '__VIEWSTATEGENERATOR': _VIEWSTATEGENERATOR,
            'Button1': '',
            'hidPdis': '',
            'hidsc': '',
            'IbLanguage': '',
            'RadioButtonList1': '%D1%A7%C9%FA',
            'Textbox1': '',
            'TextBox2': self.password,
            'txtSecretCode': captcha,
            'txtUserName': self.username
        }

        response3 = self.session.post(self.login_url, headers=self.headers, data=post_data)
        self.name = pq(response3.text).find('#xhxm').text().replace('同学', '')
        if '欢迎您：' in response3.text:
            print('登录成功！', self.name)
        else:
            print('登录失败！正在尝试重新登录')
            self.login()


    def querySchedule(self):
        '''
        课表查询
        :return: table
        '''
        url_schedule = self.url_base + 'xskbcx.aspx?xh=' + self.username + '&xm='+ parse.quote(self.name) + '&gnmkdm=N121603'
        response_schedule = self.session.get(url=url_schedule, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Referer': self.url_1
        })

        return pq(response_schedule.text).find('#Table1')

    def queryScores(self, xuenian='2017-2018', xueqi='1', button='按学期查询'):
        '''
        成绩查询
        :param xuenian: 学年
        :param xueqi: 学期
        :param button: 查询方式
        :return:
        '''
        url_scores = self.url_base + 'xscj_gc.aspx?xh=' + self.username + '&xm='+ parse.quote(self.name) + '&gnmkdm=N121603'
        response_score_get = self.session.get(url=url_scores, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Referer': self.url_1
        })
        viewstate = pq(response_score_get.text).find("#Form1 input[name='__VIEWSTATE']").attr('value')
        data = {'__VIEWSTATE': viewstate,
                'ddlXN': xuenian,
                'ddlXQ': xueqi,
                'Button1': parse.quote(button)}
        response_score_post = self.session.post(url=url_scores, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Referer': url_scores}, data=data)

        score_table = pq(response_score_post.text).find('#Datagrid1')
        print(score_table)
        achievement_point = pq(response_score_post.text).find('#pjxfjd').text().replace('平均学分绩点：', '')
        print(achievement_point)

        return score_table, achievement_point


    def qk(self):
        '''
        抢课功能，但未实现，待开发....
        :return:
        '''
        self.get_real_url()
        self.login()
        course_ordered = self.session.get(
            self.real_url + '/xsxk.aspx?xh=' + self.username + '&xm=' + self.name + '&gnmkdm=N121101',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0',
                     'Upgrade-Insecure-Requests': '1',
                     'DNT': '1',
                     'Referer': self.real_url + '/xs_main.aspx?xh=' + self.username}
            )

        doc1 = pq(course_ordered.text)
        _VIEWSTATE1 = doc1.find("#xsxk_form input[name='__VIEWSTATE']").attr('value')
        _VIEWSTATEGENERATOR1 = doc1.find("#xsxk_form input[name='__VIEWSTATEGENERATOR']").attr('value')
        zymc = parse.quote(doc1.find("#zymc").attr('value'), encoding='gb2312')

        tmp = self.session.post(
            url=self.real_url + '/xsxk.aspx?xh=' + self.username + '&xm=' + self.name + '&gnmkdm=N121101',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',
                'Referer': self.real_url + '/xsxk.aspx?xh=' + self.username + '&xm=' + self.name + '&gnmkdm=N121101',
            },
            data={'__EVENTTARGET': '',
                  '__EVENTARGUMENT': '',
                  '__VIEWSTATE': _VIEWSTATE1,
                  '__VIEWSTATEGENERATOR': _VIEWSTATEGENERATOR1,
                  'zymc': zymc,
                  'xx': '',
                  'Button2': '%D0%A3%BC%B6%D1%A1%D0%DE%BF%CE'})
        doc2 = pq(tmp.text)
        _VIEWSTATE2 = doc2.find("#xsxk_form input[name='__VIEWSTATE']").attr('value')

        data = {'__EVENTTARGET': 'zymc',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': _VIEWSTATE2,
                '__VIEWSTATEGENERATOR': _VIEWSTATEGENERATOR1,
                'zymc': '%C8%AB%B2%BF%7C%7C%D1%A1%D0%DE%BF%CE5',
                'xx': ''}

        time.sleep(3.3)

        response3 = self.session.post(
            url=self.real_url + '/xsxk.aspx?xh=' + self.username + '&xm=' + self.name + '&gnmkdm=N121101',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:65.0) Gecko/20100101 Firefox/65.0',
                     'Upgrade-Insecure-Requests': '1',
                     'Referer': self.real_url + '/xsxk.aspx?xh=' + self.username + '&xm=' + self.name + '&gnmkdm=N121101',
                     'DNT': '1',
                     'Host': '202.200.112.246',
                     'Content-Type': 'application/x-www-form-urlencoded'}, data=json.dumps(data))
        print(response3.text)
        print(response3.status_code)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    ob = SCHOOL()
    ob.queryScores()

