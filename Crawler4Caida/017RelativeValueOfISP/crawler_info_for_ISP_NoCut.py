# coding:utf-8
"""
create on Nov 5, 2019 By Wayne Yu
Fun: 全球各国骨干运营商相对价值评估模型数据爬取程序，本程序主要实现信源信息的获取、整理和计算。

1）从alexa网站中爬取，每个国家的前30个信源网站地址；
2）拿着这30个信源的网站地址，去HE网站查询该信源所接入的AS号信息;
3）针对每个AS号，利用CAIDA的全球AS号BGP互联数据，去找他们各自的Peer关系的AS号；
4）最后再去计算获取每个国家的骨干运营商AS网内的信源数量。

需要查询的国家有美国（US）、日本（JP）、印度（IN）、法国（FR）、新加坡（SG）、澳大利亚（AU）、中国香港（HK）、中国（CN）

"""
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import csv
import re


def write_to_csv(res_list, des_path):
    """
    把给定的List，写到指定路径的csv文件中
    :param res_list:
    :param des_path:
    :return None:
    """
    print("write file <%s>..." % des_path)
    csv_file = open(des_path, 'w', newline='', encoding='utf-8')
    try:
        writer = csv.writer(csv_file)
        for i in res_list:
            writer.writerow(i)
    except Exception as e:
        print(e)
    finally:
        csv_file.close()
    print('write finish!')


def obtain_top_sites_by_country(page_url):
    """
    根据每个国家的Alexa TOP Sites页面，获取每个国家top 30的信源
    :param page_url:
    :return top_sites:
    """
    top_sites = []
    # 获取页面信息
    driver.get(page_url)
    time.sleep(1)  # 延迟加载，等待页面内容加载完毕
    # 获取页面的html信息
    page_html = driver.page_source
    bs_obj = BeautifulSoup(page_html, "html.parser")
    # print(bs_obj)
    tr_list = bs_obj.findAll("div", {"class": "tr site-listing"})
    for tr_item in tr_list:
        # print(tr_item.find("a").get_text().lower())
        url_item = tr_item.find("a").get_text().lower()
        top_sites.append(url_item)
    return top_sites[0:50]


def obtain_asn_by_site(page_url):
    """
    根据每个网站的域名，去HE网站获取其接入运营商的AS号
    :param page_url:
    :return access_asn:
    """
    access_asn = []
    # 获取页面信息
    driver.get(page_url)
    time.sleep(3)  # 延迟加载，等待页面内容加载完毕
    # 获取页面html信息
    page_html = driver.page_source
    bs_obj = BeautifulSoup(page_html, "html.parser")
    # print(bs_obj)
    ip_info = bs_obj.find("div", {"id": "ipinfo"})
    ip_info_string = str(ip_info)
    pattern = re.compile(r'>AS\d+<')   # 使用正则表达式，查找页面ip_info中的AS号
    re_return = pattern.findall(ip_info_string)
    for item in re_return:
        item = item[1:-1]
        if item not in access_asn:
            access_asn.append(item)
    return access_asn


if __name__ == "__main__":
    # countries = ["US", "JP", "IN", "FR", "SG", "AU", "HK", "CN"]
    countries = ["FR"]
    # web_url = "https://www.alexa.com/topsites/countries/US"  # 爬虫的入口程序
    time_start = time.time()
    # 启动浏览器
    driver = webdriver.Firefox()
    try:
        countries_top_sites_with_as = []
        for countries_item in countries:
            web_url = "https://www.alexa.com/topsites/countries/" + countries_item
            countries_top_sites = obtain_top_sites_by_country(web_url)
            print("countries top sites:", countries_top_sites)
            print("sleep 10 seconds......")
            time.sleep(10)
            temp_list = []
            cnt_rank = 1
            for sites_url in countries_top_sites:
                temp_list.append(cnt_rank)
                temp_list.append(sites_url)
                request_url = "https://bgp.he.net/dns/" + sites_url + "#_ipinfo"
                print("request_url:", request_url)
                site_access_asn = obtain_asn_by_site(request_url)
                print("site access asn:", site_access_asn)
                for site_access_asn_item in site_access_asn:
                    temp_list.append(site_access_asn_item)
                countries_top_sites_with_as.append(temp_list)
                temp_list = []
                cnt_rank += 1
            print(countries_top_sites_with_as)
            country_string = web_url.split("/")[-1]
            save_path = "./data/top_sites_with_as_(" + country_string + ").csv"
            write_to_csv(countries_top_sites_with_as, save_path)
            countries_top_sites_with_as = []
    except Exception as e:
        print(e)
    # 关闭浏览器
    driver.quit()
    time_end = time.time()
    print("=>Scripts Finish, Time Consuming:", (time_end - time_start), "S")
