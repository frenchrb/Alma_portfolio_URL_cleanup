import configparser
import json
import requests
import sys
import time
import xlrd
import xlwt
import xlutils.copy
from threading import Thread
from queue import Queue
from time import sleep
from ratelimit import limits, sleep_and_retry

# Read config file
config = configparser.ConfigParser()
config.read('local_settings.ini')
key = config['Alma Bibs R/W']['key']

num_worker_threads = 15
work_queue = Queue()
output_queue = Queue()

portID_col_index = 1
bibID_col_index = 2
getport_col_index = 3
existing_url_col_index = 4
updateport_col_index = 5
new_url_col_index = 6

@sleep_and_retry
@limits(calls=15, period=1)
def api_request(type, port, json=None):
    if type == 'get':
        headers = {'accept':'application/json'}
        response = requests.get('https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/'+port['bibID']+'/portfolios/'+port['portID']+'?apikey='+key, headers=headers)
        return response
    if type == 'put':
        headers = {'accept':'application/json', 'Content-Type':'application/json'}
        response = requests.put('https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/'+port['bibID']+'/portfolios/'+port['portID']+'?apikey='+key, headers=headers, data=json)
        return response

def worker():
    while True:
        port = work_queue.get()
        output = []
        get_response = api_request('get', port)
        output.append((port['row'], getport_col_index, get_response.status_code))
        
        if get_response.status_code == 200:
            port_json = get_response.json()
            url = port_json['linking_details'].get('url')
            url_type = port_json['linking_details'].get('url_type').get('value')
            url_type_override = port_json['linking_details'].get('url_type_override').get('value')
            static_url = port_json['linking_details'].get('static_url')
            static_url_override = port_json['linking_details'].get('static_url_override')
            output.append((port['row'], existing_url_col_index, static_url_override))
            
            new_url = static_url_override
            port_json['linking_details'].update({'url': new_url})
            port_json['linking_details'].update({'static_url': new_url})
            port_json['linking_details'].update({'static_url_override': ''})
            
            put_response = api_request('put', port, json.dumps(port_json))
            output.append((port['row'], updateport_col_index, put_response.status_code))
            output.append((port['row'], new_url_col_index, new_url))
                
        output_queue.put(output)
        print(port['row'], port['portID'])
        work_queue.task_done()
        

def out_worker(book_in, input):
    # Copy spreadsheet for output
    book_out = xlutils.copy.copy(book_in)
    sheet_out = book_out.get_sheet(0)
    
    # Add new column headers
    sheet_out.write(0,existing_url_col_index,'Existing_URL')
    sheet_out.write(0,getport_col_index,'Get_Port')
    sheet_out.write(0,updateport_col_index,'Update_Port')
    sheet_out.write(0,new_url_col_index,'New_URL')
    
    while True:
        ports = output_queue.get()
        for port in ports:
            sheet_out.write(port[0], port[1], port[2])
        book_out.save(input+'_results.xls')
        output_queue.task_done()

def main(input):
    st = time.localtime()
    start_time = time.strftime("%H:%M:%S", st)
   
    # Read spreadsheet
    book_in = xlrd.open_workbook(input)
    sheet1 = book_in.sheet_by_index(0) # get first sheet
    
    Thread(target=out_worker, args=(book_in, input,), daemon=True).start()
    for i in range(num_worker_threads):
        Thread(target=worker, daemon=True).start()

    for row in range(1, sheet1.nrows):
        port = {}
        port['row'] = row
        port['bibID'] = sheet1.cell(row, bibID_col_index).value
        port['portID'] = sheet1.cell(row, portID_col_index).value
        work_queue.put(port)

    work_queue.join()
    output_queue.join()

    et = time.localtime()
    end_time = time.strftime("%H:%M:%S", et)
    print('Start Time: ', start_time)
    print('End Time: ', end_time)   

if __name__ == '__main__':
    main(sys.argv[1])
    