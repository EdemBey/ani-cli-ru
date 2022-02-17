"""simple useragent generator"""

from random import choice

CHROME_VERSIONS = (
    '98.0.4758.108', '98.0.4758.107', '98.0.4758.106', '97.0.4692.108', '98.0.4758.105', '98.0.4758.104',
    '98.0.4758.103', '98.0.4758.102', '98.0.4758.101', '98.0.4758.100', '98.0.4758.99', '97.0.4692.107', '98.0.4758.98',
    '96.0.4664.194',
    '98.0.4758.97', '96.0.4664.193', '98.0.4758.96', '96.0.4664.192', '97.0.4692.106', '97.0.4692.105', '96.0.4664.183',
    '97.0.4692.104', '97.0.4692.103', '96.0.4664.181', '96.0.4664.180', '96.0.4664.179', '96.0.4664.178',
    '96.0.4664.177',
    '97.0.4692.102', '96.0.4664.176', '97.0.4692.101', '96.0.4664.175', '97.0.4692.100', '96.0.4664.174',
    '97.0.4692.99',
    '97.0.4692.98', '97.0.4692.97', '96.0.4664.173', '97.0.4692.96', '96.0.4664.172', '96.0.4664.171', '96.0.4664.170',
    '96.0.4664.169', '96.0.4664.168', '96.0.4664.167', '96.0.4664.166', '96.0.4664.145', '96.0.4664.144',
    '96.0.4664.143',
    '96.0.4664.142', '96.0.4664.141', '96.0.4664.140', '96.0.4664.139', '96.0.4664.138', '96.0.4664.137',
    '96.0.4664.136',
    '96.0.4664.135', '96.0.4664.134', '96.0.4664.133', '96.0.4664.132', '96.0.4664.131', '96.0.4664.130',
    '96.0.4664.129',
    '96.0.4664.128', '96.0.4664.127', '96.0.4664.126', '96.0.4664.125', '96.0.4664.124', '96.0.4664.123',
    '96.0.4664.122',
    '96.0.4664.121', '96.0.4664.120', '96.0.4664.119', '96.0.4664.118', '96.0.4664.117', '96.0.4664.116',
    '96.0.4664.115',
    '96.0.4664.114', '96.0.4664.113', '96.0.4664.112'
)

MOBILE_NAMES = (
    "(Linux; Android 6.0; Nexus 5)",
    "(Linux; Android 7.0; Redmi Note 7 Pro)",
    "(Linux; Android 8.1.0; Redmi Note 8 Pro)",
    "(Linux; Android 9.0.0; Redmi Note 9 Pro)",
    "(Linux; Android 6.0; SM-A710F)",
    "(Linux; Android 6.0; SAMSUNG SM-C9000)"
)

DESKTOP_STRINGS = (
    "(Windows NT 10.0; Win64; x64)",
    "(Windows NT 11.0; Win64; x64)",
    "(X11; Linux x86_64)",
)


class Agent:

    @classmethod
    def mobile(cls):
        device = choice(DESKTOP_STRINGS)
        chrome = choice(CHROME_VERSIONS)
        return \
            "Mozilla/5.0 {} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Mobile Safari/537.36".format(device,
                                                                                                          chrome)

    @classmethod
    def desktop(cls):
        device = choice(DESKTOP_STRINGS)
        chrome = choice(CHROME_VERSIONS)
        return \
            "Mozilla/5.0 {} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36".format(device,
                                                                                                   chrome)
