#!/usr/bin/python3
import os
import sys
import time
import logging
import json

import astm_bidirectional_conf as conf
from astm_file2mssql_bidirectional_general import astm_file

#For mysql password
#see astm_var.py_example
sys.path.append('/var/')
import astm_var

#classes#################################
#mssql is imported from astm_file
class astm_file_sofia(astm_file):
  def manage_final_data(self):
    print_to_log('final_data',self.final_data)
    con=self.get_link(astm_var.my_host,astm_var.my_user,astm_var.my_pass,astm_var.my_db)
    if(con==None):
      return False
    prepared_sql="""
                    insert into astm_dump
                    (o_order_id,  h_equipment_id, astm)
                    values
                    (?,           ?,              ?   )
                    """
    #total ten ? in above sql
    '''
    self.final_data 
    (
      ( '1043972', 
        '', 
        (
          ('P', '1', '', '', '', '', '', '', 'U', '', '', '', '', '', '', '', '0', '0'), 
          ('O', '1', '1043972', '', '^^^GLCC', '', '', '', '', '', '', '', '', '', '', 'SERUM'), 
          ('R', '1', '^^^GLCC', '504', 'mg/dl', '^DEFAULT', 'A', 'N', 'F', '', '', '', '20200928131730'), 
          ('C', '1', 'I', 'Instrument Flag A,A,A,A'), 
          ('L', '1', 'N')
        )
      ),
    )
    '''
    for each_sample in self.final_data:
      self.o_order_id=each_sample[0]      
      self.h_equipment_id=each_sample[1]
      data_tpl=(  self.o_order_id , self.h_equipment_id, json.dumps(each_sample)) 
      try:          
        cur=self.run_query(con,prepared_sql,data_tpl)
        msg=prepared_sql
        print_to_log('prepared_sql:',msg)
        msg=data_tpl
        print_to_log('data tuple:',msg)
        print_to_log('cursor:',cur)
        self.close_cursor(cur)
      except Exception as my_ex:
        msg=prepared_sql
        print_to_log('prepared_sql:',msg)
        msg=data_tpl
        print_to_log('data tuple:',msg)
        print_to_log('exception description:',my_ex)
                            
    self.close_link(con)
    return True
  def get_checksum(self,data):
    checksum=0
    start_chk_counting=False
    for x in data:
      if(x==2):
        start_chk_counting=True
        #Exclude from chksum calculation
        continue

      if(start_chk_counting==True):
        checksum=(checksum+x)%256

      if(x==3):
        start_chk_counting=False
        #Include in chksum calculation
      if(x==23):
        start_chk_counting=False
        #Include in chksum calculation
 
    two_digit_checksum_string='{:X}'.format(checksum).zfill(2)
    return two_digit_checksum_string.encode()
  
def print_to_log(object1,object2):
  logging.debug('{} {}'.format(object1,object2))
  
#Main Code###############################
#use this to device your own script

if __name__=='__main__':
  logging.basicConfig(filename=conf.file2mssql_log_filename,level=logging.DEBUG,format='%(asctime)s : %(message)s')  

  #print('__name__ is ',__name__,',so running code')
  while True:
    m=astm_file_sofia()
    if(m.get_first_inbox_file()):
      m.analyse_file()
      m.mk_tuple()
      if(m.manage_final_data()==True): #specific for each equipment/lis
        m.archive_inbox_file() #comment, useful during debugging
    time.sleep(1)
    #break; #useful during debugging
  


