import requests
import json


def query_from_jlc():
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

    query_string = "Ω"

    body = '''{"ascFlag":false,"baseQueryDto":{"componentBrandList":null,"componentSpecificationList":["0402"],
    "inStockFlag":true,"isStoryGoods":null,"orderLibraryTypeList":["base"],"packageTypeList":null,"componentTypeIdList":[
    "439"]},"pageVo":{"pageNum":1,"pageSize":20},"paramDtoList":null,"queryString":"kΩ","sortMode":"SALES_VOLUME"}'''
    body = body.encode('utf-8')
    body = json.loads(body)
    body['pageVo']['pageNum'] = 1
    body['pageVo']['pageSize'] = 2000
    body['queryString'] = query_string
    body['baseQueryDto']['componentSpecificationList'][0] = '0603'
    body = json.dumps(body)

    rc = s.post(url, headers=headers, cookies=cookies, data=body)
    response_json = json.loads(rc.content)
    data_list = response_json['data']['data']
    # print(data_list)
    return data_list


def parse_result(data_list):
    values = []
    for item in data_list:
        name = item['componentName']
        code = item['componentCode']
        if 'Ω' in name:
            value = name.split('Ω')[0].split(' ')[-1]
            scale = 1
            if value.endswith('K') or value.endswith('k'):
                scale = 1000
                value = value[:-1]
            elif value.endswith('M') or value.endswith('m'):
                scale = 1000 * 1000
                value = value[:-1]
                continue
            else:
                continue
            value = float(value) * scale
            if value != 0:
                values.append((value, code))
    print(values)
    return values


target_v_out = 3.3
v_error = 0.1
v_ref = 0.5


def print_matched_result(values):
    total = 0
    for r1, code1 in values:
        for r2, code2 in values:
            v_out = v_out_calc(r1, r2, v_ref)
            if match_v_out(v_out) and r2>100*1000:
                feedback_current = v_out / (r1 + r2) * 1000 * 1000
                # noinspection SpellCheckingInspection
                print(
                    "R1 = {:.0f}Ω {}, R2 = {:.0f}Ω {}, Vout = {:.3f} V, Current = {:.3f} μA".format(r1, code1, r2, code2,
                                                                                                  v_out,
                                                                                                  feedback_current))
                total += 1
    print("Found %s value pair!" % total)


# 电压输出公式
def v_out_calc(r1, r2, ref):
    return ref * (1 + r1 * 1.0 / r2)


def match_v_out(real_v_out):
    error = abs(real_v_out - target_v_out)
    return error <= v_error


def main():
    data_list = query_from_jlc()
    values = parse_result(data_list)
    print_matched_result(values)


if __name__ == '__main__':
    main()
