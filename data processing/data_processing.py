import sys
import csv
import os
import operator
from datetime import datetime
from datetime import timedelta
from numpy import mean
import math






#select file function:
def select_file():
	#list the files in the input files folder
	input_file_list = os.listdir("input files")
	for f_index in range(0,len(input_file_list)):
		print(str(f_index+1)+": "+input_file_list[f_index])

	need_input = True
	#until valid selection:
	while(need_input):
		print("Enter the number that corrsponds to the file you want to work with: (1 for the first file):")
		user_input = input("")
		print("_")
		print("")
			

		try:
			file_index = int(user_input)-1
		except:
			print("Invalid Input!")

		if(file_index < len(input_file_list) and file_index >= 0):
			need_input = False
			return input_file_list[file_index]
		else:	
			print("Number entered is out of valid range") 




#Load Function:
def load_file_data(f_name,minimum_ms = 100,maximum_ms = 499):
	#NOTE MSE - The range includes 100ms - 499ms. Anything from 500 (including 500) is removed! 

	session_dict = {}

	session_keys = {}

	file_total_records = 0
	
	#open the file
	reader = csv.reader(open("input files/"+f_name), delimiter=",")


	sorted_data = sorted(reader, key= lambda x: (x[0],x[2],datetime.strptime(x[3], '%d/%m/%Y %H:%M:%S')))

	#for each row:
	for record in sorted_data:
		
		file_total_records += 1
		#if the trial name isn't in the session_dict:
		if(not(record[0] in session_dict)):
			session_keys[len(session_dict)] = record[0] #add the session name to the key dict with the key = to the length of the session dict	
			session_dict[record[0]] = [[],0,0,0,0,[]] #add a list in the format [[],0,0,0,0,[]] = (the trial list, the practise counter,the under removals,the over removals,total records pre removal,results including lapses) with key of the session name in the session dict
		
		
		#include record in total count
		session_dict[record[0]][4] += 1

		keep_result = True
		lapse_result = False
		#if the type is practise add to the practise counter in the relevent session tuple
		if(record[6] == "Practise" or record[6] == "0"):
			session_dict[record[0]][1] += 1
			keep_result = False
		else:
			#else if the check if the trial time is within acceptable bounds, if not increment the relevenet counter
			if(int(record[4]) < minimum_ms):
				session_dict[record[0]][2] += 1
				keep_result = False

			if(int(record[4]) > maximum_ms):
				session_dict[record[0]][3] += 1
				keep_result = False
				lapse_result = True

		#if it is add the record to the session list in the session_dict
		if(keep_result):
			session_dict[record[0]][0].append(record)

		if(keep_result or lapse_result):
			session_dict[record[0]][5].append(record)


	return file_total_records,session_keys,session_dict

#Choose Session Function:

def choose_session(total_records,session_keys,session_dict,f_name):
	
	
	more_session = True
	#until no more sessions:
	while(more_session):
		#display the session keys, names and data
		print("Total Records in file: "+str(total_records))
		print("Fromating: [Session Name] - [Ommited due to practise] - [Ommited due to anticipation] - [Ommited due to lapse] - [Total records pre-ommisions]")

		for key_index in range(0,len(session_keys)):
			session_name = session_keys[key_index]
			print(str(key_index+1)+": "+session_name+" - "+str(session_dict[session_name][1])+" - "+str(session_dict[session_name][2])+" - "+str(session_dict[session_name][3])+" - "+str(session_dict[session_name][4]))
		
		need_input = True
		#until the user enters a valid input:
		while(need_input):
			#ask the user to choose a session
			print("Enter the number that corrsponds to the session you want to work with (1 for the first session) or enter 'q' to exit: ")
			user_input = input("")
			print("_")
			print("")
			

			#if they typed q , exit
			if(user_input == "q"):
				need_input = False
				more_session = False
			else:	
				try:
					session_index = int(user_input)-1
				except:
					print("Invalid Input!")
				
				if(session_index < len(session_keys) and session_index >= 0):
					need_input = False
					session_name = session_keys[session_index]
					more_session = generate_outputs(session_name,session_dict[session_name][0],f_name,session_dict[session_name][5])
				else:	
					print("Number entered is out of valid range") 
		
