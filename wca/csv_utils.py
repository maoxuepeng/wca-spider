# -*- coding: utf-8 -*-

# json items to csv file

import json
import csv
import os

head_label = [
    u'公司名称'.encode('utf-8'),
    u'紧急联系方式'.encode('utf-8'),
    u'电子邮箱'.encode('utf-8'),
    u'国家'.encode('utf-8'),
    u'城市'.encode('utf-8'),
    u'电话号码'.encode('utf-8'),
    u'公司网站'.encode('utf-8'),
    u'公司地址'.encode('utf-8'),
    u'传真'.encode('utf-8'),
    u'会员注册日期'.encode('utf-8'),
    u'会员到期日期'.encode('utf-8'),
    u'更多联系方式'.encode('utf-8')
]
head = [
    'name',
    'emergency_call',
    'email',
    'country',
    'city',
    'telephone',
    'website',
    'address',
    'fax',
    'enrolled_since',
    'membership_expires',
    'contact'
]

def json2csv():
    json_file_path = os.getenv('WCA_JSON_FILE_PATH', 'var/data/members-all.json')
    csv_file_path = os.getenv('WCA_CSV_FILE_PATH', 'var/data/members-all.csv')
    if not os.path.isfile(json_file_path):
        return
    
    csv_file_fp = open(csv_file_path, 'wb')
    writer = csv.writer(csv_file_fp, delimiter=',')

    write_head(writer)

    json_data = json.loads(open(json_file_path, 'r').read())
    for data in json_data:
        write_row(writer, data)
    
    csv_file_fp.close()

def write_head(writer):
    writer.writerow(head_label)

def write_row(writer, data):
    row = []
    for k in head:
        v = data.get(k, '')
        if v is None: v = ''
        row.append(v.encode('utf-8'))
    writer.writerow(row)

if __name__ == "__main__":
    json2csv()