import requests
import json


def build_component_link(component_code):
    link = 'https://www.jlcsmt.com/lcsc/detail?componentCode=%s' %component_code
    return link

def query_from_jlcsmt():
    s = requests.Session()
    # noinspection SpellCheckingInspection
    s.headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-platform': '"macOS"',
        'Connection': 'keep-alive',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Dest': 'empty',
        'Accept': 'application/json, text/plain, */*',
        'Sec-Fetch-Mode': 'cors',
        'sec-ch-ua-mobile': '?0',
        'Content-Type': 'application/json',
        'Origin': 'https://www.jlcsmt.com',
        'Host': 'www.jlcsmt.com',
        'Referer': 'https://www.jlcsmt.com/',
    }

    url = 'https://www.jlcsmt.com/api/smtComponentOrder/componentSearchController/selectPasteComponentList'

    headers = {
    }

    cookies = {
    }

    # query_string = "Ω"

    # body = '''{"ascFlag":false,"baseQueryDto":{"componentBrandList":[],"componentSpecificationList":[],"componentTypeIdList":[369],"preferredComponentFlagList":[],"orderLibraryTypeList":["expand"],"packageTypeList":[],"productTypeIdList":[365],"inStockFlag":true},"groupFlag":false,"pageVo":{"pageNum":1,"pageSize":10},"paramDtoList":[{"paramName":"连接器类型","paramValueList":["Micro-B"]}],"queryString":"","sortMode":"COMPREHENSIVE"}'''
    body = '''{"ascFlag":true,"baseQueryDto":{"componentBrandList":[],"componentSpecificationList":[],"componentTypeIdList":[369],"preferredComponentFlagList":[],"orderLibraryTypeList":["expand"],"packageTypeList":[],"productTypeIdList":[365],"inStockFlag":false},"groupFlag":false,"pageVo":{"pageNum":1,"pageSize":10},"paramDtoList":[{"paramName":"连接器类型","paramValueList":["Micro-B"]}],"queryString":"","sortMode":"COMPREHENSIVE"}'''
    body = body.encode('utf-8')
    body = json.loads(body)
    body['pageVo']['pageNum'] = 1
    body['pageVo']['pageSize'] = 2000
    # body['queryString'] = query_string
    # body['baseQueryDto']['componentSpecificationList'][0] = '0603'
    body = json.dumps(body)

    rc = s.post(url, headers=headers, cookies=cookies, data=body)
    response_json = json.loads(rc.content)
    data_list = response_json['data']['data']
    # print(data_list)
    return data_list

def pretty_print(data_list):
    for item in data_list:
        name = item['componentName']
        componentBrand = item['componentBrand']
        componentCode = item['componentCode']
        link = build_component_link(componentCode)
        # clickable_link = '\x1B]8;;%s\x1B\\%s\x1B]8;;\x1B\\' %(link, link)
        print(componentCode, componentBrand, name, link, sep=',')

def parse_result(data_list):
    values = []
    for item in data_list:
        code = item['componentCode']
        if code.startswith('C'):
            code_num = int(code[1:])
            item['code_num'] = code_num
            values.append(item)
    values = sorted(values, key=lambda item: item['code_num']) 
    return values



def print_matched_result(values):
    total = 0
    print("Found %s!" % total)



def main():
    data_list = query_from_jlcsmt()
    values = parse_result(data_list)
    print(len(values))
    pretty_print(values)


if __name__ == '__main__':
    main()