#Choose Output Function:		
def generate_outputs(session_name,data_list,f_name,data_inc_lapses):
	output_types = ["5 minute intervals(max 25 minutes)","1 Minute intervals up to 10 minutes","5 minute intervals, slowst and fastest 10%","Number of Lapses: 1 Minute intervals up to 10 minutes","1 Minute intervals up to 25 minutes","Number of Lapses: 1 Minute intervals up to 25 minutes","Number of Lapses: 5 Minute intervals up to 25 minutes"]


	#print(data_list)		

	more_outputs = True
	#until no more sessions:
	while(more_outputs):
		#display the output keys
		for format_index,format in enumerate(output_types):
			print(str(format_index+1)+": "+format)

		need_input = True
		#until the user enters a valid input:
		while(need_input):
			#ask the user for a format of out put
			print("Enter the corresponding number for the data output desired or q to quit")

			user_input = input("")
			print("_")
			print("")

			if(user_input == "q"):
				need_input = False
				more_outputs = False
				return False
			else:	
				try:
					format_index = int(user_input)-1
				except:
					print("Invalid Input!")
				
				if(format_index < len(output_types) and format_index >= 0):
					need_input = False
					
					if(format_index == 0):
						output_5min_intervals(session_name,data_list,f_name)
						
					elif(format_index == 1):
						output_1min_intervals(session_name,data_list,f_name)

					elif(format_index == 2):
						output_percentage_5min_intervals(session_name,data_list,f_name)

					elif(format_index == 3):
						output_lapses_1min_intervals(session_name,data_inc_lapses,f_name,lapse_limit=499)

					elif(format_index == 4):
						output_1min_intervals_over_25mins(session_name,data_list,f_name)
					
					elif(format_index == 5):
						output_lapses_1min_intervals_over_25mins(session_name,data_inc_lapses,f_name,lapse_limit=499)
					
					elif(format_index == 6):
						output_lapses_5min_intervals_over_25mins(session_name,data_inc_lapses,f_name,lapse_limit=499)
					
					else:
						need_input = True
						print("Number entered is out of valid range") 

				else:	
					print("Number entered is out of valid range") 

		need_input = True
		#until the user enters a valid input:
		while(need_input):
			#ask user is they like to process another output , another session , or quit
			print("Would you like to (enter the corresponding number):")
			print("1: generate another output")
			print("2: change to another session")
			print("3/q: quit")

			user_input = str(input(""))
			print("_")
			print("")
			
			#if quit, return false
			if(user_input == "q"):
				need_input = False
				more_outputs = False
				return False
			else:	
				try:
					action_index = int(user_input)
				except:
					print("Invalid Input!")
				
				if(action_index < 4 and action_index >= 1):
					need_input = False
					
					#more output
					if(action_index == 1):
						need_input = False
					#different session
					elif(action_index == 2):
						need_input = False
						more_outputs = False
						return True
					#quit
					elif(action_index == 3):
						need_input = False
						more_outputs = False
						return False
					#invalid number
					else:
						need_input = True
						print("Number entered is out of valid range") 

				else:	
					print("Number entered is out of valid range") 
	
	
		
def output_5min_intervals(session_name,records,f_name):

	output_filename = session_name+"_5min.csv"

	intervaled_dict = generate_intervaled_records(records,5,5)
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id', '5', '10', '15', '20', '25']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]
			#print(participant_id)
			#print(current_record)
			writer.writerow({'participant_id':participant_id, '5':str(mean(current_record[1])), '10':str(mean(current_record[2])), '15':str(mean(current_record[3])), '20':str(mean(current_record[4])), '25':str(mean(current_record[5]))})
		

	print("Output saved as "+output_filename)		

def output_1min_intervals(session_name,records,f_name):
	
	output_filename = session_name+"_1min.csv"

	intervaled_dict = generate_intervaled_records(records,1,10)
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
		
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]
			#print(participant_id)
			#print(current_record)
			writer.writerow({'participant_id':participant_id, '1':str(mean(current_record[1])), '2':str(mean(current_record[2])), '3':str(mean(current_record[3])), '4':str(mean(current_record[4])), '5':str(mean(current_record[5])), '6':str(mean(current_record[6])), '7':str(mean(current_record[7])), '8':str(mean(current_record[8])), '9':str(mean(current_record[9])), '10':str(mean(current_record[10]))})


	print("Output saved as "+output_filename)


def output_1min_intervals_over_25mins(session_name,records,f_name):
	
	output_filename = session_name+"_1min_over25min.csv"

	intervaled_dict = generate_intervaled_records(records,1,25)
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id']

		fieldnames += [str(i) for i in range(1,26)]
		
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]
			#print(participant_id)
			#print(current_record)
			row_dict = {'participant_id':participant_id}

			for i in range(1,26):

				if(len(current_record[i])):
					row_dict[str(i)] = str(mean(current_record[i]))
				else:
					row_dict[str(i)] = "0"

			writer.writerow(row_dict)

