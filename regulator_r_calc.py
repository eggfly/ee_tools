import requests  
import json  
import time
import re
import brotli

def get_jlc_session(packaging: str, pageNum: int, isFreeExtendLib: bool):
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
        'Origin': 'https://www.jlc-smt.com',  
        'Host': 'www.jlc-smt.com',
        'Referer': 'https://www.jlc-smt.com/',
        'x-xsrf-token': '98ccc5b1-114a-47f6-9fa6-f459e3ed0acd'
    }  

    url = 'https://www.jlc-smt.com/api/smtComponentOrder/componentSearchController/selectPasteComponentList'  
    # ascFlag -> ?
    # 构建请求体
    body = {
        "ascFlag": False,
        "baseQueryDto": {
            "componentBrandList": [],
            "componentSpecificationList": [packaging],  # 使用传入的包装规格
            "componentTypeIdList": [439],  # 电阻类型
            "preferredComponentFlagList": ["true"] if isFreeExtendLib else ["false"],
            "orderLibraryTypeList": ["expand"] if isFreeExtendLib else ["base"],
            "packageTypeList": [],
            "productTypeIdList": [308],
            "inStockFlag": False
        },
        "groupFlag": False,
        "pageVo": {
            "pageNum": pageNum,
            "pageSize": 10
        },
        "paramDtoList": [],
        "queryString": "",
        "sortMode": "COMPREHENSIVE"
    }
    return s, url, body

def get_component_list(packaging: str, isFreeExtendLib: bool):
    results = []
    pageNum = 1
    while True:
        s, url, body = get_jlc_session(packaging, pageNum, isFreeExtendLib)
        response = s.post(url, json=body)
        print('pageNum:', pageNum)
        pageNum += 1
        if response.status_code != 200:
            print(f"Failed to query, status code: {response.status_code}")
            break  
        try:
            # 检查是否是 Brotli 压缩
            if response.headers.get('content-encoding') == 'br':
                # 手动解压 Brotli 内容
                try:
                    decompressed_content = brotli.decompress(response.content)
                    response_text = decompressed_content.decode('utf-8')
                    response_json = json.loads(response_text)
                except brotli.error:
                    # 如果 Brotli 解压失败，尝试直接解析响应文本
                    response_json = response.json()
            else:
                response_json = response.json()
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content: {response.text}")
            break  
        if response_json.get('code') != 200:
            print(f"Failed to query, response: {response_json}")
            break
        data = response_json['data']  
        data_list = data['data']
        print(len(data_list))
        if not data_list:
            print("No more data")
            break
        results.extend(data_list)  
        time.sleep(0.01)
    print(f"Total items collected: {len(results)}")  
    return results

def query_from_jlc():
    results = []
    # results += get_component_list('1206')
    # results += get_component_list('0805')
    results += get_component_list('0402', False)
    results += get_component_list('0402', True)
    # results += get_component_list('0603', False)
    # results += get_component_list('0603', True)
    return results

def extract_resistance_values(text):  
    # Regular expression to match resistance values  
    pattern = r'(\d+(\.\d+)?)([kKmM]?)Ω'  
    matches = re.findall(pattern, text)  
    
    # Convert matches to a list of tuples containing resistance values and full strings  
    for match in matches:  
        value, _, unit = match  
        full_string = f"{value}{unit}Ω"  
        value = float(value)  
        if unit.lower() == 'k':  
            value *= 1000  
        elif unit.lower() == 'm':  
            value *= 1000000  
        return value, full_string
    return (None, None)

def parse_result(data_list):  
    values = []  
    for item in data_list:  
        name = item['componentName']  
        code = item['componentCode']
        spec = item['componentSpecification']
        # print(name)
        if 'Ω' in name:
            r_val, full_str = extract_resistance_values(name)
            info = {'value': r_val, 'code':code, 'full': full_str, 'spec': spec}
            values.append(info)
            print(info)
    print('value count:', len(values))
    return values  


target_v_out = 4.6
v_error = 0.3
v_ref = 0.55

def match_extra(r2):
    return r2 > 10 * 1000

def print_matched_result(values):
    total = 0
    for v1 in values:
        r1 = v1['value']
        code1 = v1['code']
        full_str1 = v1['full']
        spec1 = v1['spec']
        for v2 in values:
            r2 = v2['value']
            code2 = v2['code']
            full_str2 = v2['full']
            spec2 = v2['spec']
            if r2 == 0:
                continue
            v_out = v_out_calc(r1, r2, v_ref)
            if match_v_out(v_out) and match_extra(r2):
                feedback_current = v_out / (r1 + r2) * 1000 * 1000
                # noinspection SpellCheckingInspection
                print(
                    "R1 = {:.0f}Ω {} {}({}), R2 = {:.0f}Ω {} {}({}), Vout = {:.3f} V, Current = {:.3f} μA".format(r1, code1, full_str1, spec1, r2, code2, full_str2, spec2,
                                                                                                    v_out, feedback_current))
                total += 1
    print("Found %s value pair!" % total)


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
