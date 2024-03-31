import os
import shutil
import datetime
import time

# Function to print banner
def print_banner():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     Splunk Frozen Buckets Rebuilder Script       ║
    ╚══════════════════════════════════════════════════╝
    """)

# Print banner
print_banner()

# Directory path grabbing
frozendb_path=input("[+] Please enter Frozen Directory path: ")
print("[-] Entered Frozen Directory path: "+frozendb_path)
thaweddb_path=input("\n[+] Please enter Thawed Directory path: ")
print("[-] Entered Thawed Directory path: "+thaweddb_path)

# Date grabbing and epoch conversions
earliest_input=input("\n[+] Please enter earliest date for bucket to be pulled(eg: 2021/12/7): ")
print("[-] Entered earliest date: "+earliest_input)
date_time = datetime.datetime(int(earliest_input.split("/")[0]),int(earliest_input.split("/")[1]),int(earliest_input.split("/")[2]))
earliest_input_epoch= int(time.mktime(date_time.timetuple()))
print("[-] Entered earliest date(epoch): "+str(earliest_input_epoch))

latest_input=input("\n[+] Please enter latest date for bucket to be pulled(eg: 2022/5/20): ")
print("[-] Entered latest date: "+latest_input)
date_time = datetime.datetime(int(latest_input.split("/")[0]),int(latest_input.split("/")[1]),int(latest_input.split("/")[2]))
latest_input_epoch= int(time.mktime(date_time.timetuple()))
print("[-] Entered latest date(epoch): "+str(latest_input_epoch))

start = time.perf_counter()

# Grabbing buckets from FrozenDB found in between mentioned time frame
files_frozen = os.listdir(frozendb_path)
found_file=list()

for file in files_frozen:
    time_calculator = file.split("_")
    earliest = int(time_calculator[2])
    latest = int(time_calculator[1])
    
    if (earliest_input_epoch<earliest<latest_input_epoch) and (earliest_input_epoch<latest<latest_input_epoch):
        found_file.append(file)
print("\n[+] Found "+str(len(found_file))+" buckets from FrozenDB in between "+earliest_input+" & "+latest_input)

# Checking for already build buckets in thaweddb
if len(found_file) > 0:
    previously_thawed_files=os.listdir(thaweddb_path)
    print("\n[+] Found "+str(len(previously_thawed_files))+" buckets in ThawedDB")
    print("[+] Checking for overlapping build buckets")
    count=0
    for file in previously_thawed_files:
        file = file.replace("inflight-","")
        if (file in found_file):
            found_file.remove(file)
            count = count + 1
    print("[+] Removed "+str(count)+" overlapping buckets from the found buckets in FrozenDB")

if len(found_file) > 0:
    # Coping & Pasting from frozendb to thaweddb
    print("\n[+] Need to Build "+str(len(found_file))+" buckets from FrozenDB in between "+earliest_input+" & "+latest_input)
    print("\n[+] Coping "+str(len(found_file))+" buckets from FrozenDB path: "+frozendb_path)
    for dir in found_file:
        copy_from = frozendb_path+dir
        command = "cp -R "+copy_from+" "+thaweddb_path
        os.system(command)
    print("[+] Copied "+str(len(found_file))+" buckets to ThawedDB path: "+thaweddb_path)
    
# Rebuilding the buckets
if len(found_file) > 0:
    print("\n[+] Rebuilding buckets...")
    count=1
    for dir in found_file:
        print("\n [+] Building bucket "+str(count)+"/"+str(len(found_file))+" , BucketID: "+dir)
        command = "/opt/splunk/bin/splunk rebuild "+thaweddb_path+dir
        count = count + 1
        os.system(command)
        
# Restarting Splunk
if len(found_file) > 0:
    print("\n[+]Restarting Splunk...")
    command = "/opt/splunk/bin/splunk restart"
    os.system(command)

end= time.perf_counter()
print(f'Finished in {round(end-start,2)}seconds')