def output_percentage_5min_intervals(session_name,records,f_name):
	output_filename = session_name+"_percentages.csv"

	intervaled_dict = generate_intervaled_records(records,1,10)
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id', '5 slowest 10%', '5 fastest 10%', '10 slowest 10%', '10 fastest 10%', '15 slowest 10%', '15 fastest 10%', '20 slowest 10%', '20 fastest 10%', '25 slowest 10%', '25 fastest 10%']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]
			#print(participant_id)
			#print(current_record)
			writer.writerow({'participant_id':participant_id, '5 slowest 10%':calc_slowest_fastest_means(current_record[1]), '5 fastest 10%':calc_slowest_fastest_means(current_record[1],False), '10 slowest 10%':calc_slowest_fastest_means(current_record[2]), '10 fastest 10%':calc_slowest_fastest_means(current_record[2],False), '15 slowest 10%':calc_slowest_fastest_means(current_record[3]), '15 fastest 10%':calc_slowest_fastest_means(current_record[3],False), '20 slowest 10%':calc_slowest_fastest_means(current_record[4]), '20 fastest 10%':calc_slowest_fastest_means(current_record[4],False), '25 slowest 10%':calc_slowest_fastest_means(current_record[5]), '25 fastest 10%':calc_slowest_fastest_means(current_record[5],False)})


	print("Output saved as "+output_filename)


def output_lapses_1min_intervals(session_name,records,f_name,lapse_limit=499):
	#NOTE MSE - Anything from 501 is removed! 
	

	output_filename = session_name+"_lapses_1min.csv"

	intervaled_dict = generate_intervaled_records(records,1,10)
	
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]
			#print(participant_id)
			#print(current_record)
			print(current_record[1])
			writer.writerow({'participant_id':participant_id, '1': str(get_lapses(current_record[1],lapse_limit)), '2':str(get_lapses(current_record[2],lapse_limit)), '3':str(get_lapses(current_record[3],lapse_limit)), '4':str(get_lapses(current_record[4],lapse_limit)), '5':str(get_lapses(current_record[5],lapse_limit)), '6':str(get_lapses(current_record[6],lapse_limit)), '7':str(get_lapses(current_record[7],lapse_limit)), '8':str(get_lapses(current_record[8],lapse_limit)), '9':str(get_lapses(current_record[9],lapse_limit)), '10':str(get_lapses(current_record[10],lapse_limit))})

def output_lapses_1min_intervals_over_25mins(session_name,records,f_name,lapse_limit=499):
	

	output_filename = session_name+"_lapses_1min_over_25mins.csv"

	intervaled_dict = generate_intervaled_records(records,1,25)
	
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id']

		fieldnames += [str(i) for i in range(1,26)]
		
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]

			row_dict = {'participant_id':participant_id}

			for i in range(1,26):

				if(len(current_record[i])):
					row_dict[str(i)] = str(get_lapses(current_record[i],lapse_limit))
				else:
					row_dict[str(i)] = "0"

			writer.writerow(row_dict)

	print("Output saved as "+output_filename)


def output_lapses_5min_intervals_over_25mins(session_name,records,f_name,lapse_limit=499):
	output_filename = session_name+"_lapses_5min_over_25mins.csv"

	intervaled_dict = generate_intervaled_records(records,5,5)
	
	with open('output files/'+f_name+" "+output_filename, 'w') as csvfile:
		fieldnames = ['participant_id']

		fieldnames += [str(i) for i in range(5,26,5)]
		
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,lineterminator='\n')
		writer.writeheader()

		sorted_ids = sorted(intervaled_dict.keys())

		for participant_id in sorted_ids:
			
			current_record = intervaled_dict[participant_id]

			row_dict = {'participant_id':participant_id}

			for i in range(1,6):

				if(len(current_record[i])):
					row_dict[str(i*5)] = str(get_lapses(current_record[i],lapse_limit))
				else:
					row_dict[str(i*5)] = "0"

			writer.writerow(row_dict)

	print("Output saved as "+output_filename)


def get_lapses(data,lapse_limit):
	return len([x for x in data if x > lapse_limit])

def calc_slowest_fastest_means(trials,slowest=True):

	if(slowest):
		return mean(sorted(trials)[(-percent_slice_length):])
	else:
		return mean(sorted(trials)[0:percent_slice_length])
	
	


def generate_intervaled_records(records,interval_mins,max_intervals):
	particpant_dict = {}

	for record in records:
		participant_id = record[2]
		datetime_date = datetime.strptime(record[3], '%d/%m/%Y %H:%M:%S')

		if(not(participant_id in particpant_dict)):
			particpant_dict[participant_id] = [datetime_date]
			for interval_index in range(0,max_intervals):
				particpant_dict[participant_id].append([])

		start_time = particpant_dict[participant_id][0]

		for interval_count in range(1,(max_intervals+1)):
			time_d = timedelta(minutes=interval_count*interval_mins)

			if(datetime_date < (start_time + time_d)):
				particpant_dict[participant_id][interval_count].append(int(record[4]))
				break

	return particpant_dict






#main:

file_name = select_file()

total_records,session_keys,session_dict = load_file_data(file_name)

choose_session(total_records,session_keys,session_dict,file_name.replace(".csv",""))
