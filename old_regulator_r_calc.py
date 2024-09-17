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

    body = '''{"ascFlag":true,"baseQueryDto":{"componentBrandList":[],"componentSpecificationList":["0603"],"componentTypeIdList":[439],"preferredComponentFlagList":["false"],"orderLibraryTypeList":["base"],"packageTypeList":[],"productTypeIdList":[308],"inStockFlag":true},"groupFlag":false,"pageVo":{"pageNum":1,"pageSize":10},"paramDtoList":[],"queryString":"","sortMode":"COMPREHENSIVE"}'''
    body = body.encode('utf-8')
    body = json.loads(body)
    body['pageVo']['pageNum'] = 1
    body['pageVo']['pageSize'] = 30
    body['queryString'] = query_string
    body['baseQueryDto']['componentSpecificationList'][0] = '0603'
    body = json.dumps(body)

    rc = s.post(url, headers=headers, cookies=cookies, data=body)
    response_json = json.loads(rc.content)
    data_list = response_json['data']['data']
    print(json.dumps(data_list))
    print(len(data_list))
    return data_list

def extract_resistance_values(text):  
    # Regular expression to match resistance values  
    pattern = r'(\d+(\.\d+)?)([kKmM]?)Ω'  
    matches = re.findall(pattern, text)  
    
    # Convert matches to a list of resistance values  
    resistance_values = []  
    for match in matches:  
        value, _, unit = match  
        value = float(value)  
        if unit.lower() == 'k':  
            value *= 1000  
        elif unit.lower() == 'm':  
            value *= 1000000  
        resistance_values.append(value)  
    
    return resistance_values  

def parse_result(data_list):
    values = []
    for item in data_list:
        name = item['componentName']
        code = item['componentCode']
        print(name)
        if 'Ω' in name:
            r_val = extract_resistance_values(name)
            values.append((r_val, code))
    print(values)
    return values


target_v_out = 5.1
v_error = 0.1
v_ref = 0.6


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
