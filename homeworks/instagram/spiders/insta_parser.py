import scrapy
from scrapy.http import HtmlResponse
from instagram.items import InstagramItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstaParserSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    # TODO !!!! заполнить значения
    insta_login = ''
    insta_pwd = ''

    parsed_users = ['a.i_programmer', 'influence_coding']

    user_relations = {'subscriber': {'hash': 'c76146de99bb02f6415203be841dd25a',
                                     'json_group_name': 'edge_followed_by'
                                     },
                      'subscribe':  {'hash': 'd04b0a864b4b54837c0d870b0e77e076',
                                     'json_group_name': 'edge_follow'
                                     }
                      }

    def parse(self, response: HtmlResponse):

        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)

        if j_body['authenticated']:

            for parsed_user in self.parsed_users:

                yield response.follow(f'/{parsed_user}',
                                      callback=self.user_data_parse,
                                      cb_kwargs={'parsed_username': parsed_user})

    def user_data_parse(self, response: HtmlResponse, parsed_username):

        parsed_user_id = self.fetch_user_id(response.text, parsed_username)

        variables = {'id': parsed_user_id,
                     'include_reel': 'true',
                     'fetch_mutual': 'false',
                     "first": 50
                     }

        for group in self.user_relations.keys():
            url_posts = f'{self.graphql_url}query_hash={self.user_relations[group]["hash"]}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_relations_parse,
                cb_kwargs={'parsed_username': parsed_username,
                           'parsed_user_id': parsed_user_id,
                           'relation': group,
                           'variables': deepcopy(variables)}
            )

    def user_relations_parse(self, response: HtmlResponse, parsed_username, parsed_user_id, relation, variables):

        j_data = json.loads(response.text)
        page_info = j_data['data']['user'][self.user_relations[relation]['json_group_name']]['page_info']

        if page_info.get('has_next_page'):
            variables['after'] = page_info['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={self.user_relations[relation]["hash"]}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_relations_parse,
                cb_kwargs={'parsed_username': parsed_username,
                           'parsed_user_id': parsed_user_id,
                           'relation': relation,
                           'variables': deepcopy(variables)}
            )

        users_list = j_data['data']['user'][self.user_relations[relation]['json_group_name']]['edges']

        for user in users_list:
            item = InstagramItem(
                parsed_username=parsed_username,
                parsed_user_id=parsed_user_id,
                relation=relation,
                relation_user_id=user['node']['id'],
                relation_username=user['node']['username'],
                relation_user_pic=user['node']['profile_pic_url'],
                relation_user_all_data=user['node'],
            )
            yield item

    def fetch_csrf_token(self, text):

        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):

        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')